from __future__ import annotations

import numpy as np
import pandas as pd

from .graph import edge_enrichment_score, knn_edges
from .topology import topology_signature


def auc_score(y_true: np.ndarray, score: np.ndarray) -> float:
    """Compute rank AUC without sklearn."""

    y_true = np.asarray(y_true, dtype=bool)
    score = np.asarray(score, dtype=float)
    pos = score[y_true]
    neg = score[~y_true]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    wins = 0.0
    for p in pos:
        wins += np.sum(p > neg) + 0.5 * np.sum(p == neg)
    return float(wins / (len(pos) * len(neg)))


def make_grid_coords(n_side: int = 30) -> np.ndarray:
    x, y = np.meshgrid(np.arange(n_side), np.arange(n_side))
    return np.column_stack([x.ravel(), y.ravel()]).astype(float)


def labels_same_composition(
    coords: np.ndarray,
    n_labels: int = 3,
    mode: str = "stripe",
    seed: int = 1,
) -> np.ndarray:
    """Create labels with exactly equal composition but different topology."""

    rng = np.random.default_rng(seed)
    n = len(coords)
    base = np.repeat(np.arange(n_labels), repeats=n // n_labels)
    if len(base) < n:
        base = np.concatenate([base, np.arange(n - len(base)) % n_labels])
    if mode == "random":
        rng.shuffle(base)
    elif mode == "stripe":
        order = np.argsort(coords[:, 0])
        out = np.empty(n, dtype=int)
        out[order] = base
        base = out
    elif mode == "block":
        center = coords.mean(axis=0)
        dist = np.sqrt(((coords - center) ** 2).sum(axis=1))
        order = np.argsort(dist)
        out = np.empty(n, dtype=int)
        out[order] = base
        base = out
    elif mode == "checker":
        side = int(round(np.sqrt(n)))
        raw = ((coords[:, 0] // 3 + coords[:, 1] // 3) % n_labels).astype(int)
        # enforce exact composition while preserving checker tendency by ranking raw with jitter
        score = raw + rng.normal(0, 0.01, n)
        order = np.argsort(score)
        out = np.empty(n, dtype=int)
        out[order] = base
        base = out
    else:
        raise ValueError(mode)
    return np.array([f"D{i+1}" for i in base], dtype=str)


def composition_features(labels: np.ndarray, target: str) -> dict[str, float]:
    labels = np.asarray(labels).astype(str)
    return {"target_fraction": float(np.mean(labels == target))}


def benchmark_composition_identical_topology(seed: int = 1, n_replicates: int = 12) -> pd.DataFrame:
    coords = make_grid_coords(n_side=30)
    edges = knn_edges(coords, k=6)
    rows: list[dict[str, object]] = []
    for rep in range(n_replicates):
        for mode, is_structured in [
            ("random", False),
            ("stripe", True),
            ("block", True),
            ("checker", True),
        ]:
            labels = labels_same_composition(coords, mode=mode, seed=seed + rep * 10)
            for target in sorted(np.unique(labels)):
                comp = composition_features(labels, target)
                topo = topology_signature(edges, labels, target)
                rows.append(
                    {
                        "replicate": rep,
                        "mode": mode,
                        "is_structured": is_structured,
                        "target": target,
                        "edge_score": edge_enrichment_score(edges, labels, target),
                        **{f"composition_{k}": v for k, v in comp.items()},
                        **{f"topology_{k}": v for k, v in topo.items()},
                    }
                )
    df = pd.DataFrame(rows)
    # Same-composition task: composition score is intentionally target_fraction only.
    df["composition_score"] = df["composition_target_fraction"]
    df["topology_score"] = (
        df["edge_score"].fillna(0)
        + df["topology_edge_homophily"].fillna(0)
        - df["topology_boundary_fraction"].fillna(0)
        - 0.05 * df["topology_target_components"].fillna(0)
    )
    return df

