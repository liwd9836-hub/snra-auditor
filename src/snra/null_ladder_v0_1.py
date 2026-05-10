from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class NullLadderResult:
    control: str
    n_rows: int
    observed_mean: float
    null_mean: float
    effect_mean: float
    empirical_p_median: float
    changed_fraction_mean: float | None

    def to_dict(self) -> dict[str, object]:
        return {
            "control": self.control,
            "n_rows": self.n_rows,
            "observed_mean": self.observed_mean,
            "null_mean": self.null_mean,
            "effect_mean": self.effect_mean,
            "empirical_p_median": self.empirical_p_median,
            "changed_fraction_mean": self.changed_fraction_mean,
        }


def _float_value(row: Mapping[str, object], key: str, default: float = np.nan) -> float:
    value = row.get(key, default)
    if value in ("", None):
        return default
    return float(value)


def summarize_null_ladder(rows: list[Mapping[str, object]]) -> list[NullLadderResult]:
    """Summarize detail rows by negative-control level.

    Expected detail rows come from SNRA-style audit TSVs with one row per
    sample x label x control. The summary is deliberately simple and stable.
    """

    grouped: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("control", "unknown"))].append(row)

    results: list[NullLadderResult] = []
    for control, control_rows in sorted(grouped.items()):
        observed = np.array(
            [_float_value(row, "observed_same_label_neighbor_fraction") for row in control_rows],
            dtype=float,
        )
        null = np.array([_float_value(row, "null_mean") for row in control_rows], dtype=float)
        pvals = np.array([_float_value(row, "empirical_p_greater") for row in control_rows], dtype=float)
        changed_values = [
            _float_value(row, "effective_changed_fraction")
            for row in control_rows
            if row.get("effective_changed_fraction", "") not in ("", None)
        ]
        changed = np.array(changed_values, dtype=float) if changed_values else np.array([], dtype=float)
        results.append(
            NullLadderResult(
                control=control,
                n_rows=len(control_rows),
                observed_mean=float(np.nanmean(observed)),
                null_mean=float(np.nanmean(null)),
                effect_mean=float(np.nanmean(observed - null)),
                empirical_p_median=float(np.nanmedian(pvals)),
                changed_fraction_mean=float(np.nanmean(changed)) if changed.size else None,
            )
        )
    return results


def label_shuffle_changed_fraction(labels: list[str] | np.ndarray, seed: int = 1) -> float:
    """Return the fraction of labels changed by a global label shuffle."""

    arr = np.asarray(labels).astype(str)
    if arr.size == 0:
        return 0.0
    shuffled = arr.copy()
    np.random.default_rng(seed).shuffle(shuffled)
    return float(np.mean(shuffled != arr))
