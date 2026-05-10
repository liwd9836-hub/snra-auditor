from __future__ import annotations

import csv
import hashlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RELEASE_ROOT = ROOT / "release"
RC_NAME = "snra-auditor-v0.1.0-rc1"
RC_DIR = RELEASE_ROOT / RC_NAME
DOC_PATH = ROOT / "docs" / "SNRA_release_candidate_rc1_report.md"
CHECKLIST_PATH = ROOT / "docs" / "SNRA_Zenodo_mint_checklist_v1_0.md"
MANIFEST_PATH = ROOT / "metadata" / "snra" / "snra_release_candidate_rc1_manifest.tsv"


ALLOW_FILES = [
    ".zenodo.json",
    "CITATION.cff",
    "LICENSE",
    "MANIFEST.in",
    "README.md",
    "environment_snra_submission.yml",
    "pyproject.toml",
    ".github/workflows/snra-tests.yml",
    "scripts_run_snra_clean_env_ci_v1_0.py",
    "scripts_run_snra_demo_cli_v0_1.py",
    "scripts_run_snra_submission_reproduction_v1_0.py",
    "scripts_profile_snra_runtime_memory_v1_0.py",
    "scripts_run_snra_synthetic_truth_benchmark_v1_0.py",
    "scripts_assemble_snra_final_figure_package_v1_0.py",
    "scripts_polish_snra_final_artwork_v1_1.py",
    "scripts_prepare_snra_release_candidate_v1_0.py",
    "scripts_download_panoptils_manual_labels_v1_0.py",
    "scripts_audit_panoptils_manual_subset_adapter_v1_0.py",
    "scripts_run_snra_panoptils_manual_validation_v1_0.py",
]

ALLOW_DIRS = [
    "src/snra",
    "examples/snra",
    "figures/final_nm_v1_0",
    "figures/final_nm_v1_1_artwork",
    "figures/source_data",
    "figures/captions",
    "figures/visual_qc",
    "notebooks",
]

ALLOW_METADATA = [
    "metadata/snra/snra_claim_control_taxonomy_v1_0.tsv",
    "metadata/snra/snra_claim_ledger_v0_9.tsv",
    "metadata/snra/snra_independent_cell_level_validation_candidates_v1_1.tsv",
    "metadata/snra/snra_jacksonfischer2020_imc_metadata_decision_v1_0.tsv",
    "metadata/snra/snra_manifest_core_evidence_v0_1.json",
    "metadata/snra/snra_manifest_g5_package_v0_1.json",
    "metadata/snra/snra_nature_methods_stage_revision_matrix_v1_0.tsv",
    "metadata/snra/snra_release_artifact_manifest_v1_0.tsv",
    "metadata/snra/snra_release_candidate_rc1_manifest.tsv",
    "metadata/snra/snra_verified_dataset_citation_table_v1_0.tsv",
]

ALLOW_DOCS = [
    "docs/SNRA_manuscript_draft_v0_6.md",
    "docs/SNRA_NatureMethods_submission_package_inventory_v1_0.md",
    "docs/SNRA_NatureMethods_post_repair_reviewer_audit_v1_2.md",
    "docs/SNRA_blocker_resolution_report_v1_0.md",
    "docs/SNRA_public_release_DOI_readiness_v1_0.md",
    "docs/SNRA_public_DOI_execution_status_v1_1.md",
    "docs/SNRA_clean_env_CI_report_v1_0.md",
    "docs/SNRA_release_candidate_clean_CI_report_v1_1.md",
    "docs/SNRA_release_candidate_clean_CI_report_v1_2.md",
    "docs/SNRA_release_candidate_rc1_finalization_report.md",
    "docs/SNRA_post_PanopTILs_DOI_status_reviewer_audit_v1_3.md",
    "docs/SNRA_NatureMethods_figure_production_polish_v1_0.md",
    "docs/SNRA_final_artwork_pass_v1_1.md",
    "docs/SNRA_independent_cell_level_validation_plan_v1_1.md",
    "docs/SNRA_jacksonfischer2020_imc_metadata_adapter_v1_0.md",
    "docs/SNRA_PanopTILs_manual_validation_v1_0.md",
    "docs/SNRA_synthetic_truth_benchmark_v1_0.md",
    "docs/SNRA_NatureMethods_reproducibility_checklist_v1_0.md",
    "docs/SNRA_package_quickstart_v1_1.md",
    "docs/SNRA_runtime_memory_report_v1_0.md",
]

