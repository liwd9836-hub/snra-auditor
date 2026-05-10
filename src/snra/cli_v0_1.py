from __future__ import annotations

import argparse
import csv
import json
import tempfile
from pathlib import Path
from typing import Mapping

from .audit_card_v0_1 import render_audit_card, write_audit_card
from .certificate_scorer_v0_1 import CertificateScore, ladder_for_certificate, score_certificate
from .input_contract_v0_1 import InputContractReport, validate_tabular_contract


TOY_ROWS = [
    {
        "sample_id": "S1",
        "label": "immune_border",
        "control": "within_sample_label_shuffle",
        "observed_same_label_neighbor_fraction": "0.62",
        "null_mean": "0.18",
        "empirical_p_greater": "0.01",
        "effective_changed_fraction": "0.72",
        "passes_control": "True",
    },
    {
        "sample_id": "S2",
        "label": "immune_border",
        "control": "within_sample_label_shuffle",
        "observed_same_label_neighbor_fraction": "0.58",
        "null_mean": "0.21",
        "empirical_p_greater": "0.02",
        "effective_changed_fraction": "0.68",
        "passes_control": "True",
    },
    {
        "sample_id": "S1",
        "label": "immune_border",
        "control": "spatial_block_shuffle",
        "observed_same_label_neighbor_fraction": "0.62",
        "null_mean": "0.34",
        "empirical_p_greater": "0.03",
        "effective_changed_fraction": "0.44",
        "passes_control": "True",
    },
    {
        "sample_id": "S2",
        "label": "immune_border",
        "control": "spatial_block_shuffle",
        "observed_same_label_neighbor_fraction": "0.58",
        "null_mean": "0.35",
        "empirical_p_greater": "0.04",
        "effective_changed_fraction": "0.41",
        "passes_control": "True",
    },
]


