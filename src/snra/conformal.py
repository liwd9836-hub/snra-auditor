from __future__ import annotations

import numpy as np


def conformal_threshold(calibration_scores: np.ndarray, alpha: float = 0.10) -> float:
    """Lower-tail conformal cutoff for scores where larger is better."""

    scores = np.asarray(calibration_scores, dtype=float)
    if len(scores) == 0:
        raise ValueError("calibration_scores must not be empty")
    q = np.ceil((len(scores) + 1) * alpha) / len(scores)
    q = min(max(q, 0.0), 1.0)
    return float(np.quantile(scores, q, method="lower"))


def certify(scores: np.ndarray, threshold: float) -> np.ndarray:
    return np.asarray(scores, dtype=float) >= float(threshold)


def observed_risk(certified: np.ndarray, failures: np.ndarray) -> float:
    certified = np.asarray(certified, dtype=bool)
    failures = np.asarray(failures, dtype=bool)
    if certified.sum() == 0:
        return 0.0
    return float(np.mean(failures[certified]))

