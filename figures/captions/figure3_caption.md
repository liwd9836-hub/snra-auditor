# figure3. Synthetic benchmark

**Central claim.** In controlled synthetic and semi-synthetic settings, SNRA reduces false-positive spatial claims while retaining sensitivity to planted niche structure.

- **A** Simulated tissue with a known true niche.
- **B** Composition-matched null tissue.
- **C** Known-null positive-call rate under uncalibrated and strict SNRA certificates.
- **D** CRC audit-score separation before strict nuisance gating.
- **E** Scenario-level sensitivity and specificity.
- **F** Stress-test summary across null, confounded-null and planted scenarios.

**Legend draft.** Panels use a shared visual language: blue denotes uncalibrated or observed spatial signal, amber denotes matched negative controls, green denotes robust/certified claims, red denotes rejected or blocked claims, and purple denotes strict block/package/reproducibility layers. Error bars and intervals indicate confidence or null-range summaries where available. All source data tables are saved under `figures/source_data/`.

**Overclaim guardrail.** This figure supports SNRA as a post-hoc claim auditor. It does not establish de novo biological niche discovery, causal mechanism, or global superiority over all spatial analysis packages.
