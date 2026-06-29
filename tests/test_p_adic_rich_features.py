from pathlib import Path

import pytest

from motif_fraud.p_adic.rich_padic_features import run_ieee_rich_padic_feature_audit


OFFICIAL_ROOT = Path(r"D:/motif-entropy-fraud/ieee-fraud-detection")


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required for real-data rich p-adic feature audit.",
)
def test_rich_padic_feature_audit_checks_strong_baseline_augmentation_on_real_ieee_data():
    result = run_ieee_rich_padic_feature_audit(
        data_root=OFFICIAL_ROOT,
        output_root="outputs/test_p_adic_rich_features",
        max_rows=85000,
        iterations=25,
        methods=("lightgbm",),
    )

    table = result["claims"]
    metadata = result["metadata"]

    assert metadata["dataset"] == "official_ieee_cis_rich_padic_features"
    assert metadata["synthetic_data_used"] is False
    assert "lightgbm_compact_tabular" in set(table["method"])
    assert "lightgbm_compact_tabular_plus_rich_padic" in set(table["method"])
    assert table["claim_status"].notna().all()
    assert set(table["claim_status"]).issubset(
        {"q1_candidate_rich_padic_improves_strong_baseline", "diagnostic_only_failed_q1_rich_feature_gate"}
    )
    assert Path(result["artifacts"]["claims_table"]).exists()
    assert Path(result["artifacts"]["feature_manifest"]).exists()
    assert Path(result["artifacts"]["figure"]).exists()
    assert result["artifacts"]["figure_dpi"][0] >= 300
