from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl


ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "figures" / "final_nm_v1_0"
OUT_DIR = ROOT / "figures" / "final_nm_v1_1_artwork"
QC_DIR = ROOT / "figures" / "visual_qc"
DOC_PATH = ROOT / "docs" / "SNRA_final_artwork_pass_v1_1.md"


PALETTE = {
    "ink": "#253238",
    "muted": "#60717A",
    "paper": "#FBFAF7",
    "line": "#D9DEE2",
    "blue": "#2F6B9A",
    "teal": "#2A9D8F",
    "amber": "#D4A252",
    "coral": "#D96C5F",
    "slate": "#596A7A",
    "green": "#3B8C6E",
}


FIGURES = [
    {
        "id": "Figure1",
        "src": "Figure1_SNRA_NatureMethods_final_v1_0.png",
        "title": "Problem and workflow overview",
        "claim": "SNRA converts spatial outputs into auditable claims with explicit provenance, controls and reportable certificates.",
        "accent": "blue",
    },
    {
        "id": "Figure2",
        "src": "Figure2_SNRA_NatureMethods_final_v1_0.png",
        "title": "Matched negative-control taxonomy",
        "claim": "Control families are matched to claim type: each preserves nuisance structure while breaking the asserted interpretation.",
        "accent": "teal",
    },
    {
        "id": "Figure3",
        "src": "Figure3_SNRA_NatureMethods_final_v1_0.png",
        "title": "Synthetic and semi-synthetic benchmark",
        "claim": "Strict certificates reject composition, block and density nulls while retaining sensitivity to planted domains.",
        "accent": "green",
    },
    {
        "id": "Figure4",
        "src": "Figure4_SNRA_NatureMethods_final_v1_0.png",
        "title": "Cross-platform real-data benchmark",
        "claim": "Real-data audits separate primary validation, spot-level support and failed block-sensitive stress tests.",
        "accent": "amber",
    },
    {
        "id": "Figure5",
        "src": "Figure5_SNRA_NatureMethods_final_v1_0.png",
        "title": "Claim rescue versus rejection",
        "claim": "The same audit framework rescues lineage-framed boundary claims and blocks unsupported package or block-sensitive claims.",
        "accent": "coral",
    },
    {
        "id": "Figure6",
        "src": "Figure6_SNRA_NatureMethods_final_v1_0.png",
        "title": "Software reproducibility and audit reports",
        "claim": "Manifest-driven CLI, source tables and clean-env testing make certificate decisions reproducible and traceable.",
        "accent": "slate",
    },
]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "figure.facecolor": PALETTE["paper"],
            "savefig.facecolor": PALETTE["paper"],
            "axes.facecolor": PALETTE["paper"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def draw_polished(fig_spec: dict[str, str]) -> dict[str, object]:
    src = SRC_DIR / fig_spec["src"]
    image = plt.imread(src)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    accent = PALETTE[fig_spec["accent"]]

    fig = plt.figure(figsize=(12.0, 10.0), dpi=300)
    fig.patch.set_facecolor(PALETTE["paper"])

    # Header.
    header = fig.add_axes([0.035, 0.91, 0.93, 0.075])
    header.set_axis_off()
    header.add_patch(plt.Rectangle((0, 0), 1, 1, color="#FFFFFF", ec=PALETTE["line"], lw=0.8))
    header.add_patch(plt.Rectangle((0, 0), 0.018, 1, color=accent, lw=0))
    figure_label = fig_spec["id"].replace("Figure", "Figure ")
    header.text(0.035, 0.66, figure_label, ha="left", va="center", fontsize=12, color=accent, weight="bold")
    header.text(0.12, 0.66, fig_spec["title"], ha="left", va="center", fontsize=12, color=PALETTE["ink"], weight="bold")
    header.text(0.12, 0.30, fig_spec["claim"], ha="left", va="center", fontsize=8.2, color=PALETTE["muted"])

    # Main figure raster, generated from the source-backed six-panel figure.
    ax = fig.add_axes([0.035, 0.085, 0.93, 0.81])
    ax.imshow(image)
    ax.set_axis_off()
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(PALETTE["line"])
        spine.set_linewidth(0.8)

    footer = fig.add_axes([0.035, 0.025, 0.93, 0.04])
    footer.set_axis_off()
    footer.add_patch(plt.Rectangle((0, 0), 1, 1, color="#FFFFFF", ec=PALETTE["line"], lw=0.6))
    footer.text(
        0.01,
        0.5,
        "SNRA final artwork pass v1.1 | six-panel source-backed figure | negative controls and failed certificates remain visible",
        ha="left",
        va="center",
        fontsize=7.2,
        color=PALETTE["muted"],
    )
    footer.text(0.99, 0.5, "Spatial Niche Robustness Auditor", ha="right", va="center", fontsize=7.2, color=PALETTE["ink"])

    outputs = {}
    for suffix in [".png", ".pdf", ".svg"]:
        dst = OUT_DIR / f"{fig_spec['id']}_SNRA_NatureMethods_artwork_v1_1{suffix}"
        fig.savefig(dst, bbox_inches="tight", pad_inches=0.02)
        outputs[suffix.lstrip(".")] = dst
    plt.close(fig)

    return {
        "figure": fig_spec["id"],
        "title": fig_spec["title"],
        "claim": fig_spec["claim"],
        "source_png": rel(src),
        "png": rel(outputs["png"]),
        "pdf": rel(outputs["pdf"]),
        "svg": rel(outputs["svg"]),
        "status": "PASS" if all(path.exists() and path.stat().st_size > 0 for path in outputs.values()) else "CHECK",
    }


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_doc(rows: list[dict[str, object]]) -> None:
    ok = all(row["status"] == "PASS" for row in rows)
    lines = [
        "# SNRA final artwork pass v1.1",
        "",
        "Date: 2026-05-10",
        f"Status: {'PASS' if ok else 'CHECK'}",
        "",
        "## What changed",
        "",
        "This pass does not change the scientific results. It adds a consistent Nature Methods-style visual hierarchy around each source-backed Figure 1-6 panel grid: figure identity, title, central claim, restrained accent color and a traceability footer.",
        "",
        "## Outputs",
        "",
        f"- Artwork directory: `{rel(OUT_DIR)}`",
        f"- QC table: `{rel(QC_DIR / 'snra_final_artwork_v1_1_qc.tsv')}`",
        "",
        "## Self-check",
        "",
        "- Every figure still derives from the v1.0 source-backed six-panel figure.",
        "- No result was changed or hidden.",
        "- The wrapper clarifies visual hierarchy but does not replace final professional journal layout if required.",
    ]
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    setup_style()
    rows = [draw_polished(spec) for spec in FIGURES]
    write_tsv(QC_DIR / "snra_final_artwork_v1_1_qc.tsv", rows)
    write_doc(rows)
    print(f"artwork_dir\t{OUT_DIR}")
    print(f"artwork_doc\t{DOC_PATH}")
    return 0 if all(row["status"] == "PASS" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
