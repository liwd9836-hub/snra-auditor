from __future__ import annotations

from datetime import date
from pathlib import Path

from .certificate_scorer_v0_1 import CertificateScore
from .input_contract_v0_1 import InputContractReport
from .null_ladder_v0_1 import NullLadderResult


def render_audit_card(
    title: str,
    contract: InputContractReport,
    certificate: CertificateScore,
    ladder: list[NullLadderResult] | None = None,
) -> str:
    """Render a compact Markdown audit card for a SNRA prototype run."""

    status = "PASS" if contract.ok and certificate.passed else "FAIL"
    lines = [
        f"# {title}",
        "",
        f"- Date: {date.today().isoformat()}",
        f"- Status: {status}",
        f"- Table kind: {contract.table_kind}",
        f"- Rows: {contract.n_rows}",
        f"- Columns: {contract.n_columns}",
        f"- Certificate score: {certificate.score:.3f}",
        f"- Certificate pass rate: {certificate.pass_rate:.3f}",
        f"- Certified rows: {certificate.certified_rows}/{certificate.total_rows}",
    ]
    if certificate.min_changed_fraction is not None:
        lines.append(f"- Minimum changed fraction: {certificate.min_changed_fraction:.3f}")
    if contract.errors:
        lines.append(f"- Contract errors: {'; '.join(contract.errors)}")
    if contract.warnings:
        lines.append(f"- Contract warnings: {'; '.join(contract.warnings)}")
    if certificate.failure_reasons:
        lines.append(f"- Certificate failure reasons: {'; '.join(certificate.failure_reasons)}")
    lines.extend(
        [
            "",
            "## Null Ladder",
            "",
            "| control | n_rows | observed_mean | null_mean | effect_mean | median_p | changed_fraction |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in ladder or []:
        changed = "" if item.changed_fraction_mean is None else f"{item.changed_fraction_mean:.3f}"
        lines.append(
            "| {control} | {n_rows} | {observed:.3f} | {null:.3f} | {effect:.3f} | {p:.3f} | {changed} |".format(
                control=item.control,
                n_rows=item.n_rows,
                observed=item.observed_mean,
                null=item.null_mean,
                effect=item.effect_mean,
                p=item.empirical_p_median,
                changed=changed,
            )
        )
    if not ladder:
        lines.append("| not_applicable | 0 |  |  |  |  |  |")
    lines.extend(
        [
            "",
            "## Interpretation Guardrail",
            "",
            "This card reports descriptive robustness and negative-control evidence only. It does not establish causal mechanism, direct spatial interaction, or clinical validity.",
            "",
        ]
    )
    return "\n".join(lines)


def write_audit_card(path: str | Path, markdown: str) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    return out
