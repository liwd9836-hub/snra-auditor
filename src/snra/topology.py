from __future__ import annotations

import numpy as np

from .graph import connected_components_count, edge_homophily


def graph_degrees(edges: np.ndarray, n_nodes: int) -> np.ndarray:
    degree = np.zeros(n_nodes, dtype=float)
    if len(edges):
        np.add.at(degree, edges[:, 0], 1)
        np.add.at(degree, edges[:, 1], 1)
    return degree


def label_entropy(labels: np.ndarray) -> float:
    _, counts = np.unique(labels, return_counts=True)
    prob = counts / counts.sum()
    return float(-np.sum(prob * np.log2(prob + 1e-12)))


def topology_signature(edges: np.ndarray, labels: np.ndarray, target_label: str) -> dict[str, float]:
    labels = np.asarray(labels).astype(str)
    n = len(labels)
    degree = graph_degrees(edges, n)
    mask = labels == str(target_label)
    active_edges = 0
    boundary_edges = 0
    for a, b in edges:
        if mask[a] or mask[b]:
            active_edges += 1
        if mask[a] != mask[b]:
            boundary_edges += 1
    return {
        "n_target": float(mask.sum()),
        "target_fraction": float(mask.mean()),
        "mean_degree": float(np.mean(degree)) if n else np.nan,
        "target_mean_degree": float(np.mean(degree[mask])) if mask.sum() else 0.0,
        "edge_homophily": edge_homophily(edges, labels),
        "target_components": float(connected_components_count(edges, n, mask=mask)),
        "boundary_fraction": float(boundary_edges / active_edges) if active_edges else 0.0,
        "label_entropy": label_entropy(labels),
    }


def topology_distance(sig_a: dict[str, float], sig_b: dict[str, float]) -> float:
    keys = sorted(set(sig_a) & set(sig_b))
    if not keys:
        return np.nan
    va = np.array([sig_a[k] for k in keys], dtype=float)
    vb = np.array([sig_b[k] for k in keys], dtype=float)
    scale = np.maximum(np.abs(va) + np.abs(vb), 1.0)
    return float(np.sqrt(np.mean(((va - vb) / scale) ** 2)))

