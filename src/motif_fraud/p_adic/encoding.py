"""Auditable p-adic encodings for hierarchical categorical attributes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd

from motif_fraud.p_adic.metrics import next_prime_at_least

MISSING_TOKEN = "__MISSING__"
OTHER_TOKEN = "__OTHER__"


@dataclass(frozen=True)
class HierarchySpec:
    """Ordered coarse-to-fine columns encoded as p-adic digits."""

    name: str
    columns: tuple[str, ...]
    prime: int | None = None


@dataclass(frozen=True)
class EncodedHierarchy:
    """Encoded p-adic integer codes and the exact maps used to produce them."""

    spec: HierarchySpec
    codes: pd.Series
    digit_maps: dict[str, dict[object, int]]


def _stable_categories(series: pd.Series) -> list[object]:
    values = series.astype("object").where(series.notna(), MISSING_TOKEN)
    # Preserve first-seen order so curated/taxonomic ordering in the input data is not
    # silently replaced by alphabetical order. pandas.unique is deterministic for a
    # fixed file and split, and digit maps are persisted for audit/reuse.
    return values.drop_duplicates().tolist()


def _build_digit_maps(frame: pd.DataFrame, columns: tuple[str, ...], prime: int) -> dict[str, dict[object, int]]:
    maps: dict[str, dict[object, int]] = {}
    for column in columns:
        categories = _stable_categories(frame[column])
        if OTHER_TOKEN not in categories:
            categories = categories + [OTHER_TOKEN]
        if len(categories) > prime:
            raise ValueError(
                f"Column {column!r} has {len(categories)} categories but prime {prime} supports "
                "only one digit; use a larger prime or pre-specified radix expansion."
            )
        maps[column] = {category: digit for digit, category in enumerate(categories)}
    return maps


def infer_prime(frame: pd.DataFrame, columns: tuple[str, ...]) -> int:
    """Infer the smallest prime supporting every hierarchy level as one digit."""
    widest = max(len(_stable_categories(frame[column])) + 1 for column in columns)
    return next_prime_at_least(max(widest, 2))


def encode_frame(
    frame: pd.DataFrame,
    spec: HierarchySpec,
    digit_maps: Mapping[str, Mapping[object, int]] | None = None,
) -> EncodedHierarchy:
    """Encode rows into finite p-adic integer codes using audited digit maps."""
    missing = [column for column in spec.columns if column not in frame.columns]
    if missing:
        raise KeyError(f"Missing hierarchy columns: {missing}")
    prime = spec.prime or infer_prime(frame, spec.columns)
    maps = (
        {column: dict(mapping) for column, mapping in digit_maps.items()}
        if digit_maps is not None
        else _build_digit_maps(frame, spec.columns, prime)
    )
    codes = pd.Series(np.zeros(len(frame), dtype=object), index=frame.index, name=f"{spec.name}_p_adic_code")
    for depth, column in enumerate(spec.columns):
        values = frame[column].astype("object").where(frame[column].notna(), MISSING_TOKEN)
        digits = values.map(maps[column])
        if digits.isna().any() and OTHER_TOKEN in maps[column]:
            digits = digits.fillna(maps[column][OTHER_TOKEN])
        digits = digits.astype(int)
        if digits.isna().any():
            unknown = sorted(set(values[digits.isna()].tolist()), key=str)
            raise ValueError(f"Column {column!r} has categories absent from digit map: {unknown}")
        if (digits >= prime).any() or (digits < 0).any():
            raise ValueError(f"Digit map for {column!r} contains digits outside [0, {prime - 1}]")
        codes = codes + digits.astype(object) * (prime**depth)
    return EncodedHierarchy(spec=HierarchySpec(spec.name, spec.columns, prime), codes=codes.astype(object), digit_maps=maps)


def randomize_digit_maps(
    digit_maps: Mapping[str, Mapping[object, int]], seed: int
) -> dict[str, dict[object, int]]:
    """Return a negative-control map that shuffles digits within each column."""
    rng = np.random.default_rng(seed)
    randomized: dict[str, dict[object, int]] = {}
    for column, mapping in digit_maps.items():
        categories = list(mapping.keys())
        digits = np.array(list(mapping.values()), dtype=int)
        rng.shuffle(digits)
        randomized[column] = {category: int(digit) for category, digit in zip(categories, digits)}
    return randomized
