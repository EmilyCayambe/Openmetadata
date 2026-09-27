# =====================================================================
# SCRIPT DE DEMOSTRACIÓN: BACKUP INCREMENTAL VÍA WAL (ARCHIVING)
# =====================================================================
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " [DEMO] GENERANDO NUEVO SEGMENTO WAL (BACKUP INCREMENTAL)" -ForegroundColor Cyan
Write-Host " En PostgreSQL, los backups incrementales se basan en capturar" -ForegroundColor Yellow
Write-Host " los segmentos de transacciones (WAL) generados desde el último backup." -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Cyan

# 1. Forzar un cambio de archivo WAL en PostgreSQL
Write-Host ">>> Forzando rotación de WAL (pg_switch_wal)..." -ForegroundColor White
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT pg_switch_wal() AS segmento_wal_cerrado, pg_current_wal_lsn() AS lsn_actual;"

Start-Sleep -Seconds 2

# 2. Listar los archivos WAL archivados en el volumen de backup separado
Write-Host ""
Write-Host ">>> Segmentos WAL archivados exitosamente en /backup_storage/wal_archive:" -ForegroundColor Green
docker exec db-primary ls -lh /backup_storage/wal_archive

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host " [CONCEPTO CLAVE PARA LA AUDIENCIA]" -ForegroundColor Yellow
Write-Host " Cada archivo de 16MB contiene todas las transacciones secuenciales (LSN)." -ForegroundColor White
Write-Host " Combinando el último Backup Total + estos archivos WAL, se puede" -ForegroundColor White
Write-Host " restaurar la base de datos a CUALQUIER segundo exacto (PITR)." -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Green
