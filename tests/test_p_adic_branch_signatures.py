from pathlib import Path

import pytest

from motif_fraud.p_adic.branch_signatures import run_ieee_branch_signature_audit


OFFICIAL_ROOT = Path(r"D:/motif-entropy-fraud/ieee-fraud-detection")


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required for real-data branch-signature audit.",
)
def test_branch_signature_audit_writes_train_only_interpretability_artifacts_on_real_ieee_data():
    result = run_ieee_branch_signature_audit(
        data_root=OFFICIAL_ROOT,
        output_root="outputs/test_p_adic_branch_signatures",
        max_rows=90000,
        min_train_support=50,
        top_k=20,
    )

    claims = result["claims"]
    metadata = result["metadata"]

    assert metadata["dataset"] == "official_ieee_cis_branch_signatures"
    assert metadata["synthetic_data_used"] is False
    assert metadata["selection_scope"] == "train_only"
    assert {"p_adic_prefix_branch_signatures", "flat_tuple_branch_signatures"}.issubset(set(claims["method"]))
    assert set(claims["claim_status"]).issubset(
        {"q1_candidate_interpretability_passed_controls", "diagnostic_only_failed_q1_interpretability_gate"}
    )
    assert Path(result["artifacts"]["claims_table"]).exists()
    assert Path(result["artifacts"]["selected_branches"]).exists()
    assert Path(result["artifacts"]["figure"]).exists()
    assert result["artifacts"]["figure_dpi"][0] >= 300
