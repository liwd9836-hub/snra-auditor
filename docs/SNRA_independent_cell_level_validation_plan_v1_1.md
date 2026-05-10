# SNRA independent positive cell-level validation plan v1.1

Date: 2026-05-09

## Verdict

The independent positive cell-level validation blocker is **partially mitigated but not fully closed**.

The strongest available supporting layer is now Schürch 2020 CRC CODEX cellular-neighborhood validation, which has already been adapted locally (`docs/SNRA_schurch2020_neighborhood_validation_v0_8.md`). It passes SNRA matched negative controls with a certified rate of 0.914286 and negative-control certification rate of 0.000. This is valuable because it is cell-level, public, cancer-focused and independent of TONIC.

However, it is not a full replacement for a manually reviewed tumor-domain or invasive-margin validation set, because the label is the source study's conserved cellular-neighborhood label rather than a pathologist-drawn anatomical tumor/stroma/invasive-margin mask.

## Evidence currently available

| Dataset | Status | What it supports | What it does not support |
|---|---:|---|---|
| TONIC MIBI | primary positive | cell-level lineage-stratified cancer/stroma boundary audit | broad cross-study generality alone |
| Schürch CRC CODEX | new supporting positive | independent cell-level cellular-neighborhood robustness | manual anatomical tumor-domain validation |
| Keren TNBC MIBI | supporting stress | cell-type spatial organization and subsampling sensitivity | niche/domain validation |
| CRC ST pathology | positive support | spot-level pathology-domain robustness | cell-level validation |
| Wu breast Visium | positive support | breast spot-level pathology support | cell-level validation |
| BCC CosMx | negative stress | block/FOV artifact rejection | positive validation |

## Public-source triage

Candidate details are recorded in `metadata/snra/snra_independent_cell_level_validation_candidates_v1_1.tsv`.

1. **Schürch CRC CODEX / CRC_FFPE-CODEX_CELLNEIGHS**  
   Public TCIA/Mendeley resource with cell-level phenotypes and tumor-invasive-front context. Local adapter already exists. Use as a supporting independent cell-level validation layer with explicit caveat.

2. **Jackson/Fischer breast cancer IMC through `imcdatasets`**  
   The metadata-only Basel SCE adapter was run. It loaded 285,851 cells and 45 markers, with `cell_x`/`cell_y`, image/patient block variables, image-level tumor/stroma composition covariates, and cluster/metacluster phenotype columns. It did **not** detect an explicit region/domain/compartment/margin/annotation column. Under the pre-specified rule, this candidate is downgraded to a phenotype/image-composition stress resource unless additional source metadata provide manual tumor-domain labels.

3. **PanopTILs breast histology**  
   Provides pathologist-approved manual region and nuclei labels across 151 patients, 1,709 ROIs and 814,886 nuclei. This is not spatial omics, but it could be used as orthogonal geometry/region-boundary validation if the manuscript clearly separates it from omics evidence.

## Actionable validation route

### Route 1: manuscript-now route

Promote Schürch CRC CODEX to a **supporting independent cell-level validation** section, but write the boundary exactly:

> Schürch CRC CODEX provides independent cell-level validation for source-study cellular-neighborhood robustness; it does not by itself prove SNRA generalizes to all pathologist-drawn tumor-domain masks.

This improves the paper without overclaiming.

### Route 2: completed Jackson/Fischer metadata route

The Jackson/Fischer IMC metadata route was executed in `scripts_audit_jacksonfischer2020_imc_metadata_adapter_v1_0.R`. The adapter intentionally requested the SCE object only and did not request images or masks. The result is `DOWNGRADE_TO_PHENOTYPE_OR_STRESS_CANDIDATE`, because tumor clinical variables and image-level composition percentages are not manual spatial domain labels.

### Route 3: orthogonal pathology route

If SNRA needs a manual region-label positive layer more than expression/protein biology, build a PanopTILs adapter. This would be framed as an orthogonal spatial-geometry audit, not a spatial-omics benchmark.

## Gate decision

For the current IF>10 methods/resource submission, do **not** wait indefinitely for a perfect second cell-level tumor-domain dataset. Instead:

- include Schürch as supporting positive cell-level evidence;
- keep TONIC as the primary cell-level boundary validation;
- keep CRC ST and Wu as spot-level independent supports;
- keep BCC as a visible failed stress test;
- list Jackson/Fischer as a completed negative metadata audit, and prioritize PanopTILs or another source with explicit pathologist-approved spatial region labels if a second manual cell/nucleus-level domain validation layer is still required.

## Self-check

- This plan does not hide that TONIC remains the main positive cell-level boundary layer.
- It does not promote cell-type labels to tumor-domain labels.
- It converts the blocker from "unaddressed" to "partially mitigated with a clear next adapter path".
