# Guia de Telemetria y Presentacion

## 1. Idea central

La telemetria es la recoleccion y exposicion de senales que permiten saber que esta ocurriendo en un sistema sin inspeccionarlo manualmente. En este proyecto la senal principal son los **logs de PostgreSQL**.

La frase que resume el proyecto es:

> PostgreSQL produce los eventos, Promtail los transporta, Loki los almacena y Grafana los visualiza.

El objetivo es demostrar que una base de datos puede producir muchos eventos de observabilidad y que conviene enviar esos eventos a un servidor de logs separado, en vez de mezclar el almacenamiento operacional con el almacenamiento de diagnostico.

## 2. Que implementamos

La implementacion contiene cuatro servicios Docker:

| Servicio | Funcion | Puerto |
|---|---|---:|
| `db-primary` | PostgreSQL 16, datos y generacion de logs | 5432 |
| `promtail-agent` | Agente que lee logs y los envia | interno |
| `loki-server` | Almacenamiento y consulta de logs | 3100 |
| `grafana-dashboard` | Interfaz visual y dashboard | 3000 |

Todos estan conectados a la red Docker `db-network`.

Archivos importantes:

- [`docker-compose.yml`](docker-compose.yml): servicios, red, volumenes y dependencias.
- [`postgres/postgresql.conf`](postgres/postgresql.conf): logging detallado de PostgreSQL.
- [`telemetry/promtail-config.yaml`](telemetry/promtail-config.yaml): archivos a leer, labels y destino.
- [`telemetry/loki-config.yaml`](telemetry/loki-config.yaml): almacenamiento local de Loki.
- [`telemetry/grafana/provisioning/datasources/datasources.yaml`](telemetry/grafana/provisioning/datasources/datasources.yaml): datasource Loki.
- [`telemetry/grafana/provisioning/dashboards/dashboards.yaml`](telemetry/grafana/provisioning/dashboards/dashboards.yaml): carga automatica del dashboard.
- [`telemetry/grafana/dashboards/db_telemetry.json`](telemetry/grafana/dashboards/db_telemetry.json): paneles y consultas LogQL.
- [`scripts/traffic_generator.py`](scripts/traffic_generator.py): trafico, consultas y errores controlados.

## 3. Flujo de un evento

```text
Consulta SQL
    |
    v
PostgreSQL ejecuta la sentencia
    |
    | logging_collector = on
    | log_statement = 'all'
    v
/var/lib/postgresql/data/log/postgresql.log
    |
    | volumen pgdata compartido en solo lectura
    v
Promtail lee y analiza cada linea
    |
    | agrega job, environment, service y level
    v
Loki recibe por /loki/api/v1/push
    |
    | almacena en lokidata
    v
Grafana consulta con LogQL
    |
    v
Contadores, tasas y flujo de logs
```

### 3.1 PostgreSQL como productor

En `postgres/postgresql.conf` se configuraron:

- `logging_collector = on`: escribe eventos en archivos.
- `log_directory = 'log'`: carpeta de logs dentro del volumen de datos.
- `log_filename = 'postgresql.log'`: archivo que vigila Promtail.
- `log_line_prefix = '%m [%p] %q%u@%d '`: timestamp, PID, usuario y base de datos.
- `log_statement = 'all'`: registra todas las sentencias SQL.
- `log_duration = on`: registra la duracion de cada consulta.
- `log_min_duration_statement = 0`: registra incluso consultas muy rapidas.
- `log_checkpoints = on` y `log_lock_waits = on`: registra checkpoints y esperas por bloqueos.

Esto es ideal para una demostracion porque hace visible cada operacion. En produccion se debe evaluar el costo de I/O, el volumen y la posible exposicion de informacion sensible.

Tambien se activo `pg_stat_statements`, pero esa extension sirve para estadisticas agregadas de consultas y no es el canal por el que Promtail obtiene los logs.

### 3.2 Promtail como agente

Promtail monta el volumen de PostgreSQL asi:

