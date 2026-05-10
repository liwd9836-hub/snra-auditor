from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


REQUIRED_SUMMARY_COLUMNS = (
    "dataset",
    "label_set",
    "n_samples",
    "audit_label_rows",
)

PACKAGE_SUMMARY_COLUMNS = (
    "dataset",
    "tool",
    "control",
    "positive_call_rate",
)

COMPOSITION_AUDIT_SUMMARY_COLUMNS = (
    "dataset",
    "audit_label_rows",
    "composition_aware_certified_rate",
)

TONIC_LINEAGE_DIGEST_COLUMNS = (
    "dataset",
    "boundary_task",
    "lineage_boundary_certified_rate",
)

REQUIRED_DETAIL_COLUMNS = (
    "sample_id",
    "label",
    "control",
    "observed_same_label_neighbor_fraction",
    "null_mean",
    "empirical_p_greater",
)


@dataclass(frozen=True)
class InputContractReport:
    ok: bool
    table_kind: str
    n_rows: int
    n_columns: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "table_kind": self.table_kind,
            "n_rows": self.n_rows,
            "n_columns": self.n_columns,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


def _missing_columns(columns: Iterable[str], required: Iterable[str]) -> list[str]:
    present = set(columns)
    return [column for column in required if column not in present]


def infer_table_kind(columns: Iterable[str]) -> str:
    columns = set(columns)
    detail_score = len(columns & set(REQUIRED_DETAIL_COLUMNS))
    summary_score = len(columns & set(REQUIRED_SUMMARY_COLUMNS))
    package_summary_score = len(columns & set(PACKAGE_SUMMARY_COLUMNS))
    composition_audit_score = len(columns & set(COMPOSITION_AUDIT_SUMMARY_COLUMNS))
    tonic_lineage_score = len(columns & set(TONIC_LINEAGE_DIGEST_COLUMNS))
    if detail_score >= summary_score and detail_score >= 3:
        return "detail"
    if summary_score >= 2 or package_summary_score >= 3 or composition_audit_score >= 3 or tonic_lineage_score >= 3:
        return "summary"
    return "unknown"


def validate_tabular_contract(
    rows: list[Mapping[str, object]],
    columns: Iterable[str],
    table_kind: str | None = None,
) -> InputContractReport:
    """Validate the minimal TSV contract accepted by the v0.1 SNRA CLI.

    The validator is intentionally structural. It does not claim biological
    validity; it only checks whether downstream scoring can be run audibly.
    """

    columns = tuple(columns)
    inferred = table_kind or infer_table_kind(columns)
    errors: list[str] = []
    warnings: list[str] = []
    if inferred == "detail":
        missing = _missing_columns(columns, REQUIRED_DETAIL_COLUMNS)
        if missing:
            errors.append(f"detail table missing columns: {','.join(missing)}")
    elif inferred == "summary":
        canonical_missing = _missing_columns(columns, REQUIRED_SUMMARY_COLUMNS)
        package_missing = _missing_columns(columns, PACKAGE_SUMMARY_COLUMNS)
        composition_missing = _missing_columns(columns, COMPOSITION_AUDIT_SUMMARY_COLUMNS)
        tonic_lineage_missing = _missing_columns(columns, TONIC_LINEAGE_DIGEST_COLUMNS)
        if canonical_missing and package_missing and composition_missing and tonic_lineage_missing:
            errors.append(
                "summary table missing columns for supported schemas: "
                f"canonical_missing={','.join(canonical_missing)}; "
                f"package_missing={','.join(package_missing)}; "
                f"composition_audit_missing={','.join(composition_missing)}; "
                f"tonic_lineage_missing={','.join(tonic_lineage_missing)}"
            )
    else:
        errors.append("could not infer table kind from columns")

    if not rows:
        errors.append("input table has no data rows")
    if len(columns) != len(set(columns)):
        errors.append("input table has duplicate column names")
    if len(rows) < 3:
        warnings.append("small table: certificate estimates are only smoke tests")

    return InputContractReport(
        ok=not errors,
        table_kind=inferred,
        n_rows=len(rows),
        n_columns=len(columns),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
