# Diagnóstico y tuning de bases de datos asistido por IA

Guía para exposición y laboratorio local con PostgreSQL 16, Promtail, Loki, Grafana, OpenMetadata 2.0.3 y Ollama/OpenAI. OpenMetadata se ejecuta en un Compose separado y comparte una red Docker estable con PostgreSQL. El agente puede recuperar el contexto de la tabla desde la API del catálogo mediante `--use-openmetadata`.

## Objetivos de la exposición

Al finalizar, la audiencia podrá explicar por qué el tuning reactivo es costoso, qué señales puede analizar un asistente de IA, qué contexto añade un catálogo como OpenMetadata y cómo un MSP convierte los hallazgos en operación gobernada. En el laboratorio se observará un plan de PostgreSQL, se pedirá un diagnóstico a un modelo y se comparará el plan después de crear un índice revisado.

## Parte 1: estructura y guion de presentación

### 1. Tuning tradicional frente a tuning asistido por IA

**Idea para la diapositiva:** el tuning tradicional suele empezar después de una alerta o queja; el asistido por IA prioriza señales, propone hipótesis y deja la decisión de cambio bajo control técnico.

**Guion oral:**

> En un enfoque tradicional, el DBA recibe una alerta de latencia, revisa logs y métricas por separado, reproduce la consulta, analiza el plan y valida si un índice ayudaría. El trabajo es valioso, pero con frecuencia es reactivo y consume tiempo en correlacionar señales dispersas. La IA puede resumir grandes volúmenes de telemetría, agrupar consultas similares, detectar regresiones y ordenar los casos por impacto probable. No reemplaza al DBA: acelera el diagnóstico y propone acciones que deben validarse.

El costo no es solo el tiempo de análisis. Una reacción tardía puede prolongar una degradación, consumir CPU/I/O, aumentar colas y afectar un SLA. En cambio, automatizar detección y priorización permite que el equipo dedique más tiempo a validar causa raíz y menos a buscar manualmente el evento relevante.

La predicción requiere datos históricos: tendencia de latencia, volumen, estacionalidad, cardinalidad observada y cambios de despliegue. Un modelo puede estimar anomalías o riesgo de saturación; no puede garantizar que una consulta futura será lenta ni inferir por sí solo reglas de negocio. Debe reportar evidencia, confianza y límites.

### 2. Cómo analiza la IA una base que no conoce

**Idea para la diapositiva:** primero observa señales; después construye hipótesis; con contexto de catálogo mejora la recomendación.

**Guion oral:**

> Si el modelo no conoce la base, no adivina su estructura mágicamente. Le entregamos evidencia acotada: SQL normalizado, plan real, métricas, definición de columnas disponible y una pregunta concreta. El modelo explica patrones y propone alternativas. La evidencia que no se le entrega permanece desconocida.

Señales útiles:

| Señal | Qué revela | Qué no demuestra por sí sola |
|---|---|---|
| Slow Query Logs y SQL | Consultas lentas, frecuencia, parámetros (si se registran), patrones repetidos y predicados | No explica por sí sola el costo interno ni la distribución de datos |
| `EXPLAIN (ANALYZE, BUFFERS)` | Nodos elegidos, filas estimadas/reales, tiempo por nodo, lecturas y aciertos de buffers | `ANALYZE` ejecuta la consulta; un plan de laboratorio no garantiza el mismo resultado en producción |
| CPU, RAM, I/O, conexiones | Saturación y correlación temporal con carga | Una métrica agregada no atribuye la causa a una consulta específica |
| Wait events | Si la sesión espera por I/O, locks, cliente, WAL u otro recurso | El evento de espera es contexto, no necesariamente la causa raíz |
| Profiling y estadísticas | Consultas de mayor costo, frecuencia, regresiones, columnas con alta selectividad | Un índice sugerido puede penalizar escrituras, espacio y mantenimiento |

Para PostgreSQL, `pg_stat_statements` agrupa estadísticas por consulta normalizada; los logs aportan eventos y tiempos; `EXPLAIN` aporta estructura de ejecución. La IA puede relacionar un `Seq Scan` con un filtro selectivo, una diferencia entre filas estimadas y reales con estadísticas desactualizadas, o un `Sort` con falta de orden aprovechable. Para sugerir un índice faltante con rigor necesita, como mínimo, predicados, ordenamiento, cardinalidad/estadísticas y definición de tabla.

