# Jackson/Fischer 2020 breast IMC metadata-only adapter audit v1.0

Date: 2026-05-10

## Scope

This audit uses `imcdatasets::JacksonFischer_2020_BreastCancer(data_type='sce', cohort='Basel')` to inspect single-cell metadata only. Images and masks were not requested.

## Summary

- Cells: 285851
- Markers: 45
- `colData` columns: 75
- Coordinate candidate columns: 4
- Block/sample candidate columns: 17
- Image-level composition covariates: 4
- Domain/compartment candidate columns: 0
- Phenotype candidate columns: 2
- Decision: `DOWNGRADE_TO_PHENOTYPE_OR_STRESS_CANDIDATE`

## Output files

- `results/snra_jacksonfischer2020_imc_metadata_v1_0/experimenthub_record.tsv`
- `results/snra_jacksonfischer2020_imc_metadata_v1_0/coldata_schema.tsv`
- `results/snra_jacksonfischer2020_imc_metadata_v1_0/coldata_snra_schema_audit.tsv`
- `results/snra_jacksonfischer2020_imc_metadata_v1_0/coldata_candidate_columns.tsv`
- `metadata/snra/snra_jacksonfischer2020_imc_metadata_decision_v1_0.tsv`

## Interpretation

No explicit region/domain/compartment/margin/annotation metadata column was detected in the Basel SCE `colData`; under the pre-specified rule, this resource is downgraded to a phenotype/image-composition stress candidate unless additional source metadata provide manual tumor/stroma/domain labels.

## Self-check

- No images or masks were downloaded by this adapter.
- A domain claim is not made from cell-type or cluster columns.
- If only phenotype labels exist, the dataset cannot close the manual tumor-domain validation blocker.
