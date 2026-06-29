from pathlib import Path

import pytest

from motif_fraud.p_adic.temporal_surveillance import run_ieee_temporal_surveillance_audit


OFFICIAL_ROOT = Path(r"D:/motif-entropy-fraud/ieee-fraud-detection")


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required for real-data temporal surveillance audit.",
)
def test_temporal_surveillance_audit_writes_q1_gate_artifacts_on_real_ieee_data():
    result = run_ieee_temporal_surveillance_audit(
        data_root=OFFICIAL_ROOT,
        output_root="outputs/test_p_adic_temporal_surveillance",
        max_rows=90000,
        n_blocks=24,
        bootstrap_samples=40,
    )

    claims = result["claims"]
    metadata = result["metadata"]

    assert metadata["dataset"] == "official_ieee_cis_temporal_surveillance"
    assert metadata["synthetic_data_used"] is False
    assert metadata["n_blocks"] == 24
    assert {"p_adic_multiresolution_temporal", "flat_tuple_rarity_temporal", "category_entropy_temporal"}.issubset(
        set(claims["method"])
    )
    assert "claim_status" in claims.columns
    assert claims["claim_status"].notna().all()
    assert set(claims["claim_status"]).issubset(
        {"q1_candidate_temporal_signal_passed_controls", "diagnostic_only_failed_q1_temporal_gate"}
    )
    assert Path(result["artifacts"]["claims_table"]).exists()
    assert Path(result["artifacts"]["block_features"]).exists()
    assert Path(result["artifacts"]["figure"]).exists()
    assert result["artifacts"]["figure_dpi"][0] >= 300