Un flujo responsable es: recopilar señales → anonimizar secretos y valores personales → correlacionar por huella/intervalo → generar hipótesis y DDL candidato → validar en staging con carga representativa → revisión humana → despliegue gradual → comparar latencia, buffers, escrituras y espacio. Nunca ejecutar SQL generado por el modelo directamente en producción.

### 3. Rol de OpenMetadata

**Idea para la diapositiva:** OpenMetadata aporta contexto semántico y de gobierno; PostgreSQL sigue siendo quien ejecuta y optimiza consultas.

**Guion oral:**

> OpenMetadata es un catálogo y plataforma de metadatos. Registra qué tablas y columnas existen, quién es su propietario, cómo se relacionan y de dónde provienen los datos. Si un asistente recibe el plan junto con el esquema y el linaje, puede evitar recomendaciones incompatibles con la semántica o con las políticas de datos. OpenMetadata no sustituye al optimizador de PostgreSQL ni crea índices automáticamente.

**Qué hace:** inventario/catálogo de activos, metadatos técnicos y descriptivos, propietarios, clasificación y gobierno; linaje entre tablas, pipelines y servicios; búsqueda y contexto para usuarios o agentes mediante API/integraciones; soporte para políticas y trazabilidad conforme a la configuración instalada.

**Qué no hace:** no es un motor de tuning de bajo nivel OLTP; no reemplaza `EXPLAIN`, `pg_stat_statements`, métricas del motor ni una plataforma de observabilidad; no decide automáticamente si un índice es rentable en la carga real y no aplica cambios a PostgreSQL por sí solo.

**Integración del laboratorio:** PostgreSQL → Promtail → Loki → Grafana muestra telemetría; el conector PostgreSQL de OpenMetadata ingiere el catálogo; `ai_db_tuning.py --use-openmetadata` consulta por API las columnas, descripción, responsables y etiquetas del FQN configurado y entrega ese contexto junto al plan real al modelo. El JWT se configura localmente y no se guarda en Git.

### 4. Operación con un MSP

**Idea para la diapositiva:** un MSP convierte diagnósticos puntuales en una operación continua con responsables, niveles de servicio y cambios auditables.

**Guion oral:**

> Un Managed Service Provider presta y opera servicios tecnológicos para un cliente bajo un alcance y acuerdos definidos. En bases de datos, puede asumir monitoreo, respaldo, incidentes, capacidad, parchado y tuning continuo. La IA ayuda a clasificar alertas y preparar diagnósticos; el MSP mantiene guardias, escalamiento, aprobación y responsabilidad operativa.

Un modelo operativo típico incluye monitoreo 24/7, guardias y escalamiento por severidad, objetivos de respuesta/restauración definidos contractualmente, revisión periódica de capacidad, pruebas de backup/restore, gestión de cambios y tuning continuo. Hay que distinguir **SLA** (compromiso contractual), **SLO** (objetivo medible) y **SLI** (medición observada). No afirmar tiempos universales: se acuerdan según criticidad, cobertura y contrato.

| Capa operativa | Responsabilidad sugerida |
|---|---|
| Telemetría | Mantener señales, umbrales, dashboards y retención; proteger datos sensibles |
| IA/agente | Correlacionar, resumir y proponer; registrar evidencia, modelo y versión |
| DBA/MSP | Validar causa, impacto, rollback, ventana y cambio aprobado |
| Cliente/propietario | Definir criticidad, semántica, aceptación de riesgo y autorización |

**Ciclo continuo:** detectar → clasificar impacto → investigar con contexto → recomendar → aprobar → probar/desplegar → verificar SLO → documentar y aprender. Una recomendación no aprobada no debe convertirse en cambio; cambios de esquema deben contemplar bloqueo, duración de creación de índices, costo de escritura y plan de reversa.

## Parte 2: laboratorio práctico

### 1. Arquitectura que se reutiliza

El proyecto ya incluye `db-primary` (PostgreSQL 16), el esquema `clientes/cuentas/transacciones`, una función que genera datos y Promtail→Loki→Grafana. El servicio PostgreSQL se publica en `localhost:5433` y Grafana en `http://localhost:3000`. El script de laboratorio ejecuta `psql` dentro del contenedor, así que no requiere instalar un driver de Python ni cambiar Docker Compose.

