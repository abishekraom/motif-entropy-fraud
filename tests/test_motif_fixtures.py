import pandas as pd

from motif_fraud.motifs.local import count_directed_3cycles, count_feed_forward_chains, local_motif_features


def test_count_directed_3cycles_counts_each_cycle_once():
    edges = pd.DataFrame({"src": [1, 2, 3, 3], "dst": [2, 3, 1, 4]})

    assert count_directed_3cycles(edges) == 1


def test_count_feed_forward_chains_counts_ordered_two_step_paths_without_closing_edge():
    edges = pd.DataFrame({"src": [1, 2, 1, 4], "dst": [2, 3, 3, 1]})

    # 1->2->3 is excluded because 1->3 closes it; 4->1->2 and 4->1->3 remain.
    assert count_feed_forward_chains(edges) == 2


def test_local_motif_features_normalize_by_edges_without_dividing_by_zero():
    empty = pd.DataFrame({"src": [], "dst": []})
    features = local_motif_features(empty)

    assert features["cycle_3"] == 0
    assert features["chain_2"] == 0
    assert features["cycle_3_per_edge"] == 0.0
    assert features["chain_2_per_edge"] == 0.0
