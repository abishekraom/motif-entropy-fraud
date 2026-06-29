"""Strong official IEEE-CIS baselines for p-adic SPL claim discipline.

Runs pre-specified stronger tabular baselines on real official IEEE-CIS data only.
The goal is not to make the p-adic result look good; it is to expose whether the
p-adic signal is competitive or merely complementary against stronger models.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from sklearn.metrics import average_precision_score, roc_auc_score

from motif_fraud.p_adic.ieee_pipeline import _load_ieee, _prepare_ieee
from motif_fraud.p_adic.official_baselines import _padic_train_test_scores, _read_p_adic_row
from motif_fraud.p_adic.splits import temporal_train_test_split

CATEGORICAL_FEATURES = (
    "ProductCD",
    "card4",
    "card6",
    "P_emaildomain",
    "R_emaildomain",
    "DeviceType",
    "DeviceInfo",
)
NUMERIC_FEATURES = (
    "TransactionAmt",
    "card1",
    "card2",
    "card3",
    "card5",
    "addr1",
    "addr2",
    "dist1",
    "dist2",
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "C6",
    "C7",
    "C8",
    "C9",
    "C10",
    "C11",
    "C12",
    "C13",
    "C14",
    "D1",
    "D2",
    "D3",
    "D4",
    "D5",
    "D10",
    "D11",
    "D15",
)


def _safe_metric(func, y_true: pd.Series, scores: pd.Series) -> float:
    if len(set(y_true.astype(int))) < 2:
        return float("nan")
    return float(func(y_true.astype(int), scores.astype(float)))


def _available_methods() -> dict[str, bool]:
    return {name: importlib.util.find_spec(name) is not None for name in ("lightgbm", "catboost", "xgboost")}


def _prepare_tree_features(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    cat_cols = [c for c in CATEGORICAL_FEATURES if c in train.columns]
    num_cols = [c for c in NUMERIC_FEATURES if c in train.columns]
    train_x = pd.DataFrame(index=train.index)
    test_x = pd.DataFrame(index=test.index)
    for col in cat_cols:
        train_x[col] = train[col].astype("object").where(train[col].notna(), "__MISSING__").astype(str)
        test_x[col] = test[col].astype("object").where(test[col].notna(), "__MISSING__").astype(str)
    for col in num_cols:
        median = float(train[col].median())
        train_x[col] = train[col].fillna(median).astype(float)
        test_x[col] = test[col].fillna(median).astype(float)
    return train_x, test_x, cat_cols, num_cols


def _append_row(rows: list[dict[str, object]], method: str, family: str, role: str, y_test: pd.Series, scores: pd.Series) -> None:
    rows.append(
        {
            "method": method,
            "family": family,
            "auprc": _safe_metric(average_precision_score, y_test, scores),
            "roc_auc": _safe_metric(roc_auc_score, y_test, scores),
            "claim_role": role,
        }
    )


def _score_lightgbm(train_x: pd.DataFrame, y_train: pd.Series, test_x: pd.DataFrame, cat_cols: list[str], iterations: int) -> pd.Series:
    import lightgbm as lgb

    x_train = train_x.copy()
    x_test = test_x.copy()
    for col in cat_cols:
        categories = pd.Index(x_train[col].astype(str).unique())
        x_train[col] = pd.Categorical(x_train[col].astype(str), categories=categories)
        x_test[col] = pd.Categorical(x_test[col].astype(str), categories=categories)
    scale_pos_weight = max(1.0, float((len(y_train) - y_train.sum()) / max(1, y_train.sum())))
    model = lgb.LGBMClassifier(
        n_estimators=iterations,
        learning_rate=0.05,
        num_leaves=64,
        max_depth=-1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary",
        class_weight=None,
        scale_pos_weight=scale_pos_weight,
        random_state=41,
        n_jobs=-1,
        verbose=-1,
    )
    model.fit(x_train, y_train.astype(int), categorical_feature=cat_cols)
    return pd.Series(model.predict_proba(x_test)[:, 1], index=test_x.index)


def _score_catboost(train_x: pd.DataFrame, y_train: pd.Series, test_x: pd.DataFrame, cat_cols: list[str], iterations: int) -> pd.Series:
    from catboost import CatBoostClassifier, Pool

    cat_indices = [train_x.columns.get_loc(c) for c in cat_cols]
    train_pool = Pool(train_x, y_train.astype(int), cat_features=cat_indices)
    test_pool = Pool(test_x, cat_features=cat_indices)
    scale_pos_weight = max(1.0, float((len(y_train) - y_train.sum()) / max(1, y_train.sum())))
    model = CatBoostClassifier(
        iterations=iterations,
        depth=6,
        learning_rate=0.08,
        loss_function="Logloss",
        eval_metric="AUC",
        scale_pos_weight=scale_pos_weight,
        random_seed=43,
        verbose=False,
        allow_writing_files=False,
    )
    model.fit(train_pool)
    return pd.Series(model.predict_proba(test_pool)[:, 1], index=test_x.index)


def _score_xgboost(train_x: pd.DataFrame, y_train: pd.Series, test_x: pd.DataFrame, cat_cols: list[str], iterations: int) -> pd.Series:
    from xgboost import XGBClassifier

    x_train = train_x.copy()
    x_test = test_x.copy()
    for col in cat_cols:
        categories = pd.Index(x_train[col].astype(str).unique())
        codes = {v: i for i, v in enumerate(categories)}
        x_train[col] = x_train[col].astype(str).map(codes).fillna(-1).astype(int)
        x_test[col] = x_test[col].astype(str).map(codes).fillna(-1).astype(int)
    scale_pos_weight = max(1.0, float((len(y_train) - y_train.sum()) / max(1, y_train.sum())))
    model = XGBClassifier(
        n_estimators=iterations,
        max_depth=6,
        learning_rate=0.06,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="aucpr",
        scale_pos_weight=scale_pos_weight,
        random_state=47,
        n_jobs=-1,
        tree_method="hist",
    )
    model.fit(x_train, y_train.astype(int))
    return pd.Series(model.predict_proba(x_test)[:, 1], index=test_x.index)


def _write_figure(table: pd.DataFrame, path: Path, dpi: int = 600) -> tuple[float, float]:
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_table = table.sort_values("auprc", ascending=True)
    colors = ["#7c3aed" if r in {"primary_method", "p_adic_augmented_strong_baseline"} else "#475569" for r in plot_table["claim_role"]]
    plt.figure(figsize=(7.2, 4.8))
    plt.barh(plot_table["method"], plot_table["auprc"], color=colors)
    plt.xlabel("AUPRC")
    plt.title("Official IEEE-CIS strong baseline audit")
    plt.tight_layout()
    plt.savefig(path, dpi=dpi)
    plt.close()
    return tuple(float(v) for v in Image.open(path).info.get("dpi", (dpi, dpi)))


def run_ieee_strong_baseline_audit(
    data_root: str | Path = Path(r"D:/motif-entropy-fraud/ieee-fraud-detection"),
    p_adic_claims_path: str | Path = Path("outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_claims.csv"),
    output_root: str | Path = Path("outputs/p_adic_ieee_cis_official"),
    train_fraction: float = 0.7,
    max_rows: int | None = None,
    iterations: int = 200,
) -> dict[str, object]:
    """Run pre-specified strong tabular baselines on official IEEE-CIS."""
    data_root = Path(data_root)
    output_root = Path(output_root)
    transaction, identity = _load_ieee(data_root)
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    if max_rows is not None:
        frame = frame.iloc[:max_rows].copy()
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=train_fraction)
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)
    y_train = train["isFraud"].astype(int).reset_index(drop=True)
    y_test = test["isFraud"].astype(int).reset_index(drop=True)
    train_x, test_x, cat_cols, num_cols = _prepare_tree_features(train, test)
    p_train, p_test = _padic_train_test_scores(train, test)
    train_x_plus = train_x.copy()
    test_x_plus = test_x.copy()
    train_x_plus["p_adic_signal"] = p_train
    test_x_plus["p_adic_signal"] = p_test

    rows: list[dict[str, object]] = [_read_p_adic_row(Path(p_adic_claims_path))]
    availability = _available_methods()
    if availability["lightgbm"]:
        scores = _score_lightgbm(train_x, y_train, test_x, cat_cols, iterations)
        _append_row(rows, "lightgbm_compact_tabular", "strong_supervised_baseline", "strong_context_baseline", y_test, scores)
        scores_plus = _score_lightgbm(train_x_plus, y_train, test_x_plus, cat_cols, iterations)
        _append_row(rows, "lightgbm_compact_tabular_plus_padic", "strong_supervised_baseline", "p_adic_augmented_strong_baseline", y_test, scores_plus)
    if availability["catboost"]:
        scores = _score_catboost(train_x, y_train, test_x, cat_cols, iterations)
        _append_row(rows, "catboost_compact_tabular", "strong_supervised_baseline", "strong_context_baseline", y_test, scores)
        scores_plus = _score_catboost(train_x_plus, y_train, test_x_plus, cat_cols, iterations)
        _append_row(rows, "catboost_compact_tabular_plus_padic", "strong_supervised_baseline", "p_adic_augmented_strong_baseline", y_test, scores_plus)
    if availability["xgboost"]:
        scores = _score_xgboost(train_x, y_train, test_x, cat_cols, iterations)
        _append_row(rows, "xgboost_compact_tabular", "strong_supervised_baseline", "strong_context_baseline", y_test, scores)
        scores_plus = _score_xgboost(train_x_plus, y_train, test_x_plus, cat_cols, iterations)
        _append_row(rows, "xgboost_compact_tabular_plus_padic", "strong_supervised_baseline", "p_adic_augmented_strong_baseline", y_test, scores_plus)
    if len(rows) == 1:
        raise RuntimeError("No strong baseline package available. Install lightgbm, catboost, or xgboost.")

    table = pd.DataFrame(rows)
    table["dataset"] = "official_ieee_cis"
    table["train_rows"] = int(len(train))
    table["test_rows"] = int(len(test))
    table["fraud_rate_test"] = float(y_test.mean())
    table["temporal_split"] = True
    table["iterations"] = int(iterations)
    table["categorical_features"] = "|".join(cat_cols)
    table["numeric_feature_count"] = len(num_cols)
    p_adic_auprc = float(table.loc[table["method"] == "p_adic_selected_hierarchy", "auprc"].iloc[0])
    best_strong = float(table.loc[table["claim_role"] == "strong_context_baseline", "auprc"].max())
    best_augmented = float(table.loc[table["claim_role"] == "p_adic_augmented_strong_baseline", "auprc"].max())
    table["p_adic_minus_best_strong_auprc"] = p_adic_auprc - best_strong
    table["best_augmented_minus_best_strong_auprc"] = best_augmented - best_strong
    table["claim_status"] = "strong_baselines_expose_detector_superiority_failure"
    table.loc[table["claim_role"] == "p_adic_augmented_strong_baseline", "claim_status"] = (
        "p_adic_augmented_strong_baseline_checked"
    )

    table_path = output_root / "tables" / "p_adic_ieee_cis_strong_baseline_comparison.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(table_path, index=False)
    table.to_markdown(table_path.with_suffix(".md"), index=False)
    figure_path = output_root / "figures" / "p_adic_ieee_cis_strong_baseline_comparison.png"
    figure_dpi = _write_figure(table, figure_path)
    metadata = {
        "available_methods": availability,
        "iterations": iterations,
        "rows": int(len(frame)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "best_strong_auprc": best_strong,
        "best_augmented_auprc": best_augmented,
        "p_adic_auprc": p_adic_auprc,
        "p_adic_minus_best_strong_auprc": p_adic_auprc - best_strong,
        "best_augmented_minus_best_strong_auprc": best_augmented - best_strong,
    }
    metadata_path = output_root / "run_metadata_strong_baselines.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {
        "baseline_table": table,
        "metadata": metadata,
        "artifacts": {"baseline_table": table_path, "figure": figure_path, "metadata": metadata_path},
        "figure_dpi": figure_dpi,
    }


if __name__ == "__main__":
    result = run_ieee_strong_baseline_audit()
    print(json.dumps(result["metadata"], indent=2))
    print(result["baseline_table"].to_json(orient="records", indent=2))
    print("figure_dpi", result["figure_dpi"])
