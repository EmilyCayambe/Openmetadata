-- ===============================================================
-- 01_INIT.SQL: ESQUEMA DE DATOS Y FUNCIÓN DE GENERACIÓN SINTÉTICA
-- ===============================================================

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 1. TABLA: CLIENTES
CREATE TABLE IF NOT EXISTS clientes (
    cliente_id SERIAL PRIMARY KEY,
    dni VARCHAR(15) NOT NULL,
    nombres VARCHAR(80) NOT NULL,
    apellidos VARCHAR(80) NOT NULL,
    email VARCHAR(120) NOT NULL,
    pais VARCHAR(50) NOT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO'
);

-- 2. TABLA: CUENTAS
CREATE TABLE IF NOT EXISTS cuentas (
    cuenta_id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL REFERENCES clientes(cliente_id) ON DELETE CASCADE,
    numero_cuenta VARCHAR(24) NOT NULL,
    tipo_cuenta VARCHAR(20) NOT NULL DEFAULT 'AHORROS',
    saldo NUMERIC(12,2) NOT NULL DEFAULT 1000.00,
    moneda VARCHAR(3) NOT NULL DEFAULT 'USD',
    fecha_apertura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLA: TRANSACCIONES (Tabla de alto volumen para telemetría y particionamiento/índices)
CREATE TABLE IF NOT EXISTS transacciones (
    transaccion_id BIGSERIAL PRIMARY KEY,
    cuenta_id INT NOT NULL REFERENCES cuentas(cuenta_id) ON DELETE CASCADE,
    tipo_transaccion VARCHAR(20) NOT NULL, -- 'TRANSFERENCIA', 'DEPOSITO', 'RETIRO', 'PAGO'
    monto NUMERIC(12,2) NOT NULL,
    descripcion TEXT,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'COMPLETADO' -- 'COMPLETADO', 'PENDIENTE', 'RECHAZADO'
);

-- ===============================================================
-- FUNCIÓN: poblar_datos_sinteticos(n_clientes INT)
-- Genera datos realistas en masa de forma ultrarrápida usando generate_series()
-- ===============================================================
CREATE OR REPLACE FUNCTION poblar_datos_sinteticos(p_clientes INT DEFAULT 50000)
RETURNS VOID AS $$
DECLARE
    v_inicio TIMESTAMP := clock_timestamp();
BEGIN
    RAISE NOTICE '>>> Iniciando generación masiva de % clientes...', p_clientes;

    -- Inserción masiva de clientes
    INSERT INTO clientes (dni, nombres, apellidos, email, pais, fecha_registro, estado)
    SELECT
        (10000000 + s)::TEXT AS dni,
        (ARRAY['Carlos','Ana','Luis','Maria','Jorge','Elena','Pedro','Sofia','Zaid','Lucia','Mateo','Valeria'])[floor(random()*12)+1] AS nombres,
        (ARRAY['Garcia','Rodriguez','Lopez','Martinez','Perez','Gomez','Sanchez','Diaz','Torres','Ramirez'])[floor(random()*10)+1] AS apellidos,
        'user_' || s || '_' || (ARRAY['gmail.com','outlook.com','yahoo.com','empresa.pe','uni.edu.pe'])[floor(random()*5)+1] AS email,
        (ARRAY['Peru','Colombia','Mexico','Chile','Argentina','Espana'])[floor(random()*6)+1] AS pais,
        CURRENT_TIMESTAMP - (random() * interval '730 days') AS fecha_registro,
        (ARRAY['ACTIVO','ACTIVO','ACTIVO','INACTIVO','BLOQUEADO'])[floor(random()*5)+1] AS estado
    FROM generate_series(1, p_clientes) AS s;

    RAISE NOTICE '>>> Insertando cuentas asociadas...';

    -- Inserción de 1 a 2 cuentas por cliente
    INSERT INTO cuentas (cliente_id, numero_cuenta, tipo_cuenta, saldo, moneda, fecha_apertura)
    SELECT
        c.cliente_id,
        'CTA-' || LPAD(c.cliente_id::TEXT, 8, '0') || '-' || (CASE WHEN random() > 0.5 THEN 'A' ELSE 'B' END),
        (ARRAY['AHORROS','CORRIENTE','PLAZO_FIJO'])[floor(random()*3)+1],
        round((random() * 15000 + 50)::numeric, 2),
        (ARRAY['USD','PEN','EUR'])[floor(random()*3)+1],
        c.fecha_registro + (random() * interval '10 days')
    FROM clientes c;

    RAISE NOTICE '>>> Insertando transacciones masivas (simulación de tráfico histórico)...';

    -- Inserción de 3 a 5 transacciones por cada cuenta
    INSERT INTO transacciones (cuenta_id, tipo_transaccion, monto, descripcion, fecha_hora, estado)
    SELECT
        cta.cuenta_id,
        (ARRAY['TRANSFERENCIA','DEPOSITO','RETIRO','PAGO'])[floor(random()*4)+1],
        round((random() * 1200 + 5)::numeric, 2),
        'Transaccion sintetica de simulacion #' || s || ' para telemetria',
        cta.fecha_apertura + (random() * interval '60 days'),
        (ARRAY['COMPLETADO','COMPLETADO','COMPLETADO','PENDIENTE','RECHAZADO'])[floor(random()*5)+1]
    FROM cuentas cta
    CROSS JOIN generate_series(1, 4) AS s;

    -- Forzar recolección de estadísticas del optimizador de PostgreSQL
    ANALYZE clientes;
    ANALYZE cuentas;
    ANALYZE transacciones;

    RAISE NOTICE '>>> Poblado exitoso finalizado en: % segundos.', round(extract(epoch from (clock_timestamp() - v_inicio))::numeric, 2);
END;
$$ LANGUAGE plpgsql;