def read_tsv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def write_summary(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "status",
        "table_kind",
        "n_rows",
        "certificate_score",
        "pass_rate",
        "certified_rows",
        "total_rows",
        "failure_reasons",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_manifest_summary(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "input_id",
        "source",
        "table_kind",
        "contract_ok",
        "status",
        "certificate_score",
        "pass_rate",
        "certified_rows",
        "total_rows",
        "failure_reasons",
        "summary_tsv",
        "audit_card_md",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_rows(input_tsv: Path | None) -> tuple[list[Mapping[str, object]], list[str], str]:
    if input_tsv:
        rows, columns = read_tsv(input_tsv)
        return rows, columns, str(input_tsv)
    return TOY_ROWS, list(TOY_ROWS[0]), "toy_dataset"


def resolve_manifest_path(value: str, manifest_path: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    manifest_relative = (manifest_path.parent / path).resolve()
    if manifest_relative.exists():
        return manifest_relative
    return (Path.cwd() / path).resolve()


def read_manifest(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ValueError("manifest root must be a JSON object")
    entries = manifest.get("inputs")
    if not isinstance(entries, list) or not entries:
        raise ValueError("manifest must contain a non-empty 'inputs' list")
    normalized: list[dict[str, object]] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"manifest input #{index} must be an object")
        input_id = str(entry.get("id") or f"input_{index}")
        if not entry.get("path"):
            raise ValueError(f"manifest input '{input_id}' is missing path")
        table_kind = entry.get("table_kind")
        if table_kind not in (None, "summary", "detail"):
            raise ValueError(f"manifest input '{input_id}' has invalid table_kind: {table_kind}")
        normalized.append(
            {
                "id": input_id,
                "path": resolve_manifest_path(str(entry["path"]), path),
                "table_kind": table_kind,
                "title": str(entry.get("title") or f"SNRA audit card: {input_id}"),
            }
        )
    return normalized


def score_rows(
    rows: list[Mapping[str, object]],
    columns: list[str],
    table_kind: str | None,
) -> tuple[InputContractReport, CertificateScore]:
    contract = validate_tabular_contract(rows, columns, table_kind=table_kind)
    if contract.ok:
        certificate = score_certificate(rows, contract.table_kind)
    else:
        certificate = score_certificate([], "unknown")
    return contract, certificate


def print_contract(contract: InputContractReport) -> None:
    print(f"contract_ok\t{contract.ok}")
    print(f"table_kind\t{contract.table_kind}")
    print(f"n_rows\t{contract.n_rows}")
    print(f"n_columns\t{contract.n_columns}")
    print(f"errors\t{';'.join(contract.errors)}")
    print(f"warnings\t{';'.join(contract.warnings)}")


def print_certificate(certificate: CertificateScore) -> None:
    print(f"certificate_passed\t{certificate.passed}")
    print(f"certificate_score\t{certificate.score:.6f}")
    print(f"pass_rate\t{certificate.pass_rate:.6f}")
    print(f"certified_rows\t{certificate.certified_rows}")
    print(f"total_rows\t{certificate.total_rows}")
    print(f"failure_reasons\t{';'.join(certificate.failure_reasons)}")


def write_audit_outputs(
    rows: list[Mapping[str, object]],
    contract: InputContractReport,
    certificate: CertificateScore,
    out_dir: Path,
    title: str,
) -> tuple[Path, Path]:
    ladder = ladder_for_certificate(rows, contract.table_kind) if contract.ok else []
    markdown = render_audit_card(title, contract, certificate, ladder)
    summary_path = out_dir / "snra_demo_audit_summary_v0_1.tsv"
    card_path = out_dir / "snra_demo_audit_card_v0_1.md"
    write_summary(
        summary_path,
        [
            {
                "status": "PASS" if contract.ok and certificate.passed else "FAIL",
                "table_kind": contract.table_kind,
                "n_rows": contract.n_rows,
                "certificate_score": f"{certificate.score:.6f}",
                "pass_rate": f"{certificate.pass_rate:.6f}",
                "certified_rows": certificate.certified_rows,
                "total_rows": certificate.total_rows,
                "failure_reasons": ";".join(certificate.failure_reasons),
            }
        ],
    )
    write_audit_card(card_path, markdown)
    return summary_path, card_path


def exit_code(contract: InputContractReport, certificate: CertificateScore, fail_on_certificate_fail: bool) -> int:
    if not contract.ok:
        return 2
    if fail_on_certificate_fail and not certificate.passed:
        return 1
    return 0


def add_common_input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input-tsv", type=Path, help="Existing SNRA summary/detail TSV. Uses toy data if omitted.")
    parser.add_argument("--table-kind", choices=("summary", "detail"), help="Override table-kind inference.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SNRA v0.1 package prototype CLI")
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="Validate a summary/detail TSV input contract.")
    add_common_input_args(validate_parser)

    score_parser = subparsers.add_parser("score", help="Validate and score a conservative SNRA certificate.")
    add_common_input_args(score_parser)
    score_parser.add_argument("--fail-on-certificate-fail", action="store_true")

    card_parser = subparsers.add_parser("audit-card", help="Write an audit-card markdown file and compact summary TSV.")
    add_common_input_args(card_parser)
    card_parser.add_argument("--out-dir", type=Path, required=True)
    card_parser.add_argument("--title", default="SNRA package prototype v0.1 audit card")
    card_parser.add_argument("--fail-on-certificate-fail", action="store_true")

    demo_parser = subparsers.add_parser("demo", help="Run the toy audit-card demo.")
    demo_parser.add_argument("--out-dir", type=Path, help="Output directory. Defaults to a temporary demo directory.")
    demo_parser.add_argument("--title", default="SNRA package prototype v0.1 audit card")
    demo_parser.add_argument("--fail-on-certificate-fail", action="store_true")

    manifest_parser = subparsers.add_parser("manifest", help="Run audit cards for all inputs in a JSON manifest.")
    manifest_parser.add_argument("--manifest-json", type=Path, required=True)
    manifest_parser.add_argument("--out-dir", type=Path, required=True)
    manifest_parser.add_argument("--fail-on-certificate-fail", action="store_true")
    return parser


def run_validate(args: argparse.Namespace) -> int:
    rows, columns, source = load_rows(args.input_tsv)
    contract, _ = score_rows(rows, columns, args.table_kind)
    print(f"source\t{source}")
    print_contract(contract)
    return 0 if contract.ok else 2


def run_score(args: argparse.Namespace) -> int:
    rows, columns, source = load_rows(args.input_tsv)
    contract, certificate = score_rows(rows, columns, args.table_kind)
    print(f"source\t{source}")
    print_contract(contract)
    print_certificate(certificate)
    return exit_code(contract, certificate, args.fail_on_certificate_fail)


def run_audit_card(args: argparse.Namespace) -> int:
    rows, columns, source = load_rows(args.input_tsv)
    contract, certificate = score_rows(rows, columns, args.table_kind)
    summary_path, card_path = write_audit_outputs(rows, contract, certificate, args.out_dir, args.title)
    print(f"source\t{source}")
    print(f"status\t{'PASS' if contract.ok and certificate.passed else 'FAIL'}")
    print(f"summary_tsv\t{summary_path}")
    print(f"audit_card_md\t{card_path}")
    return exit_code(contract, certificate, args.fail_on_certificate_fail)


def run_demo(args: argparse.Namespace) -> int:
    args.input_tsv = None
    args.table_kind = "detail"
    args.out_dir = args.out_dir or Path(tempfile.mkdtemp(prefix="snra_demo_v0_1_"))
    return run_audit_card(args)


def run_manifest(args: argparse.Namespace) -> int:
    try:
        entries = read_manifest(args.manifest_json)
    except Exception as exc:
        print(f"manifest_error\t{exc}")
        return 2

    manifest_rows: list[dict[str, object]] = []
    any_contract_error = False
    any_certificate_failure = False
    for entry in entries:
        input_id = str(entry["id"])
        input_path = Path(entry["path"])
        table_kind = entry.get("table_kind")
        if not input_path.exists():
            print(f"input_missing\t{input_id}\t{input_path}")
            any_contract_error = True
            continue
        rows, columns = read_tsv(input_path)
        contract, certificate = score_rows(rows, columns, str(table_kind) if table_kind else None)
        input_out_dir = args.out_dir / input_id
        summary_path, card_path = write_audit_outputs(rows, contract, certificate, input_out_dir, str(entry["title"]))
        status = "PASS" if contract.ok and certificate.passed else "FAIL"
        print(f"input\t{input_id}\t{status}\t{input_path}")
        manifest_rows.append(
            {
                "input_id": input_id,
                "source": str(input_path),
                "table_kind": contract.table_kind,
                "contract_ok": contract.ok,
                "status": status,
                "certificate_score": f"{certificate.score:.6f}",
                "pass_rate": f"{certificate.pass_rate:.6f}",
                "certified_rows": certificate.certified_rows,
                "total_rows": certificate.total_rows,
                "failure_reasons": ";".join(certificate.failure_reasons),
                "summary_tsv": str(summary_path),
                "audit_card_md": str(card_path),
            }
        )
        if not contract.ok:
            any_contract_error = True
        if not certificate.passed:
            any_certificate_failure = True

    write_manifest_summary(args.out_dir / "snra_manifest_audit_summary_v0_1.tsv", manifest_rows)
    if any_contract_error:
        return 2
    if args.fail_on_certificate_fail and any_certificate_failure:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate":
        return run_validate(args)
    if args.command == "score":
        return run_score(args)
    if args.command == "audit-card":
        return run_audit_card(args)
    if args.command == "demo":
        return run_demo(args)
    if args.command == "manifest":
        return run_manifest(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
