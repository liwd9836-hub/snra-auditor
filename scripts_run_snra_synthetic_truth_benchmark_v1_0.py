from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.snra import AuditConfig, SpatialDataset, run_audit


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "snra_synthetic_truth_benchmark_v1_0"
DOCS = ROOT / "docs"
META = ROOT / "metadata" / "snra"

SEED = 20260509
N_SAMPLES = 8
UNITS_PER_SAMPLE = 180
CONFIG = AuditConfig(k=8, n_permutations=59, alpha=0.10, seed=SEED, annotation_noise=0.05)

SUMMARY_COLUMNS = [
    "scenario",
    "truth_status",
    "n_units",
    "n_samples",
    "confounder_strength",
    "observed_positive_rate",
    "matched_null_positive_rate",
    "false_positive_rate",
    "sensitivity",
    "specificity",
    "certificate_rate",
    "mean_margin",
    "ci_low",
    "ci_high",
]


@dataclass(frozen=True)
class BenchmarkCase:
    scenario: str
    truth_status: str
    confounder_strength: float
    dataset: SpatialDataset
    units: pd.DataFrame
    positive_niches: tuple[str, ...]
    source: str
    proxy_note: str


def _rng(seed_offset: int) -> np.random.Generator:
    return np.random.default_rng(SEED + seed_offset)


def _unit_id(sample_id: str, i: int) -> str:
    return f"{sample_id}_U{i:04d}"


def _make_dataset(units: pd.DataFrame) -> SpatialDataset:
    coord = units[["unit_id", "sample_id", "x", "y"]].copy()
    meta_cols = ["unit_id", "sample_id", "cell_type"]
    for optional in ["block_id", "synthetic_cluster", "degree_proxy", "truth_label"]:
        if optional in units.columns:
            meta_cols.append(optional)
    meta = units[meta_cols].copy()
    labels = units.set_index("unit_id")["niche_label"].astype(str)
    labels.name = "niche_label"
    labels.index.name = "unit_id"
    return SpatialDataset(coord, meta, labels)


def _synthetic_base(seed_offset: int, clustered: bool = True) -> pd.DataFrame:
    rng = _rng(seed_offset)
    rows: list[dict[str, object]] = []
    centers = np.array([[0.22, 0.24], [0.78, 0.25], [0.50, 0.76]])
    for s in range(N_SAMPLES):
        sample_id = f"S{s + 1:02d}"
        if clustered:
            cluster = rng.choice(3, size=UNITS_PER_SAMPLE, p=[0.34, 0.34, 0.32])
            coords = centers[cluster] + rng.normal(0, 0.09, size=(UNITS_PER_SAMPLE, 2))
            coords = np.clip(coords, 0.0, 1.0)
        else:
            coords = rng.uniform(0.0, 1.0, size=(UNITS_PER_SAMPLE, 2))
            cluster = np.full(UNITS_PER_SAMPLE, -1)
        for i, (x, y) in enumerate(coords):
            rows.append(
                {
                    "scenario": "",
                    "unit_id": _unit_id(sample_id, i),
                    "sample_id": sample_id,
                    "x": float(x),
                    "y": float(y),
                    "synthetic_cluster": int(cluster[i]),
                    "cell_type": str(rng.choice(["tumor", "immune", "stromal", "other"])),
                    "niche_label": "background",
                    "truth_label": "true_negative",
                    "block_id": f"Q{int(x >= 0.5)}{int(y >= 0.5)}",
                    "degree_proxy": np.nan,
                }
            )
    return pd.DataFrame(rows)


def _pure_null() -> BenchmarkCase:
    rng = _rng(10)
    units = _synthetic_base(11, clustered=True)
    units["scenario"] = "synthetic_pure_null"
    units["niche_label"] = rng.choice(["candidate_a", "candidate_b", "background"], size=len(units), p=[0.25, 0.25, 0.50])
    units["truth_label"] = "true_negative"
    return BenchmarkCase(
        "synthetic_pure_null",
        "pure_null",
        0.0,
        _make_dataset(units),
        units,
        (),
        "fully synthetic clustered coordinates with random labels",
        "SNRA package audit; margins are score_obs minus maximum matched-null mean.",
    )


