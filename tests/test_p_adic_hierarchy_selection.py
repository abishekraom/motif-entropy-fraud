import pandas as pd

from motif_fraud.p_adic.hierarchy_selection import select_hierarchy_order_temporal


def test_select_hierarchy_order_temporal_returns_order_and_validation_table():
    frame = pd.DataFrame(
        {
            "time": range(12),
            "label": [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1],
            "a": ["x", "x", "x", "x", "z", "x", "x", "z", "x", "z", "x", "z"],
            "b": ["m", "n"] * 6,
            "c": ["u"] * 12,
        }
    )

    result = select_hierarchy_order_temporal(
        frame,
        candidate_columns=("a", "b", "c"),
        time_column="time",
        label_column="label",
        train_fraction=0.5,
    )

    assert set(result.best_order) == {"a", "b", "c"}
    assert {"order", "auprc", "roc_auc"}.issubset(result.validation_results.columns)
    assert len(result.validation_results) == 6
