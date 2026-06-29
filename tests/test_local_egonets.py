import pandas as pd

from motif_fraud.features.egonet import extract_egonet_edges, local_degree_features


def _fixture_edges():
    return pd.DataFrame(
        {
            "src": [1, 2, 3, 4, 5, 6],
            "dst": [2, 1, 1, 2, 4, 7],
        }
    )


def _fixture_nodes():
    return pd.DataFrame(
        {
            "tx_id": [1, 2, 3, 4, 5, 6, 7],
            "time_step": [1, 1, 1, 2, 3, 3, 4],
            "label": ["illicit", "licit", "unknown", "licit", "unknown", "unknown", "licit"],
        }
    )


def test_extract_egonet_edges_preserves_direction_for_one_hop_neighbors():
    egonet = extract_egonet_edges(center=1, nodes=_fixture_nodes(), edges=_fixture_edges(), hops=1)

    assert set(map(tuple, egonet[["src", "dst"]].to_records(index=False))) == {(1, 2), (2, 1), (3, 1)}


def test_extract_egonet_edges_respects_time_cutoff():
    egonet = extract_egonet_edges(
        center=1,
        nodes=_fixture_nodes(),
        edges=_fixture_edges(),
        hops=2,
        time_cutoff=1,
    )

    assert set(egonet["src"]).union(set(egonet["dst"])) == {1, 2, 3}
    assert (4, 2) not in set(map(tuple, egonet[["src", "dst"]].to_records(index=False)))


def test_local_degree_features_are_computed_for_center_not_whole_graph():
    features = local_degree_features(center=1, nodes=_fixture_nodes(), edges=_fixture_edges(), hops=1)

    assert features["center_tx_id"] == 1
    assert features["egonet_nodes"] == 3
    assert features["egonet_edges"] == 3
    assert features["center_in_degree"] == 2
    assert features["center_out_degree"] == 1
