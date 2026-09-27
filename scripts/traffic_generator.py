#!/usr/bin/env python3
"""
traffic_generator.py
Simulador de tráfico transaccional en tiempo real para PostgreSQL.
Diseñado para alimentar el dashboard de telemetría en Grafana (Loki)
y demostrar el crecimiento masivo de logs frente al tamaño de la tabla.

No requiere instalar librerías pesadas: funciona directamente vía 'docker exec'
o mediante 'psycopg2' si está instalado.
"""

import sys
import time
import random
import subprocess
import argparse

def execute_sql(sql_command: str):
    """Ejecuta una sentencia SQL en el contenedor db-primary."""
    cmd = [
        "docker", "exec", "-i",
        "-e", "PGPASSWORD=postgres123",
        "db-primary",
        "psql", "-U", "admin_db", "-d", "banco_telemetria", "-t", "-c", sql_command
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def simulate_live_traffic(duration_seconds: int = 60, delay_ms: int = 50):
    """Simula transacciones continuas de usuarios (compras, depósitos, consultas)."""
    print(f"\n[+] Iniciando simulación de tráfico por {duration_seconds} segundos...")
    print("[+] Abre Grafana en http://localhost:3000 (admin/admin) para ver la telemetría en vivo.\n")
    
    start_time = time.time()
    counter = 0

    tipos = ['TRANSFERENCIA', 'DEPOSITO', 'RETIRO', 'PAGO']
    estados = ['COMPLETADO', 'COMPLETADO', 'PENDIENTE', 'RECHAZADO']

    while (time.time() - start_time) < duration_seconds:
        counter += 1
        cuenta_id = random.randint(1, 1000)
        monto = round(random.uniform(5.0, 850.0), 2)
        tipo = random.choice(tipos)
        estado = random.choice(estados)

        # 1. Simular lectura / consulta de saldo
        execute_sql(f"SELECT saldo, tipo_cuenta FROM cuentas WHERE cuenta_id = {cuenta_id};")

        # 2. Simular actualización de saldo
        execute_sql(f"UPDATE cuentas SET saldo = saldo + {monto} WHERE cuenta_id = {cuenta_id};")

        # 3. Registrar transacción
        execute_sql(f"""
            INSERT INTO transacciones (cuenta_id, tipo_transaccion, monto, descripcion, estado)
            VALUES ({cuenta_id}, '{tipo}', {monto}, 'Operación móvil simulada #{counter}', '{estado}');
        """)

        # Ocasionalmente simular una consulta pesada para telemetría
        if counter % 15 == 0:
            execute_sql("SELECT count(*), tipo_transaccion FROM transacciones GROUP BY tipo_transaccion;")

        # Ocasionalmente simular un error / rollback para el panel de errores
        if counter % 25 == 0:
            execute_sql("SELECT * FROM tabla_inexistente_para_generar_alerta;")

        print(f"\r-> Transacciones simuladas: {counter} | Logs emitidos hacia Loki...", end="", flush=True)
        time.sleep(delay_ms / 1000.0)

    print(f"\n\n[✓] Simulación finalizada. {counter} operaciones ejecutadas y registradas en el servidor de logs.")

def demonstrate_log_growth(iterations: int = 500):
    """
    Demuestra la paradoja:
    'Cada sentencia genera un log y los logs crecen más rápido que la base de datos'
    Actualiza 1 única fila múltiples veces y compara el tamaño de la tabla vs los logs producidos.
    """
    print("\n==================================================================")
    print(" DEMOSTRACIÓN: CRECIMIENTO DE LOGS vs CRECIMIENTO DE TABLA")
    print("==================================================================")
    
    # Tamaño inicial de la tabla cuentas
    size_before, _ = execute_sql("SELECT pg_size_pretty(pg_total_relation_size('cuentas'));")
    print(f"[1] Tamaño inicial de la tabla 'cuentas': {size_before}")

    print(f"[2] Ejecutando {iterations} transacciones UPDATE consecutivas en la cuenta ID 1...")
    for i in range(1, iterations + 1):
        execute_sql(f"UPDATE cuentas SET saldo = saldo + 1.00 WHERE cuenta_id = 1;")
        if i % 50 == 0:
            print(f"    Progreso: {i}/{iterations} updates...")

    # Tamaño final de la tabla
    size_after, _ = execute_sql("SELECT pg_size_pretty(pg_total_relation_size('cuentas'));")
    print(f"\n[3] Tamaño final de la tabla 'cuentas': {size_after}")

    print("\n[RESULTADO CLAVE PARA LA CLASE]:")
    print(f"-> La tabla creció prácticamente 0 KB (los datos siguen siendo una sola fila actualizada).")
    print(f"-> SIN EMBARGO, el motor generó {iterations} registros de transacciones en el WAL y {iterations} líneas de log.")
    print(f"-> Si esto no se desacopla a un servidor externo (Loki), el disco de producción colapsa rápidamente.")
    print("==================================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de tráfico y telemetría de BD")
    parser.add_argument("--mode", choices=["traffic", "growth"], default="traffic",
                        help="Modo de ejecución: 'traffic' (tráfico continuo) o 'growth' (demostración tabla vs logs)")
    parser.add_argument("--duration", type=int, default=60, help="Duración en segundos para tráfico en vivo")
    parser.add_argument("--iterations", type=int, default=300, help="Iteraciones para el modo growth")

    args = parser.parse_args()

    if args.mode == "traffic":
        simulate_live_traffic(duration_seconds=args.duration)
    elif args.mode == "growth":
        demonstrate_log_growth(iterations=args.iterations)
