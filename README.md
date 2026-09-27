# 🚀 Simulación Teórico-Práctica: Backups, Telemetría y Optimización SQL

> **Curso:** Almacenamiento y Minería de Datos  
> **Integrantes:** 3 Estudiantes  
> **Entorno:** 100% Dockerizado y reproducible (Costo $0)

---

## 🏗️ 1. Arquitectura de la Solución

El sistema se compone de servicios desacoplados para cumplir las mejores prácticas de la industria:

```
                                  [Servidor de Logs Desacoplado]
                                  +----------------------------+
                                  | Grafana Loki (Puerto 3100) |
                                  +--------------^-------------+
                                                 |
                                     (HTTP Push vía Promtail)
                                                 |
[Base de Datos de Producción]     +--------------+-------------+
+----------------------------+    | Promtail (Agente Ingestor) |
| PostgreSQL 16 (Pto 5432)   |--->| Lee /var/log/postgresql/   |
+--------------+-------------+    +----------------------------+
               |
               | (Ship WAL & Dumps)
               v
+----------------------------+    +----------------------------+
| Volumen Aislado de Backups |    | Grafana UI (Puerto 3000)   |
| (/backup_storage)          |    | Telemetría & Live Dash     |
+----------------------------+    +----------------------------+
```

---

## ⚡ 2. Inicio Rápido (Cualquier Integrante)

### Paso 1: Iniciar los contenedores
Abre Docker Desktop en tu sistema y luego ejecuta en la terminal de este proyecto:

```bash
docker compose up -d
```

### Paso 2: Verificar que los servicios estén activos
```bash
docker compose ps
```
Deberías ver corriendo:
- `db-primary` (PostgreSQL 16 en puerto 5432)
- `loki-server` (Loki en puerto 3100)
- `promtail-agent` (Agente de logs)
- `grafana-dashboard` (Grafana en puerto 3000)

### Paso 3: Abrir Grafana
Entra en tu navegador a:
- **URL:** [http://localhost:3000](http://localhost:3000)
- **Usuario:** `admin`
- **Contraseña:** `admin`
- Ve a **Dashboards** -> **Telemetría de Base de Datos y Logs en Servidor Aislado**.

---

## 👥 3. Distribución de Roles y Guión de Presentación

### 🧑‍💻 Estudiante 1: Arquitectura de Resiliencia y Backups
**Tema:** Explicar copias totales, incrementales (WAL) y simulación de desastres.

1. **Backup Total en vivo:**
   ```powershell
   # Windows PowerShell
   .\scripts\backup_full.ps1
   # O en Bash:
   ./scripts/backup_full.sh
   ```
   *Punto clave a explicar:* Se genera un archivo `.dump` comprimido y consistente en un volumen separado.

2. **Demostración de Backup Incremental (WAL):**
   ```powershell
   .\scripts\backup_wal.ps1
   ```
   *Punto clave a explicar:* PostgreSQL no copia toda la base de datos para backups incrementales; copia los segmentos WAL de 16MB que contienen solo los cambios desde el último LSN (*Log Sequence Number*).

3. **Simulación de Desastre y Restauración en Vivo:**
   ```powershell
   .\scripts\disaster_and_restore.ps1
   ```
   *Punto clave a explicar:* Se borran las tablas (`DROP TABLE`), se demuestra que la información no existe y se restaura el estado en segundos.

---

### 🧑‍💻 Estudiante 2: Telemetría y Servidor de Logs Desacoplado
**Tema:** Crecimiento masivo de logs frente a la base de datos y monitoreo centralizado.

1. **La Paradoja de los Logs (Demostración interactiva):**
   ```bash
   python .\scripts\traffic_generator.py --mode growth --iterations 400
   ```
   *Punto clave a explicar:* Mostrar a la clase que al actualizar 400 veces una cuenta, el tamaño de la tabla en disco casi no crece, pero se generaron cientos de eventos de log y transacciones WAL. Si los logs se almacenaran en el mismo disco de la BD, el servidor colapsaría.

2. **Inyección de Tráfico en Tiempo Real y Dashboard de Grafana:**
   ```bash
   python .\scripts\traffic_generator.py --mode traffic --duration 90
   ```
   *Punto clave a explicar:* Mostrar en el proyector la pantalla de Grafana (`http://localhost:3000`):
   - Ver cómo sube la gráfica de **Eventos/segundo**.
   - Mostrar el desglose de sentencias `INSERT`, `UPDATE` y `SELECT`.
   - Mostrar la captura de errores en tiempo real y el flujo de logs en vivo.

---

### 🧑‍💻 Estudiante 3: Ingesta Masiva y Optimización de Consultas SQL
**Tema:** Generación sintética y optimización de planes de ejecución (`EXPLAIN ANALYZE`).

1. **Poblado ultrarrápido de 100,000 registros en segundos:**
   Conéctate a la BD (vía DBeaver, pgAdmin o terminal) y ejecuta:
   ```sql
   SELECT poblar_datos_sinteticos(100000);
   ```
   *Punto clave a explicar:* Uso de funciones en el motor con `generate_series()` para crear relaciones referenciales consistentes en memoria.

2. **Demostración de los 3 Casos de Optimización (Ejecutar [scripts/optimization_demo.sql](file:///scripts/optimization_demo.sql)):**
   - **Caso 1: Sequential Scan vs B-Tree Index en `dni`:**
     - Mostrar el escaneo completo de 100k filas (~50ms+) vs B-Tree Index (~0.1ms).
   - **Caso 2: Índice Compuesto `(cuenta_id, fecha_hora DESC)`:**
     - Explicar la importancia del orden de columnas y cómo elimina operaciones de ordenamiento (*Sort*) en memoria.
   - **Caso 3: Anti-patrón con funciones `LOWER(email)` e Índices Basados en Expresiones:**
     - Demostrar cómo una función en el `WHERE` anula un índice convencional y cómo se resuelve con un índice funcional.
   - **Caso 4 (Bonus):** Consultar la vista `pg_stat_statements` para auditar las 10 consultas más costosas del motor.

---

## 🛠️ 4. Comandos de Reseteo y Mantenimiento

Si desean reiniciar toda la simulación desde cero en cualquier momento:

```bash
# Apagar contenedores y limpiar volúmenes
docker compose down -v

# Volver a levantar el entorno limpio
docker compose up -d
```
