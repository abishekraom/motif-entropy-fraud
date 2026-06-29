"""Claim discipline helpers for paper-grade result tables."""

from collections.abc import Iterable, Mapping

import pandas as pd


_REQUIRED = [
    "dataset",
    "task",
    "method",
    "method_auc",
    "best_simple_baseline",
    "best_simple_baseline_auc",
    "paired_delta",
    "paired_p_value",
]


def assign_claim_status(row: Mapping[str, float | str]) -> str:
    if str(row.get("validation_scope", "")).endswith("smoke_sample"):
        return "diagnostic_or_insufficient_gain"
    delta = float(row["paired_delta"])
    p_value = float(row["paired_p_value"])
    if delta <= 0:
        return "negative_or_confounded"
    if delta >= 0.02 and p_value <= 0.05:
        return "defensible_detector_gain"
    return "diagnostic_or_insufficient_gain"


def build_claim_table(rows: Iterable[Mapping[str, object]]) -> pd.DataFrame:
    table = pd.DataFrame(list(rows))
    missing = [col for col in _REQUIRED if col not in table.columns]
    if missing:
        raise ValueError(f"claim table missing columns: {missing}")
    table = table.copy()
    table["claim_status"] = [assign_claim_status(row) for row in table.to_dict("records")]
    return table
