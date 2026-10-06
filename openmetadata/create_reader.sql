\set ON_ERROR_STOP on

SELECT format(
    'CREATE ROLE openmetadata_reader LOGIN PASSWORD %L',
    :'reader_password'
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_roles WHERE rolname = 'openmetadata_reader'
)
\gexec

SELECT format(
    'ALTER ROLE openmetadata_reader PASSWORD %L',
    :'reader_password'
)
\gexec

GRANT CONNECT ON DATABASE banco_telemetria TO openmetadata_reader;
GRANT USAGE ON SCHEMA public TO openmetadata_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO openmetadata_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE admin_db IN SCHEMA public
    GRANT SELECT ON TABLES TO openmetadata_reader;