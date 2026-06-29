"""Rich p-adic feature-family augmentation audit for strong IEEE-CIS baselines.

The previous strong-baseline audit appended a single p-adic scalar. This module
pre-specifies a richer non-Archimedean feature family: per-depth prefix rarity,
weighted/mean rarity, novelty depth, and residuals against flat tuple rarity.
It still fails closed when the features do not improve the strongest baseline.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import average_precision_score, roc_auc_score

from motif_fraud.p_adic.encoding import HierarchySpec, encode_frame
from motif_fraud.p_adic.ieee_pipeline import _load_ieee, _prepare_ieee, DEFAULT_OFFICIAL_ROOT
from motif_fraud.p_adic.metrics import next_prime_at_least
from motif_fraud.p_adic.splits import temporal_train_test_split
from motif_fraud.p_adic.strong_baselines import (
    _available_methods,
    _prepare_tree_features,
    _score_catboost,
    _score_lightgbm,
    _score_xgboost,
)
from motif_fraud.p_adic.temporal_surveillance import SELECTED_IEEE_HIERARCHY, _flat_tuple_rarity, _prefix_rarity_matrix


def _ensure_dirs(output_root: Path) -> None:
    for subdir in ("tables", "figures", "metrics", "manifests"):
        (output_root / subdir).mkdir(parents=True, exist_ok=True)


def _safe_metric(func, y_true: pd.Series, scores: pd.Series) -> float:
    if len(set(y_true.astype(int))) < 2:
        return float("nan")
    return float(func(y_true.astype(int), scores.astype(float)))


def _rich_padic_features(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    columns = SELECTED_IEEE_HIERARCHY
    widest = max(train[column].nunique(dropna=False) + 1 for column in columns)
    spec = HierarchySpec("ieee_cis_rich_padic_features", columns, next_prime_at_least(max(2, widest)))
    train_encoded = encode_frame(train, spec)
    test_encoded = encode_frame(test, train_encoded.spec, digit_maps=train_encoded.digit_maps)
    normal_mask = train["isFraud"].astype(int).reset_index(drop=True) == 0
    train_rarity = _prefix_rarity_matrix(
        train_encoded.codes[normal_mask], train_encoded.codes, int(train_encoded.spec.prime or 2), len(columns)
    )
    test_rarity = _prefix_rarity_matrix(
        train_encoded.codes[normal_mask], test_encoded.codes, int(train_encoded.spec.prime or 2), len(columns)
    )
    weights = np.arange(1, len(columns) + 1)
    depth_cols = [f"p_adic_depth{i}_rarity" for i in range(1, len(columns) + 1)]
    for frame, source in ((train_rarity, train), (test_rarity, test)):
        frame["p_adic_mean_rarity"] = frame[depth_cols].mean(axis=1)
        frame["p_adic_weighted_rarity"] = frame[depth_cols].dot(weights) / weights.sum()
        frame["p_adic_max_rarity"] = frame[depth_cols].max(axis=1)
        frame["p_adic_min_rarity"] = frame[depth_cols].min(axis=1)
        frame["p_adic_rarity_range"] = frame["p_adic_max_rarity"] - frame["p_adic_min_rarity"]
        novelty_flags = frame[depth_cols].ge(1.0 - 1e-12).astype(int)
        frame["p_adic_novel_prefix_count"] = novelty_flags.sum(axis=1)
        frame["p_adic_deep_minus_root"] = frame[depth_cols[-1]] - frame[depth_cols[0]]
    train_flat = _flat_tuple_rarity(train, train, columns).reset_index(drop=True)
    test_flat = _flat_tuple_rarity(train, test, columns).reset_index(drop=True)
    train_rarity["p_adic_minus_flat_rarity"] = train_rarity["p_adic_weighted_rarity"] - train_flat
    test_rarity["p_adic_minus_flat_rarity"] = test_rarity["p_adic_weighted_rarity"] - test_flat
    feature_cols = list(train_rarity.columns)
    train_rarity = train_rarity.add_prefix("rich_")
    test_rarity = test_rarity.add_prefix("rich_")
    metadata = {
        "prime": int(train_encoded.spec.prime or 0),
        "hierarchy": "|".join(columns),
        "rich_feature_count": len(feature_cols),
        "rich_features": [f"rich_{c}" for c in feature_cols],
    }
    return train_rarity.reset_index(drop=True), test_rarity.reset_index(drop=True), metadata


def _append_metric(rows: list[dict[str, object]], method: str, role: str, y_test: pd.Series, scores: pd.Series) -> None:
    rows.append(
        {
            "method": method,
            "claim_role": role,
            "auprc": _safe_metric(average_precision_score, y_test, scores),
            "roc_auc": _safe_metric(roc_auc_score, y_test, scores),
        }
    )


def _write_figure(table: pd.DataFrame, path: Path, dpi: int = 600) -> tuple[float, float]:
    plot_table = table.sort_values("auprc", ascending=True)
    colors = ["#2563eb" if "plus_rich_padic" in method else "#475569" for method in plot_table["method"]]
    plt.figure(figsize=(7.2, 4.8))
    plt.barh(plot_table["method"], plot_table["auprc"], color=colors)
    plt.xlabel("AUPRC")
    plt.title("IEEE-CIS rich p-adic feature-family augmentation")
    plt.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=dpi)
    plt.close()
    with Image.open(path) as image:
        return tuple(float(v) for v in image.info.get("dpi", (dpi, dpi)))


def run_ieee_rich_padic_feature_audit(
    data_root: str | Path = DEFAULT_OFFICIAL_ROOT,
    output_root: str | Path = "outputs/p_adic_ieee_cis_rich_features",
    train_fraction: float = 0.7,
    max_rows: int | None = None,
    iterations: int = 200,
    methods: tuple[str, ...] = ("lightgbm", "catboost", "xgboost"),
) -> dict[str, object]:
    output_root = Path(output_root)
    _ensure_dirs(output_root)
    data_root = Path(data_root)
    transaction, identity = _load_ieee(data_root)
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    if max_rows is not None:
        frame = frame.iloc[: int(max_rows)].copy()
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=train_fraction)
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)
    y_train = train["isFraud"].astype(int).reset_index(drop=True)
    y_test = test["isFraud"].astype(int).reset_index(drop=True)
    train_x, test_x, cat_cols, num_cols = _prepare_tree_features(train, test)
    rich_train, rich_test, feature_meta = _rich_padic_features(train, test)
    train_x_rich = pd.concat([train_x.reset_index(drop=True), rich_train], axis=1)
    test_x_rich = pd.concat([test_x.reset_index(drop=True), rich_test], axis=1)
    availability = _available_methods()
    rows: list[dict[str, object]] = []
    active_methods = tuple(method for method in methods if availability.get(method, False))
    if not active_methods:
        raise RuntimeError("No requested strong baseline package is available")
    if "lightgbm" in active_methods:
        base = _score_lightgbm(train_x, y_train, test_x, cat_cols, iterations)
        rich = _score_lightgbm(train_x_rich, y_train, test_x_rich, cat_cols, iterations)
        _append_metric(rows, "lightgbm_compact_tabular", "strong_context_baseline", y_test, base)
        _append_metric(rows, "lightgbm_compact_tabular_plus_rich_padic", "rich_padic_augmented_strong_baseline", y_test, rich)
    if "catboost" in active_methods:
        base = _score_catboost(train_x, y_train, test_x, cat_cols, iterations)
        rich = _score_catboost(train_x_rich, y_train, test_x_rich, cat_cols, iterations)
        _append_metric(rows, "catboost_compact_tabular", "strong_context_baseline", y_test, base)
        _append_metric(rows, "catboost_compact_tabular_plus_rich_padic", "rich_padic_augmented_strong_baseline", y_test, rich)
    if "xgboost" in active_methods:
        base = _score_xgboost(train_x, y_train, test_x, cat_cols, iterations)
        rich = _score_xgboost(train_x_rich, y_train, test_x_rich, cat_cols, iterations)
        _append_metric(rows, "xgboost_compact_tabular", "strong_context_baseline", y_test, base)
        _append_metric(rows, "xgboost_compact_tabular_plus_rich_padic", "rich_padic_augmented_strong_baseline", y_test, rich)
    table = pd.DataFrame(rows)
    best_base = float(table.loc[table["claim_role"] == "strong_context_baseline", "auprc"].max())
    best_rich = float(table.loc[table["claim_role"] == "rich_padic_augmented_strong_baseline", "auprc"].max())
    table["dataset"] = "official_ieee_cis"
    table["train_rows"] = int(len(train))
    table["test_rows"] = int(len(test))
    table["test_fraud_rate"] = float(y_test.mean())
    table["iterations"] = int(iterations)
    table["rich_padic_feature_count"] = int(feature_meta["rich_feature_count"])
    table["best_strong_auprc"] = best_base
    table["best_rich_augmented_auprc"] = best_rich
    table["best_rich_minus_best_strong_auprc"] = best_rich - best_base
    table["claim_status"] = (
        "q1_candidate_rich_padic_improves_strong_baseline"
        if best_rich > best_base + 0.002
        else "diagnostic_only_failed_q1_rich_feature_gate"
    )
    claims_path = output_root / "tables" / "p_adic_ieee_cis_rich_feature_claims.csv"
    feature_manifest_path = output_root / "manifests" / "p_adic_ieee_cis_rich_feature_manifest.json"
    figure_path = output_root / "figures" / "p_adic_ieee_cis_rich_feature_comparison.png"
    table.to_csv(claims_path, index=False)
    table.to_markdown(claims_path.with_suffix(".md"), index=False)
    feature_manifest = {
        **feature_meta,
        "dataset": "official_ieee_cis_rich_padic_features",
        "synthetic_data_used": False,
        "methods": list(active_methods),
        "categorical_features": cat_cols,
        "numeric_feature_count": len(num_cols),
    }
    feature_manifest_path.write_text(json.dumps(feature_manifest, indent=2), encoding="utf-8")
    figure_dpi = _write_figure(table, figure_path)
    metadata = {
        "dataset": "official_ieee_cis_rich_padic_features",
        "data_root": str(data_root),
        "synthetic_data_used": False,
        "rows": int(len(frame)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "test_fraud_rate": float(y_test.mean()),
        "iterations": int(iterations),
        "methods": list(active_methods),
        "best_strong_auprc": best_base,
        "best_rich_augmented_auprc": best_rich,
        "best_rich_minus_best_strong_auprc": best_rich - best_base,
        "claim_status": str(table["claim_status"].iloc[0]),
        "figure_dpi": list(figure_dpi),
    }
    metadata_path = output_root / "manifests" / "p_adic_ieee_cis_rich_feature_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {
        "claims": table,
        "metadata": metadata,
        "artifacts": {
            "claims_table": str(claims_path),
            "feature_manifest": str(feature_manifest_path),
            "metadata": str(metadata_path),
            "figure": str(figure_path),
            "figure_dpi": figure_dpi,
        },
    }


def main() -> None:
    result = run_ieee_rich_padic_feature_audit()
    print(json.dumps(result["metadata"], indent=2))
    print(result["claims"].to_json(orient="records", indent=2))


if __name__ == "__main__":
    main()