def _planted_domain() -> BenchmarkCase:
    units = _synthetic_base(21, clustered=True)
    units["scenario"] = "synthetic_planted_domain"
    d = np.sqrt((units["x"] - 0.22) ** 2 + (units["y"] - 0.24) ** 2)
    planted = d <= np.quantile(d, 0.24)
    units["niche_label"] = np.where(planted, "planted_domain", "background")
    units["truth_label"] = np.where(planted, "true_positive", "true_negative")
    return BenchmarkCase(
        "synthetic_planted_domain",
        "positive",
        1.0,
        _make_dataset(units),
        units,
        ("planted_domain",),
        "fully synthetic coordinates with a planted compact domain",
        "SNRA package audit; planted_domain rows are the positive truth set.",
    )


def _composition_confounder() -> BenchmarkCase:
    rng = _rng(30)
    units = _synthetic_base(31, clustered=True)
    units["scenario"] = "synthetic_composition_confounder"
    cluster = units["synthetic_cluster"].to_numpy()
    cell_type = np.where(cluster == 0, "tumor", np.where(cluster == 1, "immune", "stromal"))
    flip = rng.random(len(units)) < 0.15
    cell_type[flip] = rng.choice(["tumor", "immune", "stromal"], size=flip.sum())
    units["cell_type"] = cell_type
    units["niche_label"] = np.where(units["cell_type"].eq("tumor"), "composition_high_tumor", "background")
    units["truth_label"] = "true_negative"
    return BenchmarkCase(
        "synthetic_composition_confounder",
        "confounded_null",
        0.85,
        _make_dataset(units),
        units,
        (),
        "fully synthetic coordinates where candidate labels track spatially clustered cell composition",
        "Composition confounding is represented by cell-type driven labels; strict SNRA certification should be blocked by cell-type-preserving controls.",
    )


def _block_artifact() -> BenchmarkCase:
    units = _synthetic_base(41, clustered=False)
    units["scenario"] = "synthetic_block_artifact"
    left_block = units["x"] < 0.50
    units["niche_label"] = np.where(left_block, "block_artifact_label", "background")
    units["cell_type"] = np.where(left_block, "batch_enriched_type", "other")
    units["truth_label"] = "true_negative"
    units["block_id"] = np.where(left_block, "left_fov", "right_fov")
    return BenchmarkCase(
        "synthetic_block_artifact",
        "confounded_null",
        1.0,
        _make_dataset(units),
        units,
        (),
        "fully synthetic uniform coordinates with labels tied to acquisition-like left/right FOV block",
        "Block artifact is tested with block-preserving and celltype-block preserving controls in the matched-null ladder.",
    )


