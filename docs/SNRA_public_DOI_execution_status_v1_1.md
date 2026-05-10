# SNRA public DOI execution status v1.1

Date: 2026-05-10

## Requested action

Mint a public DOI for the `snra-auditor-v0.1.0-rc1` release candidate.

## Current local status

The release candidate is DOI-ready but not DOI-complete.

Completed locally:

- clean release candidate folder: `release/snra-auditor-v0.1.0-rc1/`
- clean release archive: `release/snra-auditor-v0.1.0-rc1.zip`
- release metadata: `CITATION.cff`, `.zenodo.json`, `MANIFEST.in`
- clean release-candidate CI: PASS
- Zenodo mint checklist: `docs/SNRA_Zenodo_mint_checklist_v1_0.md`

## Blocking facts detected

- `git remote -v` is empty; no public GitHub repository is configured.
- no GitHub upstream branch is configured.
- no release tag exists yet.
- `gh` is not installed in the current environment.
- no GitHub or Zenodo tokens were detected in environment variables:
  - `GITHUB_TOKEN`
  - `GH_TOKEN`
  - `ZENODO_TOKEN`
  - `ZENODO_ACCESS_TOKEN`
  - `ZENODO_SANDBOX_TOKEN`
- placeholder URLs remain in:
  - `CITATION.cff`
  - `.zenodo.json`
  - `README.md`
  - `pyproject.toml`
  - the mirrored files inside `release/snra-auditor-v0.1.0-rc1/`

## Decision

The DOI cannot be minted from the current local environment without a public repository destination or an authenticated Zenodo/GitHub release mechanism.

This is not a scientific blocker. It is a release-account blocker.

## Next executable steps

1. Create or choose the public repository, for example `https://github.com/<owner>/snra-auditor`.
2. Replace `REPLACE_WITH_PUBLIC_SNRA_REPOSITORY` in root and release-candidate metadata.
3. Add the public repository as `origin`.
4. Push the release candidate.
5. Create and push tag `v0.1.0`.
6. Enable Zenodo-GitHub integration or upload `release/snra-auditor-v0.1.0-rc1.zip` manually to Zenodo.
7. Insert the minted DOI in Code Availability and citation metadata.
8. Re-run clean-env CI from a fresh public clone.

## Manuscript language rule

Until the DOI exists, the manuscript must say "DOI pending" or "release candidate prepared for archiving"; it must not cite a fabricated DOI.
