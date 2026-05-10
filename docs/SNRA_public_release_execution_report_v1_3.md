# SNRA public release execution report v1.3

Date: 2026-05-10

## Public repository

- Repository: `https://github.com/liwd9836-hub/snra-auditor`
- Release: `https://github.com/liwd9836-hub/snra-auditor/releases/tag/v0.1.0`
- Branch: `main`
- Tag: `v0.1.0`

## Completed

- Prepared an isolated public release working directory from the clean release candidate archive.
- Replaced repository URL placeholders in release metadata:
  - `CITATION.cff`
  - `.zenodo.json`
  - `pyproject.toml`
  - `README.md`
- Initialized a clean Git repository for the public release content.
- Committed the release as `Release snra-auditor v0.1.0`.
- Pushed `main` to GitHub.
- Created and pushed annotated tag `v0.1.0`.
- Created GitHub Release `snra-auditor v0.1.0`.

## CI status

The first GitHub Actions run failed because Windows PowerShell wrote UTF-8 BOM bytes into `pyproject.toml`, causing Linux `pip` to fail TOML parsing.

Fix:

- rewrote `pyproject.toml`, `CITATION.cff`, `.zenodo.json`, and `README.md` as UTF-8 without BOM;
- committed `Fix release metadata encoding`;
- moved tag `v0.1.0` to the corrected commit;
- force-pushed the tag before DOI minting.

Latest GitHub Actions status:

- `SNRA tests`: success
- Python 3.10 smoke: success
- Python 3.11 smoke: success
- Manual workflow dispatch after DOI metadata update: success
- Latest checked run: `https://github.com/liwd9836-hub/snra-auditor/actions/runs/25630717933`

## Zenodo status

Zenodo DOI is **minted**.

After the repository was enabled in Zenodo-GitHub integration, the `v0.1.0` GitHub Release was recreated without moving the tag to trigger an archive event.

Zenodo record:

- Version DOI: `10.5281/zenodo.20110429`
- Version DOI URL: `https://doi.org/10.5281/zenodo.20110429`
- Concept DOI: `10.5281/zenodo.20110428`
- Zenodo record: `https://zenodo.org/records/20110429`

The DOI was verified through the Zenodo badge redirect and the Zenodo record API.

## Self-check

- No DOI was fabricated; the DOI was recorded only after Zenodo returned the archived record.
- The public release contains the clean SNRA package and manuscript-facing artifacts, not the dirty research workspace.
- CI is now passing on GitHub.
- `v0.1.0` tag was not moved after DOI minting, preserving the archived release state.
