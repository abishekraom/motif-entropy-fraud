import json
from pathlib import Path

from motif_fraud.p_adic.tree_scan_publication import (
    build_publication_summary,
    write_tree_scan_publication_artifacts,
)


def test_publication_summary_uses_all_frozen_real_dataset_gates():
    table = build_publication_summary()

    assert set(table["dataset"]) == {
        "official_ieee_cis",
        "cse_cic_ids2018_thursday",
        "cse_cic_ids2018_wednesday_2018_02_28",
    }
    assert table["fresh_preregistered"].sum() == 1
    assert not table["ci_excludes_zero"].any()
    assert set(table["claim_status"]) == {"diagnostic_only_failed_q1_tree_scan_gate"}


def test_publication_artifacts_are_source_backed_and_600dpi(tmp_path):
    artifacts = write_tree_scan_publication_artifacts(tmp_path)

    for key in ("summary_csv", "summary_md", "figure", "metadata"):
        assert Path(artifacts[key]).exists(), key
    assert artifacts["figure_dpi"][0] >= 600
    assert artifacts["figure_dpi"][1] >= 600
    metadata = json.loads(Path(artifacts["metadata"]).read_text(encoding="utf-8"))
    assert metadata["synthetic_empirical_data_used"] is False
    assert metadata["dataset_count"] == 3
    assert metadata["all_dataset_gates_passed"] is False
