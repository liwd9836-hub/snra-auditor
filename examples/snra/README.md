# SNRA example manifests

This directory contains package-facing SNRA manifest examples. They are templates for rerunning audit cards from existing result tables; they do not contain raw data and do not overwrite result inputs.

## Files

- `snra_manifest_g5_package_example_v0_1.json`: minimal one-input package benchmark manifest.
- `snra_manifest_core_evidence_example_v0_1.json`: current core evidence manifest with PASS and expected FAIL audit outcomes.

## Run examples

From the repository root:

```powershell
cd D:\projects\suanfa
python -m src.snra.cli_v0_1 manifest --manifest-json examples\snra\snra_manifest_g5_package_example_v0_1.json --out-dir reports\snra_manifest_g5_package_example_v0_1
```

```powershell
python -m src.snra.cli_v0_1 manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_manifest_core_evidence_example_v0_1
```

Strict mode is useful in CI when failed certificates should stop a workflow:

```powershell
python -m src.snra.cli_v0_1 manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_manifest_core_evidence_example_strict_v0_1 --fail-on-certificate-fail
```

For the current core evidence example, strict mode is expected to return exit code 1 because BCC CosMx and G5 are retained as failed audit outcomes.

## Manifest path rules

Relative paths are resolved first relative to the manifest file and then relative to the current working directory. These examples live in `examples/snra/`, so they use `../../results/...` paths to point to existing project result tables.

## Claim guardrails

Use these examples to reproduce audit cards and calibrate claims. Do not use them to claim CNS-level completion, global method superiority, causal tumor mechanisms, de novo niche discovery, or exact spot-level deconvolution.

