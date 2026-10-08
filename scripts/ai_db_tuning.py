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
PLAN_SAMPLE_COUNT = 5
EXPERIMENT_BASELINE_TABLE = "ai_tuning_transacciones_baseline"
EXPERIMENT_CANDIDATE_TABLE = "ai_tuning_transacciones_candidate"
EXPERIMENT_INDEXES = {
    "cuenta_id": "cuenta_id",
    "fecha_hora": "fecha_hora",
    "cuenta_id_fecha_hora": "cuenta_id, fecha_hora DESC",
}

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


def read_indexes(args):
    sql = """SELECT COALESCE(json_agg(json_build_object(
        'name', indexname, 'definition', indexdef
    ) ORDER BY indexname), '[]'::json)
    FROM pg_indexes
    WHERE schemaname = 'public' AND tablename = 'transacciones'"""
    return json.loads(run_psql(sql, args))


def read_openmetadata_table():
    base_url = os.getenv("OPENMETADATA_URL", "http://localhost:8585/api").rstrip("/")
    token = os.getenv("OPENMETADATA_JWT_TOKEN")
    table_fqn = os.getenv(
        "OPENMETADATA_TABLE_FQN",
        "postgresql_demo.banco_telemetria.public.transacciones",
    )
    if token:
        token = token.strip()
    if not token:
        raise RuntimeError("Define OPENMETADATA_JWT_TOKEN con un token de bot de OpenMetadata")
    if any(character.isspace() for character in token):
        raise RuntimeError(
            "OPENMETADATA_JWT_TOKEN debe contener solo el JWT. "
            "Copia el token desde OpenMetadata, no los comandos de PowerShell."
        )

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
    except ValueError as error:
        raise RuntimeError(
            "No se pudo construir la solicitud a OpenMetadata. "
            "Verifica que OPENMETADATA_JWT_TOKEN contenga solo el JWT."
        ) from error
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
        max_tokens = int(os.getenv("OLLAMA_NUM_PREDICT", "768"))
        payload = {
            "model": model,
            "stream": False,
            "format": "json",
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
            "max_tokens": 700,
            "response_format": {"type": "json_object"},
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


def observed_evidence(plan, indexes):
    nodes = []

    def collect(node):
        nodes.append({
            "node": node.get("Node Type"),
            "relation": node.get("Relation Name"),
            "index_used": node.get("Index Name"),
            "actual_rows": node.get("Actual Rows"),
            "rows_removed_by_filter": node.get("Rows Removed by Filter", 0),
            "filter": node.get("Filter"),
            "index_condition": node.get("Index Cond"),
        })
        for child in node.get("Plans", []):
            collect(child)

    collect(plan["Plan"])
    root = plan["Plan"]
    return {
        "execution_time_ms": plan.get("Execution Time"),
        "planning_time_ms": plan.get("Planning Time"),
        "limit": 20,
        "returned_rows": root.get("Actual Rows"),
        "root_buffers": {
            "shared_hit_blocks": root.get("Shared Hit Blocks", 0),
            "shared_read_blocks": root.get("Shared Read Blocks", 0),
        },
        "nodes": nodes,
        "existing_indexes": indexes,
    }


def median_plan_value(plans, key, *, root=False):
    values = [
        plan["Plan"].get(key, 0) if root else plan.get(key, 0)
        for plan in plans
    ]
    return statistics.median(values)


def summarize_samples(plans):
    execution_times = [plan.get("Execution Time", 0) for plan in plans]
    buffer_fields = (
        "Shared Hit Blocks",
        "Shared Read Blocks",
        "Local Hit Blocks",
        "Local Read Blocks",
    )
    buffer_medians = {
        field.lower().replace(" ", "_"): statistics.median(
            plan["Plan"].get(field, 0) for plan in plans
        )
        for field in buffer_fields
    }
    return {
        "samples": len(plans),
        "execution_time_ms": {
            "median": statistics.median(execution_times),
            "min": min(execution_times),
            "max": max(execution_times),
            "all": execution_times,
        },
        "buffers_median": buffer_medians,
        "shared_hit_blocks_median": buffer_medians["shared_hit_blocks"],
        "shared_read_blocks_median": buffer_medians["shared_read_blocks"],
        "total_hit_blocks_median": statistics.median(
            plan["Plan"].get("Shared Hit Blocks", 0)
            + plan["Plan"].get("Local Hit Blocks", 0)
            for plan in plans
        ),
        "total_read_blocks_median": statistics.median(
            plan["Plan"].get("Shared Read Blocks", 0)
            + plan["Plan"].get("Local Read Blocks", 0)
            for plan in plans
        ),
    }


def index_scans(plan):
    found = []

    def collect(node):
        node_type = node.get("Node Type")
        index_name = node.get("Index Name")
        if node_type in {"Index Scan", "Index Only Scan", "Bitmap Index Scan"}:
            if index_name:
                found.append({"node": node_type, "index": index_name})
        for child in node.get("Plans", []):
            collect(child)

    collect(plan["Plan"])
    return found


def plan_nodes(plan):
    found = []

    def collect(node):
        node_type = node.get("Node Type")
        if node_type:
            found.append(node_type)
        for child in node.get("Plans", []):
            collect(child)

    collect(plan["Plan"])
    return found


def parse_model_diagnosis(content):
    try:
        diagnosis = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "El modelo no devolvió un diagnóstico JSON válido; no se puede "
            "verificar su respuesta."
        ) from error
    required_keys = {
        "diagnosis",
        "strategies",
        "indexes_considered",
        "missing_evidence",
        "validation",
    }
    if not isinstance(diagnosis, dict) or not required_keys.issubset(diagnosis):
        missing = (
            sorted(required_keys - diagnosis.keys())
            if isinstance(diagnosis, dict)
            else ["(respuesta no es un objeto JSON)"]
        )
        raise RuntimeError(
            "La respuesta del modelo no cumple el formato requerido para "
            f"validar el diagnóstico. Campos ausentes o inválidos: {missing}."
        )
    type_errors = []
    for key in ("diagnosis", "validation"):
        if not isinstance(diagnosis[key], str):
            type_errors.append(
                f"{key}: se esperaba texto y llegó {type(diagnosis[key]).__name__}"
            )
    for key in ("strategies", "indexes_considered", "missing_evidence"):
        if not isinstance(diagnosis[key], list):
            type_errors.append(
                f"{key}: se esperaba una lista y llegó {type(diagnosis[key]).__name__}"
            )
    if type_errors:
        raise RuntimeError(
            "La respuesta del modelo contiene campos con tipos no válidos: "
            + "; ".join(type_errors)
        )
    if not 1 <= len(diagnosis["strategies"]) <= 2:
        raise RuntimeError(
            "El campo strategies debe contener de una a dos opciones; "
            f"llegaron {len(diagnosis['strategies'])}."
        )
    for key in ("indexes_considered", "missing_evidence"):
        if not all(isinstance(value, str) for value in diagnosis[key]):
            invalid = [
                f"posición {index} ({type(value).__name__})"
                for index, value in enumerate(diagnosis[key])
                if not isinstance(value, str)
            ]
            raise RuntimeError(
                f"El campo {key} debe contener solo texto; valores inválidos: "
                + ", ".join(invalid)
            )
    for strategy in diagnosis["strategies"]:
        if not isinstance(strategy, dict) or not {
            "proposal", "evidence", "benefit", "cost_or_risk"
        }.issubset(strategy):
            raise RuntimeError(
                "Cada estrategia del modelo debe incluir propuesta, evidencia, "
                "beneficio y costo/riesgo; verifica cada objeto de strategies."
            )
        invalid_strategy_fields = [
            f"{key} ({type(strategy[key]).__name__})"
            for key in ("proposal", "evidence", "benefit", "cost_or_risk")
            if not isinstance(strategy[key], str)
        ]
        if invalid_strategy_fields:
            raise RuntimeError(
                "Los campos de cada estrategia deben ser texto; valores inválidos: "
                + ", ".join(invalid_strategy_fields)
            )
    return diagnosis


