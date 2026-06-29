import numpy as np

from motif_fraud.evaluation.statistics import paired_permutation_p_value


def test_paired_permutation_p_value_is_small_when_observed_delta_is_large():
    y = [1, 1, 1, 0, 0, 0]
    method_scores = [0.9, 0.8, 0.7, 0.3, 0.2, 0.1]
    baseline_scores = [0.55, 0.20, 0.45, 0.60, 0.35, 0.30]

    p_value = paired_permutation_p_value(y, method_scores, baseline_scores, n_permutations=200, seed=1)

    assert 0.0 <= p_value <= 0.05


def test_paired_permutation_p_value_is_one_when_scores_are_identical():
    y = [1, 1, 0, 0]
    scores = [0.8, 0.7, 0.2, 0.1]

    assert paired_permutation_p_value(y, scores, scores, n_permutations=50, seed=1) == 1.0
