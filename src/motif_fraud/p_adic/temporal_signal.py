"""Signal-processing metrics for temporal p-adic fraud scores."""

from __future__ import annotations

import numpy as np
import pandas as pd


def make_time_block_table(
    frame: pd.DataFrame,
    time_column: str,
    label_column: str,
    score_column: str,
    n_blocks: int = 48,
) -> pd.DataFrame:
    """Aggregate a transaction-level score into ordered temporal signal blocks."""
    if n_blocks < 1:
        raise ValueError("n_blocks must be positive")
    for column in (time_column, label_column, score_column):
        if column not in frame.columns:
            raise KeyError(f"Missing column: {column}")
    ordered = frame.sort_values(time_column, kind="mergesort").reset_index(drop=True)
    block_ids = np.floor(np.arange(len(ordered)) * n_blocks / len(ordered)).astype(int)
    block_ids = np.minimum(block_ids, n_blocks - 1)
    work = ordered.assign(block_id=block_ids)
    rows = []
    for block_id, group in work.groupby("block_id", sort=True):
        labels = group[label_column].astype(int)
        scores = group[score_column].astype(float)
        rows.append(
            {
                "block_id": int(block_id),
                "block_start_time": group[time_column].iloc[0],
                "block_end_time": group[time_column].iloc[-1],
                "rows": int(len(group)),
                "fraud_count": int(labels.sum()),
                "fraud_rate": float(labels.mean()),
                "mean_score": float(scores.mean()),
                "max_score": float(scores.max()),
            }
        )
    return pd.DataFrame(rows)


def recall_at_fixed_fpr(y_true: pd.Series, scores: pd.Series, max_fpr: float = 0.01) -> dict[str, float]:
    """Compute recall using the highest threshold that respects a normal-class FPR budget."""
    if not 0 <= max_fpr <= 1:
        raise ValueError("max_fpr must be in [0, 1]")
    y = y_true.astype(int).reset_index(drop=True)
    s = scores.astype(float).reset_index(drop=True)
    normal_scores = s[y == 0]
    if normal_scores.empty or (y == 1).sum() == 0:
        return {"threshold": float("nan"), "recall": float("nan"), "false_positive_rate": float("nan")}
    allowed_fp = int(np.floor(max_fpr * len(normal_scores)))
    if allowed_fp <= 0:
        threshold = float(normal_scores.max()) + np.finfo(float).eps
    else:
        threshold = float(normal_scores.sort_values(ascending=False).iloc[allowed_fp - 1])
    predicted = s >= threshold
    fp = int(((predicted == 1) & (y == 0)).sum())
    tp = int(((predicted == 1) & (y == 1)).sum())
    normals = int((y == 0).sum())
    positives = int((y == 1).sum())
    return {
        "threshold": threshold,
        "recall": float(tp / positives),
        "false_positive_rate": float(fp / normals),
    }


def block_bootstrap_mean_ci(
    values: pd.Series,
    n_bootstrap: int = 1000,
    seed: int = 13,
    alpha: float = 0.05,
) -> dict[str, float]:
    """Bootstrap a mean confidence interval over temporal blocks."""
    arr = values.astype(float).to_numpy()
    if len(arr) == 0:
        raise ValueError("values must not be empty")
    rng = np.random.default_rng(seed)
    means = []
    for _ in range(n_bootstrap):
        sample = rng.choice(arr, size=len(arr), replace=True)
        means.append(float(sample.mean()))
    lower, upper = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return {"mean": float(arr.mean()), "lower": float(lower), "upper": float(upper)}
