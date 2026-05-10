# SNRA clean-environment CI report v1.0

Date: 2026-05-09
Status: PASS
Host Python: 3.11.15
Platform: Windows-10-10.0.19045-SP0
Temporary environment cleanup: removed

## Scope

This report tests the SNRA core package in a freshly created local virtual environment. It deliberately excludes heavy external package benchmarks such as Squidpy, CellCharter and SpaceFlow, which belong in the separate container benchmark environment.

## Commands

- `create_venv`: exit 0 in 5.617 s; log `results/snra_release_candidate_clean_ci_v1_1/logs/create_venv.log`
- `upgrade_pip`: exit 0 in 3.24 s; log `results/snra_release_candidate_clean_ci_v1_1/logs/upgrade_pip.log`
- `install_package`: exit 0 in 25.984 s; log `results/snra_release_candidate_clean_ci_v1_1/logs/install_package.log`
- `snra_help`: exit 0 in 0.89 s; log `results/snra_release_candidate_clean_ci_v1_1/logs/snra_help.log`
- `core_manifest`: exit 0 in 0.835 s; log `results/snra_release_candidate_clean_ci_v1_1/logs/core_manifest.log`
- `focused_unittest`: exit 0 in 6.693 s; log `results/snra_release_candidate_clean_ci_v1_1/logs/focused_unittest.log`
- `script_py_compile`: exit 0 in 0.089 s; log `results/snra_release_candidate_clean_ci_v1_1/logs/script_py_compile.log`

## Key outputs

- Command table: `results/snra_release_candidate_clean_ci_v1_1/clean_env_command_log.tsv`
- Core manifest summary: `results/snra_release_candidate_clean_ci_v1_1/core_manifest/snra_manifest_audit_summary_v0_1.tsv`; exists=True

## Interpretation

The core `snra-auditor` package installs and runs in a clean Python virtual environment. This closes the clean-env core CI blocker for the lightweight SNRA package surface.

## Self-check

- This test does not claim full reproducibility of optional external package benchmarks.
- Strict manifest failure is not tested here because scientifically failed certificates are expected in stress-control layers.
- The temporary environment is removed after execution to prevent local disk growth.
