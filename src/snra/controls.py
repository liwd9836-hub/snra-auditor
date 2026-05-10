from __future__ import annotations

import numpy as np

from .graph import knn_edges
from .null_models import (
    degree_preserving_attribute_permutation,
    global_label_permutation,
    sample_stratified_permutation,
)
from .topology import graph_degrees


def make_negative_labels(
    labels: np.ndarray,
    coords: np.ndarray,
    sample_ids: np.ndarray,
    mode: str,
    seed: int = 1,
) -> np.ndarray:
    """Generate negative-control candidate labels with preserved marginals."""

    rng = np.random.default_rng(seed)
    labels = np.asarray(labels).astype(str)
    sample_ids = np.asarray(sample_ids).astype(str)
    coords = np.asarray(coords, dtype=float)
    if mode == "global_shuffle":
        return global_label_permutation(labels, rng).astype(str)
    if mode == "within_sample_shuffle":
        return sample_stratified_permutation(labels, sample_ids, rng).astype(str)
    if mode == "degree_preserving_shuffle":
        edges = knn_edges(coords, k=8)
        degree = graph_degrees(edges, len(labels))
        return degree_preserving_attribute_permutation(labels, degree, rng).astype(str)
    if mode == "composition_matched_random":
        out = labels.copy()
        for sample in np.unique(sample_ids):
            idx = np.flatnonzero(sample_ids == sample)
            unique, counts = np.unique(labels[idx], return_counts=True)
            probs = counts / counts.sum()
            out[idx] = rng.choice(unique, size=len(idx), p=probs)
        return out.astype(str)
    raise ValueError(f"unknown negative-control mode: {mode}")

