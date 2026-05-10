# SNRA public release and DOI readiness v1.0

Date: 2026-05-09

## Verdict

**DOI-ready, not DOI-complete.** The repository now has the metadata needed for a public software release, but a DOI cannot be claimed until a public repository is tagged and archived through Zenodo or an equivalent archival service.

## Completed release artifacts

| Item | Path | Status |
|---|---|---:|
| Package metadata | `pyproject.toml` | ready |
| BSD 3-Clause license | `LICENSE` | ready |
| Citation metadata | `CITATION.cff` | DOI pending |
| Zenodo archive metadata | `.zenodo.json` | DOI pending |
| Source distribution manifest | `MANIFEST.in` | ready |
| Core CI workflow | `.github/workflows/snra-tests.yml` | ready for public runner |
| Lightweight reproducibility environment | `environment_snra_submission.yml` | ready |
| Local clean-env CI report | `docs/SNRA_clean_env_CI_report_v1_0.md` | pass |

Full trace is in `metadata/snra/snra_release_artifact_manifest_v1_0.tsv`.

## Required public-release sequence

1. Create a clean public repository or release branch that excludes large raw data, temporary virtual environments, build folders and unrelated historical exploratory artifacts.
2. Replace all `REPLACE_WITH_PUBLIC_SNRA_REPOSITORY` placeholders in `pyproject.toml`, `CITATION.cff` and `.zenodo.json`.
3. Run the clean-env CI script from a fresh clone:
   `python scripts_run_snra_clean_env_ci_v1_0.py`.
4. Tag the release as `snra-auditor-v0.1.0`.
5. Archive the release on Zenodo or an equivalent platform.
6. Replace the manuscript Code Availability placeholder with the minted DOI.

## Guardrail

The current manuscript must say that the software is prepared for public release and local clean-env testing has passed. It must not state that a public DOI already exists.

## Self-check

- No DOI was fabricated.
- The clean-env report tests the lightweight SNRA package surface, not optional Squidpy/CellCharter/SpaceFlow containers.
- Release artifacts are separated from dataset citations and package benchmark evidence.
