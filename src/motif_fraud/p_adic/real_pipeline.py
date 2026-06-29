"""Real-dataset p-adic fraud audit pipeline.

This module never manufactures research evidence: if a dataset is weak for the
p-adic hierarchy hypothesis, the claim gate records a diagnostic failure instead
of upgrading the claim.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score

from motif_fraud.p_adic.encoding import HierarchySpec, encode_frame, randomize_digit_maps
from motif_fraud.p_adic.metrics import next_prime_at_least
from motif_fraud.p_adic.scoring import PAdicFrequencyScorer
from motif_fraud.p_adic.splits import temporal_train_test_split
from motif_fraud.pipeline.p_adic_reproduce import build_q1_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CCF_PATH = PROJECT_ROOT / "data" / "creditcardfraud" / "creditcard.csv"


def _ensure_dirs(output_root: Path) -> None:
    for subdir in ("tables", "figures", "manifests", "metrics"):
        (output_root / subdir).mkdir(parents=True, exist_ok=True)


def _safe_roc_auc(y_true: Iterable[int], scores: Iterable[float]) -> float:
    y = list(y_true)
    if len(set(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, list(scores)))


def _safe_auprc(y_true: Iterable[int], scores: Iterable[float]) -> float:
    y = list(y_true)
    if len(set(y)) < 2:
        return float("nan")
    return float(average_precision_score(y, list(scores)))


def _fit_quantile_edges(train_values: pd.Series, bins: int) -> np.ndarray:
    if bins < 2:
        raise ValueError("quantile_bins must be >= 2")
    quantiles = np.linspace(0, 1, bins + 1)[1:-1]
    edges = np.unique(np.quantile(train_values.astype(float), quantiles))
    return edges.astype(float)


def _apply_buckets(values: pd.Series, edges: np.ndarray, prefix: str) -> pd.Series:
    bucket_ids = np.searchsorted(edges, values.astype(float), side="right")
    return pd.Series([f"{prefix}_{int(bucket)}" for bucket in bucket_ids], index=values.index)


def _build_creditcard_hierarchy(
    train: pd.DataFrame, test: pd.DataFrame, quantile_bins: int
) -> tuple[pd.DataFrame, pd.DataFrame, HierarchySpec]:
    amount_edges = _fit_quantile_edges(train["Amount"], quantile_bins)
    time_edges = _fit_quantile_edges(train["Time"], quantile_bins)
    train_h = train.copy()
    test_h = test.copy()
    # CCF has no semantic transaction taxonomy. These are real, train-fitted
    # discretizations for a negative-control/diagnostic p-adic audit only.
    train_h["time_bucket"] = _apply_buckets(train_h["Time"], time_edges, "time")
    test_h["time_bucket"] = _apply_buckets(test_h["Time"], time_edges, "time")
    train_h["amount_bucket"] = _apply_buckets(train_h["Amount"], amount_edges, "amount")
    test_h["amount_bucket"] = _apply_buckets(test_h["Amount"], amount_edges, "amount")
    prime = next_prime_at_least(quantile_bins + 1)
    return train_h, test_h, HierarchySpec("creditcard_time_amount", ("time_bucket", "amount_bucket"), prime)


def _evaluate_creditcard_scores(
    y_true: pd.Series,
    p_adic_scores: pd.Series,
    amount_scores: pd.Series,
    flat_frequency_scores: pd.Series,
    hierarchy_control_scores: pd.Series,
    random_control_scores: list[pd.Series],
) -> pd.DataFrame:
    rows = [
        {
            "method": "p_adic_time_amount_frequency",
            "auprc": _safe_auprc(y_true, p_adic_scores),
            "roc_auc": _safe_roc_auc(y_true, p_adic_scores),
            "control_family": "proposed",
        },
        {
            "method": "amount_only_baseline",
            "auprc": _safe_auprc(y_true, amount_scores),
            "roc_auc": _safe_roc_auc(y_true, amount_scores),
            "control_family": "simple_baseline",
        },
        {
            "method": "flat_categorical_frequency_control",
            "auprc": _safe_auprc(y_true, flat_frequency_scores),
            "roc_auc": _safe_roc_auc(y_true, flat_frequency_scores),
            "control_family": "negative_control",
        },
        {
            "method": "random_hierarchy_order_control",
            "auprc": _safe_auprc(y_true, hierarchy_control_scores),
            "roc_auc": _safe_roc_auc(y_true, hierarchy_control_scores),
            "control_family": "negative_control",
        },
    ]
    for index, control in enumerate(random_control_scores):
        rows.append(
            {
                "method": f"random_digit_map_control_seed_{index}",
                "auprc": _safe_auprc(y_true, control),
                "roc_auc": _safe_roc_auc(y_true, control),
                "control_family": "negative_control",
            }
        )
    results = pd.DataFrame(rows)
    proposed = results.loc[results["method"] == "p_adic_time_amount_frequency"].iloc[0]
    best_control = results.loc[results["method"] != "p_adic_time_amount_frequency", "auprc"].max()
    # CCF lacks semantic hierarchical categories, so even a numeric win is not enough
    # for a primary p-adic hierarchy claim. It can only pass as infrastructure smoke.
    status = (
        "q1_candidate_passed_controls"
        if float(proposed["auprc"]) > float(best_control) and float(proposed["auprc"]) >= 0.20
        else "diagnostic_only_failed_q1_gate"
    )
    results["best_control_auprc"] = float(best_control)
    results["delta_vs_best_control_auprc"] = results["auprc"] - float(best_control)
    results["claim_status"] = status
    results["claim_scope"] = "ccf_real_dataset_diagnostic_not_primary_hierarchy_claim"
    return results


def _write_pr_curve(y_true: pd.Series, scores: pd.Series, path: Path, dpi: int = 600) -> None:
    precision, recall, _ = precision_recall_curve(y_true, scores)
    plt.figure(figsize=(5, 4))
    plt.plot(recall, precision, label="p-adic diagnostic score")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("European CCF p-adic diagnostic PR curve")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(path, dpi=dpi)
    plt.close()


def run_creditcard_p_adic_audit(
    frame: pd.DataFrame | None = None,
    output_root: str | Path = "outputs/p_adic_creditcard",
    train_fraction: float = 0.7,
    quantile_bins: int = 10,
    random_control_seeds: tuple[int, ...] = (11, 17, 23, 31, 47),
) -> dict[str, object]:
    """Run a real-data diagnostic p-adic audit on European CCF."""
    output_root = Path(output_root)
    _ensure_dirs(output_root)
    if frame is None:
        if not DEFAULT_CCF_PATH.exists():
            raise FileNotFoundError(
                f"Missing {DEFAULT_CCF_PATH}; download with: "
                "kaggle datasets download -d mlg-ulb/creditcardfraud -p data/creditcardfraud --unzip"
            )
        frame = pd.read_csv(DEFAULT_CCF_PATH)
    required = {"Time", "Amount", "Class"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise KeyError(f"Creditcard frame missing required columns: {missing}")

    train, test = temporal_train_test_split(frame, temporal_column="Time", train_fraction=train_fraction)
    train_h, test_h, spec = _build_creditcard_hierarchy(train, test, quantile_bins=quantile_bins)
    train_encoded = encode_frame(train_h, spec)
    test_encoded = encode_frame(test_h, train_encoded.spec, digit_maps=train_encoded.digit_maps)
    normal_train_codes = train_encoded.codes[train_h["Class"].astype(int) == 0]
    scorer = PAdicFrequencyScorer(prime=train_encoded.spec.prime or 2, depth=len(spec.columns)).fit(normal_train_codes)
    p_adic_scores = scorer.score(test_encoded.codes)

    random_scores: list[pd.Series] = []
    for seed in random_control_seeds:
        maps = randomize_digit_maps(train_encoded.digit_maps, seed=seed)
        control_train = encode_frame(train_h, train_encoded.spec, digit_maps=maps)
        control_test = encode_frame(test_h, train_encoded.spec, digit_maps=maps)
        control_scorer = PAdicFrequencyScorer(
            prime=train_encoded.spec.prime or 2, depth=len(spec.columns)
        ).fit(control_train.codes[train_h["Class"].astype(int) == 0])
        random_scores.append(control_scorer.score(control_test.codes))

    reversed_spec = HierarchySpec(
        "creditcard_amount_time_reversed",
        tuple(reversed(spec.columns)),
        train_encoded.spec.prime,
    )
    reversed_train = encode_frame(train_h, reversed_spec)
    reversed_test = encode_frame(test_h, reversed_train.spec, digit_maps=reversed_train.digit_maps)
    hierarchy_control_scores = PAdicFrequencyScorer(
        prime=reversed_train.spec.prime or 2, depth=len(reversed_spec.columns)
    ).fit(reversed_train.codes[train_h["Class"].astype(int) == 0]).score(reversed_test.codes)

    normal_flat_keys = (
        train_h.loc[train_h["Class"].astype(int) == 0, "time_bucket"].astype(str)
        + "|"
        + train_h.loc[train_h["Class"].astype(int) == 0, "amount_bucket"].astype(str)
    )
    flat_counts = normal_flat_keys.value_counts().to_dict()
    n_normal_flat = max(1, len(normal_flat_keys))
    test_flat_keys = test_h["time_bucket"].astype(str) + "|" + test_h["amount_bucket"].astype(str)
    flat_frequency_scores = pd.Series(
        [1.0 - (flat_counts.get(key, 0) / n_normal_flat) for key in test_flat_keys],
        name="flat_categorical_frequency_score",
    )

    y_true = test_h["Class"].astype(int).reset_index(drop=True)
    amount_scores = test_h["Amount"].astype(float).reset_index(drop=True)
    claims = _evaluate_creditcard_scores(
        y_true,
        p_adic_scores,
        amount_scores,
        flat_frequency_scores,
        hierarchy_control_scores,
        random_scores,
    )
    claims_path = output_root / "tables" / "p_adic_creditcard_claims.csv"
    claims.to_csv(claims_path, index=False)
    claims.to_markdown(claims_path.with_suffix(".md"), index=False)

    scores = pd.DataFrame(
        {
            "row_index": test_h.index.to_numpy(),
            "y_true": y_true,
            "p_adic_score": p_adic_scores,
            "amount_score": amount_scores,
        }
    )
    scores.to_csv(output_root / "metrics" / "p_adic_creditcard_scores.csv", index=False)

    figure_path = output_root / "figures" / "p_adic_creditcard_pr_curve.png"
    _write_pr_curve(y_true, p_adic_scores, figure_path, dpi=600)

    artifacts = {
        "dataset_cards": ["docs/rebuild/dataset_cards/european_creditcard_kaggle.md"],
        "negative_controls": ["random_digit_map", "random_hierarchy", "flat_categorical"],
        "figures": [{"path": str(figure_path), "dpi": 600}],
        "claims_table": str(claims_path),
        "scores": str(output_root / "metrics" / "p_adic_creditcard_scores.csv"),
    }
    manifest = build_q1_manifest(artifacts, output_root / "manifests" / "p_adic_creditcard_manifest.json")
    run_metadata = {
        "dataset": "European Credit Card Fraud Detection (Kaggle mlg-ulb/creditcardfraud)",
        "rows": int(len(frame)),
        "train_rows": int(len(train_h)),
        "test_rows": int(len(test_h)),
        "fraud_rate": float(frame["Class"].astype(int).mean()),
        "train_fraction": float(train_fraction),
        "quantile_bins": int(quantile_bins),
        "prime": int(train_encoded.spec.prime or 0),
        "claim_status": str(claims["claim_status"].iloc[0]),
    }
    (output_root / "manifests" / "run_metadata.json").write_text(
        json.dumps(run_metadata, indent=2), encoding="utf-8"
    )
    return {"claims": claims, "manifest": manifest, "metadata": run_metadata}


def main() -> None:
    result = run_creditcard_p_adic_audit()
    print(json.dumps(result["metadata"], indent=2))


if __name__ == "__main__":
    main()
