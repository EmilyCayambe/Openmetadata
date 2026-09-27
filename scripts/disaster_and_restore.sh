#!/bin/bash
# =====================================================================
# SCRIPT DE DEMOSTRACIÓN: SIMULACIÓN DE DESASTRE Y RESTAURACIÓN (BASH)
# =====================================================================
echo "======================================================="
echo " [ALERTA] SIMULADOR DE DESASTRE Y RESTAURACIÓN EN VIVO"
echo "======================================================="

LATEST_BACKUP=$(docker exec db-primary sh -c "ls -t /backup_storage/full_backups/*.dump 2>/dev/null | head -n 1")
if [ -z "$LATEST_BACKUP" ]; then
    echo "No se encontró ningún backup. Ejecuta primero: ./scripts/backup_full.sh"
    exit 1
fi

echo "Último backup: ${LATEST_BACKUP}"
echo ""
echo "1. Provocando desastre accidental..."
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "DROP TABLE IF EXISTS transacciones CASCADE; DROP TABLE IF EXISTS cuentas CASCADE; DROP TABLE IF EXISTS clientes CASCADE;"

echo "Verificando tablas (debería estar vacío):"
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "\dt"

read -p "Presiona ENTER para restaurar..."

echo "2. Restaurando desde backup..."
docker exec -e PGPASSWORD=postgres123 db-primary pg_restore \
    -U admin_db \
    -d banco_telemetria \
    --no-owner \
    -v "${LATEST_BACKUP}"

echo ""
echo "======================================================="
echo " [ÉXITO] RESTAURACIÓN COMPLETADA"
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT (SELECT count(*) FROM clientes) as total_clientes, (SELECT count(*) FROM cuentas) as total_cuentas, (SELECT count(*) FROM transacciones) as total_transacciones;"
echo "======================================================="