Componentes del laboratorio:

```text
PostgreSQL 16 -- logs --> Promtail --> Loki --> Grafana
   | EXPLAIN JSON                     (telemetría)
   v
Agente Python <-- API de OpenMetadata 2.0.3 <-- ingesta PostgreSQL
   |                 (esquema, columnas, descripción, tags)
   v
Ollama / OpenAI --> diagnóstico y DDL candidato
   |
Revisión MSP/DBA --> índice fijo de laboratorio --> nuevo EXPLAIN
```

### 2. Requisitos y puesta en marcha

Requisitos: Docker Desktop y Docker Compose; Python 3.10 o superior; Ollama con un modelo descargado, o una clave `OPENAI_API_KEY`. El agente usa la biblioteca estándar. El Compose de OpenMetadata 2.0.3 incluye servidor, base interna, Elasticsearch y servicio de ingesta; la red compartida permite al conector resolver `db-primary`.

Desde PowerShell, en la raíz del repositorio:

```powershell
docker compose up -d
docker compose ps
docker exec db-primary psql -U admin_db -d banco_telemetria -c "SELECT count(*) AS transacciones FROM transacciones;"
```

Inicia OpenMetadata en una segunda etapa:

```powershell
docker compose -f .\openmetadata\docker-compose.yml up -d
docker compose -f .\openmetadata\docker-compose.yml ps
```

Espera a que servidor, MySQL, Elasticsearch e ingesta estén activos y abre `http://localhost:8585`. En un volumen nuevo, `postgres/init/01_init.sql` crea la carga inicial. Comprueba que la consulta tenga filas:

```powershell
docker exec db-primary psql -U admin_db -d banco_telemetria -c "SELECT count(*) AS filas_cuenta_1520 FROM transacciones WHERE cuenta_id = 1520;"
```

Si el conteo da 0, ejecuta `SELECT poblar_datos_sinteticos(25000);` una sola vez. La función agrega datos; no la repitas al reiniciar.

### 3. Registrar PostgreSQL en OpenMetadata

Usa el script de solo lectura para evitar conectar el catálogo como superusuario:

```powershell
$securePassword = Read-Host "Contraseña local para openmetadata_reader" -AsSecureString
$env:OPENMETADATA_DB_PASSWORD = [System.Net.NetworkCredential]::new("", $securePassword).Password
Get-Content -Raw .\openmetadata\create_reader.sql | docker exec -i db-primary psql -U admin_db -d banco_telemetria -v "reader_password=$env:OPENMETADATA_DB_PASSWORD" -f -
Remove-Item Env:OPENMETADATA_DB_PASSWORD
```

En la interfaz de OpenMetadata crea un servicio PostgreSQL con estos valores:

| Campo | Valor |
|---|---|
| Service name | `postgresql_demo` |
| Host / Port | `db-primary` / `5432` |
| Database | `banco_telemetria` |
| User | `openmetadata_reader` |

Prueba la conexión, crea el workflow **Metadata** y pulsa **Create & Deploy**. Espera a que termine la ingesta y abre `postgresql_demo.banco_telemetria.public.transacciones`. Añade una descripción o etiquetas para que el contexto semántico sea visible.

### 4. Configurar IA y API del catálogo

Ollama debe estar instalado con un modelo. Si PowerShell no encuentra `ollama`, usa la ruta completa; si la aplicación ya sirve en `localhost:11434`, no hace falta ejecutar `ollama serve`.

```powershell
ollama pull llama3.1
```

Usa el bot integrado `IngestionBot`: abre **Settings → Bots → IngestionBot**, genera un JWT con vencimiento de 7 días y usa el botón de copiar del campo **OpenMetadata JWT Token**. En la misma PowerShell copia el clipboard a una variable local:

```powershell
$env:AI_PROVIDER = "ollama"
$env:OLLAMA_MODEL = "llama3.1:latest"
$env:OLLAMA_NUM_PREDICT = "512"
$env:AI_TIMEOUT_SECONDS = "300"
$env:OPENMETADATA_URL = "http://localhost:8585/api"
$env:OPENMETADATA_TABLE_FQN = "postgresql_demo.banco_telemetria.public.transacciones"
$env:OPENMETADATA_JWT_TOKEN = (Get-Clipboard -Raw).Trim()
```

