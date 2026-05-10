from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .conformal import certify, conformal_threshold, observed_risk
from .contract import SpatialDataset, validate_dataset
from .graph import edge_enrichment_score, knn_edges
from .null_models import (
    abundance_preserving_permutation,
    bh_fdr,
    block_permutation,
    degree_preserving_attribute_permutation,
    global_label_permutation,
    grouped_attribute_permutation,
    permutation_pvalue,
    sample_stratified_permutation,
)
from .robustness import flip_labels
from .robustness import jitter_coords
from .topology import graph_degrees, topology_signature


@dataclass
class AuditConfig:
    k: int = 8
    n_permutations: int = 99
    alpha: float = 0.10
    seed: int = 1
    annotation_noise: float = 0.10


def _sample_frame(dataset: SpatialDataset, sample_id: str) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    coord = dataset.coordinates[dataset.coordinates["sample_id"] == sample_id].copy()
    meta = dataset.metadata[dataset.metadata["sample_id"] == sample_id].copy()
    coord["unit_id"] = coord["unit_id"].astype(str)
    meta["unit_id"] = meta["unit_id"].astype(str)
    shared = sorted(set(coord["unit_id"]) & set(meta["unit_id"]) & set(dataset.niche_labels.index.astype(str)))
    coord = coord.set_index("unit_id").loc[shared].reset_index()
    meta = meta.set_index("unit_id").loc[shared].reset_index()
    labels = dataset.niche_labels.loc[shared].astype(str).to_numpy()
    return coord, meta, labels


def _degree(edges: np.ndarray, n: int) -> np.ndarray:
    return graph_degrees(edges, n)


def _quantile_groups(values: np.ndarray, n_bins: int = 4) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if len(values) == 0 or len(np.unique(values[np.isfinite(values)])) < 2:
        return np.zeros(len(values), dtype=str)
    bins = pd.qcut(values, q=min(n_bins, len(np.unique(values))), labels=False, duplicates="drop")
    return np.asarray(bins).astype(str)


def _local_density_proxy(coords: np.ndarray, k: int) -> np.ndarray:
    """Return a deterministic local-density proxy from kth-neighbor distance.

    Higher values mean denser local packing. It is a nuisance variable, not a
    biological statistic.
    """

    from scipy.spatial import cKDTree

    coords = np.asarray(coords, dtype=float)
    if len(coords) <= 2:
        return np.zeros(len(coords), dtype=float)
    k_eff = min(max(2, k), len(coords) - 1)
    tree = cKDTree(coords)
    dist, _ = tree.query(coords, k=k_eff + 1)
    kth = dist[:, -1]
    return -kth


