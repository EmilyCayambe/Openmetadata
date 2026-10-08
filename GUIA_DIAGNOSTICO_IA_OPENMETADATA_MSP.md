# Diagnóstico y tuning de bases de datos asistido por IA

Guía para exposición y laboratorio local con PostgreSQL 16, Promtail, Loki, Grafana, OpenMetadata 2.0.3 y Ollama/OpenAI. OpenMetadata se ejecuta en un Compose separado y comparte una red Docker estable con PostgreSQL. El agente puede recuperar el contexto de la tabla desde la API del catálogo mediante `--use-openmetadata`.

## Objetivos de la exposición

Al finalizar, la audiencia podrá explicar por qué el tuning reactivo es costoso, qué señales puede analizar un asistente de IA, qué contexto añade un catálogo como OpenMetadata y cómo un MSP convierte los hallazgos en operación gobernada. En el laboratorio se observará un plan de PostgreSQL, se pedirá a un modelo un diagnóstico ciego y, si hay tiempo y recursos, se comparará una hipótesis de índice sobre una copia temporal, sin modificar el esquema original.

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
Ollama / OpenAI --> diagnóstico y estrategias candidatas
   |
Revisión MSP/DBA --> validación controlada antes de cualquier cambio
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
$env:OLLAMA_NUM_PREDICT = "768"
$env:AI_TIMEOUT_SECONDS = "300"
$env:OPENMETADATA_URL = "http://localhost:8585/api"
$env:OPENMETADATA_TABLE_FQN = "postgresql_demo.banco_telemetria.public.transacciones"
$env:OPENMETADATA_JWT_TOKEN = (Get-Clipboard -Raw).Trim()
```

La variable queda solo en esa sesión. Pulsa el botón de copiar del token en OpenMetadata antes de ejecutar la asignación; el portapapeles debe contener únicamente el JWT, no las instrucciones de PowerShell. No publiques el token ni lo incluyas en capturas y revócalo tras la demo.

`OLLAMA_NUM_PREDICT` limita la respuesta para reducir el tiempo de inferencia; `AI_TIMEOUT_SECONDS` amplía la espera para modelos locales. Si la respuesta aún tarda demasiado, prueba un modelo más pequeño, por ejemplo `llama3.2:3b`.

Alternativa con OpenAI:

```powershell
$env:AI_PROVIDER = "openai"
$env:OPENAI_API_KEY = "<tu-clave>"
$env:OPENAI_MODEL = "gpt-4o-mini"
```

La clave es un secreto: no la incluyas en el repositorio, una diapositiva ni una captura. En producción se usaría un gestor de secretos.

### 5. Consulta de diagnóstico y telemetría

El caso del script consulta el historial de una cuenta y ordena por fecha. El agente mide el plan real y lo envía al modelo sin prescribir un índice ni otra solución. Para observar el plan manualmente:

```powershell
docker exec db-primary psql -U admin_db -d banco_telemetria -c "EXPLAIN (ANALYZE, BUFFERS, COSTS, FORMAT TEXT) SELECT transaccion_id, tipo_transaccion, monto, fecha_hora, estado FROM transacciones WHERE cuenta_id = 1520 AND fecha_hora >= TIMESTAMP '2024-01-01 00:00:00' ORDER BY fecha_hora DESC LIMIT 20;"
```

El resultado puede ser un `Seq Scan` u otra estrategia según estadísticas, índices presentes, distribución y costo estimado. No prometas tiempos absolutos: dependen de CPU, almacenamiento, caché y tamaño real. El análisis debe distinguir las filas estimadas/reales, buffers y tiempo, y no concluir que falta un índice solo por observar un `Seq Scan`.

El logging actual registra todas las consultas y duraciones (`log_statement = 'all'`, `log_min_duration_statement = 0`), lo que sirve para una demo pero genera mucho volumen y puede exponer parámetros. No es una configuración recomendada para producción. Las métricas del sistema (CPU/RAM/I/O) no están actualmente exportadas por Prometheus en este proyecto; Grafana consulta logs de Loki, no métricas nativas.

### 6. Agente de diagnóstico en Python

El archivo [`scripts/ai_db_tuning.py`](scripts/ai_db_tuning.py) ejecuta `EXPLAIN` en formato JSON. Con `--use-openmetadata`, consulta la API del catálogo para recuperar columnas, descripciones, responsables y etiquetas del FQN indicado; sin esa opción usa `information_schema` directamente. Los planes pueden revelar nombres y patrones; anonimízalos antes de enviarlos a un proveedor externo.

Ejecuta primero el análisis, sin aplicar cambios:

```powershell
py .\scripts\ai_db_tuning.py --use-openmetadata --provider ollama
```

Si OpenMetadata no está disponible, omite `--use-openmetadata`; el agente obtendrá las columnas directamente de `information_schema` y seguirá consultando los índices actuales:

```powershell
py .\scripts\ai_db_tuning.py --provider ollama
```

El diagnóstico ciego propone estrategias según la evidencia y puede recomendar no cambiar nada. Recibe el esquema catalogado y el inventario actual de índices consultado en PostgreSQL, pero no la frecuencia de la consulta, la carga completa ni la distribución detallada de datos; debe declarar esos límites. Un `Seq Scan` por sí solo no demuestra que falte un índice. El programa exige una respuesta JSON estructurada, presenta cinco mediciones iniciales y contrasta que el modelo haya considerado los nombres exactos de los índices existentes. Si no cumple el formato o no se puede verificar su respuesta, muestra un error o una advertencia; no modifica la base.

### 7. Verificación e interpretación

Compara en la salida:

- `Execution Time`: tiempo de esa ejecución; puede variar por caché y carga concurrente.
- `Seq Scan`/`Index Scan` y presencia de `Sort`: estrategia elegida, no una meta en sí misma.
- `Buffers: shared hit/read`: páginas servidas desde caché o leídas durante el plan.
- `rows` estimadas frente a reales: diferencia persistente puede señalar estadísticas o distribución inesperada.
- Cinco mediciones iniciales: mediana y rango para evitar basarse en una única ejecución.

Si el modelo recomienda una estrategia, considérala una hipótesis. El experimento didáctico acepta solo tres candidatos predefinidos (`cuenta_id`, `fecha_hora` o `cuenta_id_fecha_hora`); no ejecuta SQL/DDL generado por el modelo. Tras revisar el diagnóstico, en una segunda ejecución se puede probar una alternativa en una copia temporal:

```powershell
py .\scripts\ai_db_tuning.py --use-openmetadata --provider ollama --experiment-index fecha_hora --confirm-experiment
```

Escribe `EXPERIMENTAR` cuando el programa lo solicite. Para evaluar el índice compuesto usa `cuenta_id_fecha_hora` en lugar de `fecha_hora`. El modo experimental usa la hipótesis elegida anteriormente y no vuelve a consultar al modelo, evitando que un timeout de Ollama impida la comparación; con `--use-openmetadata` aún necesita acceso al catálogo. El programa crea dos copias consistentes de la tabla dentro de una transacción `REPEATABLE READ`, conserva los índices actuales y agrega el candidato solo a la copia correspondiente. Calienta ambos escenarios y alterna cinco mediciones por lado. La salida compara planes, scans de índices, filas, buffers locales/compartidos, medianas/rangos, el delta porcentual y una huella de resultados, e incluye un resumen legible. Un delta negativo significa menor tiempo mediano en esta consulta, no garantiza beneficio global. La transacción elimina las dos copias al completarse; la tabla original no recibe DDL.

En el diagnóstico compartido, la primera recomendación concreta fue un índice simple en `cuenta_id`; para probar exactamente esa sugerencia, usa `cuenta_id` como valor de `--experiment-index`. La afirmación del modelo de que faltan “índices adicionales” no es correcta como dato: el programa consultó PostgreSQL y recibió el inventario completo de índices existentes (en tu salida, solo `transacciones_pkey`). La recomendación sigue siendo una hipótesis; al ejecutar el experimento comprueba también si el índice cambia el plan y los tiempos.

Esto **no es una prueba de producción**: la copia lee toda la tabla y consume recursos del mismo servidor; los tiempos pueden reflejar caché y carga concurrente. Hazlo solo en el laboratorio local desocupado. Una mejora en esta consulta no prueba mejora global; quedan por evaluar carga real, escrituras, espacio, concurrencia y reversa antes de cualquier cambio permanente.

#### Repetir la prueba en otra sesión

Para repetir mañana la hipótesis ya elegida no hace falta volver a consultar al modelo ni repetir cambios de esquema. Abre una terminal PowerShell nueva y ejecuta:

```powershell
cd "C:\Users\thaiz\Downloads\bk_telemetria_opt_bd"
docker compose up -d db-primary
docker compose ps db-primary
py .\scripts\ai_db_tuning.py --experiment-index cuenta_id --confirm-experiment
```

Escribe `EXPERIMENTAR` para iniciar. Esta ejecución no necesita `--use-openmetadata`, JWT ni una llamada a Ollama; el valor `cuenta_id` repite de forma explícita la hipótesis que se escogió del diagnóstico anterior. PostgreSQL debe estar iniciado y conservar la base en su volumen Docker `pgdata`. No ejecutes `docker compose down -v` ni elimines ese volumen si quieres reutilizar los mismos datos. No hay que quitar ningún índice después: solo se crea sobre una tabla temporal que se elimina al cerrar la transacción.

La respuesta del modelo no está garantizada si se vuelve a solicitar; puede variar o volver a exceder el tiempo límite. Asimismo, aunque se mantengan los datos, los tiempos exactos pueden cambiar por la carga de la computadora, caché o estado del servidor. En la prueba de hoy la mediana fue 8,905 ms sin índice y 0,085 ms con el candidato; se mantuvieron los resultados, el plan pasó de `Seq Scan` a `Index Scan`, las lecturas locales bajaron de 1.906 a 6 y permaneció `Sort`. Usa estas cifras como registro de la ejecución, no como resultado garantizado para mañana.

### 8. Guion minucioso de demostración en vivo

1. **Presentar el problema.** Di: “No vamos a pedirle a la IA que adivine ni le daremos la respuesta. Le proporcionaremos un plan real, el esquema y los índices actuales; después evaluaremos críticamente sus hipótesis”.
2. **Comprobar el laboratorio.** Ejecuta `docker compose ps` y el conteo de transacciones. Señala PostgreSQL y la arquitectura existente de logs en Grafana.
3. **Mostrar OpenMetadata.** Enseña el servicio `postgresql_demo` y el FQN de `transacciones`; la descripción/tag es el contexto semántico.
4. **Mostrar el estado inicial.** Ejecuta `py .\scripts\ai_db_tuning.py --use-openmetadata --provider ollama`. Busca `Seq Scan`, filas descartadas, buffers y tiempo en ms.
5. **Solicitar diagnóstico.** Lee las estrategias candidatas y la evidencia faltante. Contrástalas con el plan y el inventario real de índices; la IA puede equivocarse y no reemplaza al DBA ni al optimizador.
6. **Probar la hipótesis (opcional).** En el laboratorio local desocupado, ejecuta el modo experimental con una opción permitida y confirma escribiendo `EXPERIMENTAR`. Compara plan, filas, buffers, mediana y rango; recalca que la copia es temporal y la carga real aún debe probarse en staging.
7. **Conectar con MSP.** Relaciona alerta, diagnóstico, aprobación, ventana de cambio, SLA/SLO y rollback. Grafana, OpenMetadata y el agente demuestran capas distintas del flujo.
8. **Cerrar con límites.** Recuerda que `EXPLAIN ANALYZE` ejecuta la consulta, que el modelo puede equivocarse y que no se deben enviar datos sensibles sin autorización.

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

**¿Por qué el agente no aplica automáticamente una recomendación?** Porque el modelo no conoce todo el impacto operacional. El modo opcional solo mide candidatos predefinidos en una copia temporal; bloqueos, espacio, escrituras, concurrencia, redundancia y rollback aún deben evaluarse por el DBA/MSP.

**¿Qué está implementado y qué hay que preparar?** El repositorio incluye el Compose oficial de OpenMetadata 2.0.3, el cliente API del agente, cinco mediciones de diagnóstico y una comparación aislada en tabla temporal para dos índices candidatos; también incluye la telemetría PostgreSQL→Promtail→Loki→Grafana. Para una sesión nueva hay que iniciar ambos Compose, crear el servicio PostgreSQL y ejecutar su primera ingesta; el modo IA de catálogo requiere un JWT local. Este laboratorio no exporta métricas nativas de CPU/RAM, no aplica cambios persistentes ni despliega un MSP.