```yaml
- pgdata:/var/lib/postgresql/data:ro
```

`:ro` significa solo lectura. El agente busca:

```text
/var/lib/postgresql/data/log/*.log
```

Cada stream recibe estos labels:

```text
job="postgres_logs"
environment="production_demo"
service="db-primary"
```

El pipeline usa una expresion regular para extraer el nivel del log y agrega el label `level`. Promtail mantiene posiciones en `/tmp/positions.yaml` para recordar hasta donde leyo cada archivo.

El destino configurado es:

```text
http://loki:3100/loki/api/v1/push
```

Como `loki` es el nombre del servicio Docker, no se usa `localhost` dentro de Promtail.

### 3.3 Loki como servidor de logs

Loki recibe los eventos y los organiza por labels. No funciona como PostgreSQL: indexa principalmente labels y luego busca en el contenido del mensaje. Por eso conviene usar labels estables y de baja cardinalidad como `job`, `service`, `environment` y `level`, no un ID distinto por cada evento.

La demo configura:

- `auth_enabled: false`: sin autenticacion entre clientes y Loki.
- `replication_factor: 1`: una sola copia.
- `store: tsdb` y `object_store: filesystem`: almacenamiento local.
- Volumen `lokidata`: conserva los datos de Loki.

Esto es apropiado para un laboratorio local, pero no es alta disponibilidad. En produccion se agregarian almacenamiento durable, replicas, retencion, TLS y control de acceso.

### 3.4 Grafana como visualizador

Grafana usa Loki como datasource mediante la URL interna:

```text
http://loki:3100
```

El dashboard se carga automaticamente desde `/var/lib/grafana/dashboards`, dentro de la carpeta `Database Telemetry`. El refresh es de 5 segundos y el rango inicial es `now-15m` a `now`.

Punto importante para defenderlo correctamente: este proyecto **no usa Prometheus**. Las tasas y contadores del dashboard son consultas LogQL calculadas sobre logs de Loki. Esto permite visualizar actividad, pero no reemplaza metricas nativas de CPU, memoria, conexiones o latencia por percentiles.

## 4. Como leer el dashboard

El archivo `db_telemetry.json` tiene seis paneles.

### Panel 1: Total Eventos de Log (Loki)

```logql
count_over_time({job="postgres_logs"}[$__range])
```

Cuenta los eventos encontrados en el rango seleccionado.

### Panel 2: Sentencias INSERT / UPDATE

```logql
count_over_time({job="postgres_logs"} |~ "(INSERT|UPDATE)" [$__range])
```

Selecciona el job y filtra el contenido con una expresion regular para mostrar escrituras.

### Panel 3: Sentencias SELECT

```logql
count_over_time({job="postgres_logs"} |~ "SELECT" [$__range])
```

Cuenta consultas de lectura que aparecen en los mensajes.

### Panel 4: Errores / Rollbacks Detectados

```logql
count_over_time({job="postgres_logs"} |~ "(ERROR|FATAL|PANIC|rollback)" [$__range])
```

Busca palabras asociadas a fallos. Es una deteccion textual para la demo, no una alerta formal.

### Panel 5: Rendimiento y Generacion de Logs en Vivo

```logql
sum(rate({job="postgres_logs"}[15s]))
sum(rate({job="postgres_logs"} |~ "(INSERT|UPDATE|DELETE)" [15s]))
```

`rate` estima eventos por segundo usando una ventana de 15 segundos. Una serie muestra la tasa total y la otra las escrituras DML. Al terminar el generador, la tasa baja progresivamente.

### Panel 6: Flujo en Tiempo Real

```logql
{job="postgres_logs"}
```

Muestra las lineas que llegan a Loki. Es el panel mas importante para demostrar el flujo: se ejecuta una consulta y despues aparece su log.

## 5. Como se genera el trafico

El archivo [`scripts/traffic_generator.py`](scripts/traffic_generator.py) ejecuta `docker exec` y dentro del contenedor llama a `psql`. Cada iteracion intenta:

