import pandas as pd

from motif_fraud.p_adic.ieee_pipeline import run_ieee_cis_p_adic_audit


def test_ieee_audit_uses_categorical_hierarchy_and_negative_controls(tmp_path):
    transaction = pd.DataFrame(
        {
            "TransactionID": range(12),
            "TransactionDT": range(12),
            "isFraud": [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
            "ProductCD": ["W", "W", "H", "W", "C", "W", "C", "H", "C", "W", "C", "H"],
            "card4": ["visa", "visa", "mastercard", "visa", "visa", "mastercard", "visa", "visa", "visa", "visa", "mastercard", "visa"],
            "card6": ["debit", "debit", "credit", "debit", "debit", "credit", "debit", "debit", "credit", "debit", "credit", "debit"],
            "P_emaildomain": ["gmail.com", "gmail.com", "yahoo.com", "gmail.com", "hotmail.com", "gmail.com", "fraud.test", "gmail.com", "fraud.test", "yahoo.com", "fraud.test", "gmail.com"],
        }
    )
    identity = pd.DataFrame({"TransactionID": range(12), "DeviceType": ["mobile", "desktop"] * 6})

    result = run_ieee_cis_p_adic_audit(
        transaction=transaction,
        identity=identity,
        output_root=tmp_path,
        train_fraction=0.6,
        random_control_seeds=(1, 2),
    )

    assert result["metadata"]["rows"] == 12
    claims = pd.read_csv(tmp_path / "tables" / "p_adic_ieee_cis_claims.csv")
    assert "p_adic_ieee_cis_categorical_frequency" in set(claims["method"])
    assert {"random_digit_map", "random_hierarchy", "flat_categorical"}.issubset(
        set(result["manifest"]["required_negative_controls_present"])
    )
