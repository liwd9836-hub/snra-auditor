# Spatial Niche Robustness Auditor: negative-control-aware claim calibration for tumor-domain and boundary interpretations in spatial omics

Draft: v0.6  
Date: 2026-05-09  
Status: dataset-citation-integrated, uncertainty-integrated, clean-install-verified development draft  

## Claim Boundary

Spatial Niche Robustness Auditor (SNRA) is a post-hoc spatial claim auditor. It evaluates submitted labels, domains, boundaries, compartment masks, or package outputs and reports whether the associated interpretation survives predefined negative controls. SNRA is not a de novo niche discovery method, not a causal inference method, not an exact spatial deconvolution method, and not a replacement for upstream spatial analysis packages.

The manuscript-level contribution is claim calibration: SNRA certifies, downgrades, or blocks spatial claims under provenance-aware, composition-aware, block-aware, subsampling, and package-stress controls. Failed certificates are retained as scientific results because they prevent unsupported biological claims.

## Abstract

Spatial omics studies increasingly report tumor domains, niches, compartments, invasive margins, boundaries, and cell neighborhoods. Existing tools provide important upstream capabilities for spatial analysis, including scalable spatial workflows, niche discovery, graph embeddings, domain detection, and spatial deconvolution [1-9]. However, a positive spatial output is not automatically a calibrated biological claim, and spatial-method benchmarks show that outputs can depend on tool choice, dataset structure, and evaluation assumptions [10-14].

We developed SNRA as a post-hoc claim auditor for submitted spatial labels and package outputs. SNRA combines label-provenance recording, matched negative-control ladders, composition-aware controls, spatial-block and FOV-block controls, subsampling robustness, certificate scoring, audit-card generation, and claim-ledger reporting. In synthetic and semi-synthetic truth benchmarks, a strict SNRA certificate blocked composition-, block- and density-confounded null claims while retaining sensitivity to planted spatial domains. In real data, SNRA certified lineage-stratified TONIC breast MIBI boundary tasks, certified independent spot-level pathology-domain tasks in CRC ST and Wu breast Visium, downgraded a BCC CosMx morphology task because of FOV-block sensitivity, and identified endpoint instability in a containerized Squidpy, CellCharter, and SpaceFlow benchmark. These results support SNRA as a negative-control-aware auditor for spatial claim calibration. They do not establish causal tumor-immune mechanisms, de novo niche discovery, universal package superiority, or a complete CNS-level evidence chain.

## Introduction

Spatial omics methods have expanded the ability to map tissue domains, multicellular neighborhoods, and spatially organized molecular programs. Squidpy provides scalable analysis infrastructure for spatial graphs, image features, and neighborhood workflows [1]. CellCharter models spatial cell niches and tissue remodeling [2]. SpaceFlow learns spatially regularized embeddings for multicellular organization [3]. SpaGCN, BayesSpace, and GraphST support spatial-domain detection, clustering, integration, and deconvolution-oriented analyses [7-9]. RCTD, CARD, and STdeconvolve address spot-level mixture decomposition and reference-free deconvolution [4-6].

SNRA addresses a downstream problem. Once a spatial label, domain, boundary, or package endpoint exists, a manuscript still needs to decide what the output supports. A source-study compartment mask, a pathologist spot-domain label, a morphology label, a package-derived domain, and a manually curated boundary have different evidentiary meanings. A visually coherent pattern can reflect biological organization, but it can also reflect cell-type composition, sampling, segmentation, FOV structure, spatial blocking, or endpoint instability. Benchmarks of spatial clustering and spatially variable gene detection have shown that spatial outputs can vary across methods and datasets [10-13]. Simulation frameworks further motivate realistic stress tests and negative controls [14].

SNRA asks a narrow question: given a submitted spatial claim, does the claim survive the controls appropriate for that claim? The tool is intended to complement, not replace, upstream spatial analysis methods. Its output is an audit card and claim ledger that specify allowed claims, caveats, and blocked overclaims.

