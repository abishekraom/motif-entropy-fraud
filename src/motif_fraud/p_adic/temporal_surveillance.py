"""Multi-resolution p-adic temporal surveillance audit on official IEEE-CIS.

This module upgrades the earlier transaction-level prefix-rarity score into a
block-level temporal signal-processing audit. It deliberately keeps claim gates
strict: a polished artifact is written even when the p-adic temporal signal does
not beat flat/entropy/count controls.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score

from motif_fraud.p_adic.encoding import HierarchySpec, encode_frame
from motif_fraud.p_adic.ieee_pipeline import _load_ieee, _prepare_ieee, DEFAULT_OFFICIAL_ROOT
from motif_fraud.p_adic.metrics import next_prime_at_least
from motif_fraud.p_adic.splits import temporal_train_test_split

SELECTED_IEEE_HIERARCHY = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain")


def _ensure_dirs(output_root: Path) -> None:
    for subdir in ("tables", "figures", "metrics", "manifests"):
        (output_root / subdir).mkdir(parents=True, exist_ok=True)


def _safe_metric(func, y_true: pd.Series, scores: pd.Series) -> float:
    y = y_true.astype(int)
    if len(set(y)) < 2 or scores.astype(float).nunique(dropna=False) <= 1:
        return float("nan")
    return float(func(y, scores.astype(float)))


def _prefix_rarity_matrix(train_codes: pd.Series, test_codes: pd.Series, prime: int, depth: int) -> pd.DataFrame:
    normal_codes = [int(code) for code in train_codes]
    if not normal_codes:
        raise ValueError("normal training codes must not be empty")
    n_normal = len(normal_codes)
    counters: list[Counter[int]] = []
    for prefix_depth in range(1, depth + 1):
        modulus = prime**prefix_depth
        counters.append(Counter(code % modulus for code in normal_codes))
    rows = []
    for raw_code in list(test_codes):
        code = int(raw_code)
        row = {}
        for prefix_depth, counts in enumerate(counters, start=1):
            modulus = prime**prefix_depth
            support = counts.get(code % modulus, 0)
            row[f"p_adic_depth{prefix_depth}_rarity"] = 1.0 - support / n_normal
        rows.append(row)
    return pd.DataFrame(rows)


def _flat_tuple_rarity(train_h: pd.DataFrame, test_h: pd.DataFrame, columns: tuple[str, ...]) -> pd.Series:
    normal = train_h[train_h["isFraud"].astype(int) == 0]
    train_keys = normal[list(columns)].astype(str).agg("|".join, axis=1)
    counts = train_keys.value_counts().to_dict()
    denom = max(1, len(train_keys))
    test_keys = test_h[list(columns)].astype(str).agg("|".join, axis=1)
    return pd.Series([1.0 - counts.get(key, 0) / denom for key in test_keys], name="flat_tuple_rarity")


def _entropy_for_frame(frame: pd.DataFrame, columns: tuple[str, ...]) -> float:
    total = 0.0
    for column in columns:
        probs = frame[column].astype(str).value_counts(normalize=True)
        if len(probs):
            total += float(-(probs * np.log2(probs)).sum())
    return total


def _assign_equal_count_blocks(frame: pd.DataFrame, n_blocks: int) -> pd.Series:
    if n_blocks < 4:
        raise ValueError("n_blocks must be at least 4 for surveillance metrics")
    block_ids = np.floor(np.arange(len(frame)) * n_blocks / len(frame)).astype(int)
    return pd.Series(np.minimum(block_ids, n_blocks - 1), index=frame.index, name="block_id")


def _ewma(values: pd.Series, alpha: float = 0.25) -> pd.Series:
    return values.astype(float).ewm(alpha=alpha, adjust=False).mean()


def _cusum_positive(values: pd.Series) -> pd.Series:
    arr = values.astype(float).to_numpy()
    baseline = float(np.median(arr[: max(3, len(arr) // 4)]))
    centered = arr - baseline
    running = []
    current = 0.0
    for value in centered:
        current = max(0.0, current + float(value))
        running.append(current)
    return pd.Series(running)


def _precision_recall_at_top_fraction(y_true: pd.Series, scores: pd.Series, fraction: float = 0.1) -> dict[str, float]:
    y = y_true.astype(int).reset_index(drop=True)
    s = scores.astype(float).reset_index(drop=True)
    k = max(1, int(np.ceil(len(s) * fraction)))
    top_idx = s.sort_values(ascending=False).head(k).index
    selected = pd.Series(False, index=s.index)
    selected.loc[top_idx] = True
    tp = int(((selected == 1) & (y == 1)).sum())
    selected_count = int(selected.sum())
    positives = int(y.sum())
    return {
        "top_fraction": float(fraction),
        "selected_blocks": selected_count,
        "precision_at_top_fraction": float(tp / selected_count) if selected_count else float("nan"),
        "recall_at_top_fraction": float(tp / positives) if positives else float("nan"),
    }


def _bootstrap_delta(
    y_true: pd.Series,
    proposed: pd.Series,
    control: pd.Series,
    n_bootstrap: int,
    seed: int,
) -> dict[str, float]:
    y = y_true.astype(int).to_numpy()
    a = proposed.astype(float).to_numpy()
    b = control.astype(float).to_numpy()
    rng = np.random.default_rng(seed)
    deltas = []
    for _ in range(n_bootstrap):
        idx = rng.choice(np.arange(len(y)), size=len(y), replace=True)
        if len(set(y[idx])) < 2:
            continue
        deltas.append(float(average_precision_score(y[idx], a[idx]) - average_precision_score(y[idx], b[idx])))
    if not deltas:
        return {"lower": float("nan"), "upper": float("nan"), "p_delta_le_zero": float("nan")}
    arr = np.array(deltas)
    return {
        "lower": float(np.quantile(arr, 0.025)),
        "upper": float(np.quantile(arr, 0.975)),
        "p_delta_le_zero": float(np.mean(arr <= 0)),
    }


def _build_block_features(
    train_h: pd.DataFrame,
    test_h: pd.DataFrame,
    n_blocks: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    columns = SELECTED_IEEE_HIERARCHY
    widest = max(train_h[column].nunique(dropna=False) + 1 for column in columns)
    spec = HierarchySpec("ieee_cis_temporal_multiresolution", columns, next_prime_at_least(max(2, widest)))
    train_encoded = encode_frame(train_h, spec)
    test_encoded = encode_frame(test_h, train_encoded.spec, digit_maps=train_encoded.digit_maps)
    normal_mask = train_h["isFraud"].astype(int).reset_index(drop=True) == 0
    rarity = _prefix_rarity_matrix(
        train_encoded.codes[normal_mask],
        test_encoded.codes,
        prime=int(train_encoded.spec.prime or 2),
        depth=len(columns),
    )
    rarity["p_adic_multiresolution_score"] = rarity.mean(axis=1)
    weights = np.arange(1, len(columns) + 1)
    rarity["p_adic_weighted_depth_score"] = rarity[[f"p_adic_depth{i}_rarity" for i in range(1, len(columns) + 1)]].dot(weights) / weights.sum()
    work = test_h.reset_index(drop=True).copy()
    work["flat_tuple_rarity"] = _flat_tuple_rarity(train_h, test_h, columns).reset_index(drop=True)
    for column in rarity.columns:
        work[column] = rarity[column].reset_index(drop=True)
    ordered = work.sort_values("TransactionDT", kind="mergesort").reset_index(drop=True)
    ordered["block_id"] = _assign_equal_count_blocks(ordered, n_blocks=n_blocks).to_numpy()
    rows = []
    for block_id, group in ordered.groupby("block_id", sort=True):
        labels = group["isFraud"].astype(int)
        row: dict[str, float | int] = {
            "block_id": int(block_id),
            "block_start_time": float(group["TransactionDT"].iloc[0]),
            "block_end_time": float(group["TransactionDT"].iloc[-1]),
            "rows": int(len(group)),
            "fraud_count": int(labels.sum()),
            "fraud_rate": float(labels.mean()),
            "flat_tuple_rarity_mean": float(group["flat_tuple_rarity"].mean()),
            "category_entropy_temporal": _entropy_for_frame(group, columns),
            "transaction_count_signal": float(len(group)),
            "p_adic_multiresolution_temporal": float(group["p_adic_multiresolution_score"].mean()),
            "p_adic_weighted_depth_temporal": float(group["p_adic_weighted_depth_score"].mean()),
            "p_adic_p95_temporal": float(group["p_adic_weighted_depth_score"].quantile(0.95)),
        }
        for depth in range(1, len(columns) + 1):
            row[f"p_adic_depth{depth}_mean"] = float(group[f"p_adic_depth{depth}_rarity"].mean())
        rows.append(row)
    blocks = pd.DataFrame(rows)
    blocks["p_adic_ewma_temporal"] = _ewma(blocks["p_adic_weighted_depth_temporal"])
    blocks["p_adic_cusum_temporal"] = _cusum_positive(blocks["p_adic_weighted_depth_temporal"])
    blocks["flat_ewma_temporal"] = _ewma(blocks["flat_tuple_rarity_mean"])
    blocks["flat_cusum_temporal"] = _cusum_positive(blocks["flat_tuple_rarity_mean"])
    threshold = float(blocks["fraud_rate"].quantile(0.75))
    blocks["high_fraud_block"] = (blocks["fraud_rate"] >= threshold).astype(int)
    metadata = pd.DataFrame(
        [
            {
                "prime": int(train_encoded.spec.prime or 0),
                "hierarchy": "|".join(columns),
                "high_fraud_block_threshold": threshold,
                "block_label_rule": "fraud_rate >= heldout_block_75th_percentile",
            }
        ]
    )
    return blocks, metadata


def _add_isolation_forest_score(blocks: pd.DataFrame) -> pd.Series:
    feature_cols = [
        "flat_tuple_rarity_mean",
        "category_entropy_temporal",
        "p_adic_multiresolution_temporal",
        "p_adic_weighted_depth_temporal",
    ]
    features = blocks[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if len(features) < 8:
        return pd.Series(np.zeros(len(features)), name="isolation_forest_block_features")
    model = IsolationForest(n_estimators=100, contamination="auto", random_state=17)
    model.fit(features)
    return pd.Series(-model.score_samples(features), name="isolation_forest_block_features")


def _write_temporal_figure(blocks: pd.DataFrame, claims: pd.DataFrame, path: Path) -> tuple[float, float]:
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=False)
    axes[0].plot(blocks["block_id"], blocks["fraud_rate"], label="held-out block fraud rate", color="black", linewidth=1.6)
    axes[0].plot(blocks["block_id"], blocks["p_adic_weighted_depth_temporal"], label="p-adic weighted depth signal", alpha=0.85)
    axes[0].plot(blocks["block_id"], blocks["flat_tuple_rarity_mean"], label="flat rarity control", alpha=0.75)
    axes[0].set_ylabel("Block signal")
    axes[0].legend(fontsize=7, loc="best")
    top = claims.sort_values("auprc", ascending=True).tail(6)
    colors = ["#444444" if "p_adic" not in method else "#1f77b4" for method in top["method"]]
    axes[1].barh(top["method"], top["auprc"], color=colors)
    axes[1].set_xlabel("Block high-fraud AUPRC")
    axes[1].tick_params(axis="y", labelsize=7)
    fig.suptitle("IEEE-CIS temporal surveillance: p-adic multiresolution vs controls", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=600)
    plt.close(fig)
    with Image.open(path) as image:
        return tuple(float(x) for x in image.info.get("dpi", (600.0, 600.0)))


def run_ieee_temporal_surveillance_audit(
    data_root: str | Path = DEFAULT_OFFICIAL_ROOT,
    output_root: str | Path = "outputs/p_adic_ieee_cis_temporal_surveillance",
    max_rows: int | None = None,
    n_blocks: int = 96,
    bootstrap_samples: int = 500,
) -> dict[str, object]:
    output_root = Path(output_root)
    _ensure_dirs(output_root)
    data_root = Path(data_root)
    transaction, identity = _load_ieee(data_root)
    if max_rows is not None:
        transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(int(max_rows)).copy()
        if identity is not None:
            identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity)
    train_h, test_h = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    blocks, meta_frame = _build_block_features(train_h, test_h, n_blocks=n_blocks)
    blocks["isolation_forest_block_features"] = _add_isolation_forest_score(blocks)
    y_block = blocks["high_fraud_block"].astype(int)
    method_columns = {
        "p_adic_multiresolution_temporal": "proposed_temporal_signal",
        "p_adic_weighted_depth_temporal": "proposed_temporal_signal",
        "p_adic_ewma_temporal": "proposed_temporal_signal",
        "p_adic_cusum_temporal": "proposed_temporal_signal",
        "flat_tuple_rarity_temporal": "flat_control",
        "flat_ewma_temporal": "flat_control",
        "flat_cusum_temporal": "flat_control",
        "category_entropy_temporal": "entropy_control",
        "transaction_count_signal": "count_control",
        "isolation_forest_block_features": "unsupervised_block_context",
    }
    score_lookup = {
        "flat_tuple_rarity_temporal": blocks["flat_tuple_rarity_mean"],
        **{name: blocks[name] for name in method_columns if name in blocks.columns},
    }
    rows = []
    for method, family in method_columns.items():
        scores = score_lookup[method]
        top = _precision_recall_at_top_fraction(y_block, scores, fraction=0.1)
        rows.append(
            {
                "method": method,
                "family": family,
                "auprc": _safe_metric(average_precision_score, y_block, scores),
                "roc_auc": _safe_metric(roc_auc_score, y_block, scores),
                **top,
            }
        )
    claims = pd.DataFrame(rows)
    proposed_methods = claims[claims["family"] == "proposed_temporal_signal"]
    control_methods = claims[claims["family"].isin(["flat_control", "entropy_control", "count_control", "unsupervised_block_context"])]
    best_proposed_row = proposed_methods.sort_values("auprc", ascending=False).iloc[0]
    best_control_row = control_methods.sort_values("auprc", ascending=False).iloc[0]
    best_proposed_scores = score_lookup[str(best_proposed_row["method"])]
    best_control_scores = score_lookup[str(best_control_row["method"])]
    delta_ci = _bootstrap_delta(y_block, best_proposed_scores, best_control_scores, n_bootstrap=bootstrap_samples, seed=29)
    prevalence = float(y_block.mean())
    claims["best_proposed_method"] = str(best_proposed_row["method"])
    claims["best_control_method"] = str(best_control_row["method"])
    claims["best_proposed_auprc"] = float(best_proposed_row["auprc"])
    claims["best_control_auprc"] = float(best_control_row["auprc"])
    claims["delta_best_proposed_vs_best_control_auprc"] = float(best_proposed_row["auprc"] - best_control_row["auprc"])
    claims["bootstrap_delta_lower"] = delta_ci["lower"]
    claims["bootstrap_delta_upper"] = delta_ci["upper"]
    claims["bootstrap_p_delta_le_zero"] = delta_ci["p_delta_le_zero"]
    passed = (
        float(best_proposed_row["auprc"]) > float(best_control_row["auprc"])
        and delta_ci["lower"] > 0
        and float(best_proposed_row["auprc"]) >= prevalence
    )
    claims["claim_status"] = "q1_candidate_temporal_signal_passed_controls" if passed else "diagnostic_only_failed_q1_temporal_gate"
    claims["claim_scope"] = "official_ieee_cis_block_temporal_surveillance"
    claims_path = output_root / "tables" / "p_adic_ieee_cis_temporal_surveillance_claims.csv"
    blocks_path = output_root / "metrics" / "p_adic_ieee_cis_temporal_surveillance_blocks.csv"
    metadata_path = output_root / "manifests" / "p_adic_ieee_cis_temporal_surveillance_metadata.json"
    figure_path = output_root / "figures" / "p_adic_ieee_cis_temporal_surveillance.png"
    claims.to_csv(claims_path, index=False)
    claims.to_markdown(claims_path.with_suffix(".md"), index=False)
    blocks.to_csv(blocks_path, index=False)
    meta = meta_frame.iloc[0].to_dict()
    figure_dpi = _write_temporal_figure(blocks, claims, figure_path)
    metadata = {
        "dataset": "official_ieee_cis_temporal_surveillance",
        "data_root": str(data_root),
        "synthetic_data_used": False,
        "rows": int(len(frame)),
        "train_rows": int(len(train_h)),
        "test_rows": int(len(test_h)),
        "n_blocks": int(n_blocks),
        "test_block_positive_rate": prevalence,
        "hierarchy": str(meta["hierarchy"]),
        "prime": int(meta["prime"]),
        "best_proposed_method": str(best_proposed_row["method"]),
        "best_control_method": str(best_control_row["method"]),
        "claim_status": str(claims["claim_status"].iloc[0]),
        "figure_dpi": list(figure_dpi),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {
        "claims": claims,
        "blocks": blocks,
        "metadata": metadata,
        "artifacts": {
            "claims_table": str(claims_path),
            "block_features": str(blocks_path),
            "metadata": str(metadata_path),
            "figure": str(figure_path),
            "figure_dpi": figure_dpi,
        },
    }


def main() -> None:
    result = run_ieee_temporal_surveillance_audit()
    print(json.dumps(result["metadata"], indent=2))
    print(result["claims"].to_json(orient="records", indent=2))


if __name__ == "__main__":
    main()
