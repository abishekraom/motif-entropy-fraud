from pathlib import Path

import pandas as pd

from motif_fraud.data.elliptic import EllipticDataset, load_elliptic


DATA_ROOT = Path("data/elliptic_plusplus/elliptic_bitcoin_dataset")


def test_load_elliptic_returns_stable_contract_with_labels_time_and_edges():
    dataset = load_elliptic(DATA_ROOT)

    assert isinstance(dataset, EllipticDataset)
    assert {"tx_id", "time_step", "label"}.issubset(dataset.nodes.columns)
    assert {"src", "dst"}.issubset(dataset.edges.columns)
    assert set(dataset.nodes["label"].unique()).issubset({"licit", "illicit", "unknown"})
    assert dataset.nodes["tx_id"].is_unique
    assert dataset.nodes["time_step"].min() >= 1
    assert len(dataset.nodes) > 200_000
    assert len(dataset.edges) > 230_000


def test_temporal_edges_at_cutoff_do_not_include_future_nodes():
    dataset = load_elliptic(DATA_ROOT)
    cutoff = 10

    temporal_edges = dataset.edges_at_or_before(cutoff)
    node_times = dataset.nodes.set_index("tx_id")["time_step"]

    assert not temporal_edges.empty
    assert node_times.loc[temporal_edges["src"]].max() <= cutoff
    assert node_times.loc[temporal_edges["dst"]].max() <= cutoff


def test_dataset_summary_reports_label_counts_and_unknowns_explicitly():
    dataset = load_elliptic(DATA_ROOT)
    summary = dataset.summary()

    assert summary["n_nodes"] == len(dataset.nodes)
    assert summary["n_edges"] == len(dataset.edges)
    assert summary["label_counts"]["unknown"] > 0
    assert summary["label_counts"]["licit"] > 0
    assert summary["label_counts"]["illicit"] > 0
    assert summary["n_time_steps"] == dataset.nodes["time_step"].nunique()


def test_loader_can_sample_rows_for_fast_debug_without_changing_schema():
    dataset = load_elliptic(DATA_ROOT, max_nodes=1000)

    assert len(dataset.nodes) == 1000
    assert {"tx_id", "time_step", "label"}.issubset(dataset.nodes.columns)
    assert {"src", "dst"}.issubset(dataset.edges.columns)
    assert set(dataset.edges["src"]).issubset(set(dataset.nodes["tx_id"]))
    assert set(dataset.edges["dst"]).issubset(set(dataset.nodes["tx_id"]))
