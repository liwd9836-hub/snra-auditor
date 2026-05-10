from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.snra.audit_card_v0_1 import render_audit_card
from src.snra.certificate_scorer_v0_1 import score_detail_certificate
from src.snra.input_contract_v0_1 import validate_tabular_contract
from src.snra.null_ladder_v0_1 import label_shuffle_changed_fraction, summarize_null_ladder


PASS_ROWS = [
    {
        "sample_id": "S1",
        "label": "niche_a",
        "control": "within_sample_label_shuffle",
        "observed_same_label_neighbor_fraction": "0.60",
        "null_mean": "0.20",
        "empirical_p_greater": "0.01",
        "effective_changed_fraction": "0.70",
        "passes_control": "True",
    },
    {
        "sample_id": "S2",
        "label": "niche_a",
        "control": "within_sample_label_shuffle",
        "observed_same_label_neighbor_fraction": "0.55",
        "null_mean": "0.21",
        "empirical_p_greater": "0.02",
        "effective_changed_fraction": "0.65",
        "passes_control": "True",
    },
    {
        "sample_id": "S1",
        "label": "niche_a",
        "control": "spatial_block_shuffle",
        "observed_same_label_neighbor_fraction": "0.60",
        "null_mean": "0.34",
        "empirical_p_greater": "0.03",
        "effective_changed_fraction": "0.42",
        "passes_control": "True",
    },
]


class SnraPackagePrototypeV01Tests(unittest.TestCase):
    def test_label_shuffle_changed_fraction_is_nonzero_and_bounded(self) -> None:
        rate = label_shuffle_changed_fraction(["A", "A", "B", "B", "C", "C"], seed=3)
        self.assertGreater(rate, 0.0)
        self.assertLessEqual(rate, 1.0)

    def test_certificate_scorer_passes_and_fails(self) -> None:
        passed = score_detail_certificate(PASS_ROWS, min_pass_rate=0.60)
        self.assertTrue(passed.passed, passed)
        fail_rows = [dict(row, empirical_p_greater="0.80", passes_control="False") for row in PASS_ROWS]
        failed = score_detail_certificate(fail_rows, min_pass_rate=0.60)
        self.assertFalse(failed.passed)
        self.assertIn("median_p>0.05", failed.failure_reasons)

    def test_audit_card_output_contains_core_sections(self) -> None:
        contract = validate_tabular_contract(PASS_ROWS, PASS_ROWS[0].keys(), table_kind="detail")
        certificate = score_detail_certificate(PASS_ROWS, min_pass_rate=0.60)
        ladder = summarize_null_ladder(PASS_ROWS)
        card = render_audit_card("Prototype Card", contract, certificate, ladder)
        self.assertIn("# Prototype Card", card)
        self.assertIn("Status: PASS", card)
        self.assertIn("## Null Ladder", card)
        self.assertIn("within_sample_label_shuffle", card)
        self.assertIn("does not establish causal mechanism", card)

    def test_cli_demo_generates_summary_and_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts_run_snra_demo_cli_v0_1.py",
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((out_dir / "snra_demo_audit_summary_v0_1.tsv").exists())
            card_path = out_dir / "snra_demo_audit_card_v0_1.md"
            self.assertTrue(card_path.exists())
            self.assertIn("Status: PASS", card_path.read_text(encoding="utf-8"))

    def test_package_summary_contract_and_cli_do_not_fail_on_certificate_fail_by_default(self) -> None:
        rows = [
            {
                "dataset": "CRC_ST",
                "tool": "Squidpy",
                "control": "observed",
                "positive_call_rate": "0.60",
            },
            {
                "dataset": "CRC_ST",
                "tool": "Squidpy",
                "control": "spatial_block_shuffle",
                "positive_call_rate": "0.55",
            },
            {
                "dataset": "Wu_breast",
                "tool": "CellCharter",
                "control": "observed",
                "positive_call_rate": "0.50",
            },
        ]
        contract = validate_tabular_contract(rows, rows[0].keys(), table_kind="summary")
        self.assertTrue(contract.ok, contract)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            in_path = tmp_path / "package_summary.tsv"
            in_path.write_text(
                "dataset\ttool\tcontrol\tpositive_call_rate\n"
                "CRC_ST\tSquidpy\tobserved\t0.60\n"
                "CRC_ST\tSquidpy\tspatial_block_shuffle\t0.55\n"
                "Wu_breast\tCellCharter\tobserved\t0.50\n",
                encoding="utf-8",
            )
            out_dir = tmp_path / "out"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts_run_snra_demo_cli_v0_1.py",
                    "--input-tsv",
                    str(in_path),
                    "--table-kind",
                    "summary",
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status\tFAIL", result.stdout)
            self.assertIn("Status: FAIL", (out_dir / "snra_demo_audit_card_v0_1.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
