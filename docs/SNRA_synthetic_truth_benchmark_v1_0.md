# SNRA synthetic truth benchmark v1.0

## Analysis contract

- Biological/statistical question: can the current SNRA audit layer control false positives under known null and nuisance structures while retaining sensitivity for planted spatial domains?
- Statistical unit: independent synthetic or semi-synthetic sample/slide (`sample_id`), not cell/spot.
- Positive truth: injected compact domain labels only in planted and semi-synthetic scenarios.
- Null truth: pure random labels, composition-driven labels, block-driven labels, and degree/density-driven labels are treated as no true spatial niche.
- Evidence class: synthetic/semi-synthetic statistical benchmark, not biological mechanism.

## Implementation

The benchmark uses `src.snra.run_audit` with deterministic seed 20260509, k=8, 59 permutations, alpha=0.10, and annotation-noise stress 0.05. Semi-synthetic scenarios reuse local coordinate geometry when available and inject truth labels; source biological labels are not treated as ground truth.

`observed_positive_rate` is a naive uncalibrated comparator: candidate labels with target-target edge enrichment >=0.50. Certification uses `snra_certified` when available: a row must pass the original CRC/conformal gate and also exceed every matched control family by per-control permutation p-value. This intentionally blocks labels whose spatial structure is explained by cell-type composition, block/FOV structure, or local density.

## Benchmark summary

| scenario                         | truth_status            |   n_units |   n_samples |   confounder_strength |   observed_positive_rate |   matched_null_positive_rate |   false_positive_rate |   sensitivity |   specificity |   certificate_rate |   mean_margin |   ci_low |   ci_high |
|:---------------------------------|:------------------------|----------:|------------:|----------------------:|-------------------------:|-----------------------------:|----------------------:|--------------:|--------------:|-------------------:|--------------:|---------:|----------:|
| synthetic_pure_null              | pure_null               |      1440 |           8 |                  0    |                    0     |                        0     |                     0 |       nan     |             1 |              0     |  -0.0135898   | 0        |         0 |
| synthetic_planted_domain         | positive                |      1440 |           8 |                  1    |                    1     |                        1     |                     0 |         1     |           nan |              1     |   0.0793597   | 1        |         1 |
| synthetic_composition_confounder | confounded_null         |      1440 |           8 |                  0.85 |                    1     |                        0     |                     0 |       nan     |             1 |              0     |  -2.77556e-17 | 0        |         0 |
| synthetic_block_artifact         | confounded_null         |      1440 |           8 |                  1    |                    1     |                        0     |                     0 |       nan     |             1 |              0     |  -4.85723e-17 | 0        |         0 |
| synthetic_degree_confounder      | confounded_null         |      1440 |           8 |                  1    |                    1     |                        0     |                     0 |       nan     |             1 |              0     |   3.46945e-17 | 0        |         0 |
| semi_synthetic_tonic_coordinates | semi_synthetic_positive |      1339 |           8 |                  1    |                    0.875 |                        0.875 |                     0 |         0.875 |           nan |              0.875 |   0.13755     | 0.621875 |         1 |
| semi_synthetic_crc_coordinates   | semi_synthetic_positive |      1440 |           8 |                  1    |                    1     |                        0.75  |                     0 |         0.75  |           nan |              0.75  |   0.141226    | 0.496875 |         1 |

## Manifest

| scenario                         | truth_status            | source                                                                                        |   n_units |   n_samples |     seed |   audit_alpha |   audit_k |   n_permutations | positive_niches               | proxy_note                                                                                                                                       |
|:---------------------------------|:------------------------|:----------------------------------------------------------------------------------------------|----------:|------------:|---------:|--------------:|----------:|-----------------:|:------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|
| synthetic_pure_null              | pure_null               | fully synthetic clustered coordinates with random labels                                      |      1440 |           8 | 20260510 |           0.1 |         8 |               59 |                               | SNRA package audit; margins are score_obs minus maximum matched-null mean.                                                                       |
| synthetic_planted_domain         | positive                | fully synthetic coordinates with a planted compact domain                                     |      1440 |           8 | 20260511 |           0.1 |         8 |               59 | planted_domain                | SNRA package audit; planted_domain rows are the positive truth set.                                                                              |
| synthetic_composition_confounder | confounded_null         | fully synthetic coordinates where candidate labels track spatially clustered cell composition |      1440 |           8 | 20260512 |           0.1 |         8 |               59 |                               | Composition confounding is represented by cell-type driven labels; strict SNRA certification should be blocked by cell-type-preserving controls. |
| synthetic_block_artifact         | confounded_null         | fully synthetic uniform coordinates with labels tied to acquisition-like left/right FOV block |      1440 |           8 | 20260513 |           0.1 |         8 |               59 |                               | Block artifact is tested with block-preserving and celltype-block preserving controls in the matched-null ladder.                                |
| synthetic_degree_confounder      | confounded_null         | fully synthetic nonuniform point density with labels tied to local density/degree proxy       |      1440 |           8 | 20260514 |           0.1 |         8 |               59 |                               | Degree confounding is tested with degree- and local-density-preserving controls in the matched-null ladder.                                      |
| semi_synthetic_tonic_coordinates | semi_synthetic_positive | local TONIC SBIAD1288 segmented-cell coordinates with injected central-domain labels          |      1339 |           8 | 20260515 |           0.1 |         8 |               59 | semi_synthetic_planted_domain | Real coordinates are reused, but the truth labels are injected; this is not validation of source biological annotations.                         |
| semi_synthetic_crc_coordinates   | semi_synthetic_positive | local CRC Visium spot coordinates with injected central-domain labels                         |      1440 |           8 | 20260516 |           0.1 |         8 |               59 | semi_synthetic_planted_domain | Real coordinates are reused, but the truth labels are injected; this is not validation of source biological annotations.                         |

## Gate decision

- Gate: PASS
- Pure-null matched-control false-positive rate: 0.000
- Planted-domain sensitivity: 1.000

Stop-rule note: if confounded-null false positives exceed 0.10, the Nature Methods article path should not overstate confounder control until the method adds the missing matched null/residualization layer.