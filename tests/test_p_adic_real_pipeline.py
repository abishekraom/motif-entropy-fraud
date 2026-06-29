import pandas as pd

from motif_fraud.p_adic.real_pipeline import run_creditcard_p_adic_audit


def test_creditcard_audit_writes_claims_manifest_and_600dpi_figure(tmp_path):
    frame = pd.DataFrame(
        {
            "Time": list(range(30)),
            "Amount": [1, 2, 3, 4, 5, 100, 110, 120, 130, 140] * 3,
            "Class": [0] * 20 + [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        }
    )
    result = run_creditcard_p_adic_audit(
        frame=frame,
        output_root=tmp_path,
        train_fraction=0.67,
        quantile_bins=3,
        random_control_seeds=(1, 2),
    )

    assert result["manifest"]["minimum_figure_dpi"] == 600
    assert (tmp_path / "tables" / "p_adic_creditcard_claims.csv").exists()
    assert (tmp_path / "figures" / "p_adic_creditcard_pr_curve.png").exists()
    claims = pd.read_csv(tmp_path / "tables" / "p_adic_creditcard_claims.csv")
    assert {"method", "auprc", "roc_auc", "claim_status"}.issubset(claims.columns)
    assert set(claims["claim_status"]).issubset(
        {"q1_candidate_passed_controls", "diagnostic_only_failed_q1_gate"}
    )
