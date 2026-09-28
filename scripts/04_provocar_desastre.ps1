# =====================================================================
# PASO 4: SIMULACION DE DESASTRE (ERROR HUMANO ACCIDENTAL)
# =====================================================================
Write-Host "=======================================================" -ForegroundColor Red
Write-Host " [PASO 4] PROVOCANDO DESASTRE ACCIDENTAL EN VIVO" -ForegroundColor Red
Write-Host " Un administrador ejecuta por error DROP TABLE transacciones;" -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Red

docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "DROP TABLE transacciones CASCADE;"

Write-Host ""
Write-Host "[!] Comprobando estado de la tabla transacciones:" -ForegroundColor Yellow
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT count(*) FROM transacciones;"
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Red
Write-Host " ALERTA: La tabla transacciones ha desaparecido completamente." -ForegroundColor Red
Write-Host " Se han perdido las 410,000 transacciones de la base de datos." -ForegroundColor Red
Write-Host "=======================================================" -ForegroundColor Red
