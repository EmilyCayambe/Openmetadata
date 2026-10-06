#!/usr/bin/env python3
"""Diagnose a PostgreSQL EXPLAIN plan with Ollama or the OpenAI API."""

import argparse
import json
import os
import statistics
import subprocess
import sys
import urllib.error
import urllib.request
from urllib.parse import quote


QUERY = """SELECT transaccion_id, tipo_transaccion, monto, fecha_hora, estado
FROM transacciones
WHERE cuenta_id = 1520
  AND fecha_hora >= TIMESTAMP '2024-01-01 00:00:00'
ORDER BY fecha_hora DESC
LIMIT 20"""

DEMO_INDEX_DDL = (
    "CREATE INDEX IF NOT EXISTS idx_ai_demo_transacciones_cuenta_fecha "
    "ON transacciones (cuenta_id, fecha_hora DESC)"
)


def run_psql(sql, args):
    command = [
        "docker", "exec", "-i", "-e", f"PGPASSWORD={args.password}",
        args.container, "psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1",
        "-U", args.user, "-d", args.database, "-c", sql,
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "psql terminó con error")
    return result.stdout.strip()


def read_schema(args):
    sql = """SELECT COALESCE(json_agg(json_build_object(
        'column', column_name, 'type', data_type, 'nullable', is_nullable
    ) ORDER BY ordinal_position), '[]'::json)
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'transacciones'"""
    return json.loads(run_psql(sql, args))


def read_openmetadata_table():
    base_url = os.getenv("OPENMETADATA_URL", "http://localhost:8585/api").rstrip("/")
    token = os.getenv("OPENMETADATA_JWT_TOKEN")
    table_fqn = os.getenv(
        "OPENMETADATA_TABLE_FQN",
        "postgresql_demo.banco_telemetria.public.transacciones",
    )
    if not token:
        raise RuntimeError("Define OPENMETADATA_JWT_TOKEN con un token de bot de OpenMetadata")

    endpoint = (
        f"{base_url}/v1/tables/name/{quote(table_fqn, safe='')}"
        "?fields=columns,description,owners,tags"
    )
    request = urllib.request.Request(
        endpoint,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            table = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"OpenMetadata respondió HTTP {error.code} al consultar {table_fqn}: {detail}"
        ) from error

    return {
        "source": "OpenMetadata",
        "fullyQualifiedName": table.get("fullyQualifiedName", table_fqn),
        "description": table.get("description"),
        "owners": table.get("owners", [table["owner"]] if table.get("owner") else []),
        "tags": table.get("tags", []),
        "columns": [
            {
                "name": column.get("name"),
                "dataType": column.get("dataType"),
                "description": column.get("description"),
                "tags": column.get("tags", []),
            }
            for column in table.get("columns", [])
        ],
    }


def explain(args):
    sql = "EXPLAIN (ANALYZE, BUFFERS, COSTS, FORMAT JSON) " + QUERY
    return json.loads(run_psql(sql, args))[0]


def call_model(provider, prompt):
    if provider == "ollama":
        endpoint = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
        model = os.getenv("OLLAMA_MODEL", "llama3.1")
        max_tokens = int(os.getenv("OLLAMA_NUM_PREDICT", "512"))
        payload = {
            "model": model,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.2},
            "messages": [{"role": "user", "content": prompt}],
        }
        response_path = ("message", "content")
    else:
        endpoint = os.getenv("OPENAI_URL", "https://api.openai.com/v1/chat/completions")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Define OPENAI_API_KEY para usar el proveedor openai")
        payload = {
            "model": model,
            "temperature": 0.2,
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
        }
        response_path = ("choices", 0, "message", "content")

    headers = {"Content-Type": "application/json"}
    if provider == "openai":
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    timeout = int(os.getenv("AI_TIMEOUT_SECONDS", "300"))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"{provider} respondió HTTP {error.code}: {detail}"
        ) from error
    except TimeoutError as error:
        raise RuntimeError(
            f"El modelo excedió {timeout} segundos. Prueba un modelo local más pequeño "
            "o aumenta AI_TIMEOUT_SECONDS."
        ) from error
    for key in response_path:
        body = body[key]
    return body


