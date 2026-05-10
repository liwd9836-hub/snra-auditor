from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


MANIFEST = ROOT / "metadata" / "snra" / "snra_manifest_g5_package_v0_1.json"
CORE_MANIFEST = ROOT / "metadata" / "snra" / "snra_manifest_core_evidence_v0_1.json"


def cli_env() -> dict[str, str]:
    return {
        **os.environ,
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }


class SnraManifestCliV01Tests(unittest.TestCase):
    def run_manifest(self, out_dir: Path, *extra_args: str, manifest: Path = MANIFEST) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "src.snra.cli_v0_1",
                "manifest",
                "--manifest-json",
                str(manifest),
                "--out-dir",
                str(out_dir),
                *extra_args,
            ],
            cwd=ROOT,
            env=cli_env(),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_manifest_default_mode_g5_summary_exits_zero_and_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "manifest_out"
            result = self.run_manifest(out_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("input\tg5_container_package_summary\tFAIL", result.stdout)

            manifest_summary = out_dir / "snra_manifest_audit_summary_v0_1.tsv"
            input_out_dir = out_dir / "g5_container_package_summary"
            input_summary = input_out_dir / "snra_demo_audit_summary_v0_1.tsv"
            card = input_out_dir / "snra_demo_audit_card_v0_1.md"

            self.assertTrue(manifest_summary.exists())
            self.assertTrue(input_summary.exists())
            self.assertTrue(card.exists())
            self.assertIn("g5_container_package_summary", manifest_summary.read_text(encoding="utf-8"))
            self.assertIn("\nFAIL\tsummary\t", input_summary.read_text(encoding="utf-8"))
            self.assertIn("Status: FAIL", card.read_text(encoding="utf-8"))

    def test_manifest_strict_mode_g5_fail_certificate_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_manifest(Path(tmp) / "manifest_out", "--fail-on-certificate-fail")

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("input\tg5_container_package_summary\tFAIL", result.stdout)

    def test_invalid_manifest_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            invalid_manifest = tmp_path / "invalid_manifest.json"
            invalid_manifest.write_text('{"schema_version": "snra_manifest_v0_1", "inputs": []}', encoding="utf-8")

            result = self.run_manifest(tmp_path / "manifest_out", manifest=invalid_manifest)

            self.assertEqual(result.returncode, 2)
            self.assertIn("manifest_error\tmanifest must contain a non-empty 'inputs' list", result.stdout)

    def test_core_evidence_manifest_includes_tonic_digest_and_expected_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "core_manifest_out"
            result = self.run_manifest(out_dir, manifest=CORE_MANIFEST)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("input\ttonic_lineage_boundary_digest\tPASS", result.stdout)
            self.assertIn("input\tbcc_cosmx_fov_stress_summary\tFAIL", result.stdout)
            self.assertIn("input\tg5_container_package_summary\tFAIL", result.stdout)

            manifest_summary = out_dir / "snra_manifest_audit_summary_v0_1.tsv"
            text = manifest_summary.read_text(encoding="utf-8")
            self.assertIn("tonic_lineage_boundary_digest", text)
            self.assertIn("bcc_cosmx_fov_stress_summary", text)
            self.assertIn("g5_container_package_summary", text)

    def test_package_import_exposes_version(self) -> None:
        import src.snra as snra

        self.assertTrue(hasattr(snra, "__version__"))
        self.assertIsInstance(snra.__version__, str)
        self.assertRegex(snra.__version__, r"^\d+\.\d+\.\d+")


if __name__ == "__main__":
    unittest.main()
