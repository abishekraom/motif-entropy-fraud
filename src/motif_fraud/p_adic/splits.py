"""Leakage-safe temporal split helpers."""

from __future__ import annotations

import pandas as pd


def temporal_train_test_split(
    frame: pd.DataFrame,
    temporal_column: str,
    train_fraction: float = 0.7,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return disjoint train/test splits ordered by time.

    The original row indices are preserved for auditability.
    """
    if temporal_column not in frame.columns:
        raise KeyError(f"Missing temporal column: {temporal_column}")
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be strictly between 0 and 1")
    if len(frame) < 2:
        raise ValueError("Need at least two rows for a train/test split")
    ordered = frame.sort_values([temporal_column], kind="mergesort")
    split_at = int(len(ordered) * train_fraction)
    split_at = min(max(split_at, 1), len(ordered) - 1)
    train = ordered.iloc[:split_at].copy()
    test = ordered.iloc[split_at:].copy()
    if train[temporal_column].max() > test[temporal_column].min():
        raise AssertionError("Temporal split leakage detected")
    return train, test
