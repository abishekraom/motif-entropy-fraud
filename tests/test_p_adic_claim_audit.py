from pathlib import Path

import pandas as pd

from motif_fraud.p_adic.claim_audit import write_ieee_spl_claim_audit


def test_write_ieee_spl_claim_audit_maps_claims_to_existing_artifacts(tmp_path):
    result = write_ieee_spl_claim_audit(output_path=tmp_path / "claims.csv")

    table = pd.read_csv(result)
    assert {"claim", "status", "evidence_artifact", "command", "paper_position"}.issubset(table.columns)
    assert "unsafe" in set(table["status"])
    assert "defensible" in set(table["status"])
    for path in table.loc[table["status"] == "defensible", "evidence_artifact"]:
        assert Path(path).exists()
