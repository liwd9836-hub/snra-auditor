# SNRA Auditor

Spatial Niche Robustness Auditor (SNRA) is a negative-control-aware audit framework for spatial omics claims. It is designed to certify, downgrade, or block post-hoc tumor-domain, boundary, niche, and package-output interpretations under matched null, composition, block, subsampling, and package-stress controls.

This repository also contains historical exploratory projects. The current release-facing package is `snra-auditor`.

## SNRA Package Prototype

SNRA, the Spatial Niche Robustness Auditor, is a package-facing prototype for reproducible post-hoc auditing of spatial niche, tumor-domain, boundary, and package-output claims. It validates submitted SNRA summary/detail tables, scores conservative claim certificates, writes markdown audit cards, and runs manifest-defined batches.

SNRA is an audit and claim-calibration framework. It is not a de novo spatial niche discovery method, not a causal tumor-immune or tumor-stroma mechanism engine, not a spot-level cell deconvolution method, and not evidence for global superiority over Squidpy, CellCharter, SpaceFlow, or other spatial packages.

The current package evidence baseline is:

- TONIC lineage boundary digest: PASS, score 0.880659.
- CRC ST composition-aware summary: PASS, score 1.000000.
- Wu breast composition-aware summary: PASS, score 1.000000.
- BCC CosMx FOV/block stress summary: FAIL, score 0.333333.
- G5 package summary: FAIL, score 0.606277.

These results support SNRA as a reproducible claim auditor that can certify, downgrade, or block spatial claims under matched stress controls. Failed certificates are valid audit outcomes and should remain visible.

### SNRA Installation

From the repository root:

```powershell
cd D:\projects\suanfa
python -m pip install -e .
```

Without editable installation, run the module form:

```powershell
python -m src.snra.cli_v0_1 --help
```

After editable installation, the console entry point is:

```powershell
snra --help
```

### SNRA CLI Examples

Validate a summary table:

```powershell
python -m src.snra.cli_v0_1 validate --input-tsv results\snra_phase0_10_v0_1\snra_phase_g5_container_full_package_summary_v0_2.tsv --table-kind summary
```

Score a conservative certificate:

```powershell
python -m src.snra.cli_v0_1 score --input-tsv results\snra_phase0_10_v0_1\snra_phase_g5_container_full_package_summary_v0_2.tsv --table-kind summary
```

Write an audit card:

```powershell
python -m src.snra.cli_v0_1 audit-card --input-tsv results\snra_phase0_10_v0_1\snra_phase_g5_container_full_package_summary_v0_2.tsv --table-kind summary --out-dir reports\snra_cli_v0_1_g5_summary --title "SNRA G5 container package benchmark summary audit"
```

Run the toy demo:

```powershell
python -m src.snra.cli_v0_1 demo --out-dir reports\snra_demo_cli_v0_1
```

Run a manifest-defined batch:

```powershell
python -m src.snra.cli_v0_1 manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_manifest_core_evidence_example_v0_1
```

Strict mode returns exit code 1 when a valid input receives a failed certificate:

```powershell
python -m src.snra.cli_v0_1 manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_manifest_core_evidence_example_strict_v0_1 --fail-on-certificate-fail
```

For the current core evidence manifest, strict mode is expected to fail because BCC CosMx and G5 are retained as failed stress-test/package-audit outcomes.

Run the Nature Methods reproducibility smoke commands:

```powershell
cd D:\projects\suanfa
python -m pip install .
snra --help
snra manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_nm_core_manifest_v1_1
snra manifest --manifest-json examples\snra\snra_manifest_core_evidence_example_v0_1.json --out-dir reports\snra_nm_core_manifest_strict_v1_1 --fail-on-certificate-fail
python -m unittest tests.test_snra_package_prototype_v0_1 tests.test_snra_regression_inputs_v0_1 tests.test_snra_manifest_cli_v0_1 tests.snra.test_snra_minimal
python scripts_build_snra_publication_figures_v0_1.py
```

Strict manifest mode is expected to return exit code 1 when the manifest includes scientifically failed certificates. Figure generation requires the local figure inputs documented in `docs/SNRA_NatureMethods_reproducibility_checklist_v1_0.md`.

### SNRA Manifest Examples

Example manifests live in `examples/snra/`:

- `snra_manifest_g5_package_example_v0_1.json`: one compact package-benchmark summary input.
- `snra_manifest_core_evidence_example_v0_1.json`: TONIC digest plus external/supporting summaries and expected failed audit layers.

Manifest paths are resolved first relative to the manifest file and then relative to the current working directory. The example manifests therefore use `../../results/...` paths from `examples/snra/`.

Each manifest input has:

- `id`: stable output subdirectory name.
- `path`: summary/detail TSV path.
- `table_kind`: `summary` or `detail`.
- `title`: audit-card title.

Manifest runs write one output directory per input plus `snra_manifest_audit_summary_v0_1.tsv`.

### SNRA Claim Guardrails

Allowed wording:

- SNRA provides reproducible audit cards for submitted spatial claim outputs.
- SNRA can certify, downgrade, or block claims under null, composition, block, subsampling, and package-level stress controls.
- A failed certificate is an interpretable audit result, not a software failure.
- Package benchmark summaries support claim calibration and endpoint auditing.

Blocked wording:

- CNS-level completion or final validation.
- Global superiority over Squidpy, CellCharter, SpaceFlow, or all spatial packages.
- Causal tumor-immune, tumor-stroma, or spatial-signaling mechanisms from descriptive audit results alone.
- De novo spatial niche discovery by SNRA.
- Exact spot-level cell deconvolution from marker composition proxies.

More details for this release-hardening pass are in `docs/SNRA_package_quickstart_v1_1.md` and `docs/SNRA_NatureMethods_reproducibility_checklist_v1_0.md`.

## Quick Test

```powershell
cd D:\projects\suanfa
python -m unittest discover -s tests
```

## Release and Citation Status

```powershell
$env:PYTHONPATH="D:\projects\suanfa\src"
snra --help
```

Archived software release:

- Version DOI: [10.5281/zenodo.20110429](https://doi.org/10.5281/zenodo.20110429)
- Concept DOI for all SNRA releases: [10.5281/zenodo.20110428](https://doi.org/10.5281/zenodo.20110428)
- GitHub release: [v0.1.0](https://github.com/liwd9836-hub/snra-auditor/releases/tag/v0.1.0)

Use the version DOI when citing this exact release.

See `docs/寮€鍙戣鏄巁绗竴鐗?md` for the Chinese workflow note.

