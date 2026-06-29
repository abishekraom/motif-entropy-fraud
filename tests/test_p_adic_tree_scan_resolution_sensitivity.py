import pandas as pd
import pytest

from motif_fraud.p_adic.tree_scan_resolution_sensitivity import (
    PRIMARY_CROSS_DATASET_STATUS,
    summarize_resolution_result,
)


def _result(delta: float, lower: float, upper: float, p_delta: float):
    common = {
        "best_proposed_method": "p_adic_conditional_tree_scan_llr",
        "best_control_method": "category_entropy_temporal",
        "best_proposed_auprc": 0.42,
        "best_control_auprc": 0.42 - delta,
        "delta_best_proposed_vs_best_control_auprc": delta,
        "bootstrap_delta_lower": lower,
        "bootstrap_delta_upper": upper,
        "bootstrap_p_delta_le_zero": p_delta,
    }
    return {
        "claims": pd.DataFrame(
            [
                {"method": "p_adic_tree_scan_llr", "auprc": 0.36, **common},
                {"method": "p_adic_conditional_tree_scan_llr", "auprc": 0.42, **common},
            ]
        )
    }


def test_secondary_resolution_failure_cannot_change_primary_status():
    row = summarize_resolution_result("dataset", 48, _result(-0.02, -0.08, 0.04, 0.7))

    assert row["sensitivity_status"] == "sensitivity_failed_superiority_gate"
    assert row["primary_resolution"] is False
    assert row["conditional_minus_raw_auprc"] == pytest.approx(0.06)
    assert row["primary_cross_dataset_status_unchanged"] == PRIMARY_CROSS_DATASET_STATUS


def test_secondary_resolution_apparent_pass_is_explicitly_nonconfirmatory():
    row = summarize_resolution_result("dataset", 192, _result(0.08, 0.01, 0.15, 0.02))

    assert row["sensitivity_status"] == "exploratory_pass_not_confirmatory"
    assert row["primary_cross_dataset_status_unchanged"] == PRIMARY_CROSS_DATASET_STATUS


def test_primary_resolution_is_rejected_from_secondary_runner(tmp_path):
    from motif_fraud.p_adic.tree_scan_resolution_sensitivity import (
        run_block_resolution_sensitivity,
    )

    with pytest.raises(ValueError, match="differ from 96"):
        run_block_resolution_sensitivity(
            tmp_path,
            datasets=("official_ieee_cis",),
            resolutions=(96,),
            bootstrap_samples=1,
        )