## Results

### Result 1. SNRA defines a claim-audit contract for submitted spatial labels

SNRA starts from a submitted label set or package output and applies an audit contract: input integrity checks, label provenance, spatial unit definition, matched negative controls, certificate scoring, audit-card generation, and claim-ledger reporting. This design prevents observed spatial patterns from being automatically upgraded into topology, niche, mechanism, or causal statements.

The claim ledger separates allowed, allowed-with-caveat, blocked, and superseded statements. The current ledger includes 10 allowed, 6 allowed-with-caveat, 10 blocked, and 2 superseded claim entries. The main allowed claim is that SNRA audits submitted spatial claims under predefined controls. Blocked claims include de novo niche discovery, causal mechanism proof, exact deconvolution from spot-level proxies, and global package superiority.

Traceability: `metadata/snra/snra_claim_ledger_v0_9.tsv`, `docs/SNRA_autonomous_development_contract_2026_05_09_v0_1.md`, and `docs/SNRA_IF10_master_development_plan_v1_0.md`.

### Result 2. Synthetic and semi-synthetic truth benchmarks support strict matched-control certification

A first synthetic truth benchmark exposed a fatal blocker in the earlier certificate logic: pure random labels were controlled, but labels driven by cell-type composition, FOV-like block structure, or local density could still be certified. We therefore separated the older conformal component (`crc_certified`) from the final strict certificate (`snra_certified`). The strict certificate requires the original conformal gate and a matched-control gate in which the observed score must exceed every relevant nuisance-preserving null family.

After this repair, synthetic pure-null false-positive rate was 0.000, and composition-confounded, block-artifact, and degree-confounded null false-positive rates were all 0.000. Sensitivity was retained for planted spatial domains: 1.000 in fully synthetic planted-domain data, 0.875 in TONIC-coordinate semi-synthetic planted domains, and 0.750 in CRC-coordinate semi-synthetic planted domains. The semi-synthetic analyses reuse real coordinate geometry but inject labels; they are statistical benchmarks, not biological validation of the source annotations.

Traceability: `scripts_run_snra_synthetic_truth_benchmark_v1_0.py`, `results/snra_synthetic_truth_benchmark_v1_0/benchmark_summary.tsv`, `docs/SNRA_synthetic_truth_benchmark_v1_0.md`, and `docs/SNRA_autonomous_major_revision_round1_execution_report_2026_05_09.md`.

### Result 3. TONIC four-compartment labels expose composition-confounded topology language

The original TONIC four-compartment tumor/stroma task was useful as a confounding diagnosis but was blocked as a main topology-beyond-composition claim. At cap500, the observed CRC-certified rate was 0.912, while broad phenotype-preserving shuffling retained 0.592. At cap1000, the observed CRC-certified rate was 0.902, while broad phenotype-preserving shuffling retained 0.722. These retained shuffle rates were too high to support an unqualified topology-beyond-composition interpretation.

This is a central example of SNRA's purpose: an observed spatial pattern is not discarded, but its allowed claim is downgraded to a confounding diagnosis.

Traceability: `results/snra_phase0_10_v0_1/snra_tonic_official_phenotype_composition_controls_summary_v1_1.tsv`; claim ledger `CLM003`.

### Result 4. TONIC lineage-stratified boundary tasks provide the primary positive validation layer

After restructuring TONIC into lineage-stratified boundary tasks, SNRA certified cancer core/border and non-cancer stroma core/border claims under the tested controls. For cancer cells, certificate rates were 0.817 (95% CI 0.779-0.850) at cap250 and 0.885 (95% CI 0.852-0.911) at cap500. For non-cancer or stromal-like cells, certificate rates were 0.913 (95% CI 0.885-0.935) at cap250 and 0.908 (95% CI 0.879-0.930) at cap500. Matched within-sample and within-fine-type shuffle controls were 0 in all four boundary tasks, with upper 95% CI bounds below 0.009.

