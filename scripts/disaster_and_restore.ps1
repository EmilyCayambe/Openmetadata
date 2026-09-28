# =====================================================================
# SCRIPT DE DEMOSTRACION: SIMULACION DE DESASTRE Y RESTAURACION EN VIVO
# =====================================================================
Write-Host "=======================================================" -ForegroundColor Red
Write-Host " [ALERTA] SIMULADOR DE DESASTRE Y RESTAURACION EN VIVO" -ForegroundColor Red
Write-Host "=======================================================" -ForegroundColor Red

# 1. Contar registros actuales
Write-Host "[*] 1. Estado actual antes del desastre:" -ForegroundColor Yellow
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT (SELECT count(*) FROM clientes) as total_clientes, (SELECT count(*) FROM cuentas) as total_cuentas, (SELECT count(*) FROM transacciones) as total_transacciones;"

# 2. Localizar el ultimo backup total
$latestBackup = (docker exec db-primary sh -c "ls -t /backup_storage/full_backups/*.dump 2>/dev/null | head -n 1").Trim()
if (-not $latestBackup) {
    Write-Host "[ERROR] No se encontro ningun backup previo. Ejecuta primero: .\scripts\backup_full.ps1" -ForegroundColor Red
    exit 1
}
Write-Host ""
Write-Host "[*] Backup base seleccionado para la recuperacion: $latestBackup" -ForegroundColor Cyan

# 3. Provocar el desastre accidental
Write-Host ""
Write-Host "[*] 2. Provocando desastre accidental en vivo (DROP TABLE / FUNCTION)..." -ForegroundColor Red
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "DROP TABLE IF EXISTS transacciones CASCADE; DROP TABLE IF EXISTS cuentas CASCADE; DROP TABLE IF EXISTS clientes CASCADE; DROP FUNCTION IF EXISTS poblar_datos_sinteticos(integer) CASCADE;"

Write-Host "[*] Verificando perdida total de datos:" -ForegroundColor Yellow
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "\dt"

Write-Host ""
Write-Host "Presiona ENTER para iniciar la RESTAURACION DE EMERGENCIA..." -ForegroundColor Green
Read-Host

# 4. Restauracion
Write-Host "[*] 3. Ejecutando pg_restore desde el almacenamiento seguro..." -ForegroundColor Cyan
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

docker exec -e PGPASSWORD=postgres123 db-primary pg_restore -U admin_db -d banco_telemetria --no-owner -v $latestBackup

$stopwatch.Stop()
$segundos = [math]::Round($stopwatch.Elapsed.TotalSeconds, 2)

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host " [EXITO] RESTAURACION COMPLETADA EN $segundos SEGUNDOS" -ForegroundColor Green
Write-Host " Verificando consistencia de datos recuperados:" -ForegroundColor Cyan
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT (SELECT count(*) FROM clientes) as total_clientes, (SELECT count(*) FROM cuentas) as total_cuentas, (SELECT count(*) FROM transacciones) as total_transacciones;"
Write-Host "=======================================================" -ForegroundColor Green
