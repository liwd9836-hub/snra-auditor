# SNRA Nature Methods post-repair reviewer audit v1.2

Date: 2026-05-09  
Basis: `docs/SNRA_manuscript_draft_v0_6.md`, `docs/SNRA_blocker_resolution_report_v1_0.md`, `docs/SNRA_clean_env_CI_report_v1_0.md`, `docs/SNRA_NatureMethods_figure_production_polish_v1_0.md`, `metadata/snra/snra_independent_cell_level_validation_candidates_v1_1.tsv`.

## Overall verdict

**Potentially suitable after major revision; closer to IF>10 submission, still not Nature Methods submission-ready.**

This round closed or partially mitigated the four named blockers. The package is now DOI-ready, clean-env core CI passed, Figure 1-6 have a structurally complete final package plus a visual-hierarchy artwork pass, and Schürch CRC CODEX adds independent cell-level cellular-neighborhood support. Jackson/Fischer breast IMC was audited as a metadata-only candidate and downgraded because the Basel SCE `colData` lacked an explicit region/domain/compartment/margin/annotation label. The remaining hard limit is that the DOI has not been minted and the project still lacks a second pathologist-drawn anatomical tumor-domain validation layer.

## Improvements since v1.1

| Area | v1.1 state | v1.2 state | Reviewer interpretation |
|---|---|---|---|
| Release metadata | License/CI only; no DOI package | `CITATION.cff`, `.zenodo.json`, `MANIFEST.in`, release manifest and DOI-readiness doc added | DOI blocker reduced to an execution step, not metadata absence |
| Clean environment | Incomplete | Fresh venv install, CLI, core manifest, focused tests and script compilation passed | Core package reproducibility blocker closed |
| Figures | Development v3 figures | Final `figures/final_nm_v1_0/` package and `figures/final_nm_v1_1_artwork/` visual hierarchy pass | Ready for expert visual review; may still need illustrator polish |
| Cell-level validation | TONIC dominated | Schürch CRC CODEX added; Jackson/Fischer IMC downgraded after metadata audit | Generality improved, but manual-domain gap remains |
| Manuscript traceability | v0.6 pre-blocker update | v0.6 now includes Schürch, release/CI, Figure package and DOI-pending language | Better aligned with actual evidence |

## Remaining blockers

### 1. Public DOI remains unminted

The repository is prepared for archiving, but no DOI exists yet. The manuscript must retain DOI-pending language until a release is public and archived.

### 2. Manual positive cell-level tumor-domain validation remains incomplete

Schürch CRC CODEX is valuable independent cell-level evidence but not a pathologist-drawn anatomical domain mask. Jackson/Fischer breast IMC has now been downgraded for the manual-domain claim because metadata lacked explicit domain annotations. The next realistic target is PanopTILs or another pathology-region resource with manual labels.

### 3. Human artwork polish may still be required

The Figure 1-6 package is structurally complete, source-backed and six-panel compliant. The final Nature Methods artwork pass should still adjust exact panel sizing, typography and journal layout after text stabilizes.

## Updated readiness estimate

- Method/statistical core: **82-85%**
- Software/reproducibility: **78-82%**
- Figures: **80%**
- Manuscript traceability: **82%**

Overall: **80-83% toward IF>10 methods/resource submission.**

## Recommendation

Proceed to external expert review and public-release preparation. Do not claim Nature Methods readiness until the public DOI is minted and either Jackson/Fischer IMC provides a positive domain-like cell-level validation or the manuscript explicitly narrows the validation claim to TONIC + Schürch cellular-neighborhood + spot-level support.
