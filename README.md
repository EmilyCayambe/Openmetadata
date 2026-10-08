# Diagnóstico y Tuning de Bases de Datos Asistido por IA

Laboratorio académico local con PostgreSQL, OpenMetadata, Ollama y telemetría Promtail/Loki/Grafana. Demuestra cómo aportar al modelo una consulta, su plan real, el esquema y los índices existentes para obtener un diagnóstico y estrategias de tuneo fundamentadas, sujetas a revisión humana.

## Qué se demuestra

| Componente | Función en la exposición |
|---|---|
| PostgreSQL 16 | Ejecuta la consulta y produce `EXPLAIN (ANALYZE, BUFFERS)` |
| Promtail → Loki → Grafana | Muestra logs de PostgreSQL y actividad durante el experimento |
| OpenMetadata 2.0.3 | Ingiere el esquema PostgreSQL y cataloga tablas/columnas |
| `scripts/ai_db_tuning.py` | Envía al modelo el plan real y el contexto obtenido de OpenMetadata |
| Ollama | Ejecuta el modelo localmente, sin clave de API externa |
| Rol MSP/DBA | Revisa la recomendación y autoriza una prueba aislada antes de cualquier cambio persistente |

El MSP se representa como un proceso operativo, no como otro contenedor. El agente diagnostica y propone; no modifica el esquema original. El modo de experimento opcional compara una hipótesis sobre una copia temporal de la tabla dentro de una transacción, tras confirmación interactiva. No despliega cambios persistentes.

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
$env:OLLAMA_NUM_PREDICT = "768"
$env:AI_TIMEOUT_SECONDS = "300"
$env:OPENMETADATA_URL = "http://localhost:8585/api"
$env:OPENMETADATA_TABLE_FQN = "postgresql_demo.banco_telemetria.public.transacciones"
$env:OPENMETADATA_JWT_TOKEN = (Get-Clipboard -Raw).Trim()
```

Antes de ejecutar el bloque, abre **Settings → Bots → IngestionBot**, genera un token con vencimiento de 7 días y pulsa el botón de copiar del campo **OpenMetadata JWT Token**. Copia solo el token desde la interfaz; no selecciones ni copies el bloque de comandos. `Get-Clipboard` lo pone solo en la sesión actual. No lo pegues en el chat ni lo imprimas en la terminal. Revócalo después de la exposición. El agente lo usa para leer el contexto de la tabla.

Ejecuta el diagnóstico integrado, sin cambiar la base:

```powershell
py .\scripts\ai_db_tuning.py --provider ollama --use-openmetadata
```

La terminal debe indicar `CONTEXTO DE ESQUEMA: OpenMetadata`, mostrar el FQN y las columnas recibidas, y luego cinco mediciones del plan y un análisis JSON del modelo. El programa comprueba que el modelo haya tenido en cuenta exactamente los índices observados; las advertencias de validación indican posibles contradicciones. Grafana muestra los logs en paralelo en [http://localhost:3000](http://localhost:3000) (`admin/admin`).

Si OpenMetadata no está disponible, ejecuta el diagnóstico contra el esquema de PostgreSQL directamente:

```powershell
py .\scripts\ai_db_tuning.py --provider ollama
```

## Probar una hipótesis en una copia temporal

El diagnóstico predeterminado nunca aplica recomendaciones. Para demostrar una comparación medible, el script ofrece tres candidatos explícitos y permitidos:

| Opción | Índice candidato |
|---|---|
| `cuenta_id` | B-tree sobre `cuenta_id`, para probar exactamente la primera recomendación entregada por el modelo |
| `fecha_hora` | B-tree sobre `fecha_hora`, siguiendo la hipótesis de índice simple |
| `cuenta_id_fecha_hora` | B-tree compuesto sobre `cuenta_id` y `fecha_hora DESC`, alineado con filtro y orden de la consulta |

Primero revisa el diagnóstico. Después inicia una segunda ejecución indicando la hipótesis que quieres probar. El programa pedirá escribir `EXPERIMENTAR` antes de continuar:

```powershell
py .\scripts\ai_db_tuning.py --provider ollama --use-openmetadata --experiment-index fecha_hora --confirm-experiment
```

Para probar exactamente la primera sugerencia del modelo, usa `cuenta_id`; para comparar la alternativa compuesta, usa `cuenta_id_fecha_hora`. No se ejecuta SQL/DDL escrito por el modelo: el experimento acepta exclusivamente estas opciones predefinidas. La ejecución experimental usa la hipótesis seleccionada previamente y **no vuelve a llamar al modelo**, por lo que un timeout de Ollama no impide continuar; sí requiere OpenMetadata si se conserva `--use-openmetadata`. El comando crea dos copias temporales consistentes de `transacciones`, conserva los índices actuales, agrega el índice candidato solo a una copia, calienta ambos escenarios y alterna cinco mediciones por escenario. Compara medianas, rangos, buffers locales y compartidos, scans de índices, filas copiadas, planes y una huella de los resultados. La salida incluye una comparación en palabras; un delta porcentual negativo indica menor tiempo mediano para el candidato en esta consulta, no una garantía de beneficio global. Al terminar la transacción PostgreSQL elimina ambas copias y el índice temporal; no se modifica permanentemente el esquema de origen.

### Repetir la práctica mañana

La primera recomendación del modelo que se probó fue un índice en `cuenta_id`. Para repetir **esa misma hipótesis** no necesitas volver a preguntarle a la IA, iniciar OpenMetadata, copiar un JWT ni repetir cambios en PostgreSQL. En una terminal nueva de PowerShell, desde la carpeta del proyecto, ejecuta:

```powershell
cd "C:\Users\thaiz\Downloads\bk_telemetria_opt_bd"
docker compose up -d db-primary
docker compose ps db-primary
py .\scripts\ai_db_tuning.py --experiment-index cuenta_id --confirm-experiment
```

Cuando lo pida, escribe `EXPERIMENTAR`. El modo experimental usa el candidato indicado, sin llamar a Ollama; compara dos copias temporales del contenido que exista entonces en `transacciones`. Cada ejecución crea y elimina sus propias copias. No hay que deshacer un índice después porque el índice se crea solo en una tabla temporal que desaparece al terminar.

Los datos de PostgreSQL se guardan en el volumen Docker `pgdata`; `docker compose down` no lo elimina. **No uses `docker compose down -v` ni borres el volumen `pgdata`** si quieres conservar la misma base. Si la tabla se modifica, se reinicializa o cambia de tamaño, las mediciones de mañana pueden diferir.

No se puede prometer el mismo tiempo exacto: dependen de la carga del equipo, PostgreSQL y el estado de caché. El script calienta y alterna los escenarios para reducir sesgos, pero el resultado es experimental. Tampoco se garantiza que una consulta nueva al modelo recomiende otra vez `cuenta_id`; los modelos pueden variar o exceder el tiempo límite. Para reproducir la comparación de hoy, usa el comando de experimento anterior y conserva el mismo candidato.

En esta ejecución de laboratorio se observó como referencia: mismas filas devueltas; mediana de 8,905 ms sin el candidato y 0,085 ms con él; `Seq Scan` cambió a `Index Scan`; las lecturas locales bajaron de 1.906 a 6 y el `Sort` permaneció. Es el resultado medido hoy, **no una promesa de que mañana aparezcan los mismos números**.

**Límites y precauciones:** copiar la tabla lee todos sus datos y consume CPU, I/O y espacio temporal en el mismo servidor. Ejecuta esta demostración únicamente en el laboratorio local, con espacio disponible y sin carga concurrente importante; nunca en producción. La comparación repite una consulta sintética y no representa por sí sola la carga completa: incluye posibles efectos de caché, excluye el costo sostenido en escrituras y no sustituye pruebas con carga real. Un cambio de tiempos no demuestra causalidad bajo concurrencia ni garantiza una mejora operacional. Revisa filas iguales, planes y estabilidad de las mediciones antes de interpretar el resultado. El modo por defecto sigue siendo solo diagnóstico.

## Guion breve para exponer

1. En Grafana, muestra PostgreSQL → Promtail → Loki → Grafana.
2. En OpenMetadata, enseña la tabla, descripción y columnas ingeridas.
3. En la terminal, ejecuta el modo `--use-openmetadata`; explica que el modelo recibe plan real y contexto del catálogo.
4. Lee la estrategia sugerida y contrástala con el plan, el esquema y los índices observados; comenta también las advertencias de validación y la evidencia que falta.
5. Si el laboratorio está desocupado, vuelve a ejecutar el modo experimental con una opción permitida; escribe `EXPERIMENTAR` y compara la mediana, el rango, los buffers, el plan y la huella de resultados.
6. Concluye que la IA propone hipótesis, el programa las mide solo en una copia temporal y el DBA/MSP mantiene la autoridad sobre cualquier cambio persistente.

## Operación y solución de problemas

- PostgreSQL y telemetría: `docker compose ps` y `docker compose logs -f db-primary promtail loki grafana`.
- OpenMetadata: `docker compose -f .\openmetadata\docker-compose.yml ps` y `docker compose -f .\openmetadata\docker-compose.yml logs -f openmetadata-server ingestion`.
- Error `401/403`: revisa el JWT del bot. Error `404`: verifica que la ingesta terminó y que el FQN coincide exactamente con el nombre del servicio.
- Error Ollama `HTTP 500` con `CUDA error`: cierra Ollama desde el icono de la bandeja del sistema. En una PowerShell ejecuta `$env:OLLAMA_LLM_LIBRARY = "cpu_avx2"` y luego `& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve`; deja esa terminal abierta. En otra terminal sube `AI_TIMEOUT_SECONDS` a `900` y vuelve a ejecutar el agente. Esto evita el backend CUDA y usa CPU; puede tardar más. Si aún falla, prueba `llama3.2:3b`.
- Timeout de Ollama: prueba `llama3.2:3b`, cambia `OLLAMA_MODEL` y ejecuta de nuevo. El agente limita la salida y permite ajustar `AI_TIMEOUT_SECONDS`.
- Para detener sin borrar datos: `docker compose -f .\openmetadata\docker-compose.yml down` y `docker compose down`. No uses `-v` salvo que quieras borrar los volúmenes.

La contraseña de `openmetadata_reader`, el JWT y los datos persistentes no deben publicarse. `openmetadata/docker-volume/` y `.env` están excluidos de Git.