La variable queda solo en esa sesión. No publiques el token ni lo incluyas en capturas y revócalo tras la demo.

`OLLAMA_NUM_PREDICT` limita la respuesta para reducir el tiempo de inferencia; `AI_TIMEOUT_SECONDS` amplía la espera para modelos locales. Si la respuesta aún tarda demasiado, prueba un modelo más pequeño, por ejemplo `llama3.2:3b`.

Alternativa con OpenAI:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<tu-clave>"
$env:OPENAI_MODEL = "gpt-4o-mini"
```

La clave es un secreto: no la incluyas en el repositorio, una diapositiva ni una captura. En producción se usaría un gestor de secretos.

### 5. Consulta deliberadamente costosa y telemetría

El caso del script consulta el historial de una cuenta y ordena por fecha. El laboratorio elimina solo el índice con nombre reservado `idx_ai_demo_transacciones_cuenta_fecha`, obtiene un plan inicial y solicita análisis al modelo. Para observarlo manualmente:

```powershell
docker exec db-primary psql -U admin_db -d banco_telemetria -c "EXPLAIN (ANALYZE, BUFFERS, COSTS, FORMAT TEXT) SELECT transaccion_id, tipo_transaccion, monto, fecha_hora, estado FROM transacciones WHERE cuenta_id = 1520 AND fecha_hora >= TIMESTAMP '2024-01-01 00:00:00' ORDER BY fecha_hora DESC LIMIT 20;"
```

La ausencia del índice hace probable un `Seq Scan`; al haber pocas filas por cuenta, el nodo de ordenamiento puede ser pequeño o el optimizador podría elegir otra estrategia. No prometas tiempos absolutos: dependen de CPU, almacenamiento, caché y tamaño real. Lo que se contrasta es el plan, las filas y los buffers, además del tiempo.

El logging actual registra todas las consultas y duraciones (`log_statement = 'all'`, `log_min_duration_statement = 0`), lo que sirve para una demo pero genera mucho volumen y puede exponer parámetros. No es una configuración recomendada para producción. Las métricas del sistema (CPU/RAM/I/O) no están actualmente exportadas por Prometheus en este proyecto; Grafana consulta logs de Loki, no métricas nativas.

### 6. Agente de diagnóstico en Python

El archivo [`scripts/ai_db_tuning.py`](scripts/ai_db_tuning.py) ejecuta `EXPLAIN` en formato JSON. Con `--use-openmetadata`, consulta la API del catálogo para recuperar columnas, descripciones, responsables y etiquetas del FQN indicado; sin esa opción usa `information_schema` directamente. Los planes pueden revelar nombres y patrones; anonimízalos antes de enviarlos a un proveedor externo.

Ejecuta primero el análisis, sin aplicar cambios:

```powershell
py .\scripts\ai_db_tuning.py --use-openmetadata --provider ollama
```

Para la comparación completa, permite que el script cree el índice **fijo y predefinido para esta demo**, no el DDL devuelto por la IA:

```powershell
py .\scripts\ai_db_tuning.py --use-openmetadata --provider ollama --apply-demo-index
```

El script imprime el plan de entrada, la recomendación del modelo y el plan final. La consulta y el DDL se limitan a objetos del laboratorio. La IA nunca ejecuta SQL generado. Revisa el índice y su efecto antes de considerar cualquier uso fuera de este entorno.

### 7. Verificación e interpretación

Compara en la salida:

- `Execution Time`: tiempo de esa ejecución; puede variar por caché y carga concurrente.
- `Seq Scan`/`Index Scan` y presencia de `Sort`: estrategia elegida, no una meta en sí misma.
- `Buffers: shared hit/read`: páginas servidas desde caché o leídas durante el plan.
- `rows` estimadas frente a reales: diferencia persistente puede señalar estadísticas o distribución inesperada.

Con el índice compuesto se espera limitar el recorrido por `cuenta_id` y entregar las filas ya ordenadas por `fecha_hora`. La mejora depende de selectividad y volumen. Un índice acelera lecturas compatibles, pero ocupa almacenamiento y añade trabajo a `INSERT`, `UPDATE` y `DELETE`. La consulta puede devolver pocas filas y el tiempo absoluto ser muy pequeño; en ese caso, el cambio de plan y buffers es la evidencia más didáctica.

El índice de demo puede quitarse al terminar:

```powershell
docker exec db-primary psql -U admin_db -d banco_telemetria -c "DROP INDEX IF EXISTS idx_ai_demo_transacciones_cuenta_fecha;"
```

### 8. Guion minucioso de demostración en vivo

1. **Presentar el problema.** Di: “No vamos a pedirle a la IA que adivine; le daremos un plan real y el esquema observado. Primero medimos, luego revisamos una recomendación y finalmente medimos otra vez”.
2. **Comprobar el laboratorio.** Ejecuta `docker compose ps` y el conteo de transacciones. Señala PostgreSQL y la arquitectura existente de logs en Grafana.
3. **Mostrar OpenMetadata.** Enseña el servicio `postgresql_demo` y el FQN de `transacciones`; la descripción/tag es el contexto semántico.
4. **Mostrar el estado inicial.** Ejecuta `py .\scripts\ai_db_tuning.py --use-openmetadata --provider ollama`. Busca `Seq Scan`, filas descartadas, buffers y tiempo en ms.
5. **Solicitar diagnóstico.** Contrasta la recomendación con el plan. La IA es asistente; no reemplaza al DBA ni el optimizador.
6. **Aplicar solo el cambio revisado.** Ejecuta `py .\scripts\ai_db_tuning.py --use-openmetadata --provider ollama --apply-demo-index`. El DDL es fijo y conocido, no texto libre generado.
7. **Comparar.** Observa el nuevo nodo, el `Sort` si desaparece y los buffers/tiempo. Di: “La mejora no es solo el número de milisegundos: verificamos el plan y el costo de recursos; en producción también mediríamos escrituras, tamaño y latencia bajo carga”.
8. **Conectar con MSP.** Relaciona alerta, diagnóstico, aprobación, ventana de cambio, SLA/SLO y rollback. Grafana, OpenMetadata y el agente demuestran capas distintas del flujo; la aprobación operativa se representa en el guion.
9. **Cerrar con límites.** Recuerda que `EXPLAIN ANALYZE` ejecuta la consulta, que el modelo puede equivocarse, que un índice tiene costo y que no se deben enviar datos sensibles sin autorización.

### Recuperación si Ollama falla por CUDA en Windows

Si el agente devuelve HTTP 500 con `CUDA error: shared object initialization failed`, la base y OpenMetadata siguen funcionando; falló la inicialización de GPU de Ollama. La documentación oficial permite forzar la biblioteca CPU. Cierra Ollama desde el icono de la bandeja del sistema y, en una PowerShell, ejecuta:

```powershell
$env:OLLAMA_LLM_LIBRARY = "cpu_avx2"
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve
```

Deja esa ventana abierta. En otra PowerShell configura `AI_TIMEOUT_SECONDS=900` y vuelve a ejecutar el agente. La inferencia en CPU puede tardar más; si sigue fallando, descarga y prueba `llama3.2:3b`. No reinstales ni vuelvas a poblar PostgreSQL por este error.

## Preguntas probables

**¿La IA necesita conocer toda la base?** No necesariamente para describir un plan; para recomendar correctamente necesita el SQL, plan, esquema, estadísticas y semántica relevante. El catálogo aporta contexto, no certeza.

**¿OpenMetadata optimiza consultas?** No. Cataloga y ofrece metadatos/linaje/gobierno. PostgreSQL planifica y ejecuta; herramientas de observabilidad y un agente separado analizan.

**¿Por qué no aplicar automáticamente el índice?** Porque el modelo no conoce todo el impacto operacional; hay que validar bloqueo, espacio, escrituras, concurrencia, redundancia y rollback.

**¿Qué está implementado y qué hay que preparar?** El repositorio incluye el Compose oficial de OpenMetadata 2.0.3, el cliente API del agente y la telemetría PostgreSQL→Promtail→Loki→Grafana. Para una sesión nueva hay que iniciar ambos Compose, crear el servicio PostgreSQL y ejecutar su primera ingesta; el modo IA de catálogo requiere un JWT local. Este laboratorio no exporta métricas nativas de CPU/RAM ni despliega un MSP: el rol MSP se demuestra con la aprobación y verificación del cambio.