# SNRA runtime and memory report v1.0

Date: 2026-05-09
Python: 3.11.15
Platform: Windows-10-10.0.19045-SP0

## Scope

This lightweight profile uses synthetic SNRA inputs and bundled core manifest summary tables. It measures Python wall time and `tracemalloc` peak allocations, not whole-process resident memory.

## Summary

- Profile tasks completed: 3/3.
- Maximum measured `tracemalloc` peak: 49.975 MB.
- Median measured task runtime: 0.026 s.

## Task Results

- `synthetic_audit_small`: status=ok, seconds=2.892715, peak=49.975343 MB
- `core_manifest_summary_read`: status=ok, seconds=0.002406, peak=0.096378 MB
- `core_manifest_cli_inprocess`: status=ok, seconds=0.026040, peak=0.331403 MB

## Outputs

- TSV: `results/snra_runtime_memory_v1_0/snra_runtime_memory_profile_v1_0.tsv`
- JSON: `results/snra_runtime_memory_v1_0/snra_runtime_memory_profile_v1_0.json`

## Caveats

This is a smoke-scale software profile for submission hardening. It is not a full benchmark of external spatial packages and does not measure GPU, Docker, or optional package behavior.
