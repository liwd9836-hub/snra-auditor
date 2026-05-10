from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree


def knn_edges(coords: np.ndarray, k: int = 8) -> np.ndarray:
    """Build undirected kNN edges from 2D coordinates."""

    coords = np.asarray(coords, dtype=float)
    if coords.ndim != 2 or coords.shape[1] != 2:
        raise ValueError("coords must be an n x 2 array")
    if coords.shape[0] <= k:
        k = max(1, coords.shape[0] - 1)
    tree = cKDTree(coords)
    _, idx = tree.query(coords, k=k + 1)
    edges = set()
    for i, neigh in enumerate(idx):
        for j in neigh[1:]:
            a, b = sorted((int(i), int(j)))
            if a != b:
                edges.add((a, b))
    return np.array(sorted(edges), dtype=int)


def radius_edges(coords: np.ndarray, radius: float) -> np.ndarray:
    """Build undirected radius graph edges."""

    coords = np.asarray(coords, dtype=float)
    tree = cKDTree(coords)
    pairs = tree.query_pairs(radius)
    if not pairs:
        return np.empty((0, 2), dtype=int)
    return np.array(sorted((min(a, b), max(a, b)) for a, b in pairs), dtype=int)


def edge_homophily(edges: np.ndarray, labels: np.ndarray) -> float:
    if len(edges) == 0:
        return np.nan
    labels = np.asarray(labels)
    return float(np.mean(labels[edges[:, 0]] == labels[edges[:, 1]]))


def edge_enrichment_score(edges: np.ndarray, labels: np.ndarray, target_label: str) -> float:
    """Observed target-target edge fraction among edges touching target label."""

    if len(edges) == 0:
        return np.nan
    labels = np.asarray(labels).astype(str)
    is_target = labels == str(target_label)
    touches = is_target[edges[:, 0]] | is_target[edges[:, 1]]
    if touches.sum() == 0:
        return 0.0
    both = is_target[edges[:, 0]] & is_target[edges[:, 1]]
    return float(both[touches].sum() / touches.sum())


def connected_components_count(edges: np.ndarray, n_nodes: int, mask: np.ndarray | None = None) -> int:
    """Count connected components, optionally after subsetting nodes by mask."""

    if mask is None:
        active = np.ones(n_nodes, dtype=bool)
    else:
        active = np.asarray(mask, dtype=bool)
    nodes = np.flatnonzero(active)
    if len(nodes) == 0:
        return 0
    parent = {int(i): int(i) for i in nodes}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for a, b in edges:
        if active[a] and active[b]:
            union(int(a), int(b))
    return len({find(int(i)) for i in nodes})

