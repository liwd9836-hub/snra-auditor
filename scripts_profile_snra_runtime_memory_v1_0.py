from __future__ import annotations

import argparse
import contextlib
import csv
import io
import json
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / "results" / "snra_runtime_memory_v1_0"
DEFAULT_REPORT = ROOT / "docs" / "SNRA_runtime_memory_report_v1_0.md"
CORE_MANIFEST = ROOT / "metadata" / "snra" / "snra_manifest_core_evidence_v0_1.json"


def ensure_import_path() -> None:
    root_text = str(ROOT)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def measure(label: str, func: Callable[[], dict[str, object]]) -> dict[str, object]:
    tracemalloc.start()
    start = time.perf_counter()
    try:
        extra = func()
        status = "ok"
        error = ""
    except Exception as exc:  # pragma: no cover - report path for local audits
        extra = {}
        status = "error"
        error = repr(exc)
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "label": label,
        "status": status,
        "seconds": f"{elapsed:.6f}",
        "peak_tracemalloc_mb": f"{peak / 1024 / 1024:.6f}",
        "current_tracemalloc_mb": f"{current / 1024 / 1024:.6f}",
        "error": error,
        **extra,
    }


def profile_synthetic_audit(n_samples: int, cells_per_sample: int, n_permutations: int) -> dict[str, object]:
    ensure_import_path()
    from src.snra import AuditConfig, run_audit
    from src.snra.contract import validate_dataset
    from src.snra.simulation import simulate_spatial_dataset

    dataset = simulate_spatial_dataset(n_samples=n_samples, cells_per_sample=cells_per_sample, planted=True, seed=11)
    validation = validate_dataset(dataset)
    audit, phase = run_audit(dataset, AuditConfig(k=5, n_permutations=n_permutations, seed=13))
    return {
        "n_samples": n_samples,
        "cells_per_sample": cells_per_sample,
        "n_permutations": n_permutations,
        "contract_ok": validation["ok"],
        "audit_rows": len(audit),
        "phase_rows": len(phase),
    }


def profile_manifest_cli(out_dir: Path) -> dict[str, object]:
    ensure_import_path()
    from src.snra.cli_v0_1 import main as cli_main

    manifest_out = out_dir / "profile_core_manifest"
    buffer = io.StringIO()
    argv = ["manifest", "--manifest-json", str(CORE_MANIFEST), "--out-dir", str(manifest_out)]
    with contextlib.redirect_stdout(buffer):
        code = cli_main(argv)
    summary = manifest_out / "snra_manifest_audit_summary_v0_1.tsv"
    return {
        "cli_returncode": code,
        "manifest_summary_exists": summary.exists(),
        "manifest_stdout_lines": len(buffer.getvalue().splitlines()),
    }


def profile_manifest_summary_read() -> dict[str, object]:
    manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
    rows = []
    for entry in manifest["inputs"]:
        path = ROOT / entry["path"]
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows.extend(csv.DictReader(handle, delimiter="\t"))
    return {"manifest_input_tables": len(manifest["inputs"]), "manifest_input_rows": len(rows)}


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, rows: list[dict[str, object]], out_dir: Path) -> None:
    ok_rows = [row for row in rows if row["status"] == "ok"]
    peak_values = [float(row["peak_tracemalloc_mb"]) for row in ok_rows]
    max_peak = max(peak_values) if peak_values else 0.0
    median_seconds = statistics.median(float(row["seconds"]) for row in ok_rows) if ok_rows else 0.0
    lines = [
        "# SNRA runtime and memory report v1.0",
        "",
        "Date: 2026-05-09",
        f"Python: {sys.version.split()[0]}",
        f"Platform: {platform.platform()}",
        "",
        "## Scope",
        "",
        "This lightweight profile uses synthetic SNRA inputs and bundled core manifest summary tables. It measures Python wall time and `tracemalloc` peak allocations, not whole-process resident memory.",
        "",
        "## Summary",
        "",
        f"- Profile tasks completed: {len(ok_rows)}/{len(rows)}.",
        f"- Maximum measured `tracemalloc` peak: {max_peak:.3f} MB.",
        f"- Median measured task runtime: {median_seconds:.3f} s.",
        "",
        "## Task Results",
        "",
    ]
    for row in rows:
        lines.append(
            f"- `{row['label']}`: status={row['status']}, seconds={row['seconds']}, peak={row['peak_tracemalloc_mb']} MB"
        )
        if row.get("error"):
            lines.append(f"  - Error: `{row['error']}`")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- TSV: `{rel(out_dir / 'snra_runtime_memory_profile_v1_0.tsv')}`",
            f"- JSON: `{rel(out_dir / 'snra_runtime_memory_profile_v1_0.json')}`",
            "",
            "## Caveats",
            "",
            "This is a smoke-scale software profile for submission hardening. It is not a full benchmark of external spatial packages and does not measure GPU, Docker, or optional package behavior.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile lightweight SNRA runtime and memory tasks.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--report-md", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--n-samples", type=int, default=4)
    parser.add_argument("--cells-per-sample", type=int, default=40)
    parser.add_argument("--n-permutations", type=int, default=9)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        measure(
            "synthetic_audit_small",
            lambda: profile_synthetic_audit(args.n_samples, args.cells_per_sample, args.n_permutations),
        ),
        measure("core_manifest_summary_read", profile_manifest_summary_read),
        measure("core_manifest_cli_inprocess", lambda: profile_manifest_cli(out_dir)),
    ]
    tsv_path = out_dir / "snra_runtime_memory_profile_v1_0.tsv"
    json_path = out_dir / "snra_runtime_memory_profile_v1_0.json"
    write_tsv(tsv_path, rows)
    json_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    write_report(args.report_md.resolve(), rows, out_dir)
    print(f"profile_tsv\t{tsv_path}")
    print(f"profile_json\t{json_path}")
    print(f"profile_report\t{args.report_md.resolve()}")
    return 0 if all(row["status"] == "ok" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