1. `SELECT` de saldo y tipo de cuenta.
2. `UPDATE` del saldo.
3. `INSERT` de una transaccion.
4. Cada 15 iteraciones, un `SELECT` agrupado adicional.
5. Cada 25 iteraciones, una consulta a una tabla inexistente para generar un `ERROR` controlado.

El contador del script es el numero de iteraciones, no el numero exacto de lineas de log. Una iteracion produce varias lineas porque PostgreSQL registra sentencia, duracion y, en algunos casos, error.

Antes de ejecutar el generador hay que tener cuentas creadas. En una base limpia:

```powershell
docker compose up -d
docker compose exec -T db-primary psql -U admin_db -d banco_telemetria -c "SELECT poblar_datos_sinteticos(1000);"
```

En Windows, el comando probado es:

```powershell
py .\scripts\traffic_generator.py --mode traffic --duration 60
```

La demostracion en Grafana:

1. Abrir `http://localhost:3000`.
2. Entrar con `admin / admin`.
3. Ir a **Dashboards**.
4. Abrir **Telemetria de Base de Datos y Logs en Servidor Aislado**.
5. Seleccionar **Last 15 minutes** y refresh de 5 segundos.
6. Ejecutar el generador y observar los paneles 2, 4, 5 y 6.

Para observar el agente en otra terminal:

```powershell
docker compose logs -f promtail
```

### Demo de crecimiento de logs

```powershell
py .\scripts\traffic_generator.py --mode growth --iterations 400
```

Este modo actualiza repetidamente la cuenta 1 y compara el tamaño de la tabla antes y despues. El dato de negocio puede seguir siendo una sola fila, pero se generan eventos de logging y actividad WAL.

No hay que confundir estos conceptos:

- **Dato de negocio:** el saldo final de una fila.
- **WAL:** registro interno necesario para durabilidad y recuperacion.
- **Log de PostgreSQL:** evento textual para diagnostico y auditoria.
- **Log de Loki:** copia centralizada y consultable del archivo textual.

WAL y logs de Loki sirven para objetivos distintos.

## 6. Guion oral

### Apertura

> Mi parte trata sobre telemetria. La telemetria permite observar un sistema mientras trabaja. En nuestro caso PostgreSQL genera eventos de log, Promtail los transporta, Loki los almacena y Grafana los convierte en una vista operativa. La idea es desacoplar los logs del servidor de base de datos y detectar actividad, errores y patrones de carga.

### Arquitectura

> PostgreSQL tiene activado el colector de logs y registra todas las sentencias y sus duraciones. Los archivos viven en el volumen de datos. Promtail monta ese volumen en solo lectura, sigue el archivo y envia cada evento a Loki por la red Docker. Loki guarda los datos en su volumen y Grafana consulta Loki usando LogQL. Grafana no lee directamente el archivo de PostgreSQL.

### Demostracion

> Ahora genero trafico simulado. Cada iteracion hace un SELECT, un UPDATE y un INSERT. Ademas, cada cierto numero de iteraciones se ejecuta una consulta agrupada y se provoca un error controlado. En el dashboard aumenta la tasa de eventos, se separan lecturas y escrituras, aparecen errores y se muestran las lineas recibidas en tiempo real.

Ejecutar:

```powershell
py .\scripts\traffic_generator.py --mode traffic --duration 60
```

### Desacoplamiento

> PostgreSQL sigue siendo responsable de los datos transaccionales. Loki almacena y consulta eventos de observabilidad. Esta separacion permite buscar logs sin cargar las tablas de negocio y evita dar acceso directo al disco de PostgreSQL. En esta practica ambos usan almacenamiento local Docker; en produccion se usarian discos, retencion y replicas independientes.

### Cierre

> La implementacion demuestra el camino completo desde una sentencia SQL hasta una visualizacion. Un dashboard basado en logs es util para eventos y diagnostico, pero para observabilidad completa se agregarian metricas numericas, trazas, alertas y controles de seguridad.

## 7. Preguntas frecuentes

