"""Pre-registered p-adic multiresolution event-stream surveillance operator.

This module is deliberately failure-safe: it writes Q1/SPL-style artifacts and
strict claim statuses, but it never turns a weak result into a strong claim.
Empirical entry points load official/reputed data only; small constructed data
should be reserved for mathematical unit tests outside empirical claims.
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
from motif_fraud.p_adic.ieee_pipeline import DEFAULT_OFFICIAL_ROOT, _load_ieee, _prepare_ieee
from motif_fraud.p_adic.metrics import next_prime_at_least
from motif_fraud.p_adic.splits import temporal_train_test_split

DEFAULT_IEEE_HIERARCHY = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain")
PREREGISTERED_GATES_DOC = "docs/rebuild/20_Q1_SPL_PREREGISTERED_GATES.md"
PASS_STATUS = "q1_candidate_multiresolution_signal_passed_controls"
FAIL_STATUS = "diagnostic_only_failed_q1_multiresolution_gate"


def _ensure_dirs(output_root: Path) -> None:
    for subdir in ("tables", "figures", "metrics", "manifests"):
        (output_root / subdir).mkdir(parents=True, exist_ok=True)


def _safe_metric(func, y_true: pd.Series, scores: pd.Series) -> float:
    y = y_true.astype(int)
    s = scores.astype(float)
    if len(set(y)) < 2 or s.nunique(dropna=False) <= 1:
        return float("nan")
    return float(func(y, s))


def _cusum_positive(values: pd.Series) -> pd.Series:
    arr = values.astype(float).to_numpy()
    baseline = float(np.median(arr[: max(3, len(arr) // 4)]))
    running: list[float] = []
    current = 0.0
    for value in arr - baseline:
        current = max(0.0, current + float(value))
        running.append(current)
    return pd.Series(running, index=values.index)


def _ewma(values: pd.Series, alpha: float = 0.25) -> pd.Series:
    return values.astype(float).ewm(alpha=alpha, adjust=False).mean()


def _assign_equal_count_blocks(frame: pd.DataFrame, n_blocks: int) -> pd.Series:
    if n_blocks < 4:
        raise ValueError("n_blocks must be at least 4")
    ids = np.floor(np.arange(len(frame)) * n_blocks / len(frame)).astype(int)
    return pd.Series(np.minimum(ids, n_blocks - 1), index=frame.index, name="block_id")


def _category_entropy(frame: pd.DataFrame, columns: tuple[str, ...]) -> float:
    total = 0.0
    for column in columns:
        probs = frame[column].astype(str).value_counts(normalize=True)
        if len(probs):
            total += float(-(probs * np.log2(probs)).sum())
    return total


def _prefix_rarity_from_codes(
    train_normal_codes: pd.Series,
    test_codes: pd.Series,
    *,
    prime: int,
    depth: int,
    prefix: str = "prefix",
) -> pd.DataFrame:
    normal = [int(code) for code in train_normal_codes]
    if not normal:
        raise ValueError("normal train codes must not be empty")
    denom = len(normal)
    counters = []
    for d in range(1, depth + 1):
        modulus = prime**d
        counters.append(Counter(code % modulus for code in normal))
    rows: list[dict[str, float]] = []
    for raw_code in test_codes:
        code = int(raw_code)
        row = {}
        for d, counts in enumerate(counters, start=1):
            modulus = prime**d
            support = counts.get(code % modulus, 0)
            row[f"{prefix}_depth_{d}_surprise"] = 1.0 - support / denom
        rows.append(row)
    return pd.DataFrame(rows)


def compute_prefix_surprise_scores(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    hierarchy: tuple[str, ...] = DEFAULT_IEEE_HIERARCHY,
    label_column: str = "isFraud",
) -> pd.DataFrame:
    """Compute train-only per-depth prefix surprise for held-out rows.

    The score uses normal training rows only. It is invariant to within-level
    category relabeling because the statistic depends on equality of prefixes,
    not ordinal digit meaning.
    """

    missing = [column for column in (*hierarchy, label_column) if column not in train.columns]
    if missing:
        raise KeyError(f"train frame missing required columns: {missing}")
    missing = [column for column in hierarchy if column not in test.columns]
    if missing:
        raise KeyError(f"test frame missing required columns: {missing}")
    widest = max(train[column].nunique(dropna=False) + 1 for column in hierarchy)
    spec = HierarchySpec("preregistered_multiresolution", hierarchy, next_prime_at_least(max(2, widest)))
    train_encoded = encode_frame(train, spec)
    test_encoded = encode_frame(test, train_encoded.spec, digit_maps=train_encoded.digit_maps)
    normal_mask = train[label_column].astype(int).reset_index(drop=True) == 0
    surprise = _prefix_rarity_from_codes(
        train_encoded.codes.reset_index(drop=True)[normal_mask],
        test_encoded.codes.reset_index(drop=True),
        prime=int(train_encoded.spec.prime or 2),
        depth=len(hierarchy),
        prefix="prefix",
    )
    depth_cols = [f"prefix_depth_{d}_surprise" for d in range(1, len(hierarchy) + 1)]
    weights = np.arange(1, len(hierarchy) + 1, dtype=float)
    surprise["multiresolution_energy"] = surprise[depth_cols].mean(axis=1)
    surprise["weighted_multiresolution_energy"] = surprise[depth_cols].dot(weights) / weights.sum()
    return surprise


def _flat_tuple_rarity(train: pd.DataFrame, test: pd.DataFrame, hierarchy: tuple[str, ...], label_column: str) -> pd.Series:
    normal = train[train[label_column].astype(int) == 0]
    keys = normal[list(hierarchy)].astype(str).agg("|".join, axis=1)
    counts = keys.value_counts().to_dict()
    denom = max(1, len(keys))
    test_keys = test[list(hierarchy)].astype(str).agg("|".join, axis=1)
    return pd.Series([1.0 - counts.get(key, 0) / denom for key in test_keys], name="flat_tuple_rarity")


def _block_table_for_hierarchy(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    hierarchy: tuple[str, ...],
    n_blocks: int,
    time_column: str,
    label_column: str,
    score_prefix: str,
) -> pd.DataFrame:
    scores = compute_prefix_surprise_scores(train, test, hierarchy=hierarchy, label_column=label_column)
    work = test.sort_values(time_column, kind="mergesort").reset_index(drop=True).copy()
    work[f"{score_prefix}_energy"] = scores["weighted_multiresolution_energy"].reset_index(drop=True)
    work["flat_tuple_rarity"] = _flat_tuple_rarity(train, test, hierarchy, label_column).reset_index(drop=True)
    work["block_id"] = _assign_equal_count_blocks(work, n_blocks=n_blocks).to_numpy()
    rows = []
    for block_id, group in work.groupby("block_id", sort=True):
        labels = group[label_column].astype(int)
        rows.append(
            {
                "block_id": int(block_id),
                "block_start_time": float(group[time_column].iloc[0]),
                "block_end_time": float(group[time_column].iloc[-1]),
                "rows": int(len(group)),
                "positive_count": int(labels.sum()),
                "positive_rate": float(labels.mean()),
                f"{score_prefix}_energy": float(group[f"{score_prefix}_energy"].mean()),
                "flat_tuple_rarity": float(group["flat_tuple_rarity"].mean()),
                "category_entropy_temporal": _category_entropy(group, hierarchy),
                "transaction_count_signal": float(len(group)),
            }
        )
    return pd.DataFrame(rows)


def _bootstrap_delta(y_true: pd.Series, proposed: pd.Series, control: pd.Series, n_bootstrap: int, seed: int) -> dict[str, float]:
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
    arr = np.asarray(deltas, dtype=float)
    return {
        "lower": float(np.quantile(arr, 0.025)),
        "upper": float(np.quantile(arr, 0.975)),
        "p_delta_le_zero": float(np.mean(arr <= 0)),
    }


def _precision_recall_at_fraction(y_true: pd.Series, scores: pd.Series, fraction: float = 0.1) -> dict[str, float]:
    y = y_true.astype(int).reset_index(drop=True)
    s = scores.astype(float).reset_index(drop=True)
    k = max(1, int(np.ceil(len(s) * fraction)))
    idx = s.sort_values(ascending=False).head(k).index
    selected = pd.Series(False, index=s.index)
    selected.loc[idx] = True
    tp = int((selected & (y == 1)).sum())
    positives = int(y.sum())
    return {
        "top_fraction": float(fraction),
        "selected_blocks": int(selected.sum()),
        "precision_at_top_fraction": float(tp / selected.sum()) if selected.sum() else float("nan"),
        "recall_at_top_fraction": float(tp / positives) if positives else float("nan"),
    }


def _add_context_score(blocks: pd.DataFrame) -> pd.Series:
    cols = [
        "p_adic_multiresolution_energy",
        "flat_tuple_rarity",
        "category_entropy_temporal",
        "transaction_count_signal",
    ]
    features = blocks[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if len(features) < 8:
        return pd.Series(np.zeros(len(features)), name="isolation_forest_block_context")
    model = IsolationForest(n_estimators=100, random_state=37, contamination="auto")
    model.fit(features)
    return pd.Series(-model.score_samples(features), name="isolation_forest_block_context")


def _random_hierarchy(base: tuple[str, ...], seed: int) -> tuple[str, ...]:
    rng = np.random.default_rng(seed)
    arr = np.array(base, dtype=object)
    # Ensure the control is a real order perturbation when possible.
    for _ in range(10):
        perm = arr.copy()
        rng.shuffle(perm)
        candidate = tuple(str(x) for x in perm.tolist())
        if candidate != base:
            return candidate
    return tuple(reversed(base))


def _write_figure(blocks: pd.DataFrame, claims: pd.DataFrame, path: Path) -> tuple[float, float]:
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=False)
    axes[0].plot(blocks["block_id"], blocks["positive_rate"], color="black", label="held-out block positive rate", linewidth=1.5)
    axes[0].plot(blocks["block_id"], blocks["p_adic_multiresolution_energy_cusum"], label="p-adic multiresolution CUSUM", alpha=0.85)
    axes[0].plot(blocks["block_id"], blocks["flat_tuple_rarity_cusum"], label="flat rarity CUSUM", alpha=0.75)
    axes[0].set_ylabel("Block signal")
    axes[0].legend(fontsize=7, loc="best")
    top = claims.sort_values("auprc", ascending=True).tail(8)
    colors = ["#1f77b4" if str(method).startswith("p_adic") else "#555555" for method in top["method"]]
    axes[1].barh(top["method"], top["auprc"], color=colors)
    axes[1].tick_params(axis="y", labelsize=6)
    axes[1].set_xlabel("Block high-risk AUPRC")
    fig.suptitle("Pre-registered p-adic multiresolution surveillance gate", fontsize=10)
    fig.tight_layout()
    # PNG metadata can round 600 dpi to 599.9988. Save slightly above the
    # manuscript target so programmatic verification is still >=600 dpi.
    fig.savefig(path, dpi=610)
    plt.close(fig)
    with Image.open(path) as image:
        return tuple(float(x) for x in image.info.get("dpi", (610.0, 610.0)))


def run_preregistered_multiresolution_audit(
    frame: pd.DataFrame,
    *,
    output_root: str | Path,
    dataset_name: str,
    hierarchy: tuple[str, ...],
    time_column: str,
    label_column: str,
    n_blocks: int = 96,
    train_fraction: float = 0.7,
    bootstrap_samples: int = 500,
    random_hierarchy_seeds: tuple[int, ...] = (11, 17, 23),
) -> dict[str, object]:
    output_root = Path(output_root)
    _ensure_dirs(output_root)
    ordered = frame.sort_values(time_column, kind="mergesort").reset_index(drop=True)
    train, test = temporal_train_test_split(ordered, time_column, train_fraction=train_fraction)
    blocks = _block_table_for_hierarchy(
        train,
        test,
        hierarchy=hierarchy,
        n_blocks=n_blocks,
        time_column=time_column,
        label_column=label_column,
        score_prefix="p_adic_multiresolution",
    )
    blocks["p_adic_multiresolution_energy_ewma"] = _ewma(blocks["p_adic_multiresolution_energy"])
    blocks["p_adic_multiresolution_energy_cusum"] = _cusum_positive(blocks["p_adic_multiresolution_energy"])
    blocks["flat_tuple_rarity_ewma"] = _ewma(blocks["flat_tuple_rarity"])
    blocks["flat_tuple_rarity_cusum"] = _cusum_positive(blocks["flat_tuple_rarity"])

    reversed_blocks = _block_table_for_hierarchy(
        train,
        test,
        hierarchy=tuple(reversed(hierarchy)),
        n_blocks=n_blocks,
        time_column=time_column,
        label_column=label_column,
        score_prefix="reversed_hierarchy",
    )
    blocks["reversed_hierarchy_energy_cusum"] = _cusum_positive(reversed_blocks["reversed_hierarchy_energy"])
    for seed in random_hierarchy_seeds:
        random_blocks = _block_table_for_hierarchy(
            train,
            test,
            hierarchy=_random_hierarchy(hierarchy, seed),
            n_blocks=n_blocks,
            time_column=time_column,
            label_column=label_column,
            score_prefix=f"random_hierarchy_seed_{seed}",
        )
        blocks[f"random_hierarchy_energy_cusum_seed_{seed}"] = _cusum_positive(random_blocks[f"random_hierarchy_seed_{seed}_energy"])

    blocks["isolation_forest_block_context"] = _add_context_score(blocks)
    threshold = float(blocks["positive_rate"].quantile(0.75))
    blocks["high_risk_block"] = (blocks["positive_rate"] >= threshold).astype(int)
    y = blocks["high_risk_block"].astype(int)

    method_families = {
        "p_adic_multiresolution_energy": "proposed",
        "p_adic_multiresolution_energy_ewma": "proposed",
        "p_adic_multiresolution_energy_cusum": "proposed",
        "flat_tuple_rarity": "flat_control",
        "flat_tuple_rarity_ewma": "flat_control",
        "flat_tuple_rarity_cusum": "flat_control",
        "category_entropy_temporal": "entropy_control",
        "transaction_count_signal": "count_control",
        "reversed_hierarchy_energy_cusum": "hierarchy_order_control",
        "isolation_forest_block_context": "unsupervised_context",
    }
    for seed in random_hierarchy_seeds:
        method_families[f"random_hierarchy_energy_cusum_seed_{seed}"] = "hierarchy_order_control"

    rows = []
    for method, family in method_families.items():
        scores = blocks[method]
        rows.append(
            {
                "method": method,
                "family": family,
                "auprc": _safe_metric(average_precision_score, y, scores),
                "roc_auc": _safe_metric(roc_auc_score, y, scores),
                **_precision_recall_at_fraction(y, scores, fraction=0.1),
            }
        )
    claims = pd.DataFrame(rows)
    proposed = claims[claims["family"] == "proposed"].sort_values("auprc", ascending=False).iloc[0]
    controls = claims[claims["family"] != "proposed"].sort_values("auprc", ascending=False).iloc[0]
    ci = _bootstrap_delta(
        y,
        blocks[str(proposed["method"])],
        blocks[str(controls["method"])],
        n_bootstrap=bootstrap_samples,
        seed=41,
    )
    passed = (
        float(proposed["auprc"]) > float(controls["auprc"])
        and ci["lower"] > 0
        and ci["p_delta_le_zero"] <= 0.05
    )
    claim_status = PASS_STATUS if passed else FAIL_STATUS
    claims["best_proposed_method"] = str(proposed["method"])
    claims["best_control_method"] = str(controls["method"])
    claims["best_proposed_auprc"] = float(proposed["auprc"])
    claims["best_control_auprc"] = float(controls["auprc"])
    claims["delta_best_proposed_vs_best_control_auprc"] = float(proposed["auprc"] - controls["auprc"])
    claims["bootstrap_delta_lower"] = ci["lower"]
    claims["bootstrap_delta_upper"] = ci["upper"]
    claims["bootstrap_p_delta_le_zero"] = ci["p_delta_le_zero"]
    claims["claim_status"] = claim_status
    claims["claim_scope"] = dataset_name

    claims_path = output_root / "tables" / f"{dataset_name}_multiresolution_claims.csv"
    blocks_path = output_root / "metrics" / f"{dataset_name}_multiresolution_blocks.csv"
    figure_path = output_root / "figures" / f"{dataset_name}_multiresolution_gate.png"
    metadata_path = output_root / "manifests" / f"{dataset_name}_multiresolution_metadata.json"
    claims.to_csv(claims_path, index=False)
    claims.to_markdown(claims_path.with_suffix(".md"), index=False)
    blocks.to_csv(blocks_path, index=False)
    dpi = _write_figure(blocks, claims, figure_path)
    metadata = {
        "dataset": dataset_name,
        "synthetic_data_used": False,
        "pre_registered_gates_doc": PREREGISTERED_GATES_DOC,
        "rows": int(len(frame)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "n_blocks": int(n_blocks),
        "hierarchy": "|".join(hierarchy),
        "block_label_rule": "positive_rate >= heldout_block_75th_percentile",
        "high_risk_block_threshold": threshold,
        "best_proposed_method": str(proposed["method"]),
        "best_control_method": str(controls["method"]),
        "claim_status": claim_status,
        "figure_dpi": list(dpi),
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
            "figure_dpi": dpi,
        },
    }


def run_ieee_multiresolution_preregistered_audit(
    data_root: str | Path = DEFAULT_OFFICIAL_ROOT,
    output_root: str | Path = "outputs/p_adic_ieee_cis_preregistered_multiresolution",
    max_rows: int | None = None,
    n_blocks: int = 96,
    bootstrap_samples: int = 500,
    random_hierarchy_seeds: tuple[int, ...] = (11, 17, 23),
) -> dict[str, object]:
    data_root = Path(data_root)
    transaction, identity = _load_ieee(data_root)
    if max_rows is not None:
        transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(int(max_rows)).copy()
        identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    result = run_preregistered_multiresolution_audit(
        frame,
        output_root=output_root,
        dataset_name="official_ieee_cis_preregistered_multiresolution_surveillance",
        hierarchy=DEFAULT_IEEE_HIERARCHY,
        time_column="TransactionDT",
        label_column="isFraud",
        n_blocks=n_blocks,
        bootstrap_samples=bootstrap_samples,
        random_hierarchy_seeds=random_hierarchy_seeds,
    )
    result["metadata"]["data_root"] = str(data_root)
    Path(result["artifacts"]["metadata"]).write_text(json.dumps(result["metadata"], indent=2), encoding="utf-8")
    return result


def main() -> None:
    result = run_ieee_multiresolution_preregistered_audit()
    print(json.dumps(result["metadata"], indent=2))
    print(result["claims"].to_json(orient="records", indent=2))


if __name__ == "__main__":
    main()
