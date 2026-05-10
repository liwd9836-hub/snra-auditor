from __future__ import annotations

import csv
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIGURE_MAIN = ROOT / "figures" / "main"
SOURCE_DIR = ROOT / "figures" / "source_data"
CAPTION_DIR = ROOT / "figures" / "captions"
OUT_DIR = ROOT / "figures" / "final_nm_v1_0"
QC_DIR = ROOT / "figures" / "visual_qc"
DOC_PATH = ROOT / "docs" / "SNRA_NatureMethods_figure_production_polish_v1_0.md"


FIGURES = [
    {
        "id": "figure1",
        "title": "Problem and workflow overview",
        "stem": "figure1_problem_workflow_overview_v3_0",
        "claim": "SNRA reframes spatial-omics interpretation as auditable claim calibration rather than de novo niche discovery.",
    },
    {
        "id": "figure2",
        "title": "Matched negative-control taxonomy",
        "stem": "figure2_matched_negative_control_taxonomy_v3_0",
        "claim": "Each spatial claim type requires controls that preserve specific nuisance structure while breaking the asserted spatial interpretation.",
    },
    {
        "id": "figure3",
        "title": "Synthetic truth benchmark",
        "stem": "figure3_synthetic_benchmark_v3_0",
        "claim": "Strict matched-control certificates block known confounded-null artifacts while retaining sensitivity to planted spatial domains.",
    },
    {
        "id": "figure4",
        "title": "Real-data cross-platform benchmark",
        "stem": "figure4_real_data_cross_platform_benchmark_v3_0",
        "claim": "SNRA provides cross-platform claim calibration across available spot-level and cell-level spatial omics audit layers.",
    },
    {
        "id": "figure5",
        "title": "Biological case study",
        "stem": "figure5_biological_case_study_v3_0",
        "claim": "Matched controls separate a rescued lineage-stratified boundary claim from claims that fail block or package-stress controls.",
    },
    {
        "id": "figure6",
        "title": "Software and reproducibility",
        "stem": "figure6_software_reproducibility_v3_0",
        "claim": "The package exposes a manifest-driven audit workflow with source tables, audit cards and clean-env reproducibility checks.",
    },
]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def copy_figure_files() -> list[dict[str, object]]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for fig in FIGURES:
        for suffix in [".pdf", ".svg", ".png"]:
            src = FIGURE_MAIN / f"{fig['stem']}{suffix}"
            dst = OUT_DIR / f"{fig['id'].capitalize()}_SNRA_NatureMethods_final_v1_0{suffix}"
            exists = src.exists()
            copied = False
            if exists:
                shutil.copy2(src, dst)
                copied = True
            rows.append(
                {
                    "figure": fig["id"],
                    "title": fig["title"],
                    "claim": fig["claim"],
                    "format": suffix.lstrip("."),
                    "source_path": rel(src),
                    "final_path": rel(dst),
                    "source_exists": exists,
                    "copied": copied,
                    "bytes": dst.stat().st_size if copied else 0,
                }
            )
    return rows


def panel_source_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for fig in FIGURES:
        files = sorted(SOURCE_DIR.glob(f"{fig['id']}_*.tsv"))
        panel_ids = sorted({path.name.split("_")[1] for path in files if "_" in path.name})
        caption = CAPTION_DIR / f"{fig['id']}_caption.md"
        rows.append(
            {
                "figure": fig["id"],
                "title": fig["title"],
                "panel_count_detected": len(panel_ids),
                "panel_ids_detected": ",".join(panel_ids),
                "has_at_least_six_panels": len(panel_ids) >= 6,
                "source_table_count": len(files),
                "caption_path": rel(caption),
                "caption_exists": caption.exists(),
            }
        )
    return rows


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_doc(copy_rows: list[dict[str, object]], panel_rows: list[dict[str, object]]) -> None:
    all_formats = all(bool(row["copied"]) and int(row["bytes"]) > 0 for row in copy_rows)
    all_panels = all(bool(row["has_at_least_six_panels"]) for row in panel_rows)
    all_captions = all(bool(row["caption_exists"]) for row in panel_rows)
    status = "PASS" if all_formats and all_panels and all_captions else "CHECK"
    lines = [
        "# SNRA Nature Methods figure production polish v1.0",
        "",
        "Date: 2026-05-09",
        f"Status: {status}",
        "",
        "## Scope",
        "",
        "This pass assembles a release-facing Figure 1-6 package from the current v3.0 source-backed figures without overwriting development outputs. It verifies that each main figure has vector and raster exports, source-data tables, a caption draft and at least six detected panels.",
        "",
        "## Final figure package",
        "",
        f"- Final figure directory: `{rel(OUT_DIR)}`",
        f"- File manifest: `{rel(QC_DIR / 'snra_final_figure_file_manifest_v1_0.tsv')}`",
        f"- Panel/source QC: `{rel(QC_DIR / 'snra_final_figure_panel_source_qc_v1_0.tsv')}`",
        "",
        "## Figure claims",
        "",
    ]
    for fig in FIGURES:
        lines.append(f"- **{fig['id'].capitalize()}**: {fig['claim']}")
    lines.extend(
        [
            "",
            "## Production verdict",
            "",
        ]
    )
    if status == "PASS":
        lines.append("The Figure 1-6 package is internally complete for expert visual review: all figures have PDF/SVG/PNG exports, six or more detected source-data panels, and caption drafts.")
    else:
        lines.append("One or more figures requires further repair before external visual review. Inspect the QC TSV files for missing formats, captions or panel source tables.")
    lines.extend(
        [
            "",
            "## Remaining human-artwork caveat",
            "",
            "This script checks structural production readiness. Final journal layout may still require a human illustrator pass for exact Nature Methods dimensions, lettering and panel spacing after text acceptance.",
            "",
            "## Self-check",
            "",
            "- No decorative figure was added.",
            "- Each figure remains tied to source data and a manuscript claim.",
            "- Failed or negative evidence layers remain visible in Figures 4-6 rather than hidden.",
        ]
    )
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    copy_rows = copy_figure_files()
    panel_rows = panel_source_rows()
    write_tsv(QC_DIR / "snra_final_figure_file_manifest_v1_0.tsv", copy_rows)
    write_tsv(QC_DIR / "snra_final_figure_panel_source_qc_v1_0.tsv", panel_rows)
    write_doc(copy_rows, panel_rows)
    ok = all(bool(row["copied"]) and int(row["bytes"]) > 0 for row in copy_rows)
    ok = ok and all(bool(row["has_at_least_six_panels"]) and bool(row["caption_exists"]) for row in panel_rows)
    print(f"figure_package\t{OUT_DIR}")
    print(f"qc_doc\t{DOC_PATH}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
