"""Statistical tests for paired model comparisons."""

import numpy as np
from sklearn.metrics import roc_auc_score


def _auc(y_true: np.ndarray, scores: np.ndarray) -> float:
    if len(np.unique(y_true)) < 2:
        return float("nan")
    return float(roc_auc_score(y_true, scores))


def paired_permutation_p_value(
    y_true: list[int] | np.ndarray,
    method_scores: list[float] | np.ndarray,
    baseline_scores: list[float] | np.ndarray,
    n_permutations: int = 1000,
    seed: int = 13,
) -> float:
    """One-sided paired randomization test for AUC(method) - AUC(baseline) > 0."""

    y = np.asarray(y_true, dtype=int)
    method = np.asarray(method_scores, dtype=float)
    baseline = np.asarray(baseline_scores, dtype=float)
    observed = _auc(y, method) - _auc(y, baseline)
    if np.allclose(method, baseline) or observed <= 0:
        return 1.0

    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(n_permutations):
        swap = rng.random(len(y)) < 0.5
        perm_method = method.copy()
        perm_baseline = baseline.copy()
        perm_method[swap] = baseline[swap]
        perm_baseline[swap] = method[swap]
        delta = _auc(y, perm_method) - _auc(y, perm_baseline)
        if delta >= observed:
            exceed += 1
    return float((exceed + 1) / (n_permutations + 1))