def score_audit_table(audit: pd.DataFrame, alpha: float = 0.10) -> pd.DataFrame:
    """Add q-values, simple audit scores, CRC calls, and failure labels.

    This helper is separated so negative-control tables and real-data adapters
    use identical certification logic.
    """

    audit = audit.copy()
    audit["q_perm"] = bh_fdr(audit["p_perm"].to_numpy())
    audit["raw_certified"] = audit["q_perm"] < alpha
    control_p_cols = [c for c in audit.columns if c.startswith("null_") and c.endswith("_p")]
    control_q_cols = [c for c in audit.columns if c.startswith("null_") and c.endswith("_q90")]
    if control_p_cols:
        audit["matched_control_p_max"] = audit[control_p_cols].max(axis=1)
        audit["matched_control_gate"] = audit["matched_control_p_max"] < alpha
    else:
        audit["matched_control_p_max"] = np.nan
        audit["matched_control_gate"] = True
    if control_q_cols:
        audit["matched_control_q90_max"] = audit[control_q_cols].max(axis=1)
        audit["matched_control_margin_q90"] = audit["score_obs"] - audit["matched_control_q90_max"]
    else:
        audit["matched_control_q90_max"] = np.nan
        audit["matched_control_margin_q90"] = np.nan
    audit["audit_score"] = (
        -np.log10(audit["q_perm"].clip(lower=1e-6))
        - audit["noise_delta"].fillna(0.0)
        + audit["score_obs"].fillna(0.0)
    )
    sample_ids = sorted(audit["sample_id"].astype(str).unique())
    split = max(1, len(sample_ids) // 2)
    cal_samples = set(sample_ids[:split])
    audit["split"] = np.where(audit["sample_id"].astype(str).isin(cal_samples), "calibration", "test")
    cal_scores = audit.loc[audit["split"] == "calibration", "audit_score"].to_numpy()
    threshold = conformal_threshold(cal_scores, alpha=alpha)
    audit["crc_threshold"] = threshold
    audit["crc_certified"] = certify(audit["audit_score"].to_numpy(), threshold) & audit["raw_certified"]
    audit["snra_certified"] = audit["crc_certified"] & audit["matched_control_gate"]
    audit["failure"] = audit["q_perm"] >= alpha
    return audit


def run_audit(dataset: SpatialDataset, config: AuditConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run SNRA audit for every sample x niche.

    Returns
    -------
    audit_table:
        One row per sample/niche with null statistics and topology signature.
    phase_table:
        Compact QC summary.
    """

    validation = validate_dataset(dataset)
    if not validation["ok"]:
        raise ValueError("; ".join(validation["errors"]))

    rng = np.random.default_rng(config.seed)
    rows: list[dict[str, object]] = []
    phase_rows: list[dict[str, object]] = []
    sample_ids = sorted(dataset.coordinates["sample_id"].astype(str).unique())
    for sample_id in sample_ids:
        coord, meta, labels = _sample_frame(dataset, sample_id)
        coords = coord[["x", "y"]].to_numpy(float)
        edges = knn_edges(coords, k=config.k)
        sample_arr = coord["sample_id"].astype(str).to_numpy()
        degree = _degree(edges, len(labels))
        density_group = _quantile_groups(_local_density_proxy(coords, config.k), n_bins=6)
        degree_group = _quantile_groups(degree, n_bins=6)
        cell_type_group = meta["cell_type"].astype(str).fillna("unknown").to_numpy()
        if "block_id" in meta.columns:
            block_group = meta["block_id"].astype(str).fillna("unknown").to_numpy()
        else:
            x_group = _quantile_groups(coords[:, 0], n_bins=4)
            y_group = _quantile_groups(coords[:, 1], n_bins=4)
            block_group = np.char.add(np.char.add(x_group.astype(str), "_"), y_group.astype(str))
        cell_block_group = np.char.add(np.char.add(cell_type_group.astype(str), "_"), block_group.astype(str))
        for niche in sorted(np.unique(labels)):
            obs = edge_enrichment_score(edges, labels, niche)
            null_scores = []
            null_kind_scores: dict[str, list[float]] = {
                "global": [],
                "sample_stratified": [],
                "local_block": [],
                "abundance_preserving": [],
                "degree_preserving": [],
                "cell_type_preserving": [],
                "density_preserving": [],
                "celltype_block_preserving": [],
            }
            for _ in range(config.n_permutations):
                nulls = {
                    "global": global_label_permutation(labels, rng),
                    "sample_stratified": sample_stratified_permutation(labels, sample_arr, rng),
                    "local_block": block_permutation(labels, coords, sample_arr, rng),
                    "abundance_preserving": abundance_preserving_permutation(labels, sample_arr, rng),
                    "degree_preserving": degree_preserving_attribute_permutation(labels, degree, rng),
                    "cell_type_preserving": grouped_attribute_permutation(labels, cell_type_group, rng),
                    "density_preserving": grouped_attribute_permutation(labels, density_group, rng),
                    "celltype_block_preserving": grouped_attribute_permutation(labels, cell_block_group, rng),
                }
                for kind, p_labels in nulls.items():
                    score = edge_enrichment_score(edges, p_labels, niche)
                    null_kind_scores[kind].append(score)
                    null_scores.append(score)
            pval = permutation_pvalue(obs, np.asarray(null_scores))
            sig = topology_signature(edges, labels, niche)
            noisy_labels = flip_labels(labels, config.annotation_noise, rng)
            noisy_obs = edge_enrichment_score(edges, noisy_labels, niche)
            robustness_delta = abs(obs - noisy_obs)
            k_scores = []
            for k_alt in [max(2, config.k - 2), config.k + 2]:
                alt_edges = knn_edges(coords, k=k_alt)
                k_scores.append(edge_enrichment_score(alt_edges, labels, niche))
            jittered = jitter_coords(coords, 0.01, rng)
            jitter_edges = knn_edges(jittered, k=config.k)
            jitter_score = edge_enrichment_score(jitter_edges, labels, niche)
            stress_flags = [
                abs(s - obs) <= 0.15 for s in k_scores if np.isfinite(s)
            ] + [
                robustness_delta <= 0.15,
                abs(jitter_score - obs) <= 0.15 if np.isfinite(jitter_score) else False,
            ]
            rows.append(
                {
                    "sample_id": sample_id,
                    "niche": niche,
                    "n_units": len(labels),
                    "k": config.k,
                    "score_obs": obs,
                    "p_perm": pval,
                    "null_mean": float(np.mean(null_scores)),
                    "null_sd": float(np.std(null_scores)),
                    "noise_delta": robustness_delta,
                    "stress_k_min_score": float(np.nanmin(k_scores)),
                    "stress_k_max_score": float(np.nanmax(k_scores)),
                    "stress_jitter_score": float(jitter_score),
                    "robustness_score": float(np.mean(stress_flags)) if stress_flags else 0.0,
                    **{f"topology_{k}": v for k, v in sig.items()},
                    **{f"null_{k}_mean": float(np.mean(v)) for k, v in null_kind_scores.items()},
                    **{f"null_{k}_sd": float(np.std(v)) for k, v in null_kind_scores.items()},
                    **{f"null_{k}_q90": float(np.quantile(v, 0.90)) for k, v in null_kind_scores.items()},
                    **{f"null_{k}_q95": float(np.quantile(v, 0.95)) for k, v in null_kind_scores.items()},
                    **{f"null_{k}_p": permutation_pvalue(obs, np.asarray(v)) for k, v in null_kind_scores.items()},
                }
            )
    audit = score_audit_table(pd.DataFrame(rows), alpha=config.alpha)
    test_samples = set(sample_ids[max(1, len(sample_ids) // 2) :])
    test = audit["split"] == "test"
    risk = observed_risk(audit.loc[test, "crc_certified"].to_numpy(), audit.loc[test, "failure"].to_numpy())
    phase_rows.append(
        {
            "phase": "audit",
            "n_samples": len(sample_ids),
            "n_rows": len(audit),
            "crc_threshold": float(audit["crc_threshold"].iloc[0]),
            "test_observed_risk": risk,
            "test_crc_certified": int(audit.loc[test, "crc_certified"].sum()),
            "test_snra_certified": int(audit.loc[test, "snra_certified"].sum()),
        }
    )
    return audit, pd.DataFrame(phase_rows)