def _degree_confounder() -> BenchmarkCase:
    rng = _rng(50)
    rows: list[dict[str, object]] = []
    for s in range(N_SAMPLES):
        sample_id = f"S{s + 1:02d}"
        dense = rng.normal([0.35, 0.35], [0.05, 0.05], size=(UNITS_PER_SAMPLE // 2, 2))
        sparse = rng.uniform(0.0, 1.0, size=(UNITS_PER_SAMPLE - len(dense), 2))
        coords = np.clip(np.vstack([dense, sparse]), 0.0, 1.0)
        density_proxy = np.sqrt((coords[:, 0] - 0.35) ** 2 + (coords[:, 1] - 0.35) ** 2)
        high_degree = density_proxy <= np.quantile(density_proxy, 0.35)
        for i, (x, y) in enumerate(coords):
            rows.append(
                {
                    "scenario": "synthetic_degree_confounder",
                    "unit_id": _unit_id(sample_id, i),
                    "sample_id": sample_id,
                    "x": float(x),
                    "y": float(y),
                    "synthetic_cluster": int(high_degree[i]),
                    "cell_type": "density_enriched" if high_degree[i] else "other",
                    "niche_label": "degree_artifact_label" if high_degree[i] else "background",
                    "truth_label": "true_negative",
                    "block_id": "dense_core" if high_degree[i] else "sparse_field",
                    "degree_proxy": float(1.0 - density_proxy[i]),
                }
            )
    units = pd.DataFrame(rows)
    return BenchmarkCase(
        "synthetic_degree_confounder",
        "confounded_null",
        1.0,
        _make_dataset(units),
        units,
        (),
        "fully synthetic nonuniform point density with labels tied to local density/degree proxy",
        "Degree confounding is tested with degree- and local-density-preserving controls in the matched-null ladder.",
    )


def _prepare_real_coordinate_units(path: Path, scenario: str, cap_samples: int, cap_units: int, seed_offset: int) -> pd.DataFrame | None:
    if not path.exists():
        return None
    df = pd.read_csv(path, sep="\t")
    if "unit_id" not in df.columns and "barcode" in df.columns:
        df["unit_id"] = df["sample_id"].astype(str) + "_" + df["barcode"].astype(str)
    required = {"unit_id", "sample_id", "x", "y"}
    if not required.issubset(df.columns):
        return None
    if "cell_type" not in df.columns:
        df["cell_type"] = "unit_unknown"
    df = df.dropna(subset=["unit_id", "sample_id", "x", "y"]).copy()
    if "niche_label" in df.columns:
        df = df[~df["niche_label"].astype(str).str.lower().isin(["exclude", "artefact", "artifact"])].copy()
    if df.empty:
        return None
    rng = _rng(seed_offset)
    selected: list[pd.DataFrame] = []
    for sample_id in sorted(df["sample_id"].astype(str).unique())[:cap_samples]:
        s = df[df["sample_id"].astype(str) == sample_id].copy()
        if len(s) < 40:
            continue
        if len(s) > cap_units:
            s = s.sample(n=cap_units, random_state=int(rng.integers(1, 1_000_000)))
        selected.append(s)
    if len(selected) < 2:
        return None
    units = pd.concat(selected, ignore_index=True)
    units["scenario"] = scenario
    units["x"] = units["x"].astype(float)
    units["y"] = units["y"].astype(float)
    units["x"] = units.groupby("sample_id")["x"].transform(lambda v: (v - v.min()) / max(v.max() - v.min(), 1e-9))
    units["y"] = units.groupby("sample_id")["y"].transform(lambda v: (v - v.min()) / max(v.max() - v.min(), 1e-9))
    per_sample_planted = []
    for _, s in units.groupby("sample_id", sort=False):
        center = np.array([s["x"].median(), s["y"].median()])
        d = np.sqrt((s["x"] - center[0]) ** 2 + (s["y"] - center[1]) ** 2)
        per_sample_planted.append(d <= np.quantile(d, 0.25))
    planted = pd.concat(per_sample_planted).sort_index()
    units["niche_label"] = np.where(planted.to_numpy(), "semi_synthetic_planted_domain", "background")
    units["truth_label"] = np.where(planted.to_numpy(), "true_positive", "true_negative")
    units["block_id"] = "real_coordinate_geometry"
    units["degree_proxy"] = np.nan
    keep = [
        "scenario",
        "unit_id",
        "sample_id",
        "x",
        "y",
        "cell_type",
        "niche_label",
        "truth_label",
        "block_id",
        "degree_proxy",
    ]
    return units[keep].copy()


def _semi_synthetic_cases() -> list[BenchmarkCase]:
    specs = [
        (
            "semi_synthetic_tonic_coordinates",
            META / "snra_tonic_sbiad1288_compartment_cells_v0_9.tsv",
            "local TONIC SBIAD1288 segmented-cell coordinates with injected central-domain labels",
            60,
        ),
        (
            "semi_synthetic_crc_coordinates",
            META / "snra_plan_f_crc_st_pathology_spot_domain_cells_v0_1.tsv",
            "local CRC Visium spot coordinates with injected central-domain labels",
            70,
        ),
    ]
    cases: list[BenchmarkCase] = []
    for scenario, path, source, seed_offset in specs:
        units = _prepare_real_coordinate_units(path, scenario, N_SAMPLES, UNITS_PER_SAMPLE, seed_offset)
        if units is None:
            continue
        cases.append(
            BenchmarkCase(
                scenario,
                "semi_synthetic_positive",
                1.0,
                _make_dataset(units),
                units,
                ("semi_synthetic_planted_domain",),
                source,
                "Real coordinates are reused, but the truth labels are injected; this is not validation of source biological annotations.",
            )
        )
    return cases


def _bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int = 200) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return np.nan, np.nan
    boot = [float(np.mean(rng.choice(values, size=len(values), replace=True))) for _ in range(n_boot)]
    return float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def _summarize_case(case: BenchmarkCase, audit: pd.DataFrame) -> dict[str, object]:
    audit = audit.copy()
    null_mean_cols = [c for c in audit.columns if c.startswith("null_") and c.endswith("_mean")]
    audit["matched_null_mean_max"] = audit[null_mean_cols].max(axis=1)
    audit["margin_proxy"] = audit["score_obs"] - audit["matched_null_mean_max"]
    audit["is_truth_positive"] = audit["niche"].astype(str).isin(case.positive_niches)
    audit["is_candidate_claim"] = ~audit["niche"].astype(str).str.lower().isin({"background", "other", "none"})
    certificate_col = "snra_certified" if "snra_certified" in audit.columns else "crc_certified"
    audit["is_certified"] = audit[certificate_col].astype(bool)
    claim_audit = audit.loc[audit["is_candidate_claim"]].copy()
    if claim_audit.empty:
        claim_audit = audit.copy()

    # Naive comparator: an uncalibrated spatial-enrichment readout that calls a
    # candidate positive when the target-target edge fraction is high. This is
    # intentionally simple and transparent; it is not the SNRA certificate.
    observed_positive_rate = float((claim_audit["score_obs"] >= 0.50).mean())
    matched_positive_rate = float(claim_audit["is_certified"].mean())
    certificate_rate = matched_positive_rate
    has_positive = bool(claim_audit["is_truth_positive"].any())
    if has_positive:
        pos = claim_audit["is_truth_positive"]
        sensitivity = float(claim_audit.loc[pos, "is_certified"].mean())
        specificity = float((~claim_audit.loc[~pos, "is_certified"]).mean()) if (~pos).any() else np.nan
        false_positive_rate = float(claim_audit.loc[~pos, "is_certified"].mean()) if (~pos).any() else 0.0
        ci_values = claim_audit.loc[pos, "is_certified"].astype(float).to_numpy()
    else:
        sensitivity = np.nan
        specificity = float((~claim_audit["is_certified"]).mean())
        false_positive_rate = matched_positive_rate
        ci_values = claim_audit["is_certified"].astype(float).to_numpy()
    ci_low, ci_high = _bootstrap_ci(ci_values, _rng(90 + len(case.scenario)))
    return {
        "scenario": case.scenario,
        "truth_status": case.truth_status,
        "n_units": int(case.units["unit_id"].nunique()),
        "n_samples": int(case.units["sample_id"].nunique()),
        "confounder_strength": case.confounder_strength,
        "observed_positive_rate": observed_positive_rate,
        "matched_null_positive_rate": matched_positive_rate,
        "false_positive_rate": false_positive_rate,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "certificate_rate": certificate_rate,
        "mean_margin": float(audit["margin_proxy"].mean()),
        "ci_low": ci_low,
        "ci_high": ci_high,
    }


def _write_docs(summary: pd.DataFrame, manifest: pd.DataFrame) -> None:
    pure = summary.loc[summary["scenario"].eq("synthetic_pure_null")]
    planted = summary.loc[summary["scenario"].eq("synthetic_planted_domain")]
    pure_fpr = float(pure["false_positive_rate"].iloc[0]) if not pure.empty else np.nan
    planted_sens = float(planted["sensitivity"].iloc[0]) if not planted.empty else np.nan
    gate = "PASS" if np.isfinite(pure_fpr) and pure_fpr <= 0.10 and np.isfinite(planted_sens) and planted_sens >= 0.50 else "FAIL"
    if not summary.loc[summary["truth_status"].eq("confounded_null")].empty:
        conf_fpr = float(summary.loc[summary["truth_status"].eq("confounded_null"), "false_positive_rate"].max())
        if conf_fpr > 0.10:
            gate = "FAIL"

    report = [
        "# SNRA synthetic truth benchmark v1.0",
        "",
        "## Analysis contract",
        "",
        "- Biological/statistical question: can the current SNRA audit layer control false positives under known null and nuisance structures while retaining sensitivity for planted spatial domains?",
        "- Statistical unit: independent synthetic or semi-synthetic sample/slide (`sample_id`), not cell/spot.",
        "- Positive truth: injected compact domain labels only in planted and semi-synthetic scenarios.",
        "- Null truth: pure random labels, composition-driven labels, block-driven labels, and degree/density-driven labels are treated as no true spatial niche.",
        "- Evidence class: synthetic/semi-synthetic statistical benchmark, not biological mechanism.",
        "",
        "## Implementation",
        "",
        "The benchmark uses `src.snra.run_audit` with deterministic seed 20260509, k=8, 59 permutations, alpha=0.10, and annotation-noise stress 0.05. Semi-synthetic scenarios reuse local coordinate geometry when available and inject truth labels; source biological labels are not treated as ground truth.",
        "",
        "`observed_positive_rate` is a naive uncalibrated comparator: candidate labels with target-target edge enrichment >=0.50. Certification uses `snra_certified` when available: a row must pass the original CRC/conformal gate and also exceed every matched control family by per-control permutation p-value. This intentionally blocks labels whose spatial structure is explained by cell-type composition, block/FOV structure, or local density.",
        "",
        "## Benchmark summary",
        "",
        summary.to_markdown(index=False),
        "",
        "## Manifest",
        "",
        manifest.to_markdown(index=False),
        "",
        "## Gate decision",
        "",
        f"- Gate: {gate}",
        f"- Pure-null matched-control false-positive rate: {pure_fpr:.3f}" if np.isfinite(pure_fpr) else "- Pure-null matched-control false-positive rate: NA",
        f"- Planted-domain sensitivity: {planted_sens:.3f}" if np.isfinite(planted_sens) else "- Planted-domain sensitivity: NA",
        "",
        "Stop-rule note: if confounded-null false positives exceed 0.10, the Nature Methods article path should not overstate confounder control until the method adds the missing matched null/residualization layer.",
    ]
    (DOCS / "SNRA_synthetic_truth_benchmark_v1_0.md").write_text("\n".join(report), encoding="utf-8")

    log = [
        "# SNRA Phase B synthetic truth work log",
        "",
        "- Date: 2026-05-09",
        "- Worker: B",
        "- Scope: `scripts_run_snra_synthetic_truth_benchmark_v1_0.py`, `results/snra_synthetic_truth_benchmark_v1_0/`, `docs/SNRA_synthetic_truth_benchmark_v1_0.md`, `docs/SNRA_work_log_phase_B_synthetic_truth_2026_05_09.md`.",
        "- Action: implemented deterministic synthetic/semi-synthetic truth benchmark and ran current SNRA package audit logic.",
        "- Verification: script completed and wrote `synthetic_units.tsv`, `simulation_manifest.tsv`, per-scenario audit tables, and `benchmark_summary.tsv`.",
        f"- Gate decision: {gate}.",
        f"- Pure-null FPR: {pure_fpr:.3f}" if np.isfinite(pure_fpr) else "- Pure-null FPR: NA",
        f"- Planted sensitivity: {planted_sens:.3f}" if np.isfinite(planted_sens) else "- Planted sensitivity: NA",
        "- Residual risk: composition-, block-, and degree-confounded nulls expose whether current matched controls are sufficient; failures are recorded rather than hidden.",
    ]
    (DOCS / "SNRA_work_log_phase_B_synthetic_truth_2026_05_09.md").write_text("\n".join(log), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    cases = [_pure_null(), _planted_domain(), _composition_confounder(), _block_artifact(), _degree_confounder()]
    cases.extend(_semi_synthetic_cases())

    all_units = []
    manifest_rows = []
    summary_rows = []
    for idx, case in enumerate(cases, start=1):
        audit, phase = run_audit(case.dataset, CONFIG)
        audit.to_csv(OUT / f"{case.scenario}_audit.tsv", sep="\t", index=False)
        phase.to_csv(OUT / f"{case.scenario}_phase.tsv", sep="\t", index=False)
        all_units.append(case.units.copy())
        manifest_rows.append(
            {
                "scenario": case.scenario,
                "truth_status": case.truth_status,
                "source": case.source,
                "n_units": int(case.units["unit_id"].nunique()),
                "n_samples": int(case.units["sample_id"].nunique()),
                "seed": SEED + idx,
                "audit_alpha": CONFIG.alpha,
                "audit_k": CONFIG.k,
                "n_permutations": CONFIG.n_permutations,
                "positive_niches": ",".join(case.positive_niches) if case.positive_niches else "",
                "proxy_note": case.proxy_note,
            }
        )
        summary_rows.append(_summarize_case(case, audit))

    expected = {"semi_synthetic_tonic_coordinates", "semi_synthetic_crc_coordinates"}
    observed = {case.scenario for case in cases}
    for missing in sorted(expected - observed):
        manifest_rows.append(
            {
                "scenario": missing,
                "truth_status": "not_run",
                "source": "local coordinate table unavailable or insufficient",
                "n_units": 0,
                "n_samples": 0,
                "seed": SEED,
                "audit_alpha": CONFIG.alpha,
                "audit_k": CONFIG.k,
                "n_permutations": CONFIG.n_permutations,
                "positive_niches": "",
                "proxy_note": "Scenario skipped because required local coordinates were not available.",
            }
        )

    units_df = pd.concat(all_units, ignore_index=True)
    units_df.to_csv(OUT / "synthetic_units.tsv", sep="\t", index=False)
    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(OUT / "simulation_manifest.tsv", sep="\t", index=False)
    summary = pd.DataFrame(summary_rows)[SUMMARY_COLUMNS]
    summary.to_csv(OUT / "benchmark_summary.tsv", sep="\t", index=False)
    _write_docs(summary, manifest)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
