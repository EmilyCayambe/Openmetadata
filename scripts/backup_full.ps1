# =====================================================================
# SCRIPT DE DEMOSTRACIÓN: BACKUP TOTAL (FULL LOGICAL BACKUP)
# =====================================================================
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "/backup_storage/full_backups/full_backup_$timestamp.dump"

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " [DEMO] INICIANDO BACKUP TOTAL DE LA BASE DE DATOS" -ForegroundColor Cyan
Write-Host " Base de datos: banco_telemetria" -ForegroundColor Yellow
Write-Host " Destino montado: $backupFile" -ForegroundColor Yellow
Write-Host "=======================================================" -ForegroundColor Cyan

# Crear directorio de destino dentro del contenedor
docker exec db-primary mkdir -p /backup_storage/full_backups

# Medir tiempo de ejecución
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

# Ejecutar pg_dump con formato comprimido custom (-Fc)
docker exec -e PGPASSWORD=postgres123 db-primary pg_dump `
    -U admin_db `
    -d banco_telemetria `
    -F c `
    -b -v `
    -f $backupFile

$stopwatch.Stop()

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host " [ÉXITO] BACKUP TOTAL COMPLETADO" -ForegroundColor Green
Write-Host " Tiempo transcurrido: $($stopwatch.Elapsed.TotalSeconds.ToString("0.00")) segundos" -ForegroundColor Green
Write-Host " Listando backups totales almacenados:" -ForegroundColor Cyan
docker exec db-primary ls -lh /backup_storage/full_backups
Write-Host "=======================================================" -ForegroundColor Green
