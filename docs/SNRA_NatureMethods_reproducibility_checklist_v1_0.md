# SNRA Nature Methods reproducibility checklist v1.0

Date: 2026-05-09

## Release scope

Package: `snra-auditor`

Current version in this worktree: `0.1.0`

Version bump decision: do not bump to `0.1.1` yet because the SNRA-focused test suite fails in this worktree due to missing or renamed release fixtures.

## Dependency declaration

`pyproject.toml` declares:

```toml
dependencies = [
    "numpy>=1.23",
    "pandas>=1.5",
    "scipy>=1.10",
    "matplotlib>=3.7",
]
```

Rationale:

- `numpy`, `pandas`, and `scipy` are used by the installed SNRA package modules.
- `matplotlib` is required for publication figure generation via `scripts_build_snra_publication_figures_v0_1.py`.

## Exact commands

### Clean install

```powershell
cd D:\projects\suanfa_nm_reproducibility
python -m venv .venv_snra_nm_clean
.\.venv_snra_nm_clean\Scripts\python.exe -m pip install --upgrade pip
.\.venv_snra_nm_clean\Scripts\python.exe -m pip install .
.\.venv_snra_nm_clean\Scripts\python.exe -c "import snra; print(snra.__version__)"
```

Observed output summary:

```text
Successfully installed snra-auditor-0.1.0
0.1.0
```

### Help

```powershell
.\.venv_snra_nm_clean\Scripts\snra.exe --help
```

Observed output summary:

```text
usage: snra [-h] {validate,score,audit-card,demo,manifest} ...
SNRA v0.1 package prototype CLI
```

### Manifest

```powershell
.\.venv_snra_nm_clean\Scripts\snra.exe manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_nm_clean_core_manifest_v1_1
```

Observed status: pass, exit code `0`.

Observed manifest rows:

```text
input tonic_lineage_boundary_digest PASS
input crc_st_composition_aware_summary PASS
input wu_breast_composition_aware_summary PASS
input bcc_cosmx_fov_stress_summary FAIL
input g5_container_package_summary FAIL
```

### Strict manifest

```powershell
.\.venv_snra_nm_clean\Scripts\snra.exe manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_nm_clean_core_manifest_strict_v1_1 --fail-on-certificate-fail
```

Observed status: expected fail, exit code `1`.

Interpretation: strict mode fails because the manifest intentionally includes failed BCC CosMx and G5 certificates. This is correct for CI gating when failed certificates should block release.

### Tests

SNRA-focused tests:

```powershell
cd D:\projects\suanfa_nm_reproducibility
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
$env:NUMEXPR_NUM_THREADS="1"
.\.venv_snra_nm_clean\Scripts\python.exe -m unittest tests.test_snra_package_prototype_v0_1 tests.test_snra_regression_inputs_v0_1 tests.test_snra_manifest_cli_v0_1 tests.snra.test_snra_minimal
```

Observed status: fail.

Observed summary:

```text
Ran 14 tests
FAILED (failures=8, errors=1)
```

Failure classes:

- Missing script: `scripts_run_snra_demo_cli_v0_1.py`.
- Missing manifest fixture: `metadata\snra\snra_manifest_g5_package_v0_1.json`.
- Missing result fixture: `results\snra_phase0_10_v0_1\snra_phase_g5_package_benchmark_summary_v0_1.tsv`.
- Missing figure-ready TSVs:
  - `results\snra_phase0_10_v0_1\snra_figure_ready_benchmark_main_v0_1.tsv`
  - `results\snra_phase0_10_v0_1\snra_figure_ready_external_validation_v0_1.tsv`
  - `results\snra_phase0_10_v0_1\snra_figure_ready_package_negative_control_calibration_v0_1.tsv`
  - `results\snra_phase0_10_v0_1\snra_figure_ready_source_manifest_v0_1.tsv`

Full repository tests:

```powershell
cd D:\projects\suanfa_nm_reproducibility
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
$env:NUMEXPR_NUM_THREADS="1"
python -m unittest discover -s tests
```

Observed status: fail.

Observed summary:

```text
Ran 58 tests
FAILED (failures=8, errors=4)
```

Additional full-suite blocker outside the SNRA package fixture set:

- Missing PathoState atlas fixture: `processed\sc_state_library\sepsis_state_atlas_v0.2.json`.

### Figure generation

```powershell
cd D:\projects\suanfa_nm_reproducibility
.\.venv_snra_nm_clean\Scripts\python.exe scripts_build_snra_publication_figures_v0_1.py
```

Observed status: pass.

Observed output summary:

```text
Generated SNRA publication figure assets:
- reports/snra_publication_figures_v0_1/snra_publication_figure_source_stats_v0_1.tsv
- reports/snra_publication_figures_v0_1/snra_publication_figure_output_manifest_v0_1.tsv
- docs/SNRA_publication_figures_v0_1.md
- reports/snra_publication_figures_v0_1/figure1_snra_audit_contract_v0_2.png
- reports/snra_publication_figures_v0_1/figure1_snra_audit_contract_v0_2.svg
- reports/snra_publication_figures_v0_1/figure2_tonic_boundary_certification_v0_1.png
- reports/snra_publication_figures_v0_1/figure2_tonic_boundary_certification_v0_1.svg
- reports/snra_publication_figures_v0_1/figure3_crc_wu_spot_validation_v0_1.png
- reports/snra_publication_figures_v0_1/figure3_crc_wu_spot_validation_v0_1.svg
- reports/snra_publication_figures_v0_1/figure4_bcc_cosmx_fov_block_stress_v0_1.png
- reports/snra_publication_figures_v0_1/figure4_bcc_cosmx_fov_block_stress_v0_1.svg
- reports/snra_publication_figures_v0_1/figure5_package_negative_control_calibration_v0_1.png
- reports/snra_publication_figures_v0_1/figure5_package_negative_control_calibration_v0_1.svg
```

Note: figure generation rewrites figure/report artifacts. Run only when those outputs are intentionally in release scope.

## Release-readiness checklist

- Dependency declaration: pass after adding `matplotlib>=3.7`.
- Clean package install: pass.
- Installed `snra --help`: pass.
- Core evidence manifest default mode: pass.
- Core evidence manifest strict mode: expected exit code `1`.
- Figure generation: pass.
- SNRA-focused tests: fail due to missing or renamed fixtures.
- Full repository tests: fail due to the same SNRA fixture issues plus missing `processed\sc_state_library\sepsis_state_atlas_v0.2.json`.
- Version bump to `0.1.1`: deferred until tests pass.

## Evidence and claim guardrails

- PASS certificates support reproducible audit-card generation for submitted outputs.
- FAIL certificates are retained evidence that specific claims are downgraded or blocked under stress controls.
- SNRA results do not establish causal spatial signaling, de novo niche discovery, global package superiority, or exact spot-level deconvolution.

## Next concrete release action

Restore or intentionally replace the missing release fixtures listed above, update tests to the current fixture names if the files were renamed, rerun the SNRA-focused test command, and then bump `pyproject.toml` and `src\snra\__init__.py` to `0.1.1` if the suite passes.
