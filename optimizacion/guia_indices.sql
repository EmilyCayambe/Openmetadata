select poblar_datos_sinteticos (100000)



-- ###############################################################
-- CASO 1: ÍNDICE B-TREE (Búsqueda puntual por DNI)
-- ###############################################################
-- CONTEXTO: El índice B-Tree es una estructura de árbol balanceado.
-- Es el índice por defecto en PostgreSQL y el más versátil.
-- Es ideal para: búsquedas exactas (=), rangos (<, >, BETWEEN)
-- y ordenamientos (ORDER BY).


EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT cliente_id, nombres, apellidos, email
FROM clientes
WHERE dni = '10050000';


CREATE INDEX idx_clientes_dni_btree ON clientes USING btree (dni);

ANALYZE clientes;

-- Ejecutar la consulta inicial -->


-- ###############################################################
-- CASO 2: ÍNDICE COMPUESTO MULTICOLUMNA (Rango + Ordenamiento)
-- ###############################################################
-- CONTEXTO: Un índice compuesto indexa dos o más columnas juntas.
-- El orden de las columnas importa: la primera columna se usa para
-- filtrar y la segunda para evitar operaciones de Sort en memoria.
-- Es ideal para: consultas que filtran por una columna y ordenan
-- por otra, como "las últimas N transacciones de una cuenta".


EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT transaccion_id, tipo_transaccion, monto, fecha_hora
FROM transacciones
WHERE cuenta_id = 500
ORDER BY fecha_hora DESC
LIMIT 10;

CREATE INDEX idx_transacciones_cuenta_fecha ON transacciones USING btree (cuenta_id, fecha_hora DESC);

ANALYZE transacciones;

-- Ejecutar la consulta inicial -->
-- El nodo Sort DESAPARECE porque el índice ya entrega los datos ordenados.



-- ###############################################################
-- CASO 3: ÍNDICE HASH (Búsqueda de igualdad exacta)
-- ###############################################################
-- CONTEXTO: El índice Hash usa una función de dispersión (hash)
-- para mapear valores a posiciones fijas. Es más compacto que B-Tree
-- para búsquedas de igualdad pura (=).
-- LIMITACIÓN IMPORTANTE: No sirve para rangos (<, >, BETWEEN)
-- ni para ORDER BY. Solo funciona con el operador de igualdad (=).
-- Es ideal para: columnas donde SIEMPRE se busca un valor exacto,
-- como tipos de cuenta o códigos de estado.

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT cuenta_id, cliente_id, saldo
FROM cuentas
WHERE numero_cuenta = 'CTA-00000500-A';

CREATE INDEX idx_cuentas_numero_hash ON cuentas USING hash (numero_cuenta);

ANALYZE cuentas;

-- Ejecutar la consulta inicial -->

-- PostgreSQL podría elegir un Bitmap Heap Scan si hay muchas filas
-- que coinciden con 'AHORROS'. Esto es normal y sigue siendo una mejora.



-- Tratar de usar el índice para consultar un rango
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT cuenta_id, cliente_id, saldo
FROM cuentas
WHERE numero_cuenta > 'CTA-00000500-A';


-- ###############################################################
-- CASO 4: BITMAP INDEX SCAN (Combinación de múltiples condiciones)
-- ###############################################################
-- CONTEXTO: El Bitmap Index Scan NO es un tipo de índice que se crea
-- manualmente. Es una ESTRATEGIA que el planificador de PostgreSQL
-- usa internamente cuando necesita combinar los resultados de dos o
-- más índices individuales usando operaciones lógicas (AND/OR).
--
-- Funciona en 2 fases:
--   Fase 1 (Bitmap Index Scan): Recorre cada índice y crea un "mapa
--           de bits" que marca qué páginas del disco contienen filas válidas.
--   Fase 2 (Bitmap Heap Scan):  Lee solo las páginas marcadas del disco,
--           evitando leer la tabla completa.
--
-- Es ideal para: consultas con múltiples condiciones WHERE combinadas
-- con AND u OR, donde cada condición tiene su propio índice.

-- Crearemos un índice B-Tree sobre 'estado' en la tabla clientes
-- (ya tenemos idx_clientes_dni_btree del Caso 1)
CREATE INDEX idx_clientes_estado ON clientes USING btree (estado);

ANALYZE clientes;

-- Ejecutamos una consulta con DOS condiciones combinadas (OR)

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT cliente_id, dni, nombres, estado
FROM clientes
WHERE dni = '10050000'
   OR estado = 'BLOQUEADO';


-- ###############################################################
-- AUDITORÍA DE CONSULTAS MÁS COSTOSAS (pg_stat_statements)
-- ###############################################################
-- Esta vista acumula estadísticas de TODAS las consultas ejecutadas.
-- Útil para identificar qué queries consumen más tiempo en producción.

SELECT
    LEFT(query, 80) AS consulta_resumida,
    calls AS ejecuciones,
    ROUND(total_exec_time::numeric, 2) AS tiempo_total_ms,
    ROUND(mean_exec_time::numeric, 2) AS tiempo_promedio_ms,
    rows AS filas_retornadas
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = 'banco_telemetria')
ORDER BY total_exec_time DESC
LIMIT 10;




-- ###############################################################
-- LIMPIEZA (Ejecutar SOLO si deseas eliminar los índices creados)
-- ###############################################################
 DROP INDEX IF EXISTS idx_clientes_dni_btree;
 DROP INDEX IF EXISTS idx_transacciones_cuenta_fecha;
 DROP INDEX IF EXISTS idx_cuentas_numero_hash;
 DROP INDEX IF EXISTS idx_clientes_estado;
