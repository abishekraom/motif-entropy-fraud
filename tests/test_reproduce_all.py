import json
from pathlib import Path

import pandas as pd

from motif_fraud.pipeline.reproduce_all import reproduce_all


def test_reproduce_all_writes_manifest_and_rebuild_tables(tmp_path):
    manifest = reproduce_all(output_root=tmp_path, sample_nodes=400, null_permutations=3, seed=11)

    manifest_path = tmp_path / "manifests" / "rebuild_manifest.json"
    assert manifest_path.exists()
    saved = json.loads(manifest_path.read_text())
    assert saved["phase"] == "q1_rebuild_initial_local_audit"
    assert saved["parameters"]["sample_nodes"] == 400

    expected = {
        "dataset_summary": tmp_path / "tables" / "table1_dataset_summary.csv",
        "simple_baselines": tmp_path / "tables" / "table2_simple_baselines.csv",
        "local_motif_null_results": tmp_path / "tables" / "table3_local_motif_null_results.csv",
        "claim_table": tmp_path / "tables" / "table4_claim_discipline.csv",
    }
    assert set(manifest["artifacts"]) == set(expected)
    for path in expected.values():
        assert path.exists()


def test_initial_local_audit_claim_table_keeps_negative_results_valid(tmp_path):
    reproduce_all(output_root=tmp_path, sample_nodes=350, null_permutations=2, seed=5)

    claims = pd.read_csv(tmp_path / "tables" / "table4_claim_discipline.csv")
    assert {"method", "paired_delta", "claim_status"}.issubset(claims.columns)
    assert set(claims["claim_status"]).issubset(
        {"negative_or_confounded", "diagnostic_or_insufficient_gain", "defensible_detector_gain"}
    )
    assert len(claims) >= 1
