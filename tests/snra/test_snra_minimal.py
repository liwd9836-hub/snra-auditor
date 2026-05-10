from src.snra import AuditConfig, run_audit
from src.snra.contract import validate_dataset
from src.snra.simulation import simulate_spatial_dataset


def test_simulated_dataset_validates():
    dataset = simulate_spatial_dataset(n_samples=4, cells_per_sample=40, planted=True, seed=1)
    report = validate_dataset(dataset)
    assert report["ok"], report
    assert report["n_samples"] == 4


def test_audit_runs_on_small_simulation():
    dataset = simulate_spatial_dataset(n_samples=4, cells_per_sample=40, planted=True, seed=2)
    audit, phase = run_audit(dataset, AuditConfig(k=5, n_permutations=9, seed=3))
    assert len(audit) > 0
    assert "q_perm" in audit.columns
    assert "null_abundance_preserving_mean" in audit.columns
    assert "null_cell_type_preserving_p" in audit.columns
    assert "matched_control_gate" in audit.columns
    assert "snra_certified" in audit.columns
    assert "robustness_score" in audit.columns
    assert phase["n_samples"].iloc[0] == 4