### ¿Por que no lee Grafana directamente el archivo?

Porque Grafana es visualizacion y consulta. Promtail centraliza la recoleccion y Loki ofrece almacenamiento y busqueda por labels. Asi se pueden agregar mas fuentes y visualizadores sin dar acceso directo al disco de PostgreSQL.

### ¿Que diferencia hay entre Loki y PostgreSQL?

Loki esta optimizado para logs y usa labels para organizar streams. PostgreSQL esta optimizado para datos estructurados, relaciones y transacciones. Los logs masivos no deberian guardarse como tablas de negocio si el objetivo es observabilidad.

### ¿Por que usar labels de baja cardinalidad?

Cada combinacion de labels crea streams. Si se usa un ID distinto como label por evento, se crean demasiados streams. Por eso usamos `job`, `service`, `environment` y `level`; el mensaje completo queda como contenido.

### ¿Que mide realmente Eventos por segundo?

La tasa de lineas de log recibidas por Loki durante 15 segundos. No es directamente el numero de transacciones confirmadas ni el uso de CPU. Una consulta puede producir varias lineas.

### ¿Hay metricas de CPU, memoria o conexiones?

No en la implementacion actual. El proyecto usa logs como señal de telemetria y calcula contadores y tasas con LogQL. Para esas metricas se podria añadir `postgres_exporter` y Prometheus.

### ¿Que pasa si Loki se cae?

Promtail no podra enviar temporalmente los eventos. Esta practica no configura alta disponibilidad ni una garantia de entrega ilimitada. En produccion se añadirian almacenamiento durable, replicas, retencion y monitoreo del pipeline.

### ¿Por que `log_statement = 'all'`?

Para que cada SELECT, UPDATE e INSERT sea visible durante la demo. En produccion puede costar mucho y registrar informacion sensible; normalmente se limita por duracion, usuario, modulo o politica de auditoria.

### ¿Que seguridad falta?

Loki tiene `auth_enabled: false`, Grafana usa `admin/admin` y PostgreSQL publica el puerto en localhost. Es aceptable para un laboratorio aislado, no para Internet. En produccion se usarian secretos, TLS, autenticacion, autorizacion y rotacion de credenciales.

### ¿Que pasa al reiniciar?

Los volumenes nombrados `pgdata`, `lokidata` y `grafanadata` conservan datos con `docker compose down`. El comando `docker compose down -v` elimina esos volumenes y reinicia todo desde cero.

## 8. Limitaciones reales que conviene reconocer

1. Loki usa filesystem local, replica 1 y autenticacion desactivada.
2. El dashboard consulta logs; no es un sistema completo de metricas de infraestructura.
3. Las consultas INSERT/UPDATE/SELECT se basan en texto y pueden contar apariciones, no transacciones semanticas.
4. El generador imprime el contador aunque alguna llamada a `psql` falle; por eso se debe poblar primero la base.
5. `log_statement = 'all'` es deliberadamente intensivo y no debe copiarse sin evaluar costos y privacidad.
6. La tasa usa una ventana de 15 segundos y puede fluctuar cuando comienza o termina el generador.

Reconocer estas limitaciones aumenta la calidad de la defensa porque demuestra la diferencia entre una prueba academica y una plataforma productiva.

## 9. Checklist antes de presentar

- [ ] Docker Desktop iniciado.
- [ ] `docker compose ps` muestra cuatro contenedores activos.
- [ ] Grafana abre en `http://localhost:3000`.
- [ ] Credenciales: `admin` / `admin`.
- [ ] Cuentas pobladas antes del generador.
- [ ] Dashboard en `Last 15 minutes`.
- [ ] Terminal lista con `py .\scripts\traffic_generator.py --mode traffic --duration 60`.
- [ ] Panel de errores visible para mostrar el error controlado.
- [ ] Panel de logs abierto para enseñar una linea real.
- [ ] Frase clave memorizada: PostgreSQL produce, Promtail transporta, Loki almacena y Grafana visualiza.
