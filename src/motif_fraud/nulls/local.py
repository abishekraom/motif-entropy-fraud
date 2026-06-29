"""Local null models for motif/confound audits."""

import math
import random

import pandas as pd


def er_edge_count_null(nodes: list[int], n_edges: int, seed: int | None = None) -> pd.DataFrame:
    rng = random.Random(seed)
    possible = [(int(src), int(dst)) for src in nodes for dst in nodes if src != dst]
    if n_edges > len(possible):
        raise ValueError("n_edges exceeds number of possible directed non-self edges")
    sampled = rng.sample(possible, n_edges)
    return pd.DataFrame(sampled, columns=["src", "dst"])


def random_degree_preserving_swap(
    edges: pd.DataFrame,
    n_swaps: int,
    seed: int | None = None,
    max_attempts: int | None = None,
) -> pd.DataFrame:
    rng = random.Random(seed)
    edge_list = [(int(src), int(dst)) for src, dst in edges[["src", "dst"]].itertuples(index=False, name=None)]
    edge_set = set(edge_list)
    if len(edge_list) < 2:
        return edges.copy().reset_index(drop=True)
    attempts = max_attempts or max(100, n_swaps * 50)
    swaps = 0
    for _ in range(attempts):
        if swaps >= n_swaps:
            break
        i, j = rng.sample(range(len(edge_list)), 2)
        a, b = edge_list[i]
        c, d = edge_list[j]
        if len({a, b, c, d}) < 4:
            continue
        candidate1 = (a, d)
        candidate2 = (c, b)
        if candidate1[0] == candidate1[1] or candidate2[0] == candidate2[1]:
            continue
        if candidate1 in edge_set or candidate2 in edge_set:
            continue
        edge_set.remove(edge_list[i])
        edge_set.remove(edge_list[j])
        edge_list[i] = candidate1
        edge_list[j] = candidate2
        edge_set.add(candidate1)
        edge_set.add(candidate2)
        swaps += 1
    return pd.DataFrame(edge_list, columns=["src", "dst"])


def null_z_score(observed: float, null_values: list[float]) -> float:
    if not null_values:
        raise ValueError("null_values must not be empty")
    mean = sum(null_values) / len(null_values)
    variance = sum((x - mean) ** 2 for x in null_values) / len(null_values)
    sd = math.sqrt(variance)
    if sd == 0:
        return 0.0
    return float((observed - mean) / sd)