def audit_model_diagnosis(diagnosis, indexes):
    warnings = []
    expected_indexes = {index["name"] for index in indexes}
    considered_indexes = diagnosis["indexes_considered"]
    if not isinstance(considered_indexes, list) or set(considered_indexes) != expected_indexes:
        warnings.append(
            "El modelo no identificó exactamente los índices observados. "
            f"Índices reales: {sorted(expected_indexes)}; "
            f"mencionados como considerados: {considered_indexes!r}."
        )

    missing_evidence = " ".join(map(str, diagnosis["missing_evidence"])).lower()
    if (
        ("índice" in missing_evidence or "indice" in missing_evidence)
        and any(
            word in missing_evidence
            for word in (
                "existencia",
                "inventario",
                "listado",
                "cuáles",
                "cuales",
                "adicionales",
                "existentes",
                "falta",
                "faltan",
                "desconoc",
            )
        )
    ):
        warnings.append(
            "El modelo dice que falta conocer el inventario de índices, pero "
            "ese inventario sí fue consultado y se muestra en la evidencia."
        )
    return warnings


def run_experiment(args, candidate):
    baseline_query = QUERY.replace(
        "FROM transacciones", f"FROM pg_temp.{EXPERIMENT_BASELINE_TABLE}"
    )
    candidate_query = QUERY.replace(
        "FROM transacciones", f"FROM pg_temp.{EXPERIMENT_CANDIDATE_TABLE}"
    )
    index_columns = EXPERIMENT_INDEXES[candidate]
    baseline_result_query = (
        "SELECT md5(COALESCE(string_agg(row_to_json(q)::text, E'\\n' "
        "ORDER BY row_to_json(q)::text), '')) "
        f"FROM ({baseline_query}) AS q;"
    )
    candidate_result_query = baseline_result_query.replace(
        f"pg_temp.{EXPERIMENT_BASELINE_TABLE}",
        f"pg_temp.{EXPERIMENT_CANDIDATE_TABLE}",
    )
    baseline_explain = (
        "EXPLAIN (ANALYZE, BUFFERS, COSTS, FORMAT JSON) " + baseline_query + ";"
    )
    candidate_explain = (
        "EXPLAIN (ANALYZE, BUFFERS, COSTS, FORMAT JSON) " + candidate_query + ";"
    )
    commands = [
        "BEGIN ISOLATION LEVEL REPEATABLE READ;",
        f"CREATE TEMP TABLE {EXPERIMENT_BASELINE_TABLE} "
        "(LIKE public.transacciones INCLUDING ALL) ON COMMIT DROP;",
        f"CREATE TEMP TABLE {EXPERIMENT_CANDIDATE_TABLE} "
        "(LIKE public.transacciones INCLUDING ALL) ON COMMIT DROP;",
        f"INSERT INTO pg_temp.{EXPERIMENT_BASELINE_TABLE} "
        "SELECT * FROM public.transacciones;",
        f"INSERT INTO pg_temp.{EXPERIMENT_CANDIDATE_TABLE} "
        "SELECT * FROM public.transacciones;",
        f"ANALYZE pg_temp.{EXPERIMENT_BASELINE_TABLE};",
        f"ANALYZE pg_temp.{EXPERIMENT_CANDIDATE_TABLE};",
        r"\echo __COPY_ROWS__",
        f"SELECT count(*) FROM pg_temp.{EXPERIMENT_BASELINE_TABLE};",
        r"\echo __CANDIDATE_COPY_ROWS__",
        f"SELECT count(*) FROM pg_temp.{EXPERIMENT_CANDIDATE_TABLE};",
        f"CREATE INDEX ON pg_temp.{EXPERIMENT_CANDIDATE_TABLE} USING btree ({index_columns});",
        f"ANALYZE pg_temp.{EXPERIMENT_CANDIDATE_TABLE};",
    ]
    for _ in range(2):
        commands.extend((r"\echo __WARMUP_BASELINE__", baseline_explain))
        commands.extend((
            r"\echo __WARMUP_CANDIDATE__",
            candidate_explain,
        ))
    commands.extend((
        r"\echo __BASELINE_RESULT__",
        baseline_result_query,
        r"\echo __CANDIDATE_RESULT__",
        candidate_result_query,
    ))
    for sample in range(1, PLAN_SAMPLE_COUNT + 1):
        if sample % 2:
            commands.extend((rf"\echo __BASELINE_PLAN_{sample}__", baseline_explain))
            commands.extend((rf"\echo __CANDIDATE_PLAN_{sample}__", candidate_explain))
        else:
            commands.extend((rf"\echo __CANDIDATE_PLAN_{sample}__", candidate_explain))
            commands.extend((rf"\echo __BASELINE_PLAN_{sample}__", baseline_explain))
    commands.extend(("COMMIT;", ""))

    command = [
        "docker", "exec", "-i", "-e", f"PGPASSWORD={args.password}",
        args.container, "psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1",
        "-U", args.user, "-d", args.database, "-f", "-",
    ]
    result = subprocess.run(
        command,
        input="\n".join(commands),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            result.stderr.strip() or "Falló el experimento temporal de PostgreSQL"
        )

    marker_blocks = {}
    current_marker = None
    current_lines = []
    for line in result.stdout.splitlines():
        if line.startswith("__") and line.endswith("__"):
            if current_marker:
                marker_blocks[current_marker] = "\n".join(current_lines).strip()
            current_marker = line
            current_lines = []
        elif current_marker:
            current_lines.append(line)
    if current_marker:
        marker_blocks[current_marker] = "\n".join(current_lines).strip()

    baseline = [
        json.loads(marker_blocks[f"__BASELINE_PLAN_{sample}__"])[0]
        for sample in range(1, PLAN_SAMPLE_COUNT + 1)
    ]
    candidate_plans = [
        json.loads(marker_blocks[f"__CANDIDATE_PLAN_{sample}__"])[0]
        for sample in range(1, PLAN_SAMPLE_COUNT + 1)
    ]
    baseline_result = marker_blocks["__BASELINE_RESULT__"]
    candidate_result = marker_blocks["__CANDIDATE_RESULT__"]
    copied_rows = int(marker_blocks["__COPY_ROWS__"])
    candidate_copied_rows = int(marker_blocks["__CANDIDATE_COPY_ROWS__"])
    if not copied_rows:
        raise RuntimeError(
            "La tabla de origen está vacía; el experimento no tiene datos que comparar."
        )
    if copied_rows != candidate_copied_rows:
        raise RuntimeError(
            "Las copias de los escenarios tienen diferente número de filas; "
            "no se puede comparar el experimento."
        )
    before_ms = statistics.median(
        plan.get("Execution Time", 0) for plan in baseline
    )
    after_ms = statistics.median(
        plan.get("Execution Time", 0) for plan in candidate_plans
    )
    difference_pct = (
        ((after_ms - before_ms) / before_ms * 100) if before_ms else None
    )
    baseline_nodes = plan_nodes(baseline[-1])
    candidate_nodes = plan_nodes(candidate_plans[-1])
    baseline_summary = summarize_samples(baseline)
    candidate_summary = summarize_samples(candidate_plans)
    comparison_lines = [
        (
            "Los resultados de la consulta coinciden."
            if baseline_result == candidate_result
            else "ALERTA: los resultados de la consulta no coinciden."
        ),
        (
            f"Tiempo mediano: {before_ms:.3f} ms sin el candidato frente a "
            f"{after_ms:.3f} ms con el candidato "
            f"({after_ms - before_ms:+.3f} ms; {difference_pct:+.1f}%)."
            if difference_pct is not None
            else "No se pudo calcular el cambio porcentual porque el tiempo base fue cero."
        ),
        (
            "Nodos del plan: "
            f"{', '.join(baseline_nodes)} antes; {', '.join(candidate_nodes)} después."
        ),
        (
            "Buffers medianos hit/read: "
            f"antes shared {baseline_summary['buffers_median']['shared_hit_blocks']}/"
            f"{baseline_summary['buffers_median']['shared_read_blocks']}, local "
            f"{baseline_summary['buffers_median']['local_hit_blocks']}/"
            f"{baseline_summary['buffers_median']['local_read_blocks']}; después shared "
            f"{candidate_summary['buffers_median']['shared_hit_blocks']}/"
            f"{candidate_summary['buffers_median']['shared_read_blocks']}, local "
            f"{candidate_summary['buffers_median']['local_hit_blocks']}/"
            f"{candidate_summary['buffers_median']['local_read_blocks']}."
        ),
        (
            "El Sort permanece en ambos escenarios."
            if "Sort" in baseline_nodes and "Sort" in candidate_nodes
            else "Revisa los nodos Sort en los planes completos para ver si el ordenamiento cambió."
        ),
        (
            "Los bloques locales y compartidos se reportan por separado; "
            "no interpretes los tiempos sin revisar sus lecturas y aciertos."
        ),
        (
            "Resultado favorable solo para esta consulta y este laboratorio; "
            "no prueba mejora bajo carga real ni justifica aplicar el índice a la tabla original."
        ),
    ]

    report = {
        "storage": (
            "Dos copias temporales en una transacción repeatable read; "
            "no persiste cambios"
        ),
        "candidate_index": index_columns,
        "source_rows_copied": copied_rows,
        "warmup_runs_per_scenario": 2,
        "measurement_order": "alternado entre dos copias independientes",
        "source_row_result_fingerprint_matches": baseline_result == candidate_result,
        "baseline": baseline_summary,
        "candidate": candidate_summary,
        "median_execution_change_percent": difference_pct,
        "median_execution_delta_ms": after_ms - before_ms,
        "baseline_index_scans": index_scans(baseline[-1]),
        "candidate_index_scans": index_scans(candidate_plans[-1]),
        "baseline_last_plan": summarize_plan(baseline[-1]),
        "candidate_last_plan": summarize_plan(candidate_plans[-1]),
        "comparison": comparison_lines,
    }
    print("\nRESULTADO DEL EXPERIMENTO AISLADO:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nCOMPARACIÓN EN PALABRAS:")
    for line in comparison_lines:
        print(f"- {line}")
    if not report["source_row_result_fingerprint_matches"]:
        raise RuntimeError(
            "Los resultados de la consulta cambiaron entre escenarios; "
            "no se declara beneficio."
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("ollama", "openai"),
                        default=os.getenv("AI_PROVIDER", "ollama"))
    parser.add_argument("--container", default="db-primary")
    parser.add_argument("--database", default="banco_telemetria")
    parser.add_argument("--user", default="admin_db")
    parser.add_argument("--password", default=os.getenv("POSTGRES_PASSWORD", "postgres123"))
    parser.add_argument("--use-openmetadata", action="store_true",
                        help="Usa columnas y contexto catalogados en OpenMetadata")
    parser.add_argument(
        "--experiment-index",
        choices=tuple(EXPERIMENT_INDEXES),
        help=(
            "Prueba una alternativa predefinida en una tabla temporal: "
            "cuenta_id, fecha_hora o cuenta_id_fecha_hora"
        ),
    )
    parser.add_argument(
        "--confirm-experiment",
        action="store_true",
        help="Solicita confirmacion interactiva antes del experimento temporal",
    )
    args = parser.parse_args()

    if args.experiment_index and not args.confirm_experiment:
        parser.error("--experiment-index requiere --confirm-experiment")
    if args.confirm_experiment and not args.experiment_index:
        parser.error("--confirm-experiment requiere --experiment-index")

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

        schema_context["existing_indexes"] = read_indexes(args)
        before = [explain(args) for _ in range(PLAN_SAMPLE_COUNT)]
        before_summary = summarize_plan(before[-1])
        evidence = observed_evidence(before[-1], schema_context["existing_indexes"])
        evidence["execution_time_ms_samples"] = [
            plan.get("Execution Time") for plan in before
        ]
        evidence["execution_time_ms_median"] = statistics.median(
            evidence["execution_time_ms_samples"]
        )
        evidence["execution_time_ms_min"] = min(
            evidence["execution_time_ms_samples"]
        )
        evidence["execution_time_ms_max"] = max(
            evidence["execution_time_ms_samples"]
        )
        print("EVIDENCIA OBSERVADA (hechos extraídos del plan):")
        print(json.dumps(evidence, indent=2, ensure_ascii=False))
        print(f"PLAN ANTES (última de {PLAN_SAMPLE_COUNT} muestras):")
        print(json.dumps(before_summary, indent=2, ensure_ascii=False))

        if args.experiment_index:
            print(
                "\nMODO EXPERIMENTO: se usará la hipótesis seleccionada "
                "previamente; no se volverá a consultar al modelo."
            )
            print(
                "\nAVISO: este experimento copia la tabla completa a dos copias "
                "temporales, consume recursos y lee los datos originales. "
                "No lo ejecutes en producción."
            )
            try:
                confirmation = input(
                    f"Escribe EXPERIMENTAR para probar {args.experiment_index} "
                    "solo en copias temporales: "
                )
            except EOFError:
                confirmation = ""
            if confirmation != "EXPERIMENTAR":
                print("Experimento cancelado; la base no fue modificada.")
                return 0
            run_experiment(args, args.experiment_index)
            return 0

        prompt = f"""Actúa como especialista senior en PostgreSQL y diagnostica sin presuponer
    una solución. Usa únicamente la evidencia adjunta: no se te ha indicado una mejora esperada.
    Puedes recomendar no cambiar nada si los datos no justifican un cambio. No inventes columnas,
    filas, índices, frecuencia de consultas, métricas ni mediciones posteriores. El inventario real
    de índices y las mediciones repetidas están incluidos abajo.
    Un `Seq Scan` lee la tabla; no usa ninguno de los índices listados. No digas que un índice se usó
    salvo que el nodo sea `Index Scan` o `Index Only Scan` y el plan identifique su nombre.
    Un `Seq Scan` por sí solo tampoco demuestra que falte un índice: evalúa filas, filtros y objetivo.
    LIMIT es un máximo, no el número de filas esperado; no concluyas que pocas filas sean
    irrelevantes. No califiques el plan como ineficiente ni un tiempo como alto/bajo sin un
    umbral, SLO o línea base proporcionados.
    No inventes ni conviertas unidades de métricas; `Total Cost`/`Startup Cost` son estimaciones y
    no prueban por sí solos que algo sea alto.
    Responde exclusivamente un objeto JSON válido, en español, con estas claves:
    "diagnosis" (interpretación breve sin repetir números medidos),
    "strategies" (máximo dos objetos con proposal, evidence, benefit, cost_or_risk;
    si no cambiarías nada, una estrategia cuyo proposal sea "No cambiaría nada"),
    "indexes_considered" (lista exacta de nombres de índices existentes que tuviste en cuenta),
    "missing_evidence" (lista de datos realmente no incluidos; no enumeres índices porque
    el inventario está explícito),
    "validation" (cómo medir una hipótesis, sin SQL ni comandos).
    No añadas hechos, claves ni Markdown. No repitas tiempos: el programa los mide y presenta.
    Una estrategia es una hipótesis, no una instrucción de ejecución.

    Reglas EXPLAIN: `Total Cost`/`Startup Cost` son unidades estimadas, nunca milisegundos.
    `Actual Total Time`, `Actual Startup Time` y `Execution Time` sí son milisegundos. El tiempo
    de un nodo padre incluye a sus hijos; no atribuyas todo al Sort ni sumes tiempos de nodos.
    `Shared Hit Blocks` cuenta accesos a buffers en caché, no páginas físicas únicas ni lecturas
    de disco. No ejecutes SQL ni solicites credenciales.
    No llames "índice usado" a un `Seq Scan` o `Sort`: solo hay índice usado si un nodo
    `Index Scan`/`Index Only Scan` identifica `Index Name`. No califiques el tiempo como alto o bajo
    sin una meta/SLO o una línea base que se te haya proporcionado.

SQL:\n{QUERY}

Esquema y contexto del catálogo observados:\n{json.dumps(schema_context, ensure_ascii=False)}

Hechos medidos por el programa (fuente de verdad para nodos y cifras):\n{json.dumps(evidence, ensure_ascii=False)}

Plan real EXPLAIN ANALYZE / BUFFERS en JSON:\n{json.dumps(before[-1], ensure_ascii=False)}"""

        try:
            diagnosis = parse_model_diagnosis(call_model(args.provider, prompt))
            print("\nANÁLISIS DEL MODELO (contrastar con la evidencia observada):")
            print(json.dumps(diagnosis, indent=2, ensure_ascii=False))
            audit_warnings = audit_model_diagnosis(
                diagnosis, schema_context["existing_indexes"]
            )
            if audit_warnings:
                print("\nADVERTENCIAS DE VALIDACIÓN:")
                for warning in audit_warnings:
                    print(f"- {warning}")
            else:
                print(
                    "\nVERIFICACIÓN: el inventario de índices indicado por el "
                    "modelo coincide con el consultado en PostgreSQL."
                )
        except (OSError, RuntimeError, urllib.error.URLError, KeyError, IndexError) as error:
            print(f"\nNo se pudo consultar el modelo: {error}", file=sys.stderr)
            return 2
        return 0
    except (RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())