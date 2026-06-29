"""Scalar local directed motif counters used as correctness oracles."""

import pandas as pd


def _adjacency(edges: pd.DataFrame) -> dict[int, set[int]]:
    adj: dict[int, set[int]] = {}
    for src, dst in edges[["src", "dst"]].itertuples(index=False, name=None):
        adj.setdefault(int(src), set()).add(int(dst))
        adj.setdefault(int(dst), set())
    return adj


def count_directed_3cycles(edges: pd.DataFrame) -> int:
    adj = _adjacency(edges)
    count = 0
    for a, outs in adj.items():
        for b in outs:
            for c in adj.get(b, set()):
                if c != a and a in adj.get(c, set()):
                    count += 1
    return count // 3


def count_feed_forward_chains(edges: pd.DataFrame) -> int:
    adj = _adjacency(edges)
    count = 0
    for u, outs in adj.items():
        for v in outs:
            for w in adj.get(v, set()):
                if u == w:
                    continue
                if w not in outs:
                    count += 1
    return count


def local_motif_features(edges: pd.DataFrame) -> dict[str, float | int]:
    n_edges = int(len(edges))
    cycles = int(count_directed_3cycles(edges))
    chains = int(count_feed_forward_chains(edges))
    denom = float(n_edges) if n_edges else 1.0
    return {
        "cycle_3": cycles,
        "chain_2": chains,
        "cycle_3_per_edge": cycles / denom if n_edges else 0.0,
        "chain_2_per_edge": chains / denom if n_edges else 0.0,
    }
