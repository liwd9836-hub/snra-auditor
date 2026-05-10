from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / "results" / "snra_runtime_memory_v1_0" / "submission_reproduction_v1_0"
CORE_MANIFEST = ROOT / "metadata" / "snra" / "snra_manifest_core_evidence_v0_1.json"
FIGURE_REPORT = ROOT / "reports" / "snra_publication_figures_v0_1"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def run_command(command: list[str], out_dir: Path) -> dict[str, object]:
    env = {
        **os.environ,
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }
    start = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    elapsed = time.perf_counter() - start
    log_path = out_dir / "command_log.txt"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write("$ " + " ".join(command) + "\n")
        handle.write(f"returncode: {result.returncode}\n")
        handle.write("--- stdout ---\n")
        handle.write(result.stdout)
        handle.write("\n--- stderr ---\n")
        handle.write(result.stderr)
        handle.write("\n\n")
    return {"command": " ".join(command), "returncode": result.returncode, "seconds": elapsed}


def load_manifest_inputs(manifest_path: Path) -> list[dict[str, object]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    inputs = manifest.get("inputs", [])
    if not isinstance(inputs, list):
        raise ValueError("manifest inputs must be a list")
    return [entry for entry in inputs if isinstance(entry, dict)]


def write_source_inventory(out_dir: Path) -> Path:
    inventory_path = out_dir / "snra_core_source_inventory_v1_0.tsv"
    rows: list[dict[str, object]] = []
    for entry in load_manifest_inputs(CORE_MANIFEST):
        source = ROOT / str(entry["path"])
        rows.append(
            {
                "role": "core_manifest_input",
                "id": entry.get("id", ""),
                "path": rel(source),
                "exists": source.exists(),
                "bytes": source.stat().st_size if source.exists() else "",
            }
        )
    if FIGURE_REPORT.exists():
        for path in sorted(FIGURE_REPORT.glob("*")):
            if path.is_file() and path.suffix.lower() in {".tsv", ".md", ".png", ".svg"}:
                rows.append(
                    {
                        "role": "existing_figure_or_source_asset",
                        "id": path.stem,
                        "path": rel(path),
                        "exists": True,
                        "bytes": path.stat().st_size,
                    }
                )
    with inventory_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=["role", "id", "path", "exists", "bytes"])
        writer.writeheader()
        writer.writerows(rows)
    return inventory_path


def write_report(out_dir: Path, command_rows: list[dict[str, object]], inventory_path: Path) -> Path:
    manifest_summary = out_dir / "core_manifest" / "snra_manifest_audit_summary_v0_1.tsv"
    status = "PASS" if manifest_summary.exists() and all(row["returncode"] == 0 for row in command_rows) else "CHECK"
    lines = [
        "# SNRA submission reproduction v1.0",
        "",
        f"Status: {status}",
        f"Date: 2026-05-09",
        f"Python: {sys.version.split()[0]}",
        f"Platform: {platform.platform()}",
        "",
        "## Commands",
        "",
    ]
    for row in command_rows:
        lines.append(f"- `{row['command']}` -> exit {row['returncode']} in {float(row['seconds']):.2f} s")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Core manifest summary: `{rel(manifest_summary)}`",
            f"- Source and figure inventory: `{rel(inventory_path)}`",
            f"- Command log: `{rel(out_dir / 'command_log.txt')}`",
            "",
            "## Scope",
            "",
            "This reproduction smoke run regenerates the core SNRA manifest audit cards and writes an auditable inventory of bundled source tables and current figure/source assets. It intentionally avoids Docker and heavy optional spatial-package installation.",
        ]
    )
    report_path = out_dir / "SNRA_submission_reproduction_report_v1_0.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a lightweight SNRA submission reproduction smoke workflow.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--skip-manifest", action="store_true", help="Only write source/figure inventory and report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    command_rows: list[dict[str, object]] = []
    if not args.skip_manifest:
        command_rows.append(
            run_command(
                [
                    sys.executable,
                    "-m",
                    "src.snra.cli_v0_1",
                    "manifest",
                    "--manifest-json",
                    str(CORE_MANIFEST),
                    "--out-dir",
                    str(out_dir / "core_manifest"),
                ],
                out_dir,
            )
        )
    inventory_path = write_source_inventory(out_dir)
    report_path = write_report(out_dir, command_rows, inventory_path)
    print(f"reproduction_report\t{report_path}")
    print(f"source_inventory\t{inventory_path}")
    return 0 if all(row["returncode"] == 0 for row in command_rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
