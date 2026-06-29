from pathlib import Path

import pytest

from motif_fraud.p_adic.strong_baselines import run_ieee_strong_baseline_audit


OFFICIAL_ROOT = Path(r"D:/motif-entropy-fraud/ieee-fraud-detection")


@pytest.mark.skipif(not OFFICIAL_ROOT.exists(), reason="official IEEE-CIS data not available")
def test_strong_baseline_audit_writes_tree_boosting_results_on_real_data(tmp_path):
    result = run_ieee_strong_baseline_audit(
        data_root=OFFICIAL_ROOT,
        output_root=tmp_path,
        max_rows=5000,
        iterations=8,
    )

    table = result["baseline_table"]
    assert not table.empty
    assert "p_adic_selected_hierarchy" in set(table["method"])
    assert any(table["method"].str.contains("lightgbm|catboost|xgboost"))
    assert result["artifacts"]["baseline_table"].exists()
    assert set(["method", "family", "auprc", "roc_auc", "claim_role"]).issubset(table.columns)
