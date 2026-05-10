from __future__ import annotations

import argparse
import csv
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / "results" / "snra_clean_env_ci_v1_0"
DEFAULT_DOC = ROOT / "docs" / "SNRA_clean_env_CI_report_v1_0.md"
VENV_NAME = ".snra_clean_env_ci_tmp"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def safe_rmtree(path: Path) -> None:
    resolved = path.resolve()
    root = ROOT.resolve()
    if resolved == root or root not in resolved.parents:
        raise RuntimeError(f"Refusing to delete path outside workspace: {resolved}")
    if path.exists():
        shutil.rmtree(path)


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def venv_snra(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "snra.exe"
    return venv_dir / "bin" / "snra"


def run_command(command: list[str], out_dir: Path, label: str, timeout: int = 600) -> dict[str, object]:
    env = {
        **os.environ,
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "PYTHONUTF8": "1",
    }
    start = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    seconds = time.perf_counter() - start
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "logs" / f"{label}.log"
    log_path.write_text(
        "$ " + " ".join(command) + "\n"
        + f"returncode: {result.returncode}\n"
        + "--- stdout ---\n"
        + result.stdout
        + "\n--- stderr ---\n"
        + result.stderr
        + "\n",
        encoding="utf-8",
    )
    return {
        "label": label,
        "command": " ".join(command),
        "returncode": result.returncode,
        "seconds": round(seconds, 3),
        "stdout_bytes": len(result.stdout.encode("utf-8", errors="ignore")),
        "stderr_bytes": len(result.stderr.encode("utf-8", errors="ignore")),
        "log_path": rel(log_path),
    }


def write_command_table(rows: list[dict[str, object]], out_dir: Path) -> Path:
    path = out_dir / "clean_env_command_log.tsv"
    fieldnames = ["label", "command", "returncode", "seconds", "stdout_bytes", "stderr_bytes", "log_path"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_report(rows: list[dict[str, object]], out_dir: Path, report_path: Path, cleanup_status: str) -> Path:
    ok = all(int(row["returncode"]) == 0 for row in rows)
    manifest_summary = out_dir / "core_manifest" / "snra_manifest_audit_summary_v0_1.tsv"
    table_path = out_dir / "clean_env_command_log.tsv"
    lines = [
        "# SNRA clean-environment CI report v1.0",
        "",
        f"Date: 2026-05-09",
        f"Status: {'PASS' if ok else 'FAIL'}",
        f"Host Python: {sys.version.split()[0]}",
        f"Platform: {platform.platform()}",
        f"Temporary environment cleanup: {cleanup_status}",
        "",
        "## Scope",
        "",
        "This report tests the SNRA core package in a freshly created local virtual environment. It deliberately excludes heavy external package benchmarks such as Squidpy, CellCharter and SpaceFlow, which belong in the separate container benchmark environment.",
        "",
        "## Commands",
        "",
    ]
    for row in rows:
        lines.append(f"- `{row['label']}`: exit {row['returncode']} in {row['seconds']} s; log `{row['log_path']}`")
    lines.extend(
        [
            "",
            "## Key outputs",
            "",
            f"- Command table: `{rel(table_path)}`",
            f"- Core manifest summary: `{rel(manifest_summary)}`; exists={manifest_summary.exists()}",
            "",
            "## Interpretation",
            "",
        ]
    )
    if ok:
        lines.append("The core `snra-auditor` package installs and runs in a clean Python virtual environment. This closes the clean-env core CI blocker for the lightweight SNRA package surface.")
    else:
        lines.append("At least one clean-env command failed. The command log identifies whether the failure is installation, CLI, manifest, test or script-compilation related. Do not claim clean-env reproducibility until the failing step is repaired.")
    lines.extend(
        [
            "",
            "## Self-check",
            "",
            "- This test does not claim full reproducibility of optional external package benchmarks.",
            "- Strict manifest failure is not tested here because scientifically failed certificates are expected in stress-control layers.",
            "- The temporary environment is removed after execution to prevent local disk growth.",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a clean venv and run core SNRA package CI commands.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--keep-venv", action="store_true", help="Keep the temporary virtual environment for debugging.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    venv_dir = (ROOT / VENV_NAME).resolve()
    rows: list[dict[str, object]] = []
    cleanup_status = "not_attempted"

    safe_rmtree(venv_dir)
    try:
        rows.append(run_command([sys.executable, "-m", "venv", str(venv_dir)], out_dir, "create_venv", timeout=180))
        py = venv_python(venv_dir)
        snra = venv_snra(venv_dir)
        if int(rows[-1]["returncode"]) == 0:
            rows.append(run_command([str(py), "-m", "pip", "install", "--upgrade", "pip"], out_dir, "upgrade_pip", timeout=600))
            rows.append(run_command([str(py), "-m", "pip", "install", "."], out_dir, "install_package", timeout=900))
            rows.append(run_command([str(snra), "--help"], out_dir, "snra_help", timeout=180))
            rows.append(
                run_command(
                    [
                        str(snra),
                        "manifest",
                        "--manifest-json",
                        "examples/snra/snra_manifest_core_evidence_example_v0_1.json",
                        "--out-dir",
                        str(out_dir / "core_manifest"),
                    ],
                    out_dir,
                    "core_manifest",
                    timeout=600,
                )
            )
            rows.append(
                run_command(
                    [
                        str(py),
                        "-m",
                        "unittest",
                        "tests.test_snra_package_prototype_v0_1",
                        "tests.test_snra_regression_inputs_v0_1",
                        "tests.test_snra_manifest_cli_v0_1",
                        "tests.snra.test_snra_minimal",
                    ],
                    out_dir,
                    "focused_unittest",
                    timeout=600,
                )
            )
            rows.append(
                run_command(
                    [
                        str(py),
                        "-m",
                        "py_compile",
                        "scripts_run_snra_submission_reproduction_v1_0.py",
                        "scripts_profile_snra_runtime_memory_v1_0.py",
                        "scripts_run_snra_synthetic_truth_benchmark_v1_0.py",
                    ],
                    out_dir,
                    "script_py_compile",
                    timeout=180,
                )
            )
    finally:
        write_command_table(rows, out_dir)
        if args.keep_venv:
            cleanup_status = f"kept_at_{rel(venv_dir)}"
        else:
            safe_rmtree(venv_dir)
            cleanup_status = "removed"
        report_path = write_report(rows, out_dir, args.report_path.resolve(), cleanup_status)
        print(f"clean_env_report\t{report_path}")
        print(f"command_log\t{out_dir / 'clean_env_command_log.tsv'}")

    return 0 if rows and all(int(row["returncode"]) == 0 for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
