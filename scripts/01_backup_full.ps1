# =====================================================================
# PASO 1: BACKUP TOTAL (FULL LOGICAL BACKUP)
# =====================================================================
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " [PASO 1] GENERANDO BACKUP TOTAL DE LA BASE DE DATOS" -ForegroundColor Cyan
Write-Host " Base de datos: banco_telemetria" -ForegroundColor Yellow
Write-Host " Destino: /backup_storage/full_backups/full_backup_base.dump" -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Cyan

docker exec db-primary mkdir -p /backup_storage/full_backups
docker exec db-primary chmod 777 /backup_storage/full_backups

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

docker exec -e PGPASSWORD=postgres123 db-primary pg_dump -U admin_db -d banco_telemetria -F c -b -f /backup_storage/full_backups/full_backup_base.dump

$stopwatch.Stop()
$segundos = [math]::Round($stopwatch.Elapsed.TotalSeconds, 2)

Write-Host ""
Write-Host "[EXITO] Backup Total completado en $segundos segundos." -ForegroundColor Green
Write-Host "Tamanio y detalles del archivo generado:" -ForegroundColor Cyan
docker exec db-primary ls -lh /backup_storage/full_backups/full_backup_base.dump
Write-Host ""
Write-Host "Conteo actual en la base de datos:" -ForegroundColor Yellow
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT count(*) AS transacciones_respaldadas FROM transacciones;"
Write-Host "=======================================================" -ForegroundColor Cyan