ALLOW_RESULTS = [
    "results/snra_clean_env_ci_v1_0/clean_env_command_log.tsv",
    "results/snra_clean_env_ci_v1_0/core_manifest/snra_manifest_audit_summary_v0_1.tsv",
    "results/snra_release_candidate_clean_ci_v1_2/clean_env_command_log.tsv",
    "results/snra_synthetic_truth_benchmark_v1_0/benchmark_summary.tsv",
    "results/snra_phase0_10_v0_1/snra_crc_st_composition_aware_audit_summary_v0_1.tsv",
    "results/snra_phase0_10_v0_1/snra_figure_ready_benchmark_main_v0_1.tsv",
    "results/snra_phase0_10_v0_1/snra_figure_ready_external_validation_v0_1.tsv",
    "results/snra_phase0_10_v0_1/snra_figure_ready_package_negative_control_calibration_v0_1.tsv",
    "results/snra_phase0_10_v0_1/snra_figure_ready_source_manifest_v0_1.tsv",
    "results/snra_phase0_10_v0_1/snra_phase_g5_container_full_package_summary_v0_2.tsv",
    "results/snra_phase0_10_v0_1/snra_phase_g5_package_benchmark_summary_v0_1.tsv",
    "results/snra_phase0_10_v0_1/snra_plan_f_bcc_cosmx_morphology_composition_aware_audit_summary_v0_1.tsv",
    "results/snra_phase0_10_v0_1/snra_tonic_lineage_boundary_digest_v0_1.tsv",
    "results/snra_phase0_10_v0_1/snra_wu_breast_composition_aware_audit_summary_v0_1.tsv",
    "results/snra_jacksonfischer2020_imc_metadata_v1_0/metadata_audit_summary.tsv",
    "results/snra_jacksonfischer2020_imc_metadata_v1_0/coldata_snra_schema_audit.tsv",
    "results/snra_jacksonfischer2020_imc_metadata_v1_0/coldata_candidate_columns.tsv",
    "results/snra_panoptils_manual_adapter_v1_0/panoptils_manual_adapter_decision.tsv",
    "results/snra_panoptils_manual_adapter_v1_0/panoptils_manual_roi_audit.tsv",
    "results/snra_panoptils_manual_validation_v1_0/panoptils_manual_validation_summary.tsv",
    "results/snra_panoptils_manual_validation_v1_0/panoptils_manual_validation_controls.tsv",
    "results/snra_panoptils_manual_validation_v1_0/panoptils_manual_region_cell_counts.tsv",
]

TEST_FILES = [
    "tests/test_snra_package_prototype_v0_1.py",
    "tests/test_snra_regression_inputs_v0_1.py",
    "tests/test_snra_manifest_cli_v0_1.py",
    "tests/snra/test_snra_minimal.py",
]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def safe_rmtree(path: Path) -> None:
    resolved = path.resolve()
    root = ROOT.resolve()
    if resolved == root or root not in resolved.parents:
        raise RuntimeError(f"Refusing to delete outside workspace: {resolved}")
    if path.exists():
        shutil.rmtree(path)


def copy_file(relative: str, rows: list[dict[str, object]], role: str) -> None:
    src = ROOT / relative
    dst = RC_DIR / relative
    exists = src.exists()
    if exists:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    rows.append(
        {
            "role": role,
            "source_path": relative,
            "release_path": rel(dst),
            "copied": exists,
            "bytes": dst.stat().st_size if exists else 0,
            "sha256": sha256(dst) if exists and dst.is_file() else "",
        }
    )


