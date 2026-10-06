# Diagnóstico y Tuning de Bases de Datos Asistido por IA

Laboratorio académico local con PostgreSQL, OpenMetadata, Ollama y telemetría Promtail/Loki/Grafana. Demuestra el ciclo completo: observar una consulta, enriquecer su contexto con el catálogo, pedir un diagnóstico al modelo y validar un cambio de índice con revisión humana.

## Qué se demuestra

| Componente | Función en la exposición |
|---|---|
| PostgreSQL 16 | Ejecuta la consulta y produce `EXPLAIN (ANALYZE, BUFFERS)` |
| Promtail → Loki → Grafana | Muestra logs de PostgreSQL y actividad durante el experimento |
| OpenMetadata 2.0.3 | Ingiere el esquema PostgreSQL y cataloga tablas/columnas |
| `scripts/ai_db_tuning.py` | Envía al modelo el plan real y el contexto obtenido de OpenMetadata |
| Ollama | Ejecuta el modelo localmente, sin clave de API externa |
| Rol MSP/DBA | Revisa y aprueba la recomendación, mide el resultado y conserva una reversa |

El MSP se representa como un proceso operativo, no como otro contenedor. El laboratorio aplica un índice fijo conocido; nunca ejecuta DDL libre generado por la IA.

## Archivos principales

- [Presentación](presentacion/Presentacion_Diagnostico_IA_OpenMetadata_MSP_Final.pptx)
- [Guía y guion de laboratorio](GUIA_DIAGNOSTICO_IA_OPENMETADATA_MSP.md)
- [Agente de diagnóstico](scripts/ai_db_tuning.py)
- [Compose oficial OpenMetadata 2.0.3](openmetadata/docker-compose.yml)
- [SQL para crear el lector PostgreSQL](openmetadata/create_reader.sql)

## Requisitos

- Docker Desktop en modo contenedores Linux y Docker Compose v2.
- Python 3.10 o superior, disponible como `py` en PowerShell.
- Ollama instalado y un modelo descargado. `llama3.1` funciona; un modelo 3B puede responder más rápido si Docker y Ollama compiten por memoria.
- Varios GB libres para imágenes y modelo. OpenMetadata añade MySQL, Elasticsearch, su servidor y el servicio de ingesta.

Los valores por defecto de Compose son únicamente para laboratorio local; no se deben reutilizar en producción. Los puertos publicados están limitados a `localhost`. No expongas estos servicios ni sus credenciales de demostración a Internet.

## Puesta en marcha

Ejecuta los comandos desde la raíz del repositorio en PowerShell. El primer inicio puede descargar varias imágenes.

1. Inicia la base y la telemetría:

   ```powershell
   docker compose up -d
   docker compose ps
   ```

   El Compose usa una red estable compartida con OpenMetadata. Al actualizar la configuración Docker puede recrear contenedores; los volúmenes PostgreSQL, Loki y Grafana se conservan. No uses `down -v`.

