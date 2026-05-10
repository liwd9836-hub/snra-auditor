from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.snra.input_contract_v0_1 import validate_tabular_contract


RESULTS = ROOT / "results" / "snra_phase0_10_v0_1"


def read_tsv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


class SnraRegressionInputsV01Tests(unittest.TestCase):
    def test_claim_ledger_v0_9_claim_id_is_unique(self) -> None:
        path = ROOT / "metadata" / "snra" / "snra_claim_ledger_v0_9.tsv"
        rows, columns = read_tsv(path)

        self.assertIn("claim_id", columns)
        claim_ids = [row["claim_id"].strip() for row in rows]
        self.assertTrue(claim_ids, "claim ledger has no rows")
        self.assertNotIn("", claim_ids, "claim ledger has blank claim_id values")
        self.assertEqual(
            len(claim_ids),
            len(set(claim_ids)),
            "claim_id values in snra_claim_ledger_v0_9.tsv must be unique",
        )

    def test_g5_package_summary_is_inferred_as_summary_contract(self) -> None:
        path = RESULTS / "snra_phase_g5_package_benchmark_summary_v0_1.tsv"
        rows, columns = read_tsv(path)

        report = validate_tabular_contract(rows, columns)
        self.assertTrue(report.ok, report)
        self.assertEqual(report.table_kind, "summary")
        self.assertGreater(report.n_rows, 0)

    def test_real_summary_cli_writes_fail_card_but_exits_zero_by_default(self) -> None:
        input_tsv = RESULTS / "snra_phase_g5_container_full_package_summary_v0_2.tsv"
        rows, columns = read_tsv(input_tsv)
        contract = validate_tabular_contract(rows, columns, table_kind="summary")
        self.assertTrue(contract.ok, contract)

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "snra_cli"
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.snra.cli_v0_1",
                    "audit-card",
                    "--input-tsv",
                    str(input_tsv),
                    "--table-kind",
                    "summary",
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=ROOT,
                env={
                    **os.environ,
                    "OPENBLAS_NUM_THREADS": "1",
                    "OMP_NUM_THREADS": "1",
                    "MKL_NUM_THREADS": "1",
                    "NUMEXPR_NUM_THREADS": "1",
                },
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status\tFAIL", result.stdout)

            summary_path = out_dir / "snra_demo_audit_summary_v0_1.tsv"
            card_path = out_dir / "snra_demo_audit_card_v0_1.md"
            self.assertTrue(summary_path.exists())
            self.assertTrue(card_path.exists())
            self.assertGreater(summary_path.stat().st_size, 0)
            self.assertGreater(card_path.stat().st_size, 0)
            self.assertIn("Status: FAIL", card_path.read_text(encoding="utf-8"))

    def test_figure_ready_tsv_required_files_exist_and_are_nonempty(self) -> None:
        required = [
            RESULTS / "snra_figure_ready_benchmark_main_v0_1.tsv",
            RESULTS / "snra_figure_ready_external_validation_v0_1.tsv",
            RESULTS / "snra_figure_ready_package_negative_control_calibration_v0_1.tsv",
            RESULTS / "snra_figure_ready_source_manifest_v0_1.tsv",
        ]

        for path in required:
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertTrue(path.exists(), f"missing figure-ready TSV: {path}")
                self.assertGreater(path.stat().st_size, 0, f"empty figure-ready TSV: {path}")
                rows, columns = read_tsv(path)
                self.assertTrue(columns, f"missing header in figure-ready TSV: {path}")
                self.assertGreater(len(rows), 0, f"no data rows in figure-ready TSV: {path}")


if __name__ == "__main__":
    unittest.main()
