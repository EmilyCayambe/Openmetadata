#!/bin/bash
# =====================================================================
# SCRIPT DE DEMOSTRACIÓN: BACKUP INCREMENTAL VÍA WAL (BASH)
# =====================================================================
echo "======================================================="
echo " [DEMO] GENERANDO NUEVO SEGMENTO WAL (BACKUP INCREMENTAL)"
echo "======================================================="

docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT pg_switch_wal() AS segmento_wal_cerrado, pg_current_wal_lsn() AS lsn_actual;"

sleep 2

echo ""
echo ">>> Segmentos WAL archivados en /backup_storage/wal_archive:"
docker exec db-primary ls -lh /backup_storage/wal_archive