The dedicated TONIC digest had a manifest certificate score and pass rate of 0.880659, with 4 of 4 digest rows certified. This is the current primary validation layer for SNRA. The supported claim is lineage-framed boundary robustness under source-study and phenotype-preserving controls, not a causal tumor-stroma or tumor-immune mechanism.

Traceability: `results/snra_phase0_10_v0_1/snra_tonic_lineage_stratified_boundary_summary_v1_2.tsv`, `results/snra_phase0_10_v0_1/snra_tonic_lineage_boundary_digest_v0_1.tsv`, and `reports/snra_manifest_core_evidence_v0_1/tonic_lineage_boundary_digest/`.

### Result 5. CRC ST supports independent spot-level pathology-domain certification under coarse composition-aware controls

In colorectal cancer spatial transcriptomics, pathologist spot-domain labels remained certified after coarse composition-aware controls. The benchmark joined 14 of 14 samples, included 20,725 spots, and evaluated 56 audit label rows. The primary composition-aware certification rate was 1.000 (95% CI 0.936-1.000), the stringent block certification rate was 0.964 (95% CI 0.879-0.990), and the subsampling primary retention rate was 0.985. The core manifest summary had certificate score 1.000000 and pass rate 1.000000.

This provides independent spot-level support for SNRA's audit logic. The limitation is explicit: marker-derived composition scores are coarse spot-level controls, not RCTD-, CARD-, or STdeconvolve-like deconvolution [4-6].

Traceability: `results/snra_phase0_10_v0_1/snra_crc_st_composition_aware_audit_summary_v0_1.tsv`; manifest output in `reports/snra_manifest_core_evidence_v0_1/crc_st_composition_aware_summary/`; claim ledger `CLM011` and `CLM012`.

### Result 6. Wu breast Visium adds supporting breast spot-domain evidence

In Wu breast Visium data, spot pathological labels remained certified after coarse composition-aware controls. The benchmark joined 6 of 6 samples, included 15,599 spots, and evaluated 23 audit label rows. The primary composition-aware certification rate and stringent block certification rate were both 1.000 (95% CI 0.857-1.000), and the subsampling primary retention rate was 1.000. The core manifest summary had certificate score 1.000000 and pass rate 1.000000.

Wu breast provides supporting independent breast spot-domain evidence. It is not the main validation layer because it contains six samples and uses spot-level marker-proxy composition rather than cell-level phenotype-preserving controls.

Traceability: `results/snra_phase0_10_v0_1/snra_wu_breast_composition_aware_audit_summary_v0_1.tsv`; manifest output in `reports/snra_manifest_core_evidence_v0_1/wu_breast_composition_aware_summary/`; claim ledger `CLM014` and `CLM015`.

### Result 7. BCC CosMx reveals FOV-block dependence rather than definitive validation

In BCC CosMx, SNRA evaluated a cell-level morphology stress test containing 63,092 cells from 2 patients and 27 FOVs. Global patient-label shuffle and within-celltype shuffle controls passed 6 of 6 audit rows, but FOV-block label shuffle passed only 2 of 6 rows. The FOV-block-sensitive composition-aware certified rate was 0.333 (95% CI 0.097-0.700). The core manifest marked this input as FAIL, with certificate score 0.333333 and pass rate 0.333333.

SNRA therefore downgrades the BCC morphology claim rather than forcing certification. This is a useful negative stress test because it exposes FOV-block dependence, but it does not complete independent cell-level tumor-domain validation.

Traceability: `results/snra_phase0_10_v0_1/snra_plan_f_bcc_cosmx_morphology_composition_aware_audit_summary_v0_1.tsv`; manifest output in `reports/snra_manifest_core_evidence_v0_1/bcc_cosmx_fov_stress_summary/`; claim ledger `CLM013`.

### Result 8. Schürch CRC CODEX provides supporting independent cell-level neighborhood validation

