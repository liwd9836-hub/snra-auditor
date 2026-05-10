from __future__ import annotations

import numpy as np


def flip_labels(labels: np.ndarray, rate: float, rng: np.random.Generator) -> np.ndarray:
    labels = np.asarray(labels).astype(str).copy()
    unique = np.unique(labels)
    n_flip = int(round(len(labels) * rate))
    if n_flip == 0 or len(unique) < 2:
        return labels
    idx = rng.choice(len(labels), size=n_flip, replace=False)
    for i in idx:
        choices = unique[unique != labels[i]]
        labels[i] = rng.choice(choices)
    return labels


def subsample_mask(n: int, fraction: float, rng: np.random.Generator) -> np.ndarray:
    keep = max(3, int(round(n * fraction)))
    idx = rng.choice(n, size=keep, replace=False)
    mask = np.zeros(n, dtype=bool)
    mask[idx] = True
    return mask


def jitter_coords(coords: np.ndarray, scale_fraction: float, rng: np.random.Generator) -> np.ndarray:
    coords = np.asarray(coords, dtype=float)
    span = np.maximum(coords.max(axis=0) - coords.min(axis=0), 1.0)
    noise = rng.normal(0, scale_fraction * span, size=coords.shape)
    return coords + noise


def robustness_score(certified_flags: list[bool]) -> float:
    if not certified_flags:
        return 0.0
    return float(np.mean(certified_flags))

