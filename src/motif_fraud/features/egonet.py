"""Local egonet extraction and simple confound features."""

from collections import deque

import pandas as pd


def _eligible(nodes: pd.DataFrame, time_cutoff: int | None) -> set[int]:
    if time_cutoff is None:
        return set(nodes["tx_id"].astype(int))
    return set(nodes.loc[nodes["time_step"] <= time_cutoff, "tx_id"].astype(int))


def extract_egonet_edges(
    center: int,
    nodes: pd.DataFrame,
    edges: pd.DataFrame,
    hops: int = 1,
    time_cutoff: int | None = None,
) -> pd.DataFrame:
    eligible = _eligible(nodes, time_cutoff)
    if center not in eligible:
        return edges.iloc[0:0].copy()

    filtered = edges[edges["src"].isin(eligible) & edges["dst"].isin(eligible)]
    adjacency: dict[int, set[int]] = {}
    for src, dst in filtered[["src", "dst"]].itertuples(index=False, name=None):
        adjacency.setdefault(int(src), set()).add(int(dst))
        adjacency.setdefault(int(dst), set()).add(int(src))

    visited = {int(center)}
    queue: deque[tuple[int, int]] = deque([(int(center), 0)])
    while queue:
        node, depth = queue.popleft()
        if depth >= hops:
            continue
        for nbr in adjacency.get(node, set()):
            if nbr not in visited:
                visited.add(nbr)
                queue.append((nbr, depth + 1))

    mask = filtered["src"].isin(visited) & filtered["dst"].isin(visited)
    return filtered.loc[mask].reset_index(drop=True)


def local_degree_features(
    center: int,
    nodes: pd.DataFrame,
    edges: pd.DataFrame,
    hops: int = 1,
    time_cutoff: int | None = None,
) -> dict[str, int]:
    egonet = extract_egonet_edges(center, nodes, edges, hops=hops, time_cutoff=time_cutoff)
    egonet_nodes = set(egonet["src"]).union(set(egonet["dst"])) if not egonet.empty else {center}
    return {
        "center_tx_id": int(center),
        "egonet_nodes": int(len(egonet_nodes)),
        "egonet_edges": int(len(egonet)),
        "center_in_degree": int((egonet["dst"] == center).sum()) if not egonet.empty else 0,
        "center_out_degree": int((egonet["src"] == center).sum()) if not egonet.empty else 0,
    }