To reduce dependence on TONIC as the only positive cell-level evidence layer, we screened independent cancer multiplexed-imaging resources and reclassified Schürch CRC CODEX as the strongest current supporting validation layer [19]. The local SNRA adapter used a public Mendeley/TCIA-derived cell table with 104,891 cells across 140 regions and nine source-study cellular-neighborhood labels. SNRA certified 896 of 980 audit rows, for a certified rate of 0.914286, while composition-matched random and within-sample shuffle controls had certified rates of 0.000. Same-neighborhood retrieval also showed topology beyond composition: graph-topology-only AUC was 0.756, compared with 0.503 for composition only.

This result partially mitigates the independent positive cell-level validation blocker. Its boundary is important: the Schürch label is a source-study conserved cellular-neighborhood label from CRC invasive-front imaging, not a pathologist-drawn anatomical tumor/stroma/invasive-margin mask. A metadata-only audit of Jackson/Fischer breast IMC [20,21] loaded the Basel SCE object but detected no explicit region/domain/compartment/margin/annotation label in `colData`; the dataset is therefore downgraded to a phenotype/image-composition stress candidate unless additional source metadata provide manual domain labels. PanopTILs [22] was then added as an orthogonal H&E manual-label validation layer. A partial label-layer download currently contains 59 manual ROI CSVs, 55 matched region masks, and 1,745 annotated objects. In 56 usable ROIs, the manual region-cell match score was 0.823 and passed global cell-label, within-ROI cell-label, global region-label, and within-ROI region-label shuffle controls. This strengthens the manual pathology-region evidence chain, but it remains histopathology validation rather than molecular spatial-omics validation.

Traceability: `docs/SNRA_schurch2020_neighborhood_validation_v0_8.md`, `results/snra_phase0_10_v0_1/snra_schurch2020_summary_v0_8.tsv`, `docs/SNRA_jacksonfischer2020_imc_metadata_adapter_v1_0.md`, `metadata/snra/snra_jacksonfischer2020_imc_metadata_decision_v1_0.tsv`, `docs/SNRA_PanopTILs_manual_validation_v1_0.md`, `results/snra_panoptils_manual_validation_v1_0/panoptils_manual_validation_summary.tsv`, `metadata/snra/snra_independent_cell_level_validation_candidates_v1_1.tsv`, and `docs/SNRA_independent_cell_level_validation_plan_v1_1.md`.

### Result 9. Containerized package benchmark supports claim-calibration positioning

SNRA's fixed-container package benchmark evaluated Squidpy, CellCharter, and SpaceFlow endpoints on CRC ST and Wu breast tasks [1-3]. The benchmark produced 1,040 detail rows with 0 failed rows. In CRC ST, observed positive-call rates were 0.985 for Squidpy (95% CI 0.919-0.997), 0.970 for CellCharter (95% CI 0.896-0.992), and 0.714 for SpaceFlow (95% CI 0.454-0.883), while maximum negative-control positive-call rates were 0.955, 0.985, and 0.429, respectively. In Wu breast, observed positive-call rates were 0.964 for Squidpy (95% CI 0.823-0.994), 0.821 for CellCharter (95% CI 0.644-0.921), and 0.500 for SpaceFlow (95% CI 0.188-0.812), while maximum negative-control positive-call rates were 0.964, 0.929, and 0.167, respectively.

These are package endpoint positive-call rates under stress tests. They are not SNRA certificate rates and are not global package-quality rankings. The result supports the need for explicit claim calibration because selected package endpoints can remain positive under matched stress controls.

Traceability: `results/snra_phase0_10_v0_1/snra_phase_g5_container_full_package_summary_v0_2.tsv`, `results/snra_phase0_10_v0_1/snra_phase_g5_container_full_package_detail_v0_2.tsv`, `metadata/snra/snra_phase_g5_container_package_audit_v0_3.tsv`, and claim ledger `CLM025-CLM028`.

### Result 10. Package hardening establishes a manuscript-facing tool prototype

