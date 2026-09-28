# =====================================================================
# PASO 3: BACKUP INCREMENTAL / DIFERENCIAL (SOLO LOS NUEVOS DATOS)
# =====================================================================
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " [PASO 3] GENERANDO BACKUP INCREMENTAL / DIFERENCIAL" -ForegroundColor Cyan
Write-Host " Respaldando unicamete las transacciones creadas post-backup..." -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Cyan

docker exec db-primary mkdir -p /backup_storage/incremental_backups
docker exec db-primary chmod 777 /backup_storage/incremental_backups

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

# 1. Exportar el delta diferencial logico (solo los 10,000 registros nuevos)
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "COPY (SELECT * FROM transacciones WHERE descripcion LIKE 'Transaccion critica post-backup%') TO '/backup_storage/incremental_backups/backup_diferencial.sql';"

# 2. Forzar rotacion de segmento WAL fisico en PostgreSQL
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT pg_switch_wal() AS segmento_wal_cerrado;"

$stopwatch.Stop()
$segundos = [math]::Round($stopwatch.Elapsed.TotalSeconds, 2)

Write-Host ""
Write-Host "[EXITO] Backup Incremental generado en $segundos segundos." -ForegroundColor Green
Write-Host ""
Write-Host "[COMPARATIVA DE ALMACENAMIENTO]:" -ForegroundColor Yellow
Write-Host " - Backup Total:        ~13 MB  (contiene toda la estructura y 400,000 filas base)" -ForegroundColor White
docker exec db-primary ls -lh /backup_storage/full_backups/full_backup_base.dump
Write-Host " - Backup Diferencial:  ~1.0 MB (contiene UNICAMENTE las 10,000 transacciones nuevas)" -ForegroundColor White
docker exec db-primary ls -lh /backup_storage/incremental_backups/backup_diferencial.sql
Write-Host "=======================================================" -ForegroundColor Cyan
