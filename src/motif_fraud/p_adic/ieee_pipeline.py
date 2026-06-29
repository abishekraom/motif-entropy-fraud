"""IEEE-CIS categorical p-adic audit pipeline.

The code can run on the Kaggle competition files when access is accepted. If run
on a mirror, the manifest and dataset card must keep that provenance visible.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score

from motif_fraud.p_adic.encoding import HierarchySpec, encode_frame, randomize_digit_maps
from motif_fraud.p_adic.hierarchy_selection import select_hierarchy_order_temporal
from motif_fraud.p_adic.metrics import next_prime_at_least
from motif_fraud.p_adic.scoring import PAdicPrefixRarityScorer
from motif_fraud.p_adic.splits import temporal_train_test_split
from motif_fraud.p_adic.statistics import bootstrap_metric_delta_ci
from motif_fraud.p_adic.temporal_signal import make_time_block_table, recall_at_fixed_fpr
from motif_fraud.pipeline.p_adic_reproduce import build_q1_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OFFICIAL_ROOT = PROJECT_ROOT.parent / "ieee-fraud-detection"
DEFAULT_MIRROR_ROOT = PROJECT_ROOT / "data" / "ieee_cis_mirror"
IEEE_COLUMNS = ("ProductCD", "card4", "card6", "P_emaildomain", "DeviceType")


def _ensure_dirs(output_root: Path) -> None:
    for subdir in ("tables", "figures", "manifests", "metrics"):
        (output_root / subdir).mkdir(parents=True, exist_ok=True)


def _safe_metric(func, y_true: pd.Series, scores: pd.Series) -> float:
    if len(set(y_true.astype(int))) < 2:
        return float("nan")
    return float(func(y_true.astype(int), scores.astype(float)))


def _default_data_root() -> Path:
    return DEFAULT_OFFICIAL_ROOT if (DEFAULT_OFFICIAL_ROOT / "train_transaction.csv").exists() else DEFAULT_MIRROR_ROOT


def _load_ieee(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    transaction_path = root / "train_transaction.csv"
    identity_path = root / "train_identity.csv"
    if not transaction_path.exists() or not identity_path.exists():
        raise FileNotFoundError(
            f"Missing IEEE-CIS train files under {root}. Official Kaggle command after "
            "competition access: kaggle competitions download -c ieee-fraud-detection -p data/ieee_cis --unzip"
        )
    return pd.read_csv(transaction_path), pd.read_csv(identity_path)


def _prepare_ieee(transaction: pd.DataFrame, identity: pd.DataFrame | None) -> pd.DataFrame:
    frame = transaction.copy()
    if identity is not None and "TransactionID" in identity.columns:
        keep_identity = [col for col in ("TransactionID", "DeviceType") if col in identity.columns]
        frame = frame.merge(identity[keep_identity], on="TransactionID", how="left")
    if "DeviceType" not in frame.columns:
        frame["DeviceType"] = "__MISSING__"
    for column in IEEE_COLUMNS:
        if column not in frame.columns:
            frame[column] = "__MISSING__"
        frame[column] = frame[column].fillna("__MISSING__").astype(str)
    required = {"TransactionDT", "isFraud", *IEEE_COLUMNS}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise KeyError(f"IEEE-CIS frame missing required columns: {missing}")
    return frame


def _score_encoded(train_h: pd.DataFrame, test_h: pd.DataFrame, spec: HierarchySpec) -> tuple[pd.Series, object, object]:
    train_encoded = encode_frame(train_h, spec)
    test_encoded = encode_frame(test_h, train_encoded.spec, digit_maps=train_encoded.digit_maps)
    scorer = PAdicPrefixRarityScorer(
        prime=train_encoded.spec.prime or 2, depth=len(train_encoded.spec.columns), weighting="weighted_deep"
    ).fit(train_encoded.codes[train_h["isFraud"].astype(int) == 0])
    return scorer.score(test_encoded.codes), train_encoded, test_encoded


def _flat_frequency_scores(train_h: pd.DataFrame, test_h: pd.DataFrame) -> pd.Series:
    normal = train_h[train_h["isFraud"].astype(int) == 0]
    normal_keys = normal[list(IEEE_COLUMNS)].astype(str).agg("|".join, axis=1)
    counts = normal_keys.value_counts().to_dict()
    denom = max(1, len(normal_keys))
    test_keys = test_h[list(IEEE_COLUMNS)].astype(str).agg("|".join, axis=1)
    return pd.Series([1.0 - counts.get(key, 0) / denom for key in test_keys])


def _write_pr_curve(y_true: pd.Series, scores: pd.Series, path: Path) -> None:
    precision, recall, _ = precision_recall_curve(y_true.astype(int), scores.astype(float))
    plt.figure(figsize=(5, 4))
    plt.plot(recall, precision, label="p-adic IEEE-CIS categorical")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("IEEE-CIS categorical p-adic PR curve")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(path, dpi=600)
    plt.close()


def run_ieee_cis_p_adic_audit(
    transaction: pd.DataFrame | None = None,
    identity: pd.DataFrame | None = None,
    output_root: str | Path = "outputs/p_adic_ieee_cis_official",
    data_root: str | Path | None = None,
    train_fraction: float = 0.7,
    random_control_seeds: tuple[int, ...] = (11, 17, 23, 31, 47),
) -> dict[str, object]:
    output_root = Path(output_root)
    _ensure_dirs(output_root)
    if transaction is None:
        selected_root = Path(data_root) if data_root is not None else _default_data_root()
        transaction, identity = _load_ieee(selected_root)
    else:
        selected_root = Path(data_root) if data_root is not None else Path("<in-memory>")
    frame = _prepare_ieee(transaction, identity)
    train_h, test_h = temporal_train_test_split(frame, "TransactionDT", train_fraction=train_fraction)
    selection = select_hierarchy_order_temporal(
        train_h,
        candidate_columns=IEEE_COLUMNS,
        time_column="TransactionDT",
        label_column="isFraud",
        train_fraction=0.7,
    )
    selected_columns = selection.best_order
    widest = max(train_h[column].nunique(dropna=False) + 1 for column in selected_columns)
    spec = HierarchySpec("ieee_cis_categorical", selected_columns, next_prime_at_least(max(2, widest)))
    validation_path = output_root / "metrics" / "p_adic_ieee_cis_hierarchy_selection.csv"
    selection.validation_results.to_csv(validation_path, index=False)
    p_adic_scores, train_encoded, _ = _score_encoded(train_h, test_h, spec)

    random_scores = []
    for seed in random_control_seeds:
        maps = randomize_digit_maps(train_encoded.digit_maps, seed=seed)
        control_train = encode_frame(train_h, train_encoded.spec, digit_maps=maps)
        control_test = encode_frame(test_h, train_encoded.spec, digit_maps=maps)
        random_scores.append(
            PAdicPrefixRarityScorer(
                prime=train_encoded.spec.prime or 2,
                depth=len(spec.columns),
                weighting="weighted_deep",
            )
            .fit(control_train.codes[train_h["isFraud"].astype(int) == 0])
            .score(control_test.codes)
        )
    reversed_spec = HierarchySpec("ieee_cis_reversed", tuple(reversed(selected_columns)), spec.prime)
    hierarchy_scores, _, _ = _score_encoded(train_h, test_h, reversed_spec)
    flat_scores = _flat_frequency_scores(train_h, test_h)

    y_true = test_h["isFraud"].astype(int).reset_index(drop=True)
    score_map = {
        "p_adic_ieee_cis_categorical_frequency": p_adic_scores.reset_index(drop=True),
        "flat_categorical_frequency_control": flat_scores.reset_index(drop=True),
        "random_hierarchy_order_control": hierarchy_scores.reset_index(drop=True),
    }
    for index, scores in enumerate(random_scores):
        score_map[f"random_digit_map_control_seed_{index}"] = scores.reset_index(drop=True)
    rows = [
        {
            "method": "p_adic_ieee_cis_categorical_frequency",
            "control_family": "proposed",
            "auprc": _safe_metric(average_precision_score, y_true, p_adic_scores),
            "roc_auc": _safe_metric(roc_auc_score, y_true, p_adic_scores),
        },
        {
            "method": "flat_categorical_frequency_control",
            "control_family": "negative_control",
            "auprc": _safe_metric(average_precision_score, y_true, flat_scores),
            "roc_auc": _safe_metric(roc_auc_score, y_true, flat_scores),
        },
        {
            "method": "random_hierarchy_order_control",
            "control_family": "negative_control",
            "auprc": _safe_metric(average_precision_score, y_true, hierarchy_scores),
            "roc_auc": _safe_metric(roc_auc_score, y_true, hierarchy_scores),
        },
    ]
    for index, scores in enumerate(random_scores):
        rows.append(
            {
                "method": f"random_digit_map_control_seed_{index}",
                "control_family": "invariance_control",
                "auprc": _safe_metric(average_precision_score, y_true, scores),
                "roc_auc": _safe_metric(roc_auc_score, y_true, scores),
            }
        )
    claims = pd.DataFrame(rows)
    recall_metrics = {
        method: recall_at_fixed_fpr(y_true, scores, max_fpr=0.01)
        for method, scores in score_map.items()
    }
    claims["recall_at_1pct_fpr"] = claims["method"].map(lambda method: recall_metrics[method]["recall"])
    claims["threshold_at_1pct_fpr"] = claims["method"].map(lambda method: recall_metrics[method]["threshold"])
    claims["observed_fpr_at_1pct_budget"] = claims["method"].map(
        lambda method: recall_metrics[method]["false_positive_rate"]
    )
    material_controls = claims[claims["control_family"].isin(["negative_control", "simple_baseline"])]
    best_control = material_controls["auprc"].max()
    proposed = float(claims.loc[claims["control_family"] == "proposed", "auprc"].iloc[0])
    hierarchy_delta_ci = bootstrap_metric_delta_ci(
        y_true,
        score_map["p_adic_ieee_cis_categorical_frequency"],
        score_map["random_hierarchy_order_control"],
        metric="auprc",
        n_bootstrap=500,
        seed=13,
    )
    flat_delta_ci = bootstrap_metric_delta_ci(
        y_true,
        score_map["p_adic_ieee_cis_categorical_frequency"],
        score_map["flat_categorical_frequency_control"],
        metric="auprc",
        n_bootstrap=500,
        seed=17,
    )
    claims["best_control_auprc"] = float(best_control)
    claims["delta_vs_best_control_auprc"] = claims["auprc"] - float(best_control)
    claims["bootstrap_delta_vs_random_hierarchy_lower"] = hierarchy_delta_ci["lower"]
    claims["bootstrap_delta_vs_random_hierarchy_upper"] = hierarchy_delta_ci["upper"]
    claims["bootstrap_p_delta_vs_random_hierarchy_le_zero"] = hierarchy_delta_ci[
        "p_delta_le_zero"
    ]
    claims["bootstrap_delta_vs_flat_lower"] = flat_delta_ci["lower"]
    claims["bootstrap_delta_vs_flat_upper"] = flat_delta_ci["upper"]
    prevalence = float(y_true.mean())
    claims["auprc_lift_vs_prevalence"] = claims["auprc"] / prevalence if prevalence > 0 else float("nan")
    claims["claim_status"] = (
        "q1_candidate_passed_controls"
        if proposed > float(best_control)
        and proposed >= 2.0 * prevalence
        and hierarchy_delta_ci["lower"] > 0
        else "diagnostic_only_failed_q1_gate"
    )
    claims["claim_scope"] = "official_ieee_cis_temporal_categorical_signal_audit"
    claims_path = output_root / "tables" / "p_adic_ieee_cis_claims.csv"
    claims.to_csv(claims_path, index=False)
    claims.to_markdown(claims_path.with_suffix(".md"), index=False)
    scores_path = output_root / "metrics" / "p_adic_ieee_cis_scores.csv"
    score_frame = pd.DataFrame({"row_index": test_h.index, "y_true": y_true, "p_adic_score": p_adic_scores})
    for method, scores in score_map.items():
        if method != "p_adic_ieee_cis_categorical_frequency":
            score_frame[method] = scores
    score_frame.to_csv(scores_path, index=False)
    block_table = make_time_block_table(
        pd.DataFrame(
            {
                "TransactionDT": test_h["TransactionDT"].reset_index(drop=True),
                "isFraud": y_true,
                "p_adic_score": p_adic_scores.reset_index(drop=True),
            }
        ),
        time_column="TransactionDT",
        label_column="isFraud",
        score_column="p_adic_score",
        n_blocks=48,
    )
    block_path = output_root / "metrics" / "p_adic_ieee_cis_temporal_blocks.csv"
    block_table.to_csv(block_path, index=False)
    figure_path = output_root / "figures" / "p_adic_ieee_cis_pr_curve.png"
    _write_pr_curve(y_true, p_adic_scores, figure_path)
    artifacts = {
        "dataset_cards": ["docs/rebuild/dataset_cards/ieee_cis_kaggle_competition.md"],
        "negative_controls": ["random_digit_map", "random_hierarchy", "flat_categorical"],
        "figures": [{"path": str(figure_path), "dpi": 600}],
        "claims_table": str(claims_path),
        "scores": str(scores_path),
        "temporal_blocks": str(block_path),
        "hierarchy_selection": str(validation_path),
    }
    manifest = build_q1_manifest(artifacts, output_root / "manifests" / "p_adic_ieee_cis_manifest.json")
    metadata = {
        "dataset": "IEEE-CIS Fraud Detection categorical audit",
        "rows": int(len(frame)),
        "train_rows": int(len(train_h)),
        "test_rows": int(len(test_h)),
        "fraud_rate": float(frame["isFraud"].astype(int).mean()),
        "prime": int(spec.prime or 0),
        "selected_hierarchy_order": list(selected_columns),
        "claim_status": str(claims["claim_status"].iloc[0]),
        "data_root": str(selected_root),
        "provenance_warning": "official Kaggle competition files used" if selected_root == DEFAULT_OFFICIAL_ROOT else "local mirror is development-only unless user accepts official competition rules",
    }
    (output_root / "manifests" / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {"claims": claims, "manifest": manifest, "metadata": metadata}


def main() -> None:
    result = run_ieee_cis_p_adic_audit()
    print(json.dumps(result["metadata"], indent=2))


if __name__ == "__main__":
    main()
