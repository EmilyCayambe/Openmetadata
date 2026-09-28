# =====================================================================
# PASO 2: INSERCION DE NUEVOS DATOS SINTETICOS (POST-BACKUP)
# =====================================================================
Write-Host "=======================================================" -ForegroundColor Yellow
Write-Host " [PASO 2] INYECTANDO 10,000 NUEVAS TRANSACCIONES CRITICAS" -ForegroundColor Yellow
Write-Host " Simulando actividad de clientes posterior al backup total..." -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Yellow

$sql = @"
INSERT INTO transacciones (cuenta_id, tipo_transaccion, monto, descripcion, estado)
SELECT
    floor(random() * 90000 + 100001)::INT,
    (ARRAY['TRANSFERENCIA','DEPOSITO','RETIRO','PAGO'])[floor(random()*4)+1],
    round((random() * 2500 + 10)::numeric, 2),
    'Transaccion critica post-backup #' || s,
    'COMPLETADO'
FROM generate_series(1, 10000) AS s;
"@

docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "$sql"

Write-Host ""
Write-Host "[*] Conteo actual de transacciones en la BD (debe mostrar 410,000):" -ForegroundColor Green
docker exec -e PGPASSWORD=postgres123 db-primary psql -U admin_db -d banco_telemetria -c "SELECT count(*) AS total_transacciones FROM transacciones;"
Write-Host "=======================================================" -ForegroundColor Yellow
Write-Host " NOTA PARA LA AUDIENCIA:" -ForegroundColor Cyan
Write-Host " El Backup Total previo solo tiene 400,000 registros." -ForegroundColor White
Write-Host " Estas 10,000 transacciones nuevas aun no estan respaldadas." -ForegroundColor White
Write-Host "=======================================================" -ForegroundColor Yellow