The package-hardening round converted SNRA from a script-only prototype into an installable, versioned package prototype. The package includes version metadata, a console entry point, CLI subcommands for `validate`, `score`, `audit-card`, `demo`, and `manifest`, example manifests, audit cards, and regression tests. Clean isolated install testing identified missing `pandas` and `scipy` dependency declarations; these were corrected in `pyproject.toml`. A later clean virtual-environment CI run installed the package from source, ran `snra --help`, reproduced the core evidence manifest, ran the focused SNRA regression tests, and compiled the submission reproduction/profiling/synthetic-benchmark scripts.

The CLI preserves the scientific meaning of failed certificates: valid inputs with failed certificates exit with code 0 by default, while strict mode can return code 1 with `--fail-on-certificate-fail`.

Traceability: `docs/SNRA_clean_isolated_install_test_v1_1.md`, `docs/SNRA_clean_env_CI_report_v1_0.md`, `results/snra_clean_env_ci_v1_0/clean_env_command_log.tsv`, `README.md`, `docs/SNRA_package_quickstart_v1_0.md`, `examples/snra/`, and `tests/`.

## Methods

### Data resources and label provenance

Data-source citations are recorded separately from method citations in `metadata/snra/snra_verified_dataset_citation_table_v1_0.tsv`. TONIC/S-BIAD1288 was used as the primary MIBI imaging validation layer, with source-study compartment masks and official cell phenotype information from the TONIC metastatic TNBC imaging study [15]. CRC ST used pathologist spot annotations and Visium data from the Valdeolivas colorectal cancer spatial transcriptomics resource [16]. Wu breast used Visium spatial transcriptomics data and spot pathological metadata from the Wu breast cancer atlas [17]. BCC CosMx used the Yerly/Andreatta basal-cell carcinoma CosMx SMI dataset and source metadata, including x/y coordinates, cell types, FOVs, morphology, and cell-level QC fields [18]. Schürch CRC CODEX was used as a supporting independent cell-level cellular-neighborhood validation layer [19]. Jackson/Fischer breast IMC was audited and downgraded for the manual-domain claim because no explicit domain-like column was detected in the Basel SCE metadata [20,21]. PanopTILs was added as an orthogonal H&E manual region+nuclei validation layer, with the explicit caveat that it validates manual pathology-region geometry rather than molecular spatial-omics signal [22].

Each label source is assigned a provenance class before interpretation: source-study compartment mask, lineage-stratified boundary label, pathologist spot-domain label, morphology/FOV-level label, package endpoint label, or marker-proxy composition label. Provenance determines allowed manuscript language.

### Negative-control ladder

SNRA uses claim-specific controls, including broad phenotype-preserving shuffles, fine-phenotype-preserving shuffles, composition-aware matching, sample/patient label shuffles, spatial-block controls, FOV-block controls, subsampling robustness, and package endpoint stress controls. A positive observed endpoint is interpreted only relative to the controls relevant to the stated claim.

The final v0.6 certificate is `snra_certified`. It is intentionally stricter than the internal `crc_certified` calibration component: a row must pass the conformal/CRC score gate and the matched-control gate. The matched-control gate uses per-control permutation p-values from global, abundance-preserving, block-preserving, degree-preserving, cell-type-preserving, local-density-preserving, and combined celltype-block preserving null families when the required metadata are available. This design downgrades claims that are spatially coherent but fully explained by nuisance structure.

### Certificate scoring and uncertainty

SNRA reports certificate/pass rates for audit tasks and endpoint positive-call rates for package comparators. For v0.6, Wilson 95% confidence intervals were added for key rates using audit label rows or package benchmark rows as the denominator. These intervals quantify uncertainty in audit-row rates; they should not be interpreted as independent cell- or spot-level Bernoulli trials. The uncertainty table is stored in `results/snra_uncertainty_v1_0/snra_key_certificate_uncertainty_v1_0.tsv`.