def summarize_plan(plan):
    root = plan["Plan"]
    return {
        "node": root.get("Node Type"),
        "execution_ms": plan.get("Execution Time"),
        "planning_ms": plan.get("Planning Time"),
        "shared_hit_blocks": root.get("Shared Hit Blocks", 0),
        "shared_read_blocks": root.get("Shared Read Blocks", 0),
        "plan_rows": root.get("Plan Rows"),
        "actual_rows": root.get("Actual Rows"),
        "plan": root,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("ollama", "openai"),
                        default=os.getenv("AI_PROVIDER", "ollama"))
    parser.add_argument("--container", default="db-primary")
    parser.add_argument("--database", default="banco_telemetria")
    parser.add_argument("--user", default="admin_db")
    parser.add_argument("--password", default=os.getenv("POSTGRES_PASSWORD", "postgres123"))
    parser.add_argument("--apply-demo-index", action="store_true",
                        help="Crea el índice fijo del laboratorio y compara los planes")
    parser.add_argument("--use-openmetadata", action="store_true",
                        help="Usa columnas y contexto catalogados en OpenMetadata")
    args = parser.parse_args()

    try:
        if args.use_openmetadata:
            schema_context = read_openmetadata_table()
            if not schema_context["columns"]:
                raise RuntimeError("OpenMetadata no devolvió columnas para la tabla solicitada")
            print("CONTEXTO DE ESQUEMA: OpenMetadata")
            print(json.dumps(schema_context, indent=2, ensure_ascii=False))
        else:
            schema_context = {
                "source": "PostgreSQL information_schema",
                "columns": read_schema(args),
            }
            if not schema_context["columns"]:
                raise RuntimeError("No existe public.transacciones o no contiene columnas")
            print("CONTEXTO DE ESQUEMA: PostgreSQL information_schema")

        run_psql("DROP INDEX IF EXISTS idx_ai_demo_transacciones_cuenta_fecha", args)
        before = [explain(args) for _ in range(3)]
        before_summary = summarize_plan(before[-1])
        print("PLAN ANTES:")
        print(json.dumps(before_summary, indent=2, ensure_ascii=False))

        prompt = f"""Actúa como especialista senior en PostgreSQL. Usa solo la evidencia adjunta.
     No inventes columnas, filas, frecuencia de consultas ni mediciones posteriores. Devuelve cuatro
     secciones completas en español, en no más de 150 palabras:
     1. Diagnóstico: cita `Execution Time` en ms, `Actual Rows` del Limit y `Rows Removed by Filter`.
         `LIMIT 20` es un máximo, no prueba que se devolvieran 20 filas.
     2. DDL candidato de este laboratorio: evalúa y escribe completo
         `CREATE INDEX idx_ai_demo_transacciones_cuenta_fecha ON transacciones (cuenta_id, fecha_hora DESC);`
         como hipótesis para comparar, no como mejora garantizada. `cuenta_id` filtra por igualdad;
         `fecha_hora` filtra por rango y ordena. No alegues frecuencia no proporcionada ni propongas
         solo `fecha_hora` para esta consulta.
     3. SQL: reescribe solo si aporta valor; si no, "No necesaria".
     4. Validación: indica qué métricas comparar después. Solo se proporciona el plan ANTES; no
         inventes valores DESPUÉS.

    Reglas EXPLAIN: `Total Cost`/`Startup Cost` son unidades estimadas, NUNCA milisegundos.
    `Actual Total Time`, `Actual Startup Time` y `Execution Time` sí son milisegundos. El tiempo
    de un nodo padre incluye a sus hijos; no atribuyas todo al Sort ni sumes tiempos de nodos.
    `Shared Hit Blocks` cuenta accesos a buffers en caché, no páginas físicas únicas ni lecturas
    de disco. Basa la causa en el scan, filas reales/descartadas y buffers. No ejecutes SQL ni
    solicites credenciales.

SQL:\n{QUERY}

Contexto del catálogo y columnas observadas:\n{json.dumps(schema_context, ensure_ascii=False)}

Plan real EXPLAIN ANALYZE / BUFFERS en JSON:\n{json.dumps(before[-1], ensure_ascii=False)}"""

        try:
            diagnosis = call_model(args.provider, prompt)
            print("\nDIAGNÓSTICO DEL MODELO:")
            print(diagnosis)
        except (OSError, RuntimeError, urllib.error.URLError, KeyError, IndexError) as error:
            diagnosis = None
            print(f"\nNo se pudo consultar el modelo: {error}", file=sys.stderr)
            if not args.apply_demo_index:
                return 2

        if args.apply_demo_index:
            print("\nAplicando DDL fijo del laboratorio (no generado por IA):")
            print(DEMO_INDEX_DDL + ";")
            run_psql(DEMO_INDEX_DDL, args)
            after = [explain(args) for _ in range(3)]
            after_summary = summarize_plan(after[-1])
            before_median = statistics.median(item["Execution Time"] for item in before)
            after_median = statistics.median(item["Execution Time"] for item in after)
            print("\nPLAN DESPUÉS:")
            print(json.dumps(after_summary, indent=2, ensure_ascii=False))
            print("\nCOMPARACIÓN (3 ejecuciones por estado):")
            print(f"Mediana antes:  {before_median:.3f} ms")
            print(f"Mediana después: {after_median:.3f} ms")
            print(f"Buffers hit/read antes: {before_summary['shared_hit_blocks']}/{before_summary['shared_read_blocks']}")
            print(f"Buffers hit/read después: {after_summary['shared_hit_blocks']}/{after_summary['shared_read_blocks']}")
            print("Los tiempos dependen de caché, hardware y carga; compara también los nodos y buffers.")
        return 0
    except (RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())