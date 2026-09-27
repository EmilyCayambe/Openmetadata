-- =====================================================================
-- DEMOSTRACIÓN DE OPTIMIZACIÓN DE CONSULTAS SQL Y ANÁLISIS DE PLANES
-- =====================================================================
-- Curso: Almacenamiento y Minería de Datos
-- Objetivo: Demostrar el impacto de índices y técnicas de optimización
-- utilizando EXPLAIN (ANALYZE, BUFFERS, COSTS)
-- =====================================================================

-- NOTA: Antes de ejecutar, asegúrate de haber ejecutado:
-- SELECT poblar_datos_sinteticos(100000); para tener suficiente volumen.


-- =====================================================================
-- CASO 1: BÚSQUEDA PUNTUAL - SEQUENTIAL SCAN vs B-TREE INDEX
-- =====================================================================

-- 1.1 Consulta SIN índice en la columna 'dni'
-- Observa: 'Seq Scan' (escaneo secuencial de toda la tabla) y 'Buffers: shared read'
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT cliente_id, nombres, apellidos, email, pais
FROM clientes
WHERE dni = '10045678';

-- 1.2 Creamos el índice B-Tree (el estándar para comparaciones de igualdad y rango)
CREATE UNIQUE INDEX IF NOT EXISTS idx_clientes_dni ON clientes(dni);

-- 1.3 Misma consulta CON índice B-Tree
-- Observa el cambio radical: 'Index Scan' y tiempo reducido en más de 95%
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT cliente_id, nombres, apellidos, email, pais
FROM clientes
WHERE dni = '10045678';


-- =====================================================================
-- CASO 2: FILTRO MULTICOLUMNA Y RANGO - ÍNDICE COMPUESTO
-- =====================================================================

-- 2.1 Consulta buscando transacciones de una cuenta específica en un rango de fechas
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT transaccion_id, tipo_transaccion, monto, fecha_hora, estado
FROM transacciones
WHERE cuenta_id = 1520
  AND fecha_hora >= '2024-01-01 00:00:00'
ORDER BY fecha_hora DESC;

-- 2.2 Creamos un índice compuesto respetando la cardinalidad (cuenta_id primero, luego fecha_hora)
CREATE INDEX IF NOT EXISTS idx_transacciones_cuenta_fecha 
ON transacciones(cuenta_id, fecha_hora DESC);

-- 2.3 Repetimos la consulta:
-- PostgreSQL usa el índice compuesto no solo para filtrar sino también para evitar el SORT en memoria.
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT transaccion_id, tipo_transaccion, monto, fecha_hora, estado
FROM transacciones
WHERE cuenta_id = 1520
  AND fecha_hora >= '2024-01-01 00:00:00'
ORDER BY fecha_hora DESC;


-- =====================================================================
-- CASO 3: EL ANTI-PATRÓN COMÚN - INVALIDACIÓN DE ÍNDICES POR FUNCIONES
-- =====================================================================

-- Supongamos que tenemos un índice normal en el email:
CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes(email);

-- 3.1 Consulta con función LOWER() en el WHERE:
-- ¡EL ÍNDICE idx_clientes_email NO SE USA! El motor tiene que evaluar LOWER() fila por fila (Seq Scan)
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT cliente_id, nombres, email
FROM clientes
WHERE LOWER(email) = 'user_25000_gmail.com';

-- 3.2 Solución arquitectónica: Índice Basado en Expresiones (Functional Index)
CREATE INDEX IF NOT EXISTS idx_clientes_email_lower ON clientes(LOWER(email));

-- 3.3 Repetimos la consulta:
-- Ahora el motor utiliza 'Bitmap Index Scan' o 'Index Scan' sobre la expresión calculada
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT cliente_id, nombres, email
FROM clientes
WHERE LOWER(email) = 'user_25000_gmail.com';


-- =====================================================================
-- CASO 4 (BONUS TELEMETRÍA): IDENTIFICACIÓN DE SLOW QUERIES CON PG_STAT_STATEMENTS
-- Demuestra cómo un DBA detecta consultas que saturan el servidor
-- =====================================================================

SELECT 
    substring(query, 1, 60) AS consulta,
    calls AS veces_ejecutada,
    round(total_exec_time::numeric, 2) AS tiempo_total_ms,
    round(mean_exec_time::numeric, 2) AS tiempo_promedio_ms,
    rows AS filas_retornadas
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
