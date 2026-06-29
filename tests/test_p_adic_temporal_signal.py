import pandas as pd

from motif_fraud.p_adic.temporal_signal import (
    block_bootstrap_mean_ci,
    make_time_block_table,
    recall_at_fixed_fpr,
)


def test_make_time_block_table_preserves_time_order_and_computes_block_rates():
    frame = pd.DataFrame(
        {
            "time": [10, 1, 2, 3, 4, 5],
            "y": [0, 0, 1, 0, 1, 1],
            "score": [0.1, 0.2, 0.8, 0.3, 0.9, 0.7],
        }
    )

    blocks = make_time_block_table(frame, time_column="time", label_column="y", score_column="score", n_blocks=3)

    assert blocks["block_start_time"].tolist() == [1, 3, 5]
    assert blocks["rows"].tolist() == [2, 2, 2]
    assert blocks["fraud_rate"].tolist() == [0.5, 0.5, 0.5]
    assert blocks["mean_score"].iloc[0] == 0.5


def test_recall_at_fixed_fpr_uses_normal_scores_as_threshold_reference():
    y = pd.Series([0, 0, 0, 1, 1])
    scores = pd.Series([0.1, 0.2, 0.3, 0.4, 0.5])

    result = recall_at_fixed_fpr(y, scores, max_fpr=1 / 3)

    assert result["threshold"] == 0.3
    assert result["recall"] == 1.0
    assert result["false_positive_rate"] <= 1 / 3


def test_block_bootstrap_mean_ci_is_reproducible_and_ordered():
    values = pd.Series([0.1, 0.2, 0.3, 0.4])

    ci1 = block_bootstrap_mean_ci(values, n_bootstrap=200, seed=13)
    ci2 = block_bootstrap_mean_ci(values, n_bootstrap=200, seed=13)

    assert ci1 == ci2
    assert ci1["lower"] <= ci1["mean"] <= ci1["upper"]