### Composition-aware controls

For cell-level data, composition-aware controls preserve relevant phenotype or cell-type structure. For spot-level data, SNRA uses marker-derived composition proxies only as coarse controls. These proxies are not deconvolution. RCTD, CARD, and STdeconvolve solve different mixture-estimation questions and are cited to define the boundary of SNRA's spot-level controls [4-6].

### Manifest and audit-card workflow

The package exposes `validate`, `score`, `audit-card`, `demo`, and `manifest` commands. The core evidence manifest includes TONIC lineage digest, CRC ST, Wu breast, BCC CosMx, and G5 package benchmark summaries. Manifest runs write per-input audit cards and a combined manifest summary. Failed BCC and G5 certificates remain visible rather than being suppressed.

### Package-comparator benchmark

The package benchmark uses selected Squidpy, CellCharter, and SpaceFlow endpoints. It evaluates endpoint behavior under observed and stress-control conditions. It does not compare universal tool quality, and SNRA does not replace upstream discovery or embedding methods. SpaceFlow is interpreted through an adapter-bounded embedding-label alignment comparator.

### Ligand-receptor and cell-cell communication scope

Ligand-receptor or cell-cell communication claims are explicitly excluded from SNRA v1. Such claims require sender/receiver expression, a ligand-receptor database, spatial adjacency, expression-matched decoy pairs, database-degree controls, sender/receiver abundance controls, and a dedicated truth or semi-synthetic benchmark. SNRA v1 can audit spatial label robustness but does not certify communication or causal signaling.

## How SNRA should not be used

SNRA should not be used to claim de novo discovery of tissue niches from raw spatial data. It should not be used as proof of causal tumor-immune or tumor-stroma mechanisms. It should not be used as exact cell-type deconvolution for mixed Visium spots. It should not be used to rank all spatial packages globally. It should not be used to rescue a spatial claim when the relevant FOV/block/composition controls fail. A failed SNRA certificate is an interpretable audit result, not a software failure.

## Discussion

SNRA reframes spatial-domain analysis as a claim-auditing problem. This is useful because spatial labels can be visually persuasive while still reflecting composition, FOV structure, block effects, segmentation, or endpoint instability. Instead of treating every positive map or package output as a biological claim, SNRA records what survives matched controls and what must be downgraded.

The strongest current evidence is TONIC lineage-stratified boundary certification. The original TONIC four-compartment result is not promoted as a main topology claim because broad phenotype-preserving controls remained high. Schürch CRC CODEX adds independent cell-level cellular-neighborhood support, CRC ST and Wu breast extend the evidence to independent spot-level pathology-domain settings, and BCC CosMx shows that cell-level data can still be vulnerable to FOV-block structure. The package benchmark supports SNRA's role as a downstream auditor rather than an upstream discovery package.

The current manuscript is suitable for continued development as an IF>10 benchmark-first methods/resource article. It is not a CNS-level discovery manuscript. A stronger independent manually reviewed cell-level tumor-domain validation dataset would improve the evidence chain, but the current contribution remains coherent if the manuscript keeps a conservative benchmark/resource framing.

## Limitations

SNRA audits submitted labels and outputs; it does not discover niches de novo. SNRA does not prove causal mechanisms. CRC ST and Wu breast are spot-level analyses with coarse marker-derived composition controls, not exact deconvolution. Schürch CRC CODEX is independent cell-level evidence but uses source-study cellular-neighborhood labels rather than pathologist-drawn anatomical tumor-domain masks. BCC CosMx is a block-sensitive stress-test failure, not definitive independent validation. SpaceFlow is evaluated through an adapter-bounded comparator. A local clean-env package CI run now passes, but public release DOI completion still requires repository archiving.

## Figure Plan

