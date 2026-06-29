from pathlib import Path

import pytest

from motif_fraud.p_adic.official_baselines import run_ieee_official_baseline_audit


OFFICIAL_ROOT = Path(r"D:/motif-entropy-fraud/ieee-fraud-detection")


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="official IEEE-CIS Kaggle files are required; synthetic data is forbidden for this test",
)
def test_official_baseline_audit_writes_research_grade_artifacts(tmp_path):
    result = run_ieee_official_baseline_audit(
        data_root=OFFICIAL_ROOT,
        p_adic_claims_path=Path("outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_claims.csv"),
        output_root=tmp_path,
        max_rows=25000,
    )

    table = result["baseline_table"]
    assert {"method", "family", "auprc", "roc_auc", "claim_role"}.issubset(table.columns)
    assert "p_adic_selected_hierarchy" in set(table["method"])
    assert "logistic_frequency_supervised" in set(table["method"])
    assert "isolation_forest_frequency_unsupervised" in set(table["method"])
    assert "logistic_frequency_plus_padic_signal" in set(table["method"])
    assert result["artifacts"]["baseline_table"].exists()
    assert result["artifacts"]["comparison_figure"].exists()
    assert result["figure_dpi"][0] >= 300
    assert result["figure_dpi"][1] >= 300
