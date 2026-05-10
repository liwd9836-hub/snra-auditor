# SNRA release candidate rc1 finalization report

Date: 2026-05-10

## Summary

Release candidate `snra-auditor-v0.1.0-rc1` was rebuilt from a strict whitelist and then tested from inside the release candidate directory.

## Release package

- Candidate directory: `release/snra-auditor-v0.1.0-rc1/`
- Candidate archive: `release/snra-auditor-v0.1.0-rc1.zip`
- Archive size: 15.85 MB
- Manifest: `metadata/snra/snra_release_candidate_rc1_manifest.tsv`
- Missing allowlist files: 0

The first release-candidate build was rejected because it copied large cell-level metadata tables from `metadata/snra/`. The script was repaired to include only selected small ledgers, manifests and summary files. The current archive excludes raw data, temporary environments, large cell-level tables and unrelated historical exploratory projects.

## Release-candidate clean CI

The clean-env CI script was run from `release/snra-auditor-v0.1.0-rc1/`, not from the original workspace. It passed:

- create virtual environment: PASS
- install package from release candidate: PASS
- `snra --help`: PASS
- core manifest: PASS
- focused SNRA unit tests: PASS
- script compilation: PASS

Report copied to `docs/SNRA_release_candidate_clean_CI_report_v1_0.md`; command table copied to `results/snra_release_candidate_clean_ci_v1_0/clean_env_command_log.tsv`.

## Remaining DOI step

This is still a local release candidate. The public DOI remains unminted until this candidate is pushed to a public repository, tagged, archived and assigned a DOI by Zenodo or an equivalent archive.

## Self-check

- The public release archive was not built from the dirty workspace wholesale.
- Large raw or cell-level data tables were excluded.
- The release candidate was independently clean-env tested after packaging.
- DOI-pending language remains mandatory.

## 2026-05-10 v1.1 update

After adding the PanopTILs orthogonal manual-label validation layer, the release allowlist was updated to include:

- PanopTILs downloader/adapter/validation scripts;
- PanopTILs validation report;
- small PanopTILs adapter and validation summary tables;
- DOI execution-status report.

The release candidate was rebuilt and clean-env CI was rerun from inside `release/snra-auditor-v0.1.0-rc1/`.

Result: PASS.

Report: `docs/SNRA_release_candidate_clean_CI_report_v1_1.md`.
