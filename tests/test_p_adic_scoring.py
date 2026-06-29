import pandas as pd

from motif_fraud.p_adic.encoding import HierarchySpec, encode_frame
from motif_fraud.p_adic.scoring import PAdicFrequencyScorer, PAdicPrefixRarityScorer


def test_frequency_scorer_flags_codes_without_normal_prefix_support_as_more_anomalous():
    train = pd.DataFrame({"root": ["A", "A", "A", "A"], "leaf": ["x", "x", "y", "y"]})
    test = pd.DataFrame({"root": ["A", "B"], "leaf": ["x", "z"]})
    spec = HierarchySpec(name="toy", columns=("root", "leaf"), prime=3)
    train_encoded = encode_frame(train, spec)
    test_encoded = encode_frame(test, train_encoded.spec, digit_maps={
        "root": {"A": 0, "B": 1},
        "leaf": {"x": 0, "y": 1, "z": 2},
    })

    scorer = PAdicFrequencyScorer(prime=3, depth=2).fit(train_encoded.codes)
    scores = scorer.score(test_encoded.codes)

    assert scores[1] > scores[0]
    assert scores[0] >= 0


def test_frequency_scorer_is_deterministic_for_identical_inputs():
    codes = pd.Series([0, 0, 3, 6])
    scorer = PAdicFrequencyScorer(prime=3, depth=2).fit(codes)

    assert scorer.score(pd.Series([0, 3])).tolist() == scorer.score(pd.Series([0, 3])).tolist()


def test_prefix_rarity_scorer_uses_all_hierarchy_prefixes_not_only_exact_leaf_counts():
    # With p=3 and depth=2, codes 0 and 3 share the root prefix modulo 3.
    # Code 1 differs at the root, so it must receive a larger anomaly score.
    scorer = PAdicPrefixRarityScorer(prime=3, depth=2, weighting="weighted_deep").fit(
        pd.Series([0, 0, 3, 3])
    )
    scores = scorer.score(pd.Series([0, 3, 1]))

    assert scores.iloc[2] > scores.iloc[0]
    assert scores.iloc[2] > scores.iloc[1]