- **Figure 1:** SNRA audit contract and claim-ledger workflow. Final package: `figures/final_nm_v1_0/Figure1_SNRA_NatureMethods_final_v1_0.*`.
- **Figure 2:** Claim taxonomy and matched-control ladder.
- **Figure 3:** Synthetic and semi-synthetic truth benchmark using `snra_certified`.
- **Figure 4:** Real-data cross-platform benchmark across TONIC, CRC ST, Wu breast, and BCC CosMx.
- **Figure 5:** Biological case study showing claim rescue versus claim rejection.
- **Figure 6:** Software usability, runtime/memory, and reproducibility workflow. Structural production QC: `docs/SNRA_NatureMethods_figure_production_polish_v1_0.md`.

## Data Availability

TONIC imaging data are available through BioStudies BioImages S-BIAD1288 and associated SpaceCat analysis files [15]. CRC ST data and pathologist spot annotations are available through Zenodo 10.5281/zenodo.7760264 [16]. Wu breast Visium data are available through Zenodo 10.5281/zenodo.4739739 [17]. BCC CosMx data are available through Zenodo 10.5281/zenodo.14330691 [18]. Schürch CRC CODEX data are available through TCIA and Mendeley [19]. Jackson/Fischer breast IMC was screened through imcdatasets and Zenodo [20,21]. PanopTILs manual regions and manual nuclei labels are available from the public PanopTILs site and were used as an orthogonal H&E manual-label validation layer [22]. SNRA records the exact local resource roles in `metadata/snra/snra_verified_dataset_citation_table_v1_0.tsv`.

## Code Availability

The manuscript-facing package is `snra-auditor==0.1.0`. The core CLI exposes `validate`, `score`, `audit-card`, `demo`, and `manifest`. Example manifests are in `examples/snra/`. A submission environment file is provided in `environment_snra_submission.yml`; the quickstart notebook is `notebooks/SNRA_quickstart_tutorial_v1_0.ipynb`; runtime/memory profiling is documented in `docs/SNRA_runtime_memory_report_v1_0.md`. Clean install testing is documented in `docs/SNRA_clean_isolated_install_test_v1_1.md` and `docs/SNRA_clean_env_CI_report_v1_0.md`. Release metadata are prepared in `CITATION.cff`, `.zenodo.json`, `MANIFEST.in`, and `metadata/snra/snra_release_artifact_manifest_v1_0.tsv`. A DOI has not yet been minted; the public repository URL and DOI must be inserted only after release archiving. The main regression command is:

```powershell
python -m unittest tests.test_snra_package_prototype_v0_1 tests.test_snra_regression_inputs_v0_1 tests.test_snra_manifest_cli_v0_1
```

## References

