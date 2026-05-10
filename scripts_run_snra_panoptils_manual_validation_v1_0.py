#!/usr/bin/env python
"""Run a minimal PanopTILs manual region+nuclei validation audit.

This is an orthogonal histopathology validation layer for SNRA.  It tests
whether manual cell classes align with manual region masks beyond matched
label shuffles.  It is not spatial-omics molecular validation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


REGION_EXPECTED_FAMILY = {
    "Cancerous_epithelium": "cancer_cell",
    "Stroma": "stromal_cell",
    "TILs_region": "til_cell",
}


def match_score(df: pd.DataFrame) -> float:
    valid = df[df["manual_region_label"].isin(REGION_EXPECTED_FAMILY)].copy()
    valid = valid[valid["cell_family"].isin(["cancer_cell", "stromal_cell", "til_cell"])]
    if len(valid) == 0:
        return float("nan")
    expected = valid["manual_region_label"].map(REGION_EXPECTED_FAMILY)
    return float((valid["cell_family"].to_numpy() == expected.to_numpy()).mean())


def permutation_scores(df: pd.DataFrame, mode: str, n_perm: int, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    scores = []
    for _ in range(n_perm):
        shuffled = df.copy()
        if mode == "global_cell_label_shuffle":
            shuffled["cell_family"] = rng.permutation(shuffled["cell_family"].to_numpy())
        elif mode == "within_roi_cell_label_shuffle":
            parts = []
            for _, sub in shuffled.groupby("roi", sort=False):
                sub = sub.copy()
                sub["cell_family"] = rng.permutation(sub["cell_family"].to_numpy())
                parts.append(sub)
            shuffled = pd.concat(parts, ignore_index=True)
        elif mode == "global_region_label_shuffle":
            shuffled["manual_region_label"] = rng.permutation(shuffled["manual_region_label"].to_numpy())
        elif mode == "within_roi_region_label_shuffle":
            parts = []
            for _, sub in shuffled.groupby("roi", sort=False):
                sub = sub.copy()
                sub["manual_region_label"] = rng.permutation(sub["manual_region_label"].to_numpy())
                parts.append(sub)
            shuffled = pd.concat(parts, ignore_index=True)
        else:
            raise ValueError(mode)
        scores.append(match_score(shuffled))
    return scores


def summarize_control(observed: float, name: str, scores: list[float]) -> dict[str, float | str | int]:
    arr = np.asarray(scores, dtype=float)
    arr = arr[np.isfinite(arr)]
    p = float((1 + np.sum(arr >= observed)) / (len(arr) + 1)) if len(arr) else float("nan")
    return {
        "control": name,
        "observed_score": observed,
        "null_mean": float(np.mean(arr)) if len(arr) else float("nan"),
        "null_p95": float(np.quantile(arr, 0.95)) if len(arr) else float("nan"),
        "null_max": float(np.max(arr)) if len(arr) else float("nan"),
        "empirical_p": p,
        "n_permutations": int(len(arr)),
        "passes": bool(np.isfinite(p) and p <= 0.01 and observed > np.quantile(arr, 0.95)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cell-table",
        default="results/snra_panoptils_manual_adapter_v1_0/panoptils_manual_cell_region_table.tsv",
    )
    parser.add_argument("--out-dir", default="results/snra_panoptils_manual_validation_v1_0")
    parser.add_argument("--n-perm", type=int, default=99)
    parser.add_argument("--seed", type=int, default=1701)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.cell_table, sep="\t")
    df = df[df["has_region_mask"].astype(bool)].copy()
    df = df[df["manual_region_label"].isin(REGION_EXPECTED_FAMILY)].copy()
    df = df[df["cell_family"].isin(["cancer_cell", "stromal_cell", "til_cell"])].copy()

    observed = match_score(df)
    controls = [
        "global_cell_label_shuffle",
        "within_roi_cell_label_shuffle",
        "global_region_label_shuffle",
        "within_roi_region_label_shuffle",
    ]
    control_rows = []
    for i, control in enumerate(controls):
        scores = permutation_scores(df, control, args.n_perm, args.seed + i)
        control_rows.append(summarize_control(observed, control, scores))

    control_table = pd.DataFrame(control_rows)
    pass_rate = float(control_table["passes"].mean()) if len(control_table) else 0.0
    decision = {
        "dataset": "PanopTILs_manual_regions_manual_nuclei",
        "n_rois": int(df["roi"].nunique()),
        "n_objects_used": int(len(df)),
        "observed_match_score": observed,
        "controls_passed": int(control_table["passes"].sum()),
        "controls_total": int(len(control_table)),
        "control_pass_rate": pass_rate,
        "decision": "PASS_ORTHOGONAL_MANUAL_REGION_CELL_VALIDATION"
        if pass_rate == 1.0
        else "PARTIAL_OR_FAIL_ORTHOGONAL_VALIDATION",
        "claim_boundary": "H&E manual region+nuclei geometry validation; not molecular spatial-omics validation",
    }

    region_summary = (
        df.groupby(["manual_region_label", "cell_family"])
        .size()
        .reset_index(name="n_objects")
        .sort_values(["manual_region_label", "cell_family"])
    )
    control_table.to_csv(out_dir / "panoptils_manual_validation_controls.tsv", sep="\t", index=False)
    region_summary.to_csv(out_dir / "panoptils_manual_region_cell_counts.tsv", sep="\t", index=False)
    pd.DataFrame([decision]).to_csv(out_dir / "panoptils_manual_validation_summary.tsv", sep="\t", index=False)
    (out_dir / "panoptils_manual_validation_summary.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
