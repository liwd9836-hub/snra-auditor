# SNRA blocker resolution report v1.0

Date: 2026-05-09

## Scope

This report addresses the four blockers named for the SNRA IF>10 / Nature Methods-style tool manuscript:

1. public release DOI;
2. complete clean-environment CI;
3. final Figure 1-6 production polish;
4. stronger independent positive cell-level validation.

## Blocker status

| Blocker | Status after this round | Evidence | Remaining limitation |
|---|---:|---|---|
| Public release DOI | DOI-ready, not DOI-complete | `CITATION.cff`, `.zenodo.json`, `MANIFEST.in`, `metadata/snra/snra_release_artifact_manifest_v1_0.tsv`, `docs/SNRA_public_release_DOI_readiness_v1_0.md` | A DOI cannot be claimed until a public repository is tagged and archived. Placeholder URLs remain intentionally visible. |
| Clean-env CI | PASS for core SNRA package | `docs/SNRA_clean_env_CI_report_v1_0.md`, `results/snra_clean_env_ci_v1_0/clean_env_command_log.tsv` | Optional Squidpy/CellCharter/SpaceFlow package benchmark remains a separate container layer. |
| Figure 1-6 production polish | Structural production package PASS | `figures/final_nm_v1_0/`, `figures/visual_qc/snra_final_figure_file_manifest_v1_0.tsv`, `figures/visual_qc/snra_final_figure_panel_source_qc_v1_0.tsv`, `docs/SNRA_NatureMethods_figure_production_polish_v1_0.md` | Human illustrator/journal-size adjustment may still be needed after final acceptance of text. |
| Independent positive cell-level validation | Partially mitigated | `docs/SNRA_schurch2020_neighborhood_validation_v0_8.md`, `metadata/snra/snra_independent_cell_level_validation_candidates_v1_1.tsv`, `docs/SNRA_independent_cell_level_validation_plan_v1_1.md`, `docs/SNRA_jacksonfischer2020_imc_metadata_adapter_v1_0.md` | Schürch CRC CODEX supports cell-level cellular-neighborhood robustness, not pathologist-drawn anatomical tumor-domain validation. Jackson/Fischer IMC was downgraded after metadata audit because no explicit domain/compartment label was detected. |

## Updated manuscript consequence

`docs/SNRA_manuscript_draft_v0_6.md` now includes:

- a supporting Schürch CRC CODEX cell-level validation result and a Jackson/Fischer metadata-only downgrade decision;
- updated data-resource citations for Schürch, Keren, Jackson/Fischer and PanopTILs;
- clean-env CI traceability;
- release DOI-ready but DOI-pending Code Availability language;
- final Figure 1-6 package paths and QC reference.

## Current readiness estimate

- Statistical/methodological core: **82-85%** after synthetic truth repair and Schürch support.
- Software/reproducibility: **78-82%** after clean-env CI and release metadata; still capped by absent public DOI.
- Figures: **80%** after structural final package; still capped by possible human artwork polish.
- Manuscript/evidence traceability: **82%** after v0.6 update.

Overall: **approximately 80-83% toward an IF>10 benchmark-first methods/resource submission.** It is closer to external expert review, but not yet Nature Methods submission-ready because public DOI and one stronger manual-domain cell-level validation remain incomplete.

## Next defensible action

1. Create a clean public release branch/repository and replace placeholder URLs.
2. Archive release tag `snra-auditor-v0.1.0` to mint a DOI.
3. Run the clean-env CI script from a fresh clone after archiving.
4. Prioritize PanopTILs or another manual region-label resource for the remaining manual-domain validation gap.
5. Send the v0.6 manuscript and Figure 1-6 package for external expert review.

## Self-check

- No DOI was fabricated.
- Failed BCC/G5 results remain visible.
- Schürch is not overclaimed as pathologist-drawn tumor-domain evidence.
- Optional heavy package benchmarks are separated from core clean-env CI.
