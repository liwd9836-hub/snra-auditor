from __future__ import annotations

import numpy as np
import pandas as pd


def global_label_permutation(labels: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    perm = np.asarray(labels).copy()
    rng.shuffle(perm)
    return perm


def sample_stratified_permutation(
    labels: np.ndarray, sample_ids: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    out = np.asarray(labels).copy()
    sample_ids = np.asarray(sample_ids)
    for sample in np.unique(sample_ids):
        idx = np.flatnonzero(sample_ids == sample)
        shuffled = out[idx].copy()
        rng.shuffle(shuffled)
        out[idx] = shuffled
    return out


def abundance_preserving_permutation(
    labels: np.ndarray, sample_ids: np.ndarray | None, rng: np.random.Generator
) -> np.ndarray:
    """Shuffle labels while preserving label abundance.

    If sample_ids are supplied this preserves abundance within each sample;
    otherwise it preserves abundance globally.
    """

    if sample_ids is None:
        return global_label_permutation(labels, rng)
    return sample_stratified_permutation(labels, sample_ids, rng)


def block_permutation(
    labels: np.ndarray, coords: np.ndarray, sample_ids: np.ndarray, rng: np.random.Generator, n_bins: int = 4
) -> np.ndarray:
    """Permute labels within coarse spatial blocks per sample."""

    out = np.asarray(labels).copy()
    coords = np.asarray(coords, dtype=float)
    sample_ids = np.asarray(sample_ids)
    for sample in np.unique(sample_ids):
        sidx = np.flatnonzero(sample_ids == sample)
        x = coords[sidx, 0]
        y = coords[sidx, 1]
        xb = pd.qcut(x, q=min(n_bins, len(np.unique(x))), labels=False, duplicates="drop")
        yb = pd.qcut(y, q=min(n_bins, len(np.unique(y))), labels=False, duplicates="drop")
        blocks = np.asarray(xb).astype(str) + "_" + np.asarray(yb).astype(str)
        for block in np.unique(blocks):
            idx = sidx[blocks == block]
            if len(idx) > 1:
                shuffled = out[idx].copy()
                rng.shuffle(shuffled)
                out[idx] = shuffled
    return out


def degree_preserving_attribute_permutation(
    labels: np.ndarray, degree: np.ndarray, rng: np.random.Generator, n_bins: int = 4
) -> np.ndarray:
    """Shuffle labels within degree quantile bins."""

    out = np.asarray(labels).copy()
    degree = np.asarray(degree, dtype=float)
    bins = pd.qcut(degree, q=min(n_bins, len(np.unique(degree))), labels=False, duplicates="drop")
    bins = np.asarray(bins)
    for b in np.unique(bins):
        idx = np.flatnonzero(bins == b)
        if len(idx) > 1:
            shuffled = out[idx].copy()
            rng.shuffle(shuffled)
            out[idx] = shuffled
    return out


def grouped_attribute_permutation(
    labels: np.ndarray, groups: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    """Shuffle labels within supplied nuisance groups.

    This is used for matched controls where a candidate claim must exceed a
    nuisance-preserving null, for example cell-type composition, FOV/block, or
    local-density strata. Groups with a single member are left unchanged.
    """

    out = np.asarray(labels).copy()
    groups = np.asarray(groups).astype(str)
    for group in np.unique(groups):
        idx = np.flatnonzero(groups == group)
        if len(idx) > 1:
            shuffled = out[idx].copy()
            rng.shuffle(shuffled)
            out[idx] = shuffled
    return out


def permutation_pvalue(obs: float, null_scores: np.ndarray) -> float:
    null_scores = np.asarray(null_scores, dtype=float)
    return float((1 + np.sum(null_scores >= obs)) / (len(null_scores) + 1))


def bh_fdr(pvalues: np.ndarray) -> np.ndarray:
    pvalues = np.asarray(pvalues, dtype=float)
    n = len(pvalues)
    order = np.argsort(pvalues)
    ranked = pvalues[order]
    q = ranked * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty_like(q)
    out[order] = np.minimum(q, 1.0)
    return out
