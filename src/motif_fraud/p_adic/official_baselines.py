"""Official IEEE-CIS baseline audit for SPL/Q1 positioning.

This module intentionally uses only the official Kaggle IEEE-CIS files already
present on disk. It does not generate synthetic research data.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from motif_fraud.p_adic.encoding import HierarchySpec, encode_frame
from motif_fraud.p_adic.ieee_pipeline import IEEE_COLUMNS, _load_ieee, _prepare_ieee
from motif_fraud.p_adic.metrics import next_prime_at_least
from motif_fraud.p_adic.scoring import PAdicPrefixRarityScorer
from motif_fraud.p_adic.splits import temporal_train_test_split


def _safe_metric(func, y_true: pd.Series, scores: pd.Series) -> float:
    if len(set(y_true.astype(int))) < 2:
        return float("nan")
    return float(func(y_true.astype(int), scores.astype(float)))


def _frequency_encode(train: pd.DataFrame, test: pd.DataFrame, columns: tuple[str, ...]) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_features = pd.DataFrame(index=train.index)
    test_features = pd.DataFrame(index=test.index)
    for column in columns:
        values_train = train[column].astype("object").where(train[column].notna(), "__MISSING__")
        values_test = test[column].astype("object").where(test[column].notna(), "__MISSING__")
        frequencies = values_train.value_counts(normalize=True)
        train_features[f"freq_{column}"] = values_train.map(frequencies).fillna(0.0).astype(float)
        test_features[f"freq_{column}"] = values_test.map(frequencies).fillna(0.0).astype(float)
    for column in ("TransactionAmt", "dist1", "dist2"):
        if column in train.columns:
            median = float(train[column].median())
            train_features[column] = train[column].fillna(median).astype(float)
            test_features[column] = test[column].fillna(median).astype(float)
    return train_features, test_features


def _score_logistic(train_x: pd.DataFrame, train_y: pd.Series, test_x: pd.DataFrame) -> pd.Series:
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=1000, solver="lbfgs"),
    )
    model.fit(train_x, train_y.astype(int))
    return pd.Series(model.predict_proba(test_x)[:, 1], index=test_x.index)


def _score_isolation_forest(train_x: pd.DataFrame, train_y: pd.Series, test_x: pd.DataFrame) -> pd.Series:
    normal_x = train_x[train_y.astype(int) == 0]
    model = IsolationForest(n_estimators=150, contamination="auto", random_state=13, n_jobs=-1)
    model.fit(normal_x)
    # sklearn returns larger decision_function for normal samples; invert for anomaly/fraud score.
    return pd.Series(-model.decision_function(test_x), index=test_x.index)


def _padic_train_test_scores(
    train: pd.DataFrame,
    test: pd.DataFrame,
    label_column: str = "isFraud",
    columns: tuple[str, ...] = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain"),
) -> tuple[pd.Series, pd.Series]:
    widest = max(train[column].nunique(dropna=False) + 1 for column in columns)
    prime = next_prime_at_least(max(2, widest))
    spec = HierarchySpec("baseline_p_adic_signal", columns, prime)
    train_encoded = encode_frame(train, spec)
    test_encoded = encode_frame(test, train_encoded.spec, digit_maps=train_encoded.digit_maps)
    scorer = PAdicPrefixRarityScorer(prime=prime, depth=len(columns), weighting="weighted_deep").fit(
        train_encoded.codes[train[label_column].astype(int) == 0]
    )
    return scorer.score(train_encoded.codes).reset_index(drop=True), scorer.score(test_encoded.codes).reset_index(drop=True)


def _read_p_adic_row(path: Path) -> dict[str, object]:
    claims = pd.read_csv(path)
    row = claims.loc[claims["method"].astype(str).str.contains("p_adic")].iloc[0]
    return {
        "method": "p_adic_selected_hierarchy",
        "family": "proposed_unsupervised_signal",
        "auprc": float(row["auprc"]),
        "roc_auc": float(row["roc_auc"]),
        "claim_role": "primary_method",
    }


def _write_baseline_figure(table: pd.DataFrame, path: Path, dpi: int = 600) -> tuple[float, float]:
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_table = table.sort_values("auprc", ascending=True)
    colors = ["#8b5cf6" if role == "primary_method" else "#64748b" for role in plot_table["claim_role"]]
    plt.figure(figsize=(6.5, 4.2))
    plt.barh(plot_table["method"], plot_table["auprc"], color=colors)
    plt.xlabel("AUPRC")
    plt.title("Official IEEE-CIS baseline comparison")
    plt.tight_layout()
    plt.savefig(path, dpi=dpi)
    plt.close()
    image = Image.open(path)
    dpi_info = image.info.get("dpi", (dpi, dpi))
    return float(dpi_info[0]), float(dpi_info[1])


def run_ieee_official_baseline_audit(
    data_root: str | Path = Path(r"D:/motif-entropy-fraud/ieee-fraud-detection"),
    p_adic_claims_path: str | Path = Path("outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_claims.csv"),
    output_root: str | Path = Path("outputs/p_adic_ieee_cis_official"),
    train_fraction: float = 0.7,
    max_rows: int | None = None,
) -> dict[str, object]:
    """Run conventional baselines on official IEEE-CIS temporal split."""
    data_root = Path(data_root)
    output_root = Path(output_root)
    p_adic_claims_path = Path(p_adic_claims_path)
    transaction, identity = _load_ieee(data_root)
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    if max_rows is not None:
        frame = frame.iloc[:max_rows].copy()
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=train_fraction)
    y_train = train["isFraud"].astype(int).reset_index(drop=True)
    y_test = test["isFraud"].astype(int).reset_index(drop=True)
    train_x, test_x = _frequency_encode(train.reset_index(drop=True), test.reset_index(drop=True), IEEE_COLUMNS)

    baseline_rows = [_read_p_adic_row(p_adic_claims_path)]
    logistic_scores = _score_logistic(train_x, y_train, test_x)
    baseline_rows.append(
        {
            "method": "logistic_frequency_supervised",
            "family": "supervised_context_baseline",
            "auprc": _safe_metric(average_precision_score, y_test, logistic_scores),
            "roc_auc": _safe_metric(roc_auc_score, y_test, logistic_scores),
            "claim_role": "context_not_primary_claim",
        }
    )
    p_adic_train_scores, p_adic_test_scores = _padic_train_test_scores(
        train.reset_index(drop=True), test.reset_index(drop=True)
    )
    train_x_plus = train_x.copy()
    test_x_plus = test_x.copy()
    train_x_plus["p_adic_signal"] = p_adic_train_scores
    test_x_plus["p_adic_signal"] = p_adic_test_scores
    logistic_plus_scores = _score_logistic(train_x_plus, y_train, test_x_plus)
    baseline_rows.append(
        {
            "method": "logistic_frequency_plus_padic_signal",
            "family": "supervised_context_baseline",
            "auprc": _safe_metric(average_precision_score, y_test, logistic_plus_scores),
            "roc_auc": _safe_metric(roc_auc_score, y_test, logistic_plus_scores),
            "claim_role": "complementarity_check",
        }
    )
    isolation_scores = _score_isolation_forest(train_x, y_train, test_x)
    baseline_rows.append(
        {
            "method": "isolation_forest_frequency_unsupervised",
            "family": "unsupervised_context_baseline",
            "auprc": _safe_metric(average_precision_score, y_test, isolation_scores),
            "roc_auc": _safe_metric(roc_auc_score, y_test, isolation_scores),
            "claim_role": "context_not_primary_claim",
        }
    )
    table = pd.DataFrame(baseline_rows)
    table["dataset"] = "official_ieee_cis"
    table["train_rows"] = int(len(train))
    table["test_rows"] = int(len(test))
    table["fraud_rate_test"] = float(y_test.mean())
    table["temporal_split"] = True

    table_path = output_root / "tables" / "p_adic_ieee_cis_baseline_comparison.csv"
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(table_path, index=False)
    table.to_markdown(table_path.with_suffix(".md"), index=False)
    figure_path = output_root / "figures" / "p_adic_ieee_cis_baseline_comparison.png"
    figure_dpi = _write_baseline_figure(table, figure_path, dpi=600)
    return {
        "baseline_table": table,
        "artifacts": {"baseline_table": table_path, "comparison_figure": figure_path},
        "figure_dpi": figure_dpi,
    }


if __name__ == "__main__":
    result = run_ieee_official_baseline_audit()
    print(result["baseline_table"].to_json(orient="records", indent=2))
    print("figure_dpi", result["figure_dpi"])
