# SNRA package quickstart v1.1

Date: 2026-05-09

## Scope

This quickstart covers the SNRA package-facing reproducibility path for the `D:\projects\suanfa_nm_reproducibility` worktree. It is intended for package installation, command-line help, manifest audit reruns, strict-mode behavior, test execution, and publication figure regeneration.

SNRA is a post-hoc claim auditor. A failed certificate is a valid audit result when a submitted spatial claim does not survive the specified stress controls.

## Install

From the repository root:

```powershell
cd D:\projects\suanfa_nm_reproducibility
python -m pip install .
```

Editable developer install:

```powershell
cd D:\projects\suanfa_nm_reproducibility
python -m pip install -e .
```

Clean virtual environment install:

```powershell
cd D:\projects\suanfa_nm_reproducibility
python -m venv .venv_snra_nm_clean
.\.venv_snra_nm_clean\Scripts\python.exe -m pip install --upgrade pip
.\.venv_snra_nm_clean\Scripts\python.exe -m pip install .
.\.venv_snra_nm_clean\Scripts\python.exe -c "import snra; print(snra.__version__)"
```

Declared runtime dependencies in `pyproject.toml` are `numpy`, `pandas`, `scipy`, and `matplotlib`. `matplotlib` is required by `scripts_build_snra_publication_figures_v0_1.py`.

## Help

Installed console entry point:

```powershell
snra --help
```

Module form from the repository root:

```powershell
python -m src.snra.cli_v0_1 --help
```

Expected commands:

```text
validate, score, audit-card, demo, manifest
```

## Manifest audit

Run the package-facing core evidence manifest:

```powershell
cd D:\projects\suanfa_nm_reproducibility
snra manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_nm_core_manifest_v1_1
```

Expected default-mode exit code: `0`.

Expected input statuses:

```text
tonic_lineage_boundary_digest      PASS
crc_st_composition_aware_summary   PASS
wu_breast_composition_aware_summary PASS
bcc_cosmx_fov_stress_summary       FAIL
g5_container_package_summary       FAIL
```

## Strict manifest

Strict mode is for CI workflows where failed certificates should stop the run:

```powershell
cd D:\projects\suanfa_nm_reproducibility
snra manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_nm_core_manifest_strict_v1_1 --fail-on-certificate-fail
```

Expected strict-mode exit code for the current manifest: `1`, because BCC CosMx and G5 are retained as failed scientific audit outcomes.

## Tests

SNRA-focused package tests:

```powershell
cd D:\projects\suanfa_nm_reproducibility
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
$env:NUMEXPR_NUM_THREADS="1"
python -m unittest tests.test_snra_package_prototype_v0_1 tests.test_snra_regression_inputs_v0_1 tests.test_snra_manifest_cli_v0_1 tests.snra.test_snra_minimal
```

Full repository tests:

```powershell
cd D:\projects\suanfa_nm_reproducibility
python -m unittest discover -s tests
```

Observed status in this worktree on 2026-05-09: the SNRA-focused test command fails with `8` failures and `1` error because release test fixtures are missing or out of sync:

- `scripts_run_snra_demo_cli_v0_1.py` is absent.
- `metadata\snra\snra_manifest_g5_package_v0_1.json` is absent.
- `results\snra_phase0_10_v0_1\snra_phase_g5_package_benchmark_summary_v0_1.tsv` is absent.
- Four `snra_figure_ready_*_v0_1.tsv` files are absent.

These are packaging/fixture blockers, not evidence that the installed `snra` console entry point is broken.

## Figure generation

Regenerate publication figure assets:

```powershell
cd D:\projects\suanfa_nm_reproducibility
python scripts_build_snra_publication_figures_v0_1.py
```

Observed status in this worktree on 2026-05-09 after declaring `matplotlib`: passed. The script prints the generated PNG/SVG assets and source-stat manifests under `reports\snra_publication_figures_v0_1\` and updates `docs\SNRA_publication_figures_v0_1.md`.

Because figure generation rewrites manuscript-facing figure/report artifacts, do not run this command during documentation-only release edits unless those outputs are intentionally in scope.

## Version decision

Package version remains `0.1.0` in this pass. Although clean install, help, manifest, strict manifest, and figure generation pass, the SNRA-focused test suite does not pass in this worktree due to missing release fixtures. Bump to `0.1.1` after those fixture blockers are resolved and tests pass.
