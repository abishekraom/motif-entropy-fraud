"""Train-only hierarchy-order selection for p-adic categorical signals."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations

import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from motif_fraud.p_adic.encoding import HierarchySpec, encode_frame
from motif_fraud.p_adic.metrics import next_prime_at_least
from motif_fraud.p_adic.scoring import PAdicPrefixRarityScorer
from motif_fraud.p_adic.splits import temporal_train_test_split


@dataclass(frozen=True)
class HierarchySelectionResult:
    best_order: tuple[str, ...]
    validation_results: pd.DataFrame


def _safe_metric(func, y_true: pd.Series, scores: pd.Series) -> float:
    if len(set(y_true.astype(int))) < 2:
        return float("nan")
    return float(func(y_true.astype(int), scores.astype(float)))


def select_hierarchy_order_temporal(
    frame: pd.DataFrame,
    candidate_columns: tuple[str, ...],
    time_column: str,
    label_column: str,
    train_fraction: float = 0.7,
) -> HierarchySelectionResult:
    """Select hierarchy order using only an inner temporal train/validation split."""
    inner_train, validation = temporal_train_test_split(
        frame, temporal_column=time_column, train_fraction=train_fraction
    )
    rows = []
    for order in permutations(candidate_columns):
        widest = max(inner_train[column].nunique(dropna=False) + 1 for column in order)
        spec = HierarchySpec("inner_selection", tuple(order), next_prime_at_least(max(2, widest)))
        train_encoded = encode_frame(inner_train, spec)
        validation_encoded = encode_frame(
            validation, train_encoded.spec, digit_maps=train_encoded.digit_maps
        )
        normal_codes = train_encoded.codes[inner_train[label_column].astype(int) == 0]
        scores = PAdicPrefixRarityScorer(
            prime=train_encoded.spec.prime or 2,
            depth=len(order),
            weighting="weighted_deep",
        ).fit(normal_codes).score(validation_encoded.codes)
        y_val = validation[label_column].astype(int).reset_index(drop=True)
        rows.append(
            {
                "order": "|".join(order),
                "auprc": _safe_metric(average_precision_score, y_val, scores),
                "roc_auc": _safe_metric(roc_auc_score, y_val, scores),
            }
        )
    results = pd.DataFrame(rows).sort_values(["auprc", "roc_auc"], ascending=False).reset_index(drop=True)
    best_order = tuple(str(results.iloc[0]["order"]).split("|"))
    return HierarchySelectionResult(best_order=best_order, validation_results=results)
