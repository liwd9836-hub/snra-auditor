from __future__ import annotations

import numpy as np
import pandas as pd

from .topology_benchmark import auc_score


COMPOSITION_FEATURES = [
    "topology_target_fraction",
]

TOPOLOGY_FEATURES = [
    "score_obs",
    "robustness_score",
    "topology_target_mean_degree",
    "topology_target_components",
    "topology_boundary_fraction",
]


def _zscore_matrix(df: pd.DataFrame, columns: list[str]) -> tuple[np.ndarray, list[str]]:
    present = [c for c in columns if c in df.columns]
    if not present:
        raise ValueError(f"none of the requested columns exist: {columns}")
    x = df[present].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(float)
    mean = x.mean(axis=0, keepdims=True)
    sd = x.std(axis=0, keepdims=True)
    sd[sd == 0] = 1.0
    return (x - mean) / sd, present


def _pairwise_distance_rows(
    df: pd.DataFrame,
    features: np.ndarray,
    feature_set: str,
    sample_col: str = "sample_id",
    label_col: str = "niche",
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    samples = df[sample_col].astype(str).to_numpy()
    labels = df[label_col].astype(str).to_numpy()
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            if samples[i] == samples[j]:
                continue
            dist = float(np.sqrt(np.mean((features[i] - features[j]) ** 2)))
            rows.append(
                {
                    "feature_set": feature_set,
                    "left_sample": samples[i],
                    "right_sample": samples[j],
                    "left_label": labels[i],
                    "right_label": labels[j],
                    "same_layer": labels[i] == labels[j],
                    "distance": dist,
                    "retrieval_score": -dist,
                }
            )
    return pd.DataFrame(rows)


def same_layer_retrieval_benchmark(
    audit: pd.DataFrame,
    sample_col: str = "sample_id",
    label_col: str = "niche",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Benchmark whether distances retrieve same labels across independent samples.

    Rows are candidate domain/niche labels within samples. Pairwise comparisons are
    restricted to different samples to avoid within-slide pseudo-replication.
    """

    needed = {sample_col, label_col}
    missing = needed - set(audit.columns)
    if missing:
        raise ValueError(f"audit table missing required columns: {sorted(missing)}")
    audit = audit.copy()
    comp_x, comp_cols = _zscore_matrix(audit, COMPOSITION_FEATURES)
    topo_x, topo_cols = _zscore_matrix(audit, TOPOLOGY_FEATURES)
    combined_x = np.column_stack([comp_x, topo_x])

    detail = pd.concat(
        [
            _pairwise_distance_rows(audit, comp_x, "composition_only", sample_col, label_col),
            _pairwise_distance_rows(audit, topo_x, "topology_only", sample_col, label_col),
            _pairwise_distance_rows(audit, combined_x, "topology_plus_composition", sample_col, label_col),
        ],
        ignore_index=True,
    )
    summary_rows = []
    for feature_set, sub in detail.groupby("feature_set"):
        auc = auc_score(sub["same_layer"].to_numpy(), sub["retrieval_score"].to_numpy())
        pos = sub[sub["same_layer"]]
        neg = sub[~sub["same_layer"]]
        summary_rows.append(
            {
                "feature_set": feature_set,
                "n_pairs": len(sub),
                "n_positive_pairs": len(pos),
                "n_negative_pairs": len(neg),
                "same_layer_auc": auc,
                "median_positive_distance": float(pos["distance"].median()) if len(pos) else np.nan,
                "median_negative_distance": float(neg["distance"].median()) if len(neg) else np.nan,
                "feature_columns": ";".join(comp_cols if feature_set == "composition_only" else topo_cols if feature_set == "topology_only" else comp_cols + topo_cols),
            }
        )
    summary = pd.DataFrame(summary_rows)
    comp_auc = float(summary.loc[summary["feature_set"] == "composition_only", "same_layer_auc"].iloc[0])
    for idx in summary.index:
        summary.loc[idx, "increment_over_composition"] = summary.loc[idx, "same_layer_auc"] - comp_auc
    return detail, summary.sort_values("feature_set").reset_index(drop=True)