2. Inicia OpenMetadata:

   ```powershell
   docker compose -f .\openmetadata\docker-compose.yml up -d
   docker compose -f .\openmetadata\docker-compose.yml ps
   ```

   Espera a que `openmetadata-server`, `mysql`, `elasticsearch` e `ingestion` estén activos. La primera carga puede tardar unos minutos. Abre [http://localhost:8585](http://localhost:8585); para el quickstart local, las credenciales iniciales son `admin@open-metadata.org` / `admin`.

3. Comprueba que hay datos:

   ```powershell
   docker exec db-primary psql -U admin_db -d banco_telemetria -c "SELECT count(*) AS transacciones FROM transacciones;"
   docker exec db-primary psql -U admin_db -d banco_telemetria -c "SELECT count(*) AS cuenta_1520 FROM transacciones WHERE cuenta_id = 1520;"
   ```

   En un volumen nuevo, `postgres/init/01_init.sql` genera una carga grande automáticamente. Si la cuenta de prueba no tiene transacciones, genera datos **una sola vez**:

   ```powershell
   docker exec db-primary psql -U admin_db -d banco_telemetria -c "SELECT poblar_datos_sinteticos(25000);"
   ```

## Conectar PostgreSQL a OpenMetadata

Usa un usuario dedicado de solo lectura; no uses `admin_db` en el conector.

1. Crea una contraseña local y aplica los permisos. PowerShell la solicita sin mostrarla; no la compartas ni la guardes en Git:

   ```powershell
   $securePassword = Read-Host "Contraseña local para openmetadata_reader" -AsSecureString
   $env:OPENMETADATA_DB_PASSWORD = [System.Net.NetworkCredential]::new("", $securePassword).Password
   Get-Content -Raw .\openmetadata\create_reader.sql | docker exec -i db-primary psql -U admin_db -d banco_telemetria -v "reader_password=$env:OPENMETADATA_DB_PASSWORD" -f -
   Remove-Item Env:OPENMETADATA_DB_PASSWORD
   ```

2. En OpenMetadata abre **Settings → Services → Database Services → Add Service → PostgreSQL**. Usa:

   | Campo | Valor |
   |---|---|
   | Service name | `postgresql_demo` |
   | Host | `db-primary` |
   | Port | `5432` |
   | Database | `banco_telemetria` |
   | Username | `openmetadata_reader` |
   | Password | La que acabas de crear |
   | SSL | Desactivado solo para este laboratorio local |

   Prueba la conexión, conserva el workflow **Metadata**, pulsa **Create & Deploy** y espera a que la ingesta termine correctamente. El nombre del servicio forma parte del FQN y no debe cambiar luego.

3. Abre la tabla `postgresql_demo.banco_telemetria.public.transacciones`. Para que el contexto se vea en la demo, añade una descripción y, si deseas, propietario o etiquetas.

## Configurar Ollama y el agente

Comprueba Ollama:

```powershell
ollama list
```

Si PowerShell no reconoce `ollama`, abre una terminal nueva o usa la ruta habitual de Windows:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list
```

El servidor normalmente lo inicia la aplicación de Ollama. No ejecutes `ollama serve` si `http://localhost:11434` ya responde. Descarga un modelo si aún no aparece:

```powershell
ollama pull llama3.1
```

En la terminal donde correrá el agente, configura el modelo y OpenMetadata:

```powershell
$env:AI_PROVIDER = "ollama"
$env:OLLAMA_MODEL = "llama3.1:latest"
$env:OLLAMA_NUM_PREDICT = "512"
$env:AI_TIMEOUT_SECONDS = "300"
$env:OPENMETADATA_URL = "http://localhost:8585/api"
$env:OPENMETADATA_TABLE_FQN = "postgresql_demo.banco_telemetria.public.transacciones"
$env:OPENMETADATA_JWT_TOKEN = (Get-Clipboard -Raw).Trim()
```

Antes de ejecutar el bloque, abre **Settings → Bots → IngestionBot**, genera un token con vencimiento de 7 días y usa el botón de copiar del campo **OpenMetadata JWT Token**. `Get-Clipboard` lo pone solo en la sesión actual; no lo pegues en el chat ni lo imprimas en la terminal. Revócalo después de la exposición. El agente solo lo usa para leer el contexto de la tabla.

Ejecuta el diagnóstico integrado, sin cambiar la base:

```powershell
py .\scripts\ai_db_tuning.py --provider ollama --use-openmetadata
```

La terminal debe indicar `CONTEXTO DE ESQUEMA: OpenMetadata`, mostrar el FQN y las columnas recibidas, y luego el plan y análisis del modelo. Grafana muestra los logs en paralelo en [http://localhost:3000](http://localhost:3000) (`admin/admin`).

## Tuning controlado

Después de revisar el diagnóstico, ejecuta:

```powershell
py .\scripts\ai_db_tuning.py --provider ollama --use-openmetadata --apply-demo-index
```

El agente vuelve a medir la línea base, consulta catálogo e IA, aplica únicamente `idx_ai_demo_transacciones_cuenta_fecha` sobre `(cuenta_id, fecha_hora DESC)` y muestra plan, buffers y mediana antes/después. El índice puede acelerar este patrón, pero cuesta espacio y trabajo adicional en escrituras. El resultado depende de caché y carga.

Para retirar solo el índice de demo:

```powershell
docker exec db-primary psql -U admin_db -d banco_telemetria -c "DROP INDEX IF EXISTS idx_ai_demo_transacciones_cuenta_fecha;"
```

## Guion breve para exponer

1. En Grafana, muestra PostgreSQL → Promtail → Loki → Grafana.
2. En OpenMetadata, enseña la tabla, descripción y columnas ingeridas.
3. En la terminal, ejecuta el modo `--use-openmetadata`; explica que el modelo recibe plan real y contexto del catálogo.
4. Como MSP/DBA, revisa la recomendación y explica el control de cambio antes de ejecutar `--apply-demo-index`.
5. Compara los planes y concluye: OpenMetadata aporta contexto, PostgreSQL ejecuta el índice y el equipo operativo aprueba y mide.

## Operación y solución de problemas

- PostgreSQL y telemetría: `docker compose ps` y `docker compose logs -f db-primary promtail loki grafana`.
- OpenMetadata: `docker compose -f .\openmetadata\docker-compose.yml ps` y `docker compose -f .\openmetadata\docker-compose.yml logs -f openmetadata-server ingestion`.
- Error `401/403`: revisa el JWT del bot. Error `404`: verifica que la ingesta terminó y que el FQN coincide exactamente con el nombre del servicio.
- Error Ollama `HTTP 500` con `CUDA error`: cierra Ollama desde el icono de la bandeja del sistema. En una PowerShell ejecuta `$env:OLLAMA_LLM_LIBRARY = "cpu_avx2"` y luego `& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve`; deja esa terminal abierta. En otra terminal sube `AI_TIMEOUT_SECONDS` a `900` y vuelve a ejecutar el agente. Esto evita el backend CUDA y usa CPU; puede tardar más. Si aún falla, prueba `llama3.2:3b`.
- Timeout de Ollama: prueba `llama3.2:3b`, cambia `OLLAMA_MODEL` y ejecuta de nuevo. El agente limita la salida y permite ajustar `AI_TIMEOUT_SECONDS`.
- Para detener sin borrar datos: `docker compose -f .\openmetadata\docker-compose.yml down` y `docker compose down`. No uses `-v` salvo que quieras borrar los volúmenes.

La contraseña de `openmetadata_reader`, el JWT y los datos persistentes no deben publicarse. `openmetadata/docker-volume/` y `.env` están excluidos de Git.