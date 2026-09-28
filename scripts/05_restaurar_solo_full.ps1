# =====================================================================
# PASO 5: RESTAURACION FASE 1 (SOLO BACKUP TOTAL)
# =====================================================================
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " [PASO 5] RESTAURACION FASE 1: APLICANDO SOLO EL BACKUP TOTAL" -ForegroundColor Cyan
Write-Host " Archivo origen: /backup_storage/full_backups/full_backup_base.dump" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Cyan

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

docker exec -e PGPASSWORD=postgres123 db-primary pg_restore -U admin_db -d banco_telemetria --data-only -t transacciones /backup_storage/full_backups/full_backup_base.dump

$stopwatch.Stop()
$segundos = [math]::Round($stopwatch.Elapsed.TotalSeconds, 2)

Write-Host ""
Write-Host "[*] Backup Total restaurado en $segundos segundos." -ForegroundColor Green
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Yellow
Write-Host " [OBSERVACION CRITICA PARA LA AUDIENCIA]" -ForegroundColor Yellow
Write-Host " Conteo de transacciones recuperadas:" -ForegroundColor White
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT count(*) AS transacciones_actuales FROM transacciones;"
Write-Host ""
Write-Host " ALERTA: Solo hay 400,000 transacciones." -ForegroundColor Red
Write-Host " FALTAN las 10,000 transacciones criticas que entraron durante el dia." -ForegroundColor Red
Write-Host " Si el banco solo dependiera del Backup Total, habria PERDIDA DE DATOS." -ForegroundColor Red
Write-Host "=======================================================" -ForegroundColor Yellow
