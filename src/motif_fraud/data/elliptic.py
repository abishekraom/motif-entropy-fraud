"""Elliptic Bitcoin dataset loader."""

from pathlib import Path

import pandas as pd

from motif_fraud.data.contracts import GraphDataset


class EllipticDataset(GraphDataset):
    """Elliptic transaction graph with explicit labels and temporal blocks."""


_LABEL_MAP = {"1": "illicit", "2": "licit", "unknown": "unknown", 1: "illicit", 2: "licit"}


def load_elliptic(root: str | Path, max_nodes: int | None = None) -> EllipticDataset:
    root = Path(root)
    classes_path = root / "elliptic_txs_classes.csv"
    edges_path = root / "elliptic_txs_edgelist.csv"
    features_path = root / "elliptic_txs_features.csv"

    classes = pd.read_csv(classes_path)
    features = pd.read_csv(features_path, header=None, usecols=[0, 1], names=["tx_id", "time_step"])
    nodes = features.merge(classes.rename(columns={"txId": "tx_id", "class": "raw_label"}), on="tx_id", how="left")
    nodes["label"] = nodes["raw_label"].map(_LABEL_MAP).fillna("unknown")
    nodes = nodes[["tx_id", "time_step", "label"]].copy()
    nodes["tx_id"] = nodes["tx_id"].astype(int)
    nodes["time_step"] = nodes["time_step"].astype(int)

    if max_nodes is not None:
        nodes = nodes.head(max_nodes).copy()

    edges = pd.read_csv(edges_path).rename(columns={"txId1": "src", "txId2": "dst"})
    edges = edges[["src", "dst"]].astype(int)
    if max_nodes is not None:
        keep = set(nodes["tx_id"])
        edges = edges[edges["src"].isin(keep) & edges["dst"].isin(keep)].copy()

    return EllipticDataset(name="elliptic_bitcoin", nodes=nodes.reset_index(drop=True), edges=edges.reset_index(drop=True))
