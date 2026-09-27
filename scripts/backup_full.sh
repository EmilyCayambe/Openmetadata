#!/bin/bash
# =====================================================================
# SCRIPT DE DEMOSTRACIÓN: BACKUP TOTAL (BASH)
# =====================================================================
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="/backup_storage/full_backups/full_backup_${TIMESTAMP}.dump"

echo "======================================================="
echo " [DEMO] INICIANDO BACKUP TOTAL DE LA BASE DE DATOS"
echo " Base de datos: banco_telemetria"
echo " Destino: ${BACKUP_FILE}"
echo "======================================================="

docker exec db-primary mkdir -p /backup_storage/full_backups

docker exec -e PGPASSWORD=postgres123 db-primary pg_dump \
    -U admin_db \
    -d banco_telemetria \
    -F c \
    -b -v \
    -f "${BACKUP_FILE}"

echo ""
echo "======================================================="
echo " [ÉXITO] BACKUP TOTAL COMPLETADO"
docker exec db-primary ls -lh /backup_storage/full_backups
echo "======================================================="
