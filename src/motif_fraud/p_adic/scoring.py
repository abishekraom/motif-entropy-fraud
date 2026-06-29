"""Training-free p-adic anomaly scorers."""

from __future__ import annotations

from collections import Counter

import pandas as pd


class PAdicPrefixRarityScorer:
    """Score anomaly by rarity across every p-adic hierarchy prefix."""

    def __init__(self, prime: int, depth: int, weighting: str = "weighted_deep"):
        self.prime = int(prime)
        self.depth = int(depth)
        self.weighting = weighting
        self._prefix_counts: list[Counter[int]] = []
        self._n = 0

    def fit(self, codes: pd.Series | list[int]) -> "PAdicPrefixRarityScorer":
        values = [int(code) for code in list(codes)]
        if not values:
            raise ValueError("Cannot fit PAdicPrefixRarityScorer on empty codes")
        self._n = len(values)
        self._prefix_counts = []
        for prefix_depth in range(1, self.depth + 1):
            modulus = self.prime**prefix_depth
            self._prefix_counts.append(Counter(code % modulus for code in values))
        return self

    def _combine(self, rarities: list[float]) -> float:
        if self.weighting == "mean":
            return float(sum(rarities) / len(rarities))
        if self.weighting == "root":
            return float(rarities[0])
        if self.weighting == "deep":
            return float(rarities[-1])
        if self.weighting == "weighted_deep":
            weights = list(range(1, len(rarities) + 1))
            return float(sum(w * r for w, r in zip(weights, rarities)) / sum(weights))
        raise ValueError(f"Unknown prefix weighting: {self.weighting}")

    def score(self, codes: pd.Series | list[int]) -> pd.Series:
        if not self._prefix_counts:
            raise ValueError("Scorer must be fit before scoring")
        scores = []
        for raw_code in list(codes):
            code = int(raw_code)
            rarities = []
            for prefix_depth, counts in enumerate(self._prefix_counts, start=1):
                modulus = self.prime**prefix_depth
                support = counts.get(code % modulus, 0)
                rarities.append(1.0 - support / self._n)
            scores.append(self._combine(rarities))
        return pd.Series(scores, name="p_adic_prefix_rarity_score")


class PAdicFrequencyScorer:
    """Score low-support p-adic branches as anomalous.

    The scorer is trained only on normal/licit codes. For a candidate code, it
    finds the deepest p-adic prefix supported by any normal training code and
    combines branch novelty with exact-code rarity. Higher scores are more
    anomalous. This is a deterministic baseline, not a fitted neural model.
    """

    def __init__(self, prime: int, depth: int):
        self.prime = int(prime)
        self.depth = int(depth)
        self._counts: Counter[int] = Counter()
        self._codes: list[int] = []
        self._n = 0

    def fit(self, codes: pd.Series | list[int]) -> "PAdicFrequencyScorer":
        self._codes = [int(code) for code in list(codes)]
        self._counts = Counter(self._codes)
        self._prefix_sets = [set() for _ in range(self.depth + 1)]
        for code in self._codes:
            for prefix_depth in range(self.depth + 1):
                modulus = self.prime**prefix_depth
                self._prefix_sets[prefix_depth].add(code % modulus if modulus > 1 else 0)
        self._n = len(self._codes)
        if self._n == 0:
            raise ValueError("Cannot fit PAdicFrequencyScorer on empty codes")
        return self

    def _shared_depth(self, code: int) -> int:
        # Fast prefix lookup: two p-adic integers share depth k iff they are
        # congruent modulo p^k. This avoids O(n_train * n_test) scans.
        best = 0
        for prefix_depth in range(1, self.depth + 1):
            modulus = self.prime**prefix_depth
            if code % modulus in self._prefix_sets[prefix_depth]:
                best = prefix_depth
            else:
                break
        return best

    def score(self, codes: pd.Series | list[int]) -> pd.Series:
        if self._n == 0:
            raise ValueError("Scorer must be fit before scoring")
        scores = []
        for raw_code in list(codes):
            code = int(raw_code)
            shared_depth = self._shared_depth(code)
            novelty = 1.0 - (shared_depth / max(self.depth, 1))
            exact_count = self._counts.get(code, 0)
            rarity = 1.0 - (exact_count / self._n)
            scores.append(float(novelty + 0.25 * rarity))
        return pd.Series(scores, name="p_adic_frequency_score")
