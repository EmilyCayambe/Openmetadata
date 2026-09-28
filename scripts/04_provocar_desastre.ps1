# =====================================================================
# PASO 4: SIMULACION DE DESASTRE (BORRADO ACCIDENTAL DE DATOS)
# =====================================================================
Write-Host "=======================================================" -ForegroundColor Red
Write-Host " [PASO 4] PROVOCANDO DESASTRE ACCIDENTAL EN VIVO" -ForegroundColor Red
Write-Host " Un administrador ejecuta por error: TRUNCATE TABLE transacciones;" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Red

docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "TRUNCATE TABLE transacciones;"

Write-Host ""
Write-Host "[!] Comprobando estado de la tabla transacciones (debe dar 0):" -ForegroundColor Yellow
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT count(*) AS total_transacciones FROM transacciones;"
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Red
Write-Host " ALERTA: La tabla transacciones ha quedado en CERO registros." -ForegroundColor Red
Write-Host " Se han borrado accidentalmente las 410,000 transacciones." -ForegroundColor Red
Write-Host "=======================================================" -ForegroundColor Red
