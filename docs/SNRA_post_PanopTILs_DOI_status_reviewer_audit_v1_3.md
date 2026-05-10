# SNRA post-PanopTILs / DOI-status reviewer audit v1.3

Date: 2026-05-10

## Overall verdict

**Potentially suitable for an IF>10 benchmark-first methods/resource submission after release-account completion and final artwork review.**

This round improved the main scientific evidence gap by adding PanopTILs as an orthogonal H&E manual region+nuclei validation layer. It did not mint a DOI because the local environment lacks a configured public repository, release tag, GitHub CLI, and Zenodo/GitHub token.

## Evidence changes

| Area | Previous status | Current status | Interpretation |
|---|---|---|---|
| DOI | DOI-ready but not minted | Still not minted; exact account/tool blockers documented | Release-account blocker remains |
| Jackson/Fischer IMC | Metadata-only candidate | Downgraded after no explicit domain label found | Correctly prevents overclaim |
| PanopTILs | Orthogonal candidate | Partial manual-label adapter PASS; validation PASS in 56 ROIs, 1,415 objects, 4/4 controls | Strengthens manual cell-level pathology-region evidence |
| Release candidate | RC1 clean CI PASS | RC1 rebuilt with PanopTILs assets; clean CI v1.1 PASS | Reproducibility preserved |

## What PanopTILs supports

PanopTILs supports the claim that SNRA-style matched-control auditing can certify a manual region+nuclei geometry relationship in a pathologist-approved H&E dataset.

This is valuable because it closes part of the "manual region + cell-level label" gap that Schurch and TONIC did not fully solve.

## What PanopTILs does not support

PanopTILs is not spatial transcriptomics, imaging mass cytometry, MIBI, CODEX, CosMx, Xenium, or MERFISH. It does not validate molecular spatial-omics signal. It should be described as **orthogonal manual histopathology validation**, not as an additional molecular spatial-omics validation cohort.

## Remaining blockers

1. Public DOI remains unminted.
2. PanopTILs is currently a partial label subset because full Google Drive transfer was interrupted by Drive file resolution failures.
3. Figure 1-6 may still need final illustrator/journal layout adjustment.

## Updated readiness

- Method/statistical core: **84-87%**
- Software/reproducibility: **80-84%**
- Figures: **80-83%**
- Manuscript/evidence traceability: **84-86%**

Overall: **83-86% toward IF>10 methods/resource submission**.

## Editorial recommendation

Proceed with public release setup and external expert review. The manuscript should not wait indefinitely for full PanopTILs download if the partial validation remains explicitly labeled and source-backed, but expanding PanopTILs beyond the current 56 usable ROIs would further strengthen the revision package.
