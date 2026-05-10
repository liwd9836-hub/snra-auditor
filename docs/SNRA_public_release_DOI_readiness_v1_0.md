# SNRA public release and DOI readiness v1.1

Date: 2026-05-09

## Verdict

**DOI-complete.** The public GitHub release `v0.1.0` has been archived through Zenodo.

- Version DOI: `10.5281/zenodo.20110429`
- Concept DOI: `10.5281/zenodo.20110428`
- Zenodo record: `https://zenodo.org/records/20110429`

## Completed release artifacts

| Item | Path | Status |
|---|---|---:|
| Package metadata | `pyproject.toml` | ready |
| BSD 3-Clause license | `LICENSE` | ready |
| Citation metadata | `CITATION.cff` | DOI recorded |
| Zenodo archive metadata | `.zenodo.json` | DOI recorded |
| Source distribution manifest | `MANIFEST.in` | ready |
| Core CI workflow | `.github/workflows/snra-tests.yml` | ready for public runner |
| Lightweight reproducibility environment | `environment_snra_submission.yml` | ready |
| Local clean-env CI report | `docs/SNRA_clean_env_CI_report_v1_0.md` | pass |

Full trace is in `metadata/snra/snra_release_artifact_manifest_v1_0.tsv`.

## Completed public-release sequence

1. Created clean public repository `https://github.com/liwd9836-hub/snra-auditor`.
2. Replaced public repository placeholders.
3. Passed GitHub Actions smoke tests on Python 3.10 and 3.11 after fixing metadata encoding.
4. Tagged the release as `v0.1.0`.
5. Archived the release on Zenodo.
6. Recorded the minted DOI in manuscript-facing metadata.

## Guardrail

The manuscript may now cite the Zenodo software DOI. The DOI does not change the scientific evidence tier; biological validation limits still need to be stated separately.

## Self-check

- DOI was recorded only after Zenodo returned the archived record.
- The clean-env report tests the lightweight SNRA package surface, not optional Squidpy/CellCharter/SpaceFlow containers.
- Release artifacts are separated from dataset citations and package benchmark evidence.
