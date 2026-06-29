"""External real-dataset p-adic audit on vehicle insurance claim fraud.

Uses Kaggle shivamb/vehicle-claim-fraud-detection (CC0-1.0, source listed as
Oracle Databases). This is a real/reputed external categorical fraud dataset,
not synthetic research data.
"""

from __future__ import annotations

import json
from itertools import permutations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score

from motif_fraud.p_adic.encoding import HierarchySpec, encode_frame
from motif_fraud.p_adic.metrics import next_prime_at_least
from motif_fraud.p_adic.scoring import PAdicPrefixRarityScorer
from motif_fraud.p_adic.splits import temporal_train_test_split
from motif_fraud.p_adic.statistics import bootstrap_metric_delta_ci

SOURCE_NOTE = "Kaggle shivamb/vehicle-claim-fraud-detection; CC0-1.0; userSpecifiedSources=Oracle Databases"
CANDIDATE_COLUMNS = (
    "Make",
    "AccidentArea",
    "Fault",
    "PolicyType",
    "VehicleCategory",
    "BasePolicy",
)


def _month_number(series: pd.Series) -> pd.Series:
    order = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}
    return series.map(order).fillna(0).astype(int)


def _load_vehicle(data_root: Path) -> pd.DataFrame:
    path = data_root / "fraud_oracle.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing vehicle claim fraud CSV: {path}")
    frame = pd.read_csv(path)
    frame["temporal_order"] = (
        frame["Year"].astype(int) * 1000
        + _month_number(frame["Month"]) * 50
        + frame["WeekOfMonth"].astype(int)
    )
    return frame.sort_values(["temporal_order", "PolicyNumber"], kind="mergesort").reset_index(drop=True)


def _safe_metric(func, y_true: pd.Series, scores: pd.Series) -> float:
    if len(set(y_true.astype(int))) < 2:
        return float("nan")
    return float(func(y_true.astype(int), scores.astype(float)))


def _score_order(train: pd.DataFrame, test: pd.DataFrame, columns: tuple[str, ...]) -> tuple[pd.Series, pd.Series, HierarchySpec]:
    widest = max(train[column].nunique(dropna=False) + 1 for column in columns)
    prime = next_prime_at_least(max(2, widest))
    spec = HierarchySpec("vehicle_claim", columns, prime)
    train_encoded = encode_frame(train, spec)
    test_encoded = encode_frame(test, train_encoded.spec, digit_maps=train_encoded.digit_maps)
    scorer = PAdicPrefixRarityScorer(prime=prime, depth=len(columns), weighting="weighted_deep").fit(
        train_encoded.codes[train["FraudFound_P"].astype(int) == 0]
    )
    return scorer.score(train_encoded.codes).reset_index(drop=True), scorer.score(test_encoded.codes).reset_index(drop=True), spec


def _select_order(train: pd.DataFrame) -> tuple[tuple[str, ...], pd.DataFrame]:
    inner_train, validation = temporal_train_test_split(train, "temporal_order", train_fraction=0.7)
    rows = []
    for order in permutations(CANDIDATE_COLUMNS):
        _, scores, _ = _score_order(inner_train.reset_index(drop=True), validation.reset_index(drop=True), tuple(order))
        y_val = validation["FraudFound_P"].astype(int).reset_index(drop=True)
        rows.append(
            {
                "order": "|".join(order),
                "auprc": _safe_metric(average_precision_score, y_val, scores),
                "roc_auc": _safe_metric(roc_auc_score, y_val, scores),
            }
        )
    table = pd.DataFrame(rows).sort_values(["auprc", "roc_auc"], ascending=False).reset_index(drop=True)
    return tuple(str(table.iloc[0]["order"]).split("|")), table


def _flat_frequency(train: pd.DataFrame, test: pd.DataFrame, columns: tuple[str, ...]) -> pd.Series:
    tuples_train = train[list(columns)].astype("object").where(train[list(columns)].notna(), "__MISSING__").agg(tuple, axis=1)
    tuples_test = test[list(columns)].astype("object").where(test[list(columns)].notna(), "__MISSING__").agg(tuple, axis=1)
    normal = tuples_train[train["FraudFound_P"].astype(int) == 0]
    freq = normal.value_counts(normalize=True)
    return 1.0 - tuples_test.map(freq).fillna(0.0).astype(float).reset_index(drop=True)