1. Palla G, Spitzer H, Klein M, et al. Squidpy: a scalable framework for spatial omics analysis. Nature Methods. 2022. https://doi.org/10.1038/s41592-021-01358-2
2. Varrone M, et al. CellCharter reveals spatial cell niches associated with tissue remodeling and cell plasticity. Nature Genetics. 2024. https://doi.org/10.1038/s41588-023-01588-4
3. Ren H, et al. Identifying multicellular spatiotemporal organization of cells with SpaceFlow. Nature Communications. 2022. https://doi.org/10.1038/s41467-022-31739-w
4. Cable DM, et al. Robust decomposition of cell type mixtures in spatial transcriptomics. Nature Biotechnology. 2022. https://doi.org/10.1038/s41587-021-00830-w
5. Ma Y, Zhou X. Spatially informed cell-type deconvolution for spatial transcriptomics. Nature Biotechnology. 2022. https://doi.org/10.1038/s41587-022-01273-7
6. Miller BF, et al. Reference-free cell type deconvolution of multi-cellular pixel-resolution spatially resolved transcriptomics data. Nature Communications. 2022. https://doi.org/10.1038/s41467-022-30033-z
7. Hu J, et al. SpaGCN: integrating gene expression, spatial location and histology to identify spatial domains and spatially variable genes by graph convolutional network. Nature Methods. 2021. https://doi.org/10.1038/s41592-021-01255-8
8. Zhao E, et al. Spatial transcriptomics at subspot resolution with BayesSpace. Nature Biotechnology. 2021. https://doi.org/10.1038/s41587-021-00935-2
9. Long Y, et al. Spatially informed clustering, integration, and deconvolution of spatial transcriptomics with GraphST. Nature Communications. 2023. https://doi.org/10.1038/s41467-023-36796-3
10. Yuan Z, et al. Benchmarking spatial clustering methods with spatially resolved transcriptomics data. Nature Methods. 2024. https://doi.org/10.1038/s41592-024-02215-8
11. Charitakis N, et al. Disparities in spatially variable gene calling highlight the need for benchmarking spatial transcriptomics methods. Genome Biology. 2023. https://doi.org/10.1186/s13059-023-03045-1
12. Chen S, et al. Evaluating spatially variable gene detection methods for spatial transcriptomics data. Genome Biology. 2024. https://doi.org/10.1186/s13059-023-03145-y
13. Kang S, et al. Benchmarking computational methods for detecting spatial domains and domain-specific spatially variable genes from spatial transcriptomics data. Nucleic Acids Research. 2025. https://doi.org/10.1093/nar/gkaf303
14. Zhu J, et al. SRTsim: spatial pattern preserving simulations for spatially resolved transcriptomics. Genome Biology. 2023. https://doi.org/10.1186/s13059-023-02879-z
15. Greenwald NF, Nederlof I, Sowers C, et al. Temporal and spatial composition of the tumor microenvironment predicts response to immune checkpoint inhibition in metastatic TNBC. Nature Cancer. 2026. https://doi.org/10.1038/s43018-026-01114-5
16. Valdeolivas A, Amberg B, Giroud N, et al. Profiling the heterogeneity of colorectal cancer consensus molecular subtypes using spatial transcriptomics. npj Precision Oncology. 2024;8:10. https://doi.org/10.1038/s41698-023-00488-4
17. Wu SZ, Al-Eryani G, Roden DL, et al. A single-cell and spatially resolved atlas of human breast cancers. Nature Genetics. 2021;53:1334-1347. https://doi.org/10.1038/s41588-021-00911-1
18. Yerly L, Andreatta M, Carmona SJ, Kuonen F, et al. Single-cell spatial transcriptomics dataset of human basal-cell carcinoma. Zenodo. 2024; associated bioRxiv preprint. https://doi.org/10.5281/zenodo.14330691 and https://doi.org/10.1101/2024.05.31.596823
19. Schürch CM, Bhate SS, Barlow GL, et al. Coordinated Cellular Neighborhoods Orchestrate Antitumoral Immunity at the Colorectal Cancer Invasive Front. Cell. 2020. https://doi.org/10.1016/j.cell.2020.07.005
20. Jackson HW, Fischer JR, Zanotelli VRT, et al. The single-cell pathology landscape of breast cancer. Nature. 2020;578:615-620. https://doi.org/10.1038/s41586-019-1876-x
21. BodenmillerGroup imcdatasets documentation. JacksonFischer_2020_BreastCancer dataset; Zenodo raw data 10.5281/zenodo.3518284. https://rdrr.io/github/BodenmillerGroup/imcdatasets/man/JacksonFischer_2020_BreastCancer.html
22. PanopTILs dataset. Integrated region and cell-level annotation dataset for panoptic segmentation of the breast tumor microenvironment. https://sites.google.com/view/panoptils/

## Draft Self-Check

- Dataset-source citations and method citations are separated.
- Uncertainty intervals are included for key certificate and endpoint rates.
- Clean isolated install test is reflected in the software result and Code Availability.
- Release metadata are DOI-ready but DOI is not claimed.
- Schürch CRC CODEX is added as supporting cell-level evidence with an explicit label-provenance caveat.
- Figure 1 no longer uses placeholder language.
- No de novo niche discovery, causal mechanism, exact deconvolution, global package superiority, or CNS-level final completion claim is made.
