# SNRA PanopTILs manual region+nuclei validation v1.0

Date: 2026-05-10

## Purpose

This validation layer addresses the remaining positive cell-level evidence gap: SNRA needed a truly manual tumor-domain / immune-compartment style resource rather than another package-derived or cell-type-only dataset.

PanopTILs is appropriate as an **orthogonal histopathology validation layer** because it provides pathologist-approved histologic region annotations and nuclei labels in the same breast-cancer ROIs. It is not a molecular spatial-omics dataset, so it cannot replace TONIC or Schurch as spatial-omics imaging validation.

## Source evidence

- PubMed PMID: `38942745`
- DOI: `10.1038/s41523-024-00663-1`
- Public site: `https://sites.google.com/view/panoptils/`
- Manual-label folder: `Manual regions & manual nuclei labels`
- Source description: 151 patients, 814,886 nuclei, region and cell-level annotation dataset.

## Download status

The Google Drive folder contains four classes: `csv/`, `masks/`, `rgbs/`, and `vis/`.

For SNRA, we deliberately prioritized label files:

- downloaded CSV labels: 60 files including `ALL_FOV_LOCATIONS.csv`
- downloaded matched mask PNGs: 55 files
- local label-layer size: approximately 1.4 MB after partial transfer
- failed transfer mode: several Google Drive files could not be resolved by `gdown`; a direct `drive.google.com/uc?export=download&id=...` fallback recovered most mask files for already-downloaded CSVs, but the full folder still requires resume/skip handling.

This is a **partial but usable manual-label subset**, not the full PanopTILs dataset.

## Adapter result

Script:

- `scripts_audit_panoptils_manual_subset_adapter_v1_0.py`

Outputs:

- `results/snra_panoptils_manual_adapter_v1_0/panoptils_manual_cell_region_table.tsv`
- `results/snra_panoptils_manual_adapter_v1_0/panoptils_manual_roi_audit.tsv`
- `results/snra_panoptils_manual_adapter_v1_0/panoptils_manual_adapter_decision.tsv`

Adapter summary:

- ROI CSV files parsed: 59
- annotated objects parsed: 1,745
- region masks available: yes
- region labels at cell centroids: Cancerous epithelium, Stroma, TILs region, Other, Junk/Debris, Whitespace/Empty
- decision: `PASS_MINIMAL_ORTHOGONAL_CELL_LEVEL_VALIDATION`

## Validation result

Script:

- `scripts_run_snra_panoptils_manual_validation_v1_0.py`

Outputs:

- `results/snra_panoptils_manual_validation_v1_0/panoptils_manual_validation_summary.tsv`
- `results/snra_panoptils_manual_validation_v1_0/panoptils_manual_validation_controls.tsv`
- `results/snra_panoptils_manual_validation_v1_0/panoptils_manual_region_cell_counts.tsv`

Validation summary:

- usable ROIs: 56
- usable annotated objects: 1,415
- observed manual region-cell match score: 0.823
- controls tested: global cell-label shuffle, within-ROI cell-label shuffle, global region-label shuffle, within-ROI region-label shuffle
- controls passed: 4/4
- decision: `PASS_ORTHOGONAL_MANUAL_REGION_CELL_VALIDATION`

## Allowed claim

PanopTILs supports an orthogonal, manually annotated H&E validation layer showing that SNRA-style matched-control logic can certify manual region+nuclei geometry beyond label shuffles.

## Blocked claim

PanopTILs must not be described as molecular spatial-omics validation. It does not provide multiplex protein/RNA signal. It strengthens the manual pathology-region evidence chain, but the main spatial-omics positive validation remains TONIC, with Schurch as supporting cell-level cellular-neighborhood validation.

## Self-check

- The validation uses manual label files, not RGB image content.
- The result is partial because the full Google Drive folder was not completely downloaded.
- Failed download attempts are retained rather than hidden.
- The manuscript should use conservative language: "orthogonal H&E manual-label validation" rather than "complete independent spatial-omics validation."
