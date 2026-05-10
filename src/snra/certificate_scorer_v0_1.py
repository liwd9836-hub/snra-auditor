from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from .null_ladder_v0_1 import NullLadderResult, summarize_null_ladder


@dataclass(frozen=True)
class CertificateScore:
    passed: bool
    score: float
    certified_rows: int
    total_rows: int
    pass_rate: float
    median_p: float
    min_changed_fraction: float | None
    failure_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "score": self.score,
            "certified_rows": self.certified_rows,
            "total_rows": self.total_rows,
            "pass_rate": self.pass_rate,
            "median_p": self.median_p,
            "min_changed_fraction": self.min_changed_fraction,
            "failure_reasons": list(self.failure_reasons),
        }


def _bool_value(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def score_detail_certificate(
    rows: list[Mapping[str, object]],
    p_threshold: float = 0.05,
    min_pass_rate: float = 0.70,
    min_changed_fraction: float = 0.20,
) -> CertificateScore:
    """Score detail audit rows into a compact pass/fail certificate.

    Certification requires enough control rows to pass, a sufficiently low
    median empirical p value, and non-degenerate shuffles when change-rate
    information is available.
    """

    if not rows:
        return CertificateScore(False, 0.0, 0, 0, 0.0, 1.0, None, ("no rows",))

    certified = []
    pvals = []
    changed = []
    for row in rows:
        pval = float(row.get("empirical_p_greater", 1.0) or 1.0)
        pvals.append(pval)
        pass_flag = row.get("passes_control")
        if pass_flag in ("", None):
            pass_flag = pval <= p_threshold
        certified.append(_bool_value(pass_flag) and pval <= p_threshold)
        if row.get("effective_changed_fraction", "") not in ("", None):
            changed.append(float(row["effective_changed_fraction"]))

    total = len(rows)
    certified_rows = int(np.sum(certified))
    pass_rate = certified_rows / total
    median_p = float(np.median(np.asarray(pvals, dtype=float)))
    min_changed = float(np.min(np.asarray(changed, dtype=float))) if changed else None
    reasons: list[str] = []
    if pass_rate < min_pass_rate:
        reasons.append(f"pass_rate<{min_pass_rate:g}")
    if median_p > p_threshold:
        reasons.append(f"median_p>{p_threshold:g}")
    if min_changed is not None and min_changed < min_changed_fraction:
        reasons.append(f"changed_fraction<{min_changed_fraction:g}")

    p_component = max(0.0, -np.log10(max(median_p, 1e-12)) / -np.log10(p_threshold))
    score = float(0.7 * pass_rate + 0.3 * min(p_component, 2.0) / 2.0)
    return CertificateScore(
        passed=not reasons,
        score=score,
        certified_rows=certified_rows,
        total_rows=total,
        pass_rate=float(pass_rate),
        median_p=median_p,
        min_changed_fraction=min_changed,
        failure_reasons=tuple(reasons),
    )


def score_summary_certificate(
    rows: list[Mapping[str, object]],
    min_primary_rate: float = 0.70,
) -> CertificateScore:
    if not rows:
        return CertificateScore(False, 0.0, 0, 0, 0.0, 1.0, None, ("no rows",))

    rates = []
    for row in rows:
        for key in (
            "primary_composition_certified_rate",
            "stringent_block_certified_rate",
            "certified_rate",
            "positive_call_rate",
            "composition_aware_certified_rate",
            "lineage_boundary_certified_rate",
        ):
            if row.get(key, "") not in ("", None):
                rates.append(float(row[key]))
                break
    if not rates:
        return CertificateScore(False, 0.0, 0, len(rows), 0.0, 1.0, None, ("no certificate rate column",))
    pass_rate = float(np.mean(np.asarray(rates, dtype=float)))
    reasons = [] if pass_rate >= min_primary_rate else [f"pass_rate<{min_primary_rate:g}"]
    certified_rows = int(sum(rate >= min_primary_rate for rate in rates))
    return CertificateScore(
        passed=not reasons,
        score=pass_rate,
        certified_rows=certified_rows,
        total_rows=len(rates),
        pass_rate=pass_rate,
        median_p=0.0,
        min_changed_fraction=None,
        failure_reasons=tuple(reasons),
    )


def score_certificate(rows: list[Mapping[str, object]], table_kind: str) -> CertificateScore:
    if table_kind == "detail":
        return score_detail_certificate(rows)
    if table_kind == "summary":
        return score_summary_certificate(rows)
    return CertificateScore(False, 0.0, 0, len(rows), 0.0, 1.0, None, ("unsupported table kind",))


def ladder_for_certificate(rows: list[Mapping[str, object]], table_kind: str) -> list[NullLadderResult]:
    if table_kind != "detail":
        return []
    return summarize_null_ladder(rows)
