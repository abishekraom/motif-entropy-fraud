import pandas as pd

from motif_fraud.nulls.local import er_edge_count_null, null_z_score, random_degree_preserving_swap


def _edges():
    return pd.DataFrame({"src": [1, 1, 2, 3], "dst": [2, 3, 3, 4]})


def _degree_signature(edges):
    nodes = sorted(set(edges["src"]).union(edges["dst"]))
    return {
        node: (
            int((edges["src"] == node).sum()),
            int((edges["dst"] == node).sum()),
        )
        for node in nodes
    }


def test_er_edge_count_null_preserves_edge_count_and_avoids_self_loops():
    sampled = er_edge_count_null(nodes=[1, 2, 3, 4], n_edges=4, seed=7)

    assert len(sampled) == 4
    assert not (sampled["src"] == sampled["dst"]).any()


def test_degree_preserving_swap_preserves_in_and_out_degree():
    edges = _edges()
    swapped = random_degree_preserving_swap(edges, n_swaps=10, seed=3)

    assert len(swapped) == len(edges)
    assert _degree_signature(swapped) == _degree_signature(edges)


def test_null_z_score_returns_neutral_zero_when_null_variance_is_zero():
    assert null_z_score(observed=5.0, null_values=[5.0, 5.0, 5.0]) == 0.0