def copy_dir(relative: str, rows: list[dict[str, object]], role: str) -> None:
    src = ROOT / relative
    if not src.exists():
        rows.append({"role": role, "source_path": relative, "release_path": "", "copied": False, "bytes": 0, "sha256": ""})
        return
    for path in sorted(src.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            copy_file(path.relative_to(ROOT).as_posix(), rows, role)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(rows: list[dict[str, object]]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=["role", "source_path", "release_path", "copied", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)
    copy_file(rel(MANIFEST_PATH), rows, "release_manifest")


def zip_release() -> Path:
    zip_path = RELEASE_ROOT / f"{RC_NAME}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(RC_DIR.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(RELEASE_ROOT).as_posix())
    return zip_path


def write_report(rows: list[dict[str, object]], zip_path: Path) -> None:
    copied = [r for r in rows if r["copied"]]
    missing = [r for r in rows if not r["copied"]]
    size_mb = sum(int(r["bytes"]) for r in copied) / (1024 * 1024)
    lines = [
        "# SNRA release candidate rc1 report",
        "",
        "Date: 2026-05-10",
        f"Release candidate directory: `{rel(RC_DIR)}`",
        f"Release archive: `{rel(zip_path)}`",
        f"Copied files: {len(copied)}",
        f"Approximate uncompressed copied size: {size_mb:.2f} MB",
        f"Missing allowlist files: {len(missing)}",
        "",
        "## Inclusion policy",
        "",
        "This release candidate is built by whitelist, not by copying the whole dirty research workspace. It keeps the package, focused tests, CI, examples, manuscript-facing docs, final figures, figure source data, SNRA metadata, and small summary results. It excludes raw data, large exploratory folders, temporary virtual environments, build artifacts, and unrelated historical projects.",
        "",
        "## Remaining release blocker",
        "",
        "The archive is a local release candidate. A public DOI still requires creating a public repository/release tag and archiving that tag through Zenodo or an equivalent service.",
    ]
    if missing:
        lines.extend(["", "## Missing allowlist files", ""])
        for row in missing:
            lines.append(f"- `{row['source_path']}`")
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_zenodo_checklist(zip_path: Path) -> None:
    lines = [
        "# SNRA Zenodo mint checklist v1.0",
        "",
        "Date: 2026-05-10",
        "",
        "## Preconditions",
        "",
        "- [ ] Create a clean public GitHub repository or public release branch.",
        "- [ ] Replace `REPLACE_WITH_PUBLIC_SNRA_REPOSITORY` in `pyproject.toml`, `CITATION.cff`, and `.zenodo.json`.",
        "- [ ] Push release candidate content from `release/snra-auditor-v0.1.0-rc1/`.",
        "- [ ] Confirm GitHub Actions core CI passes on the public repository.",
        "- [ ] Tag `snra-auditor-v0.1.0`.",
        "- [ ] Enable Zenodo-GitHub integration or upload the tagged archive manually.",
        "- [ ] Mint DOI and record it in Code Availability.",
        "- [ ] Re-run `python scripts_run_snra_clean_env_ci_v1_0.py` from a fresh public clone.",
        "",
        "## Local candidate",
        "",
        f"- Candidate directory: `release/{RC_NAME}/`",
        f"- Candidate archive: `{rel(zip_path)}`",
        f"- Candidate manifest: `{rel(MANIFEST_PATH)}`",
        "",
        "## Do not do",
        "",
        "- Do not upload raw unpublished data or temporary environments.",
        "- Do not claim a DOI before Zenodo or another archive mints it.",
        "- Do not replace failed audit layers with passing-only summaries.",
    ]
    CHECKLIST_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    RELEASE_ROOT.mkdir(parents=True, exist_ok=True)
    safe_rmtree(RC_DIR)
    RC_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for item in ALLOW_FILES:
        copy_file(item, rows, "root_or_script")
    for item in ALLOW_DOCS:
        copy_file(item, rows, "manuscript_doc")
    for item in ALLOW_RESULTS:
        copy_file(item, rows, "small_result_summary")
    for item in ALLOW_METADATA:
        copy_file(item, rows, "release_metadata")
    for item in TEST_FILES:
        copy_file(item, rows, "focused_test")
    for item in ALLOW_DIRS:
        copy_dir(item, rows, f"allow_dir:{item}")
    write_manifest(rows)
    zip_path = zip_release()
    write_report(rows, zip_path)
    write_zenodo_checklist(zip_path)
    print(f"release_dir\t{RC_DIR}")
    print(f"release_zip\t{zip_path}")
    print(f"manifest\t{MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
