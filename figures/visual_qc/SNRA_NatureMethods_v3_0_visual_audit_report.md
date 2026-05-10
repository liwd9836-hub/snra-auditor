# SNRA Nature Methods v3.0 Visual Audit Report

Date: 2026-05-09

Manuscript:
**Spatial Niche Robustness Auditor calibrates spatial omics claims with matched negative controls**

## Overall Verdict

**Pass for manuscript-draft figure package.**

The v3.0 set is substantially stronger than v2.1 because it no longer only satisfies a panel-count requirement. It now has:

- six main figures;
- six panels per figure;
- one source-data table per panel;
- PDF/SVG/PNG outputs for every figure;
- caption drafts for every figure;
- visual QC rows for every figure;
- consistent claim-status color grammar;
- paired observed-vs-null visualization where relevant;
- explicit software/reproducibility figure.

This is still a programmatic draft. Final Nature Methods submission should undergo manual production finishing in Illustrator/Inkscape for exact panel alignment, font kerning, and final journal-size typography.

## Figure-Level Audit

| Figure | Verdict | Main Strength | Remaining Limitation |
|---|---|---|---|
| Figure 1 | PASS | Clear problem/workflow/claim-ledger architecture | Workflow schematic can still be polished manually |
| Figure 2 | PASS | Matched-control taxonomy and preserve/break semantics are explicit | Region/degree controls are schematic examples |
| Figure 3 | PASS | Adds synthetic false-positive calibration missing from v2.1 | Confounder-strength panel is simulated and must be described as synthetic |
| Figure 4 | PASS | Cross-platform real-data summary with package-calibration heatmap | Runtime/memory values are benchmark-style summaries and need final profiling if used as measured values |
| Figure 5 | PASS | Shows claim rescue and claim rejection in one biological case-study figure | Tissue map uses sampled TONIC cells; final panel should use selected representative FOV |
| Figure 6 | PASS | Adds CLI/API, schema, report, scaling, docs and reproducibility | Documentation panels are schematic and should be matched to final README/API state |

## Rejection Criteria Check

| Criterion | Status |
|---|---|
| Looks like default notebook plot | PASS: custom palette, typography, grid, layouts |
| Uses rainbow/over-saturated colors | PASS: restrained colorblind-aware palette |
| Only one simple panel | PASS: six panels per figure |
| Lacks visual hierarchy | PASS: figure titles, panel titles, consistent layout |
| No method schematic | PASS: Figures 1, 2 and 6 include schematics |
| Benchmark plots lack uncertainty/sample/statistical comparison | PASS with caveat: Figure 3/4/5 include thresholds/nulls; final runtime profiling still needed |
| Spatial plots lack tissue context | PASS with caveat: synthetic and sampled tissue maps included |
| Negative controls not paired with observed claim | PASS: observed/null pairing included in Figures 2-5 |
| Figure cannot stand independently | PASS: panel titles and captions support standalone interpretation |
| Not comparable to computational tool-paper figures | PASS for draft; final production polish still required |

## Required Follow-Up Before Submission

1. Replace schematic runtime/memory values with final measured profiler logs if the manuscript reports them quantitatively.
2. Select one representative TONIC FOV for the Figure 5 tissue map instead of using a generic sampled cell map.
3. Convert Figure 1 and Figure 6 schematic panels to manually aligned vector layouts for final production.
4. Perform sentence-to-panel traceability against the next manuscript draft.
5. Confirm that every simulated panel is clearly labeled as synthetic/semi-synthetic in Methods and caption.
