"""Bootstrap statistics for p-adic fraud claim gates."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score


def _metric_value(y_true: np.ndarray, scores: np.ndarray, metric: str) -> float:
    if len(set(y_true.tolist())) < 2:
        return float("nan")
    if metric == "auprc":
        return float(average_precision_score(y_true, scores))
    if metric == "roc_auc":
        return float(roc_auc_score(y_true, scores))
    raise ValueError(f"Unsupported metric: {metric}")


def bootstrap_metric_delta_ci(
    y_true: pd.Series,
    proposed_scores: pd.Series,
    control_scores: pd.Series,
    metric: str = "auprc",
    n_bootstrap: int = 1000,
    seed: int = 13,
    alpha: float = 0.05,
) -> dict[str, float]:
    """Bootstrap CI for proposed-minus-control metric delta."""
    y = y_true.astype(int).to_numpy()
    proposed = proposed_scores.astype(float).to_numpy()
    control = control_scores.astype(float).to_numpy()
    if not (len(y) == len(proposed) == len(control)):
        raise ValueError("y_true, proposed_scores, and control_scores must have equal length")
    rng = np.random.default_rng(seed)
    deltas = []
    n = len(y)
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        if len(set(y[idx].tolist())) < 2:
            continue
        deltas.append(
            _metric_value(y[idx], proposed[idx], metric) - _metric_value(y[idx], control[idx], metric)
        )
    if not deltas:
        return {"delta_mean": float("nan"), "lower": float("nan"), "upper": float("nan"), "p_delta_le_zero": float("nan")}
    arr = np.array(deltas, dtype=float)
    lower, upper = np.quantile(arr, [alpha / 2, 1 - alpha / 2])
    return {
        "delta_mean": float(arr.mean()),
        "lower": float(lower),
        "upper": float(upper),
        "p_delta_le_zero": float(np.mean(arr <= 0)),
    }
