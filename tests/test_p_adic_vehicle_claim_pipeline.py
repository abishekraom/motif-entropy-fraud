from pathlib import Path

import pytest

from motif_fraud.p_adic.vehicle_claim_pipeline import run_vehicle_claim_external_audit


VEHICLE_ROOT = Path(r"D:/motif-entropy-fraud/vehicle-claim-fraud-detection")


@pytest.mark.skipif(
    not (VEHICLE_ROOT / "fraud_oracle.csv").exists(),
    reason="official/reputed Kaggle vehicle-claim fraud CSV is required; no synthetic data",
)
def test_vehicle_claim_external_audit_uses_real_dataset_and_writes_claims(tmp_path):
    result = run_vehicle_claim_external_audit(data_root=VEHICLE_ROOT, output_root=tmp_path)

    claims = result["claims"]
    assert result["metadata"]["rows"] == 15420
    assert result["metadata"]["source"] == "Kaggle shivamb/vehicle-claim-fraud-detection; CC0-1.0; userSpecifiedSources=Oracle Databases"
    assert {"method", "auprc", "roc_auc", "claim_status"}.issubset(claims.columns)
    assert "p_adic_vehicle_selected_hierarchy" in set(claims["method"])
    assert result["artifacts"]["claims"].exists()
    assert result["artifacts"]["figure"].exists()
    assert result["figure_dpi"][0] >= 300
    assert result["figure_dpi"][1] >= 300
