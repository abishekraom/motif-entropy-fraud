"""Data loading contracts."""

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class GraphDataset:
    """Minimal directed temporal graph dataset contract."""

    name: str
    nodes: pd.DataFrame
    edges: pd.DataFrame

    def edges_at_or_before(self, cutoff: int) -> pd.DataFrame:
        node_times = self.nodes.set_index("tx_id")["time_step"]
        eligible = set(self.nodes.loc[self.nodes["time_step"] <= cutoff, "tx_id"])
        mask = self.edges["src"].isin(eligible) & self.edges["dst"].isin(eligible)
        return self.edges.loc[mask].reset_index(drop=True)

    def summary(self) -> dict[str, Any]:
        label_counts = self.nodes["label"].value_counts().to_dict()
        for label in ("licit", "illicit", "unknown"):
            label_counts.setdefault(label, 0)
        return {
            "name": self.name,
            "n_nodes": int(len(self.nodes)),
            "n_edges": int(len(self.edges)),
            "n_time_steps": int(self.nodes["time_step"].nunique()),
            "label_counts": {k: int(v) for k, v in label_counts.items()},
        }
