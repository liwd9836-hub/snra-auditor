# SNRA Nature Methods Submission Package Inventory v1.0

Date: 2026-05-09

## Main Manuscript Package

| Item | Path | Status |
|---|---|---:|
| Nature Methods manuscript draft | `docs/SNRA_NatureMethods_manuscript_v1_0.md` | ready for expert review |
| Manuscript self-check | `docs/SNRA_NatureMethods_manuscript_v1_0_self_check.md` | pass |
| Online Methods | `docs/SNRA_NatureMethods_OnlineMethods_v1_0.md` | pass |
| Supplementary Note | `docs/SNRA_NatureMethods_Supplementary_Note_v1_0.md` | pass |
| Final audit | `docs/SNRA_NatureMethods_final_audit_v1_0.md` | pass for external review |
| Pre-submission inquiry | `docs/SNRA_NatureMethods_presubmission_inquiry_v1_0.md` | draft ready |

## Figure Package

Final source-backed Figure 1-6 package:

| Item | Path | Status |
|---|---|---:|
| Final Figure 1-6 exports | `figures/final_nm_v1_0/` | pass structural QC |
| Final figure file manifest | `figures/visual_qc/snra_final_figure_file_manifest_v1_0.tsv` | pass |
| Final figure panel/source QC | `figures/visual_qc/snra_final_figure_panel_source_qc_v1_0.tsv` | pass |
| Figure production polish report | `docs/SNRA_NatureMethods_figure_production_polish_v1_0.md` | pass with human-artwork caveat |

| Figure | PNG | SVG |
|---|---|---|
| Figure 1 audit workflow | `reports/snra_nature_methods_figures_v1_0/figure1_snra_audit_contract_workflow_nm_v1_0.png` | `reports/snra_nature_methods_figures_v1_0/figure1_snra_audit_contract_workflow_nm_v1_0.svg` |
| Figure 2 TONIC confounding/rescue | `reports/snra_nature_methods_figures_v1_0/figure2_tonic_naive_confounding_lineage_rescue_nm_v1_0.png` | `reports/snra_nature_methods_figures_v1_0/figure2_tonic_naive_confounding_lineage_rescue_nm_v1_0.svg` |
| Figure 3 TONIC uncertainty | `reports/snra_nature_methods_figures_v1_0/figure3_tonic_primary_validation_uncertainty_nm_v1_0.png` | `reports/snra_nature_methods_figures_v1_0/figure3_tonic_primary_validation_uncertainty_nm_v1_0.svg` |
| Figure 4 CRC/Wu spot validation | `reports/snra_nature_methods_figures_v1_0/figure4_crc_wu_spot_validation_caveat_nm_v1_0.png` | `reports/snra_nature_methods_figures_v1_0/figure4_crc_wu_spot_validation_caveat_nm_v1_0.svg` |
| Figure 5 BCC FOV-block failure | `reports/snra_nature_methods_figures_v1_0/figure5_bcc_cosmx_fov_block_failure_nm_v1_0.png` | `reports/snra_nature_methods_figures_v1_0/figure5_bcc_cosmx_fov_block_failure_nm_v1_0.svg` |
| Figure 6 package calibration | `reports/snra_nature_methods_figures_v1_0/figure6_package_endpoint_calibration_nm_v1_0.png` | `reports/snra_nature_methods_figures_v1_0/figure6_package_endpoint_calibration_nm_v1_0.svg` |

Source files:

- `scripts_build_snra_nature_methods_figures_v1_0.py`
- `reports/snra_nature_methods_figures_v1_0/snra_nature_methods_figure_source_stats_v1_0.tsv`
- `reports/snra_nature_methods_figures_v1_0/snra_nature_methods_figure_output_manifest_v1_0.tsv`
- `docs/SNRA_NatureMethods_figure_storyboard_v1_0.md`

## Supplementary Tables

| Table | Path | Rows |
|---|---|---:|
| Supplementary Table 1 dataset resources | `supplementary/Supplementary_Table_1_dataset_resources.tsv` | 5 |
| Supplementary Table 2 claim ledger | `supplementary/Supplementary_Table_2_claim_ledger.tsv` | 28 |
| Supplementary Table 3 uncertainty | `supplementary/Supplementary_Table_3_uncertainty.tsv` | 51 |
| Supplementary Table 4 package benchmark | `supplementary/Supplementary_Table_4_package_benchmark.tsv` | 6 |
| Supplementary Table 5 reproducibility commands | `supplementary/Supplementary_Table_5_reproducibility_commands.tsv` | 13 |

## Reproducibility Package

| Item | Path | Status |
|---|---|---:|
| Package metadata | `pyproject.toml` | updated |
| Citation metadata | `CITATION.cff` | DOI pending |
| Archive metadata | `.zenodo.json` | DOI pending |
| Source distribution manifest | `MANIFEST.in` | ready |
| README quickstart | `README.md` | updated |
| Package quickstart | `docs/SNRA_package_quickstart_v1_1.md` | pass |
| Reproducibility checklist | `docs/SNRA_NatureMethods_reproducibility_checklist_v1_0.md` | pass |
| Clean-env CI report | `docs/SNRA_clean_env_CI_report_v1_0.md` | pass |
| Release readiness report | `docs/SNRA_public_release_DOI_readiness_v1_0.md` | DOI ready, no DOI minted |
| Core manifest output | `reports/snra_nm_final_core_manifest_v1_0/` | pass |
| Clean-env core manifest output | `reports/snra_nm_clean_env_core_manifest_v1_0/` | pass |
| Gate matrix | `metadata/snra/snra_nature_methods_gate_matrix_v1_0.tsv` | pass for external review |

## Independent Cell-Level Validation Addendum

| Item | Path | Status |
|---|---|---:|
| Schürch CRC CODEX supporting validation | `docs/SNRA_schurch2020_neighborhood_validation_v0_8.md` | supporting positive; not manual domain |
| Candidate inventory | `metadata/snra/snra_independent_cell_level_validation_candidates_v1_1.tsv` | updated |
| Validation plan | `docs/SNRA_independent_cell_level_validation_plan_v1_1.md` | updated |

## Remaining Before Submission

- Public release tag/archive and DOI.
- Post-release clean install and manifest run from a fresh public clone.
- Optional human illustrator pass for exact journal-size artwork polish.
- Jackson/Fischer IMC or equivalent adapter if a true manual/domain-like cell-level label is available.
- External expert review of manuscript claim boundary and figure story.
