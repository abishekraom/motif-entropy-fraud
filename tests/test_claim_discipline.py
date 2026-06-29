import pandas as pd

from motif_fraud.evaluation.claims import assign_claim_status, build_claim_table


def test_claim_status_requires_beating_best_simple_baseline_with_support():
    row = {
        "method_auc": 0.81,
        "best_simple_baseline_auc": 0.80,
        "paired_delta": 0.01,
        "paired_p_value": 0.40,
    }

    assert assign_claim_status(row) == "diagnostic_or_insufficient_gain"

    row["paired_delta"] = 0.04
    row["paired_p_value"] = 0.01
    assert assign_claim_status(row) == "defensible_detector_gain"


def test_claim_status_never_calls_smoke_sample_a_defensible_detector_gain():
    row = {
        "method_auc": 0.90,
        "best_simple_baseline_auc": 0.60,
        "paired_delta": 0.30,
        "paired_p_value": 0.001,
        "validation_scope": "single_dataset_smoke_sample",
    }

    assert assign_claim_status(row) == "diagnostic_or_insufficient_gain"


def test_build_claim_table_serializes_negative_results_as_valid_rows():
    rows = [
        {
            "dataset": "fixture",
            "task": "node_ranking",
            "method": "local_motif_null",
            "method_auc": 0.45,
            "best_simple_baseline": "degree",
            "best_simple_baseline_auc": 0.70,
            "paired_delta": -0.25,
            "paired_p_value": 0.99,
        }
    ]

    table = build_claim_table(rows)

    assert isinstance(table, pd.DataFrame)
    assert table.loc[0, "claim_status"] == "negative_or_confounded"
    assert table.loc[0, "paired_delta"] == -0.25
