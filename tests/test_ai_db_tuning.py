import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from scripts.ai_db_tuning import (
    audit_model_diagnosis,
    index_scans,
    main,
    parse_model_diagnosis,
    run_experiment,
    summarize_samples,
)


class DiagnosisValidationTests(unittest.TestCase):
    def setUp(self):
        self.indexes = [
            {
                "name": "transacciones_pkey",
                "definition": "CREATE UNIQUE INDEX transacciones_pkey",
            }
        ]
        self.diagnosis = {
            "diagnosis": "El filtro puede justificar una prueba controlada.",
            "strategies": [
                {
                    "proposal": "No cambiaría nada",
                    "evidence": "No hay una línea base de rendimiento.",
                    "benefit": "Evitar costo de mantenimiento innecesario.",
                    "cost_or_risk": "Podrían persistir lecturas amplias.",
                }
            ],
            "indexes_considered": ["transacciones_pkey"],
            "missing_evidence": ["Frecuencia de consultas."],
            "validation": "Comparar planes y resultados en una copia.",
        }

    def test_model_contract_accepts_structured_response(self):
        parsed = parse_model_diagnosis(json.dumps(self.diagnosis))
        self.assertEqual(parsed, self.diagnosis)

    def test_non_json_response_fails_explicitly(self):
        with self.assertRaisesRegex(RuntimeError, "JSON válido"):
            parse_model_diagnosis("No cambiaría nada")

    def test_invalid_top_level_type_names_the_field_and_received_type(self):
        response = dict(self.diagnosis)
        response["missing_evidence"] = "No hay métricas."
        with self.assertRaisesRegex(
            RuntimeError, "missing_evidence: se esperaba una lista y llegó str"
        ):
            parse_model_diagnosis(json.dumps(response))

    def test_invalid_strategy_type_names_the_field(self):
        response = dict(self.diagnosis)
        response["strategies"] = [dict(self.diagnosis["strategies"][0])]
        response["strategies"][0]["benefit"] = ["Más rapidez"]
        with self.assertRaisesRegex(RuntimeError, "benefit \\(list\\)"):
            parse_model_diagnosis(json.dumps(response))

    def test_audit_accepts_exact_observed_index_list(self):
        warnings = audit_model_diagnosis(self.diagnosis, self.indexes)
        self.assertEqual(warnings, [])

    def test_audit_flags_omitted_observed_indexes(self):
        self.diagnosis["indexes_considered"] = []
        warnings = audit_model_diagnosis(self.diagnosis, self.indexes)
        self.assertTrue(any("Índices reales" in warning for warning in warnings))

    def test_audit_flags_claim_that_index_inventory_is_missing(self):
        self.diagnosis["missing_evidence"] = ["índices adicionales"]
        warnings = audit_model_diagnosis(self.diagnosis, self.indexes)
        self.assertTrue(any("sí fue consultado" in warning for warning in warnings))

    def test_sample_summary_reports_median_and_range(self):
        plans = [
            {"Execution Time": 5.0, "Plan": {"Shared Hit Blocks": 12}},
            {"Execution Time": 7.0, "Plan": {"Shared Hit Blocks": 14}},
            {"Execution Time": 6.0, "Plan": {"Shared Hit Blocks": 13}},
        ]
        summary = summarize_samples(plans)
        self.assertEqual(summary["execution_time_ms"]["median"], 6.0)
        self.assertEqual(summary["execution_time_ms"]["min"], 5.0)
        self.assertEqual(summary["execution_time_ms"]["max"], 7.0)
        self.assertEqual(summary["shared_hit_blocks_median"], 13)

    def test_plan_index_scan_extractor_reports_only_index_nodes(self):
        plan = {
            "Plan": {
                "Node Type": "Limit",
                "Plans": [
                    {
                        "Node Type": "Index Scan",
                        "Index Name": "transacciones_pkey",
                        "Plans": [],
                    },
                    {"Node Type": "Sort", "Plans": []},
                ],
            }
        }
        self.assertEqual(
            index_scans(plan),
            [{"node": "Index Scan", "index": "transacciones_pkey"}],
        )

    def test_experiment_uses_transactional_temp_copy_and_parses_multiline_plans(self):
        lines = [
            "__COPY_ROWS__", "112249",
            "__CANDIDATE_COPY_ROWS__", "112249",
            "__BASELINE_RESULT__", "same-result",
        ]
        for sample in range(1, 6):
            lines.extend((
                f"__BASELINE_PLAN_{sample}__",
                json.dumps([{
                    "Plan": {
                        "Node Type": "Limit",
                        "Actual Rows": 4,
                        "Shared Hit Blocks": 10,
                        "Shared Read Blocks": 0,
                    },
                    "Execution Time": 6.0,
                    "Planning Time": 0.1,
                }], indent=2),
            ))
        lines.extend(("__CANDIDATE_RESULT__", "same-result"))
        for sample in range(1, 6):
            lines.extend((
                f"__CANDIDATE_PLAN_{sample}__",
                json.dumps([{
                    "Plan": {
                        "Node Type": "Limit",
                        "Actual Rows": 4,
                        "Shared Hit Blocks": 8,
                        "Shared Read Blocks": 0,
                    },
                    "Execution Time": 3.0,
                    "Planning Time": 0.1,
                }], indent=2),
            ))
        process_result = SimpleNamespace(
            returncode=0,
            stdout="\n".join(lines),
            stderr="",
        )
        args = SimpleNamespace(
            password="local-only",
            container="db-primary",
            user="admin_db",
            database="banco_telemetria",
        )
        output = io.StringIO()
        with patch("scripts.ai_db_tuning.subprocess.run", return_value=process_result) as run:
            with redirect_stdout(output):
                report = run_experiment(args, "cuenta_id")

        sql_script = run.call_args.kwargs["input"]
        self.assertIn("BEGIN ISOLATION LEVEL REPEATABLE READ", sql_script)
        self.assertIn("CREATE TEMP TABLE ai_tuning_transacciones_baseline", sql_script)
        self.assertIn("CREATE TEMP TABLE ai_tuning_transacciones_candidate", sql_script)
        self.assertIn("ON COMMIT DROP", sql_script)
        self.assertIn(
            "CREATE INDEX ON pg_temp.ai_tuning_transacciones_candidate", sql_script
        )
        self.assertIn("USING btree (cuenta_id)", sql_script)
        self.assertNotIn("CREATE INDEX ON public.", sql_script)
        self.assertEqual(sql_script.count("__WARMUP_BASELINE__"), 2)
        self.assertEqual(sql_script.count("__WARMUP_CANDIDATE__"), 2)
        self.assertIn("__BASELINE_PLAN_1__\n", sql_script)
        self.assertTrue(report["source_row_result_fingerprint_matches"])
        self.assertEqual(report["source_rows_copied"], 112249)
        self.assertEqual(report["baseline"]["execution_time_ms"]["median"], 6.0)
        self.assertEqual(report["candidate"]["execution_time_ms"]["median"], 3.0)
        self.assertEqual(report["baseline"]["buffers_median"]["local_read_blocks"], 0)
        self.assertTrue(any("Tiempo mediano" in line for line in report["comparison"]))

    def test_experiment_mode_does_not_call_slow_model_again(self):
        plan = {
            "Plan": {
                "Node Type": "Limit",
                "Actual Rows": 4,
                "Shared Hit Blocks": 0,
                "Shared Read Blocks": 0,
                "Plans": [],
            },
            "Execution Time": 6.0,
            "Planning Time": 0.1,
        }
        with (
            patch(
                "sys.argv",
                [
                    "ai_db_tuning.py",
                    "--experiment-index",
                    "cuenta_id",
                    "--confirm-experiment",
                ],
            ),
            patch("scripts.ai_db_tuning.read_schema", return_value=[{"column": "id"}]),
            patch("scripts.ai_db_tuning.read_indexes", return_value=self.indexes),
            patch("scripts.ai_db_tuning.explain", return_value=plan),
            patch("scripts.ai_db_tuning.call_model") as call_model_mock,
            patch("scripts.ai_db_tuning.run_experiment") as experiment_mock,
            patch("builtins.input", return_value="EXPERIMENTAR"),
        ):
            result = main()

        self.assertEqual(result, 0)
        call_model_mock.assert_not_called()
        experiment_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