def _write_pr(y_true: pd.Series, scores: pd.Series, path: Path) -> tuple[float, float]:
    path.parent.mkdir(parents=True, exist_ok=True)
    precision, recall, _ = precision_recall_curve(y_true, scores)
    plt.figure(figsize=(5.0, 4.0))
    plt.plot(recall, precision, color="#7c3aed", linewidth=1.8)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Vehicle claim external p-adic PR curve")
    plt.tight_layout()
    plt.savefig(path, dpi=600)
    plt.close()
    dpi = Image.open(path).info.get("dpi", (600, 600))
    return float(dpi[0]), float(dpi[1])


def run_vehicle_claim_external_audit(
    data_root: str | Path = Path(r"D:/motif-entropy-fraud/vehicle-claim-fraud-detection"),
    output_root: str | Path = Path("outputs/p_adic_vehicle_claim"),
    train_fraction: float = 0.7,
) -> dict[str, object]:
    data_root = Path(data_root)
    output_root = Path(output_root)
    frame = _load_vehicle(data_root)
    train, test = temporal_train_test_split(frame, "temporal_order", train_fraction=train_fraction)
    selected_order, selection_table = _select_order(train.reset_index(drop=True))
    _, p_scores, spec = _score_order(train.reset_index(drop=True), test.reset_index(drop=True), selected_order)
    _, reversed_scores, _ = _score_order(train.reset_index(drop=True), test.reset_index(drop=True), tuple(reversed(selected_order)))
    flat_scores = _flat_frequency(train.reset_index(drop=True), test.reset_index(drop=True), selected_order)
    y = test["FraudFound_P"].astype(int).reset_index(drop=True)
    rows = [
        {"method": "p_adic_vehicle_selected_hierarchy", "family": "proposed_external", "auprc": _safe_metric(average_precision_score, y, p_scores), "roc_auc": _safe_metric(roc_auc_score, y, p_scores)},
        {"method": "flat_vehicle_tuple_rarity", "family": "negative_control", "auprc": _safe_metric(average_precision_score, y, flat_scores), "roc_auc": _safe_metric(roc_auc_score, y, flat_scores)},
        {"method": "reversed_vehicle_hierarchy", "family": "negative_control", "auprc": _safe_metric(average_precision_score, y, reversed_scores), "roc_auc": _safe_metric(roc_auc_score, y, reversed_scores)},
    ]
    claims = pd.DataFrame(rows)
    best_control = claims.loc[claims["family"] == "negative_control", "auprc"].max()
    proposed = float(claims.loc[claims["family"] == "proposed_external", "auprc"].iloc[0])
    delta_ci = bootstrap_metric_delta_ci(y, p_scores, reversed_scores, n_bootstrap=500, seed=29)
    claims["best_control_auprc"] = float(best_control)
    claims["delta_vs_best_control_auprc"] = claims["auprc"] - float(best_control)
    claims["bootstrap_delta_vs_reversed_lower"] = delta_ci["lower"]
    claims["bootstrap_delta_vs_reversed_upper"] = delta_ci["upper"]
    claims["claim_status"] = "external_support_passed_controls" if proposed > float(best_control) and delta_ci["lower"] > 0 else "external_diagnostic_failed_controls"
    claims["claim_scope"] = "external_vehicle_claim_categorical_temporal_order_audit"

    table_dir = output_root / "tables"
    metrics_dir = output_root / "metrics"
    figure_dir = output_root / "figures"
    for d in (table_dir, metrics_dir, figure_dir):
        d.mkdir(parents=True, exist_ok=True)
    claims_path = table_dir / "p_adic_vehicle_claim_claims.csv"
    selection_path = metrics_dir / "p_adic_vehicle_claim_hierarchy_selection.csv"
    figure_path = figure_dir / "p_adic_vehicle_claim_pr_curve.png"
    claims.to_csv(claims_path, index=False)
    claims.to_markdown(claims_path.with_suffix(".md"), index=False)
    selection_table.to_csv(selection_path, index=False)
    figure_dpi = _write_pr(y, p_scores, figure_path)
    metadata = {
        "dataset": "Vehicle Insurance Claim Fraud Detection",
        "source": SOURCE_NOTE,
        "rows": int(len(frame)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "fraud_rate": float(frame["FraudFound_P"].mean()),
        "selected_hierarchy_order": list(selected_order),
        "prime": int(spec.prime or 0),
        "claim_status": str(claims["claim_status"].iloc[0]),
    }
    metadata_path = output_root / "run_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {
        "claims": claims,
        "metadata": metadata,
        "artifacts": {"claims": claims_path, "selection": selection_path, "figure": figure_path, "metadata": metadata_path},
        "figure_dpi": figure_dpi,
    }


if __name__ == "__main__":
    result = run_vehicle_claim_external_audit()
    print(json.dumps(result["metadata"], indent=2))
    print(result["claims"].to_json(orient="records", indent=2))
    print("figure_dpi", result["figure_dpi"])
