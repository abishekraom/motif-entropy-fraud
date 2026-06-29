"""Train-only p-adic branch-signature interpretability audit on IEEE-CIS.

This route treats p-adic hierarchy as an interpretable branch surveillance tool:
select suspicious coarse-to-fine prefixes on the training period only, then audit
held-out enrichment, coverage, and recall against flat full-tuple branch rules.
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

from motif_fraud.p_adic.ieee_pipeline import _load_ieee, _prepare_ieee, DEFAULT_OFFICIAL_ROOT
from motif_fraud.p_adic.splits import temporal_train_test_split
from motif_fraud.p_adic.temporal_surveillance import SELECTED_IEEE_HIERARCHY


def _ensure_dirs(output_root: Path) -> None:
    for subdir in ("tables", "figures", "metrics", "manifests"):
        (output_root / subdir).mkdir(parents=True, exist_ok=True)


def _prefix_key_frame(frame: pd.DataFrame, columns: tuple[str, ...], depth: int) -> pd.Series:
    return frame[list(columns[:depth])].astype(str).agg("|".join, axis=1)


def _select_prefix_branches(
    train: pd.DataFrame,
    columns: tuple[str, ...],
    min_train_support: int,
    top_k: int,
    min_depth: int = 2,
    max_train_support_fraction: float = 0.25,
    min_train_lift: float = 1.1,
) -> pd.DataFrame:
    train_prevalence = float(train["isFraud"].astype(int).mean())
    max_support = max(min_train_support, int(len(train) * max_train_support_fraction))
    rows = []
    for depth in range(min_depth, len(columns) + 1):
        keys = _prefix_key_frame(train, columns, depth)
        work = pd.DataFrame({"key": keys, "isFraud": train["isFraud"].astype(int)})
        grouped = work.groupby("key", sort=False)["isFraud"].agg(["count", "sum", "mean"]).reset_index()
        grouped["train_lift_candidate"] = grouped["mean"] / max(train_prevalence, 1e-12)
        grouped = grouped[
            (grouped["count"] >= min_train_support)
            & (grouped["count"] <= max_support)
            & (grouped["train_lift_candidate"] >= min_train_lift)
        ].copy()
        grouped["depth"] = depth
        grouped["branch_type"] = "p_adic_prefix"
        grouped["train_support"] = grouped["count"].astype(int)
        grouped["train_fraud_count"] = grouped["sum"].astype(int)
        grouped["train_fraud_rate"] = grouped["mean"].astype(float)
        grouped["train_lift"] = grouped["train_fraud_rate"] / max(train_prevalence, 1e-12)
        # Conservative enrichment score: smoothed lift weighted by fraud evidence,
        # with overly broad shallow branches excluded above using train-only support.
        grouped["selection_score"] = np.log1p(grouped["train_lift"]) * np.sqrt(grouped["train_fraud_count"].clip(lower=1))
        rows.append(grouped[["branch_type", "depth", "key", "train_support", "train_fraud_count", "train_fraud_rate", "train_lift", "selection_score"]])
    if not rows:
        return pd.DataFrame(columns=["branch_type", "depth", "key", "train_support", "train_fraud_count", "train_fraud_rate", "train_lift", "selection_score"])
    all_branches = pd.concat(rows, ignore_index=True)
    return all_branches.sort_values(["selection_score", "train_support"], ascending=False).head(top_k).reset_index(drop=True)


def _select_flat_branches(train: pd.DataFrame, columns: tuple[str, ...], min_train_support: int, top_k: int) -> pd.DataFrame:
    train_prevalence = float(train["isFraud"].astype(int).mean())
    keys = _prefix_key_frame(train, columns, len(columns))
    work = pd.DataFrame({"key": keys, "isFraud": train["isFraud"].astype(int)})
    grouped = work.groupby("key", sort=False)["isFraud"].agg(["count", "sum", "mean"]).reset_index()
    grouped["train_lift_candidate"] = grouped["mean"] / max(train_prevalence, 1e-12)
    grouped = grouped[(grouped["count"] >= min_train_support) & (grouped["train_lift_candidate"] >= 1.1)].copy()
    grouped["branch_type"] = "flat_tuple"
    grouped["depth"] = len(columns)
    grouped["train_support"] = grouped["count"].astype(int)
    grouped["train_fraud_count"] = grouped["sum"].astype(int)
    grouped["train_fraud_rate"] = grouped["mean"].astype(float)
    grouped["train_lift"] = grouped["train_fraud_rate"] / max(train_prevalence, 1e-12)
    grouped["selection_score"] = np.log1p(grouped["train_lift"]) * np.sqrt(grouped["train_support"])
    return grouped[["branch_type", "depth", "key", "train_support", "train_fraud_count", "train_fraud_rate", "train_lift", "selection_score"]].sort_values(
        ["selection_score", "train_support"], ascending=False
    ).head(top_k).reset_index(drop=True)


def _alert_mask(test: pd.DataFrame, columns: tuple[str, ...], branches: pd.DataFrame) -> pd.Series:
    mask = pd.Series(False, index=test.index)
    for depth, group in branches.groupby("depth"):
        keys = set(group["key"].astype(str))
        if not keys:
            continue
        test_keys = _prefix_key_frame(test, columns, int(depth))
        mask = mask | test_keys.isin(keys)
    return mask.reset_index(drop=True)


def _truncate_to_matched_coverage(
    test: pd.DataFrame,
    columns: tuple[str, ...],
    ranked_branches: pd.DataFrame,
    target_alert_rows: int,
) -> pd.DataFrame:
    """Keep train-ranked branches until unlabeled held-out coverage reaches target."""
    if ranked_branches.empty:
        return ranked_branches.copy()
    # Common fast path for flat tuple controls: all candidate branches share depth.
    if ranked_branches["depth"].nunique() == 1:
        depth = int(ranked_branches["depth"].iloc[0])
        test_keys = _prefix_key_frame(test, columns, depth)
        selected_keys: set[str] = set()
        selected_indices = []
        mask = pd.Series(False, index=test.index)
        for idx, row in ranked_branches.iterrows():
            selected_keys.add(str(row["key"]))
            selected_indices.append(idx)
            mask = test_keys.isin(selected_keys)
            if int(mask.sum()) >= target_alert_rows:
                return ranked_branches.loc[selected_indices].reset_index(drop=True)
        return ranked_branches.loc[selected_indices].reset_index(drop=True)
    selected_rows = []
    for _, row in ranked_branches.iterrows():
        selected_rows.append(row)
        selected = pd.DataFrame(selected_rows)
        if int(_alert_mask(test, columns, selected).sum()) >= target_alert_rows:
            return selected.reset_index(drop=True)
    return pd.DataFrame(selected_rows).reset_index(drop=True)


def _bootstrap_precision_delta(y: pd.Series, mask_a: pd.Series, mask_b: pd.Series, n_bootstrap: int = 500, seed: int = 19) -> dict[str, float]:
    """Bootstrap alert precision delta by resampling alert pools directly.

    This avoids repeatedly resampling the entire held-out transaction table. The
    estimand is the uncertainty of alert fraud-rate difference for the two
    pre-selected train-only branch sets.
    """
    y_arr = y.astype(int).to_numpy()
    a_values = y_arr[mask_a.astype(bool).to_numpy()]
    b_values = y_arr[mask_b.astype(bool).to_numpy()]
    if len(a_values) == 0 or len(b_values) == 0:
        return {"lower": float("nan"), "upper": float("nan"), "p_delta_le_zero": float("nan")}
    rng = np.random.default_rng(seed)
    deltas = []
    for _ in range(n_bootstrap):
        a_sample = rng.choice(a_values, size=len(a_values), replace=True)
        b_sample = rng.choice(b_values, size=len(b_values), replace=True)
        deltas.append(float(a_sample.mean() - b_sample.mean()))
    arr = np.array(deltas)
    return {
        "lower": float(np.quantile(arr, 0.025)),
        "upper": float(np.quantile(arr, 0.975)),
        "p_delta_le_zero": float(np.mean(arr <= 0)),
    }


def _summarize_alerts(method: str, family: str, y_test: pd.Series, mask: pd.Series, branches: pd.DataFrame, prevalence: float) -> dict[str, object]:
    selected = mask.astype(bool)
    frauds = y_test.astype(int)
    alert_rows = int(selected.sum())
    alert_frauds = int(frauds[selected].sum()) if alert_rows else 0
    total_frauds = int(frauds.sum())
    alert_rate = float(alert_frauds / alert_rows) if alert_rows else float("nan")
    return {
        "method": method,
        "family": family,
        "selected_train_branches": int(len(branches)),
        "test_alert_rows": alert_rows,
        "test_alert_coverage": float(alert_rows / len(frauds)),
        "test_alert_fraud_count": alert_frauds,
        "test_alert_fraud_rate": alert_rate,
        "test_alert_lift_vs_prevalence": float(alert_rate / max(prevalence, 1e-12)) if alert_rows else float("nan"),
        "test_fraud_recall_in_alerts": float(alert_frauds / total_frauds) if total_frauds else float("nan"),
    }


def _write_branch_figure(claims: pd.DataFrame, path: Path, dpi: int = 600) -> tuple[float, float]:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    colors = ["#1f77b4" if "p_adic" in method else "#475569" for method in claims["method"]]
    axes[0].bar(claims["method"], claims["test_alert_lift_vs_prevalence"], color=colors)
    axes[0].set_ylabel("Held-out alert lift")
    axes[0].tick_params(axis="x", rotation=25, labelsize=7)
    axes[1].bar(claims["method"], claims["test_fraud_recall_in_alerts"], color=colors)
    axes[1].set_ylabel("Fraud recall in alerts")
    axes[1].tick_params(axis="x", rotation=25, labelsize=7)
    fig.suptitle("Train-only IEEE-CIS branch signatures", fontsize=10)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    with Image.open(path) as image:
        return tuple(float(v) for v in image.info.get("dpi", (dpi, dpi)))


def run_ieee_branch_signature_audit(
    data_root: str | Path = DEFAULT_OFFICIAL_ROOT,
    output_root: str | Path = "outputs/p_adic_ieee_cis_branch_signatures",
    max_rows: int | None = None,
    min_train_support: int = 200,
    top_k: int = 30,
    bootstrap_samples: int = 500,
) -> dict[str, object]:
    output_root = Path(output_root)
    _ensure_dirs(output_root)
    data_root = Path(data_root)
    transaction, identity = _load_ieee(data_root)
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    if max_rows is not None:
        frame = frame.iloc[: int(max_rows)].copy()
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)
    columns = SELECTED_IEEE_HIERARCHY
    p_branches = _select_prefix_branches(train, columns, min_train_support=min_train_support, top_k=top_k)
    f_branches = _select_flat_branches(train, columns, min_train_support=min_train_support, top_k=top_k)
    f_ranked_for_coverage = _select_flat_branches(train, columns, min_train_support=min_train_support, top_k=max(top_k * 10, top_k + 1))
    p_mask = _alert_mask(test, columns, p_branches)
    f_mask = _alert_mask(test, columns, f_branches)
    f_matched_branches = _truncate_to_matched_coverage(test, columns, f_ranked_for_coverage, target_alert_rows=int(p_mask.sum()))
    f_matched_mask = _alert_mask(test, columns, f_matched_branches)
    y_test = test["isFraud"].astype(int).reset_index(drop=True)
    prevalence = float(y_test.mean())
    rows = [
        _summarize_alerts("p_adic_prefix_branch_signatures", "proposed_interpretability", y_test, p_mask, p_branches, prevalence),
        _summarize_alerts("flat_tuple_branch_signatures", "flat_interpretability_control", y_test, f_mask, f_branches, prevalence),
        _summarize_alerts("flat_tuple_matched_coverage_signatures", "flat_interpretability_control", y_test, f_matched_mask, f_matched_branches, prevalence),
    ]
    claims = pd.DataFrame(rows)
    p_row = claims[claims["method"] == "p_adic_prefix_branch_signatures"].iloc[0]
    control_rows = claims[claims["family"] == "flat_interpretability_control"]
    best_control = control_rows.sort_values("test_alert_fraud_rate", ascending=False).iloc[0]
    best_control_mask = f_mask if best_control["method"] == "flat_tuple_branch_signatures" else f_matched_mask
    delta = _bootstrap_precision_delta(y_test, p_mask, best_control_mask, n_bootstrap=bootstrap_samples, seed=19)
    claims["best_flat_control_method"] = str(best_control["method"])
    claims["delta_padic_vs_best_flat_alert_fraud_rate"] = float(p_row["test_alert_fraud_rate"] - best_control["test_alert_fraud_rate"])
    claims["bootstrap_delta_precision_lower"] = delta["lower"]
    claims["bootstrap_delta_precision_upper"] = delta["upper"]
    claims["bootstrap_p_delta_precision_le_zero"] = delta["p_delta_le_zero"]
    passed = (
        float(p_row["test_alert_lift_vs_prevalence"]) > float(best_control["test_alert_lift_vs_prevalence"])
        and float(p_row["test_fraud_recall_in_alerts"]) >= float(best_control["test_fraud_recall_in_alerts"])
        and delta["lower"] > 0
    )
    claims["claim_status"] = "q1_candidate_interpretability_passed_controls" if passed else "diagnostic_only_failed_q1_interpretability_gate"
    claims["claim_scope"] = "official_ieee_cis_train_only_branch_interpretability"
    claims_path = output_root / "tables" / "p_adic_ieee_cis_branch_signature_claims.csv"
    branch_path = output_root / "tables" / "p_adic_ieee_cis_selected_branch_signatures.csv"
    figure_path = output_root / "figures" / "p_adic_ieee_cis_branch_signature_lift.png"
    metadata_path = output_root / "manifests" / "p_adic_ieee_cis_branch_signature_metadata.json"
    selected = pd.concat([p_branches, f_branches, f_matched_branches], ignore_index=True)
    claims.to_csv(claims_path, index=False)
    claims.to_markdown(claims_path.with_suffix(".md"), index=False)
    selected.to_csv(branch_path, index=False)
    figure_dpi = _write_branch_figure(claims, figure_path)
    metadata = {
        "dataset": "official_ieee_cis_branch_signatures",
        "data_root": str(data_root),
        "synthetic_data_used": False,
        "selection_scope": "train_only",
        "rows": int(len(frame)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "test_fraud_rate": prevalence,
        "min_train_support": int(min_train_support),
        "top_k": int(top_k),
        "hierarchy": "|".join(columns),
        "claim_status": str(claims["claim_status"].iloc[0]),
        "figure_dpi": list(figure_dpi),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {
        "claims": claims,
        "selected_branches": selected,
        "metadata": metadata,
        "artifacts": {
            "claims_table": str(claims_path),
            "selected_branches": str(branch_path),
            "metadata": str(metadata_path),
            "figure": str(figure_path),
            "figure_dpi": figure_dpi,
        },
    }


def main() -> None:
    result = run_ieee_branch_signature_audit()
    print(json.dumps(result["metadata"], indent=2))
    print(result["claims"].to_json(orient="records", indent=2))


if __name__ == "__main__":
    main()
