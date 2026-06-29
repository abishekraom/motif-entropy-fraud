"""Calibrated p-adic tree-scan CUSUM primitives.

This module is the replacement path for the failed prefix-rarity detector route.
It treats p-adic codes as auditable prefix-tree / p-adic-ball indexes and keeps
all empirical claims fail-closed under explicit controls.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import average_precision_score, roc_auc_score

from motif_fraud.p_adic.encoding import EncodedHierarchy, HierarchySpec, encode_frame
from motif_fraud.p_adic.ieee_pipeline import DEFAULT_OFFICIAL_ROOT, _load_ieee, _prepare_ieee
from motif_fraud.p_adic.metrics import next_prime_at_least
from motif_fraud.p_adic.splits import temporal_train_test_split

CSE_CIC_THURSDAY_FILE = Path(
    "data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv"
)
CSE_CIC_WEDNESDAY_FILE = Path(
    "data/cse_cic_ids2018/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv"
)
CSE_CIC_WEDNESDAY_SHA256 = "F15E2A12304446058A0186C8AD67DE2BD15735A9BA5C70C9A1F4C4242AB06771"
CSE_CIC_HIERARCHY = (
    "Protocol",
    "dst_port_band",
    "Dst Port",
    "SYN Flag Cnt",
    "ACK Flag Cnt",
    "PSH Flag Cnt",
)


@dataclass(frozen=True)
class TreeScanHierarchyConfig:
    """Configuration for train-only p-adic tree-scan statistics."""

    hierarchy: tuple[str, ...]
    label_column: str
    min_support: int = 20
    alpha: float = 0.5

    def __post_init__(self) -> None:
        if not self.hierarchy:
            raise ValueError("hierarchy must contain at least one column")
        if self.min_support < 1:
            raise ValueError("min_support must be positive")
        if self.alpha <= 0:
            raise ValueError("alpha must be positive")


def _infer_spec(train: pd.DataFrame, hierarchy: tuple[str, ...]) -> HierarchySpec:
    widest = max(train[column].nunique(dropna=False) + 1 for column in hierarchy)
    return HierarchySpec("p_adic_tree_scan", hierarchy, next_prime_at_least(max(2, widest)))


def binomial_excess_llr(observed: int, total: int, expected_probability: float) -> float:
    """One-sided Bernoulli/binomial excess log-likelihood ratio.

    Returns zero unless the observed count exceeds the expected count under the
    train-normal node probability. This is the primitive scan statistic used for
    prefix-ball excess detection.
    """

    observed = int(observed)
    total = int(total)
    if total <= 0:
        raise ValueError("total must be positive")
    if observed < 0 or observed > total:
        raise ValueError("observed must be in [0, total]")
    p = float(expected_probability)
    if not math.isfinite(p) or p <= 0.0 or p >= 1.0:
        eps = 1e-12
        p = min(max(p, eps), 1.0 - eps)
    if observed <= total * p:
        return 0.0
    q = observed / total
    eps = 1e-12
    q = min(max(q, eps), 1.0 - eps)
    return float(observed * math.log(q / p) + (total - observed) * math.log((1.0 - q) / (1.0 - p)))


def build_prefix_node_table(train: pd.DataFrame, config: TreeScanHierarchyConfig) -> tuple[pd.DataFrame, EncodedHierarchy]:
    """Build train-only prefix-node probabilities from normal rows.

    The returned table includes observed train-normal prefix nodes only. The
    smoothing denominator reserves one extra unknown bucket per depth, so the
    listed probabilities sum to slightly below one; this keeps unseen held-out
    prefixes well-defined without adding synthetic empirical rows.
    """

    missing = [column for column in (*config.hierarchy, config.label_column) if column not in train.columns]
    if missing:
        raise KeyError(f"train frame missing required columns: {missing}")
    spec = _infer_spec(train, config.hierarchy)
    encoded = encode_frame(train, spec)
    labels = train[config.label_column].astype(int).reset_index(drop=True)
    normal_codes = encoded.codes.reset_index(drop=True)[labels == 0]
    if normal_codes.empty:
        raise ValueError("normal training rows are required to estimate prefix probabilities")
    normal_values = [int(code) for code in normal_codes]
    n_normal = len(normal_values)
    rows: list[dict[str, object]] = []
    prime = int(encoded.spec.prime or 2)
    counts_by_depth: dict[int, Counter[int]] = {}
    for depth in range(1, len(config.hierarchy) + 1):
        modulus = prime**depth
        counts = Counter(code % modulus for code in normal_values)
        counts_by_depth[depth] = counts
    children_by_parent: dict[tuple[int, int], set[int]] = {}
    for depth, counts in counts_by_depth.items():
        if depth <= 1:
            continue
        parent_modulus = prime ** (depth - 1)
        for node in counts:
            parent_node = node % parent_modulus
            children_by_parent.setdefault((depth, parent_node), set()).add(node)
    for depth in range(1, len(config.hierarchy) + 1):
        counts = counts_by_depth[depth]
        # +1 reserves an unseen/unknown prefix bucket without fabricating rows.
        denominator = n_normal + config.alpha * (len(counts) + 1)
        for node, count in sorted(counts.items(), key=lambda item: item[0]):
            parent_node = None
            parent_count = None
            conditional_probability = None
            conditional_support_ok = False
            if depth > 1:
                parent_node = int(node % (prime ** (depth - 1)))
                parent_count = int(counts_by_depth[depth - 1][parent_node])
                n_children = len(children_by_parent.get((depth, parent_node), set()))
                conditional_denominator = parent_count + config.alpha * (n_children + 1)
                conditional_probability = float((count + config.alpha) / conditional_denominator)
                conditional_support_ok = bool(count >= config.min_support and parent_count >= config.min_support)
            rows.append(
                {
                    "depth": int(depth),
                    "node": int(node),
                    "parent_node": parent_node,
                    "train_normal_parent_count": parent_count,
                    "train_normal_count": int(count),
                    "train_normal_probability": float((count + config.alpha) / denominator),
                    "train_normal_conditional_probability": conditional_probability,
                    "support_ok": bool(count >= config.min_support),
                    "conditional_support_ok": conditional_support_ok,
                }
            )
    return pd.DataFrame(rows), encoded


def _assign_equal_count_blocks(frame: pd.DataFrame, n_blocks: int) -> pd.Series:
    if n_blocks < 1:
        raise ValueError("n_blocks must be positive")
    if frame.empty:
        raise ValueError("cannot assign blocks to an empty frame")
    ids = (pd.RangeIndex(len(frame)).to_series(index=frame.index).astype(float) * n_blocks / len(frame)).astype(int)
    return ids.clip(upper=n_blocks - 1).rename("block_id")


def _prefix_counts_by_depth(
    codes: list[int],
    prime: int,
    max_depth: int,
) -> dict[int, Counter[int]]:
    """Count all observed p-adic prefixes once per depth for one block."""

    return {
        depth: Counter(code % (prime**depth) for code in codes)
        for depth in range(1, max_depth + 1)
    }


def run_fixed_block_tree_scan(
    train: pd.DataFrame,
    test: pd.DataFrame,
    config: TreeScanHierarchyConfig,
    *,
    time_column: str,
    n_blocks: int = 96,
) -> pd.DataFrame:
    """Run a fixed equal-count block p-adic prefix-ball excess scan."""

    if time_column not in train.columns or time_column not in test.columns:
        raise KeyError(f"missing time column: {time_column}")
    if config.label_column not in test.columns:
        raise KeyError(f"test frame missing label column: {config.label_column}")
    node_table, train_encoded = build_prefix_node_table(train, config)
    test_ordered = test.sort_values(time_column, kind="mergesort").reset_index(drop=True).copy()
    test_encoded = encode_frame(test_ordered, train_encoded.spec, digit_maps=train_encoded.digit_maps)
    test_ordered["_tree_scan_code"] = test_encoded.codes.reset_index(drop=True).astype(object)
    test_ordered["block_id"] = _assign_equal_count_blocks(test_ordered, n_blocks).to_numpy()
    supported = node_table[node_table["support_ok"]].copy()
    if supported.empty:
        supported = node_table.sort_values("train_normal_count", ascending=False).head(1).copy()
    prime = int(train_encoded.spec.prime or 2)
    rows: list[dict[str, object]] = []
    for block_id, group in test_ordered.groupby("block_id", sort=True):
        total = int(len(group))
        labels = group[config.label_column].astype(int)
        codes = [int(code) for code in group["_tree_scan_code"].tolist()]
        prefix_counts = _prefix_counts_by_depth(codes, prime, len(config.hierarchy))
        best: dict[str, object] | None = None
        for node in supported.itertuples(index=False):
            depth = int(getattr(node, "depth"))
            node_value = int(getattr(node, "node"))
            probability = float(getattr(node, "train_normal_probability"))
            observed = int(prefix_counts[depth].get(node_value, 0))
            llr = binomial_excess_llr(observed, total, probability)
            candidate = {
                "tree_scan_llr": float(llr),
                "tree_scan_depth": depth,
                "tree_scan_node": node_value,
                "tree_scan_observed": observed,
                "tree_scan_expected": float(total * probability),
                "tree_scan_support_ok": bool(getattr(node, "support_ok")),
            }
            if best is None or float(candidate["tree_scan_llr"]) > float(best["tree_scan_llr"]):
                best = candidate
        assert best is not None
        rows.append(
            {
                "block_id": int(block_id),
                "block_start_time": float(group[time_column].iloc[0]),
                "block_end_time": float(group[time_column].iloc[-1]),
                "rows": total,
                "positive_count": int(labels.sum()),
                "positive_rate": float(labels.mean()),
                **best,
            }
        )
    return pd.DataFrame(rows)


def run_fixed_block_conditional_tree_scan(
    train: pd.DataFrame,
    test: pd.DataFrame,
    config: TreeScanHierarchyConfig,
    *,
    time_column: str,
    n_blocks: int = 96,
) -> pd.DataFrame:
    """Run parent-conditioned p-adic prefix-ball excess scans.

    This residual variant asks whether a child prefix has excess mass after
    conditioning on its observed parent prefix mass inside the same block. It
    reduces plain high-level volume or entropy shifts from masquerading as
    hierarchy-specific branch concentration.
    """

    if time_column not in train.columns or time_column not in test.columns:
        raise KeyError(f"missing time column: {time_column}")
    if config.label_column not in test.columns:
        raise KeyError(f"test frame missing label column: {config.label_column}")
    node_table, train_encoded = build_prefix_node_table(train, config)
    test_ordered = test.sort_values(time_column, kind="mergesort").reset_index(drop=True).copy()
    test_encoded = encode_frame(test_ordered, train_encoded.spec, digit_maps=train_encoded.digit_maps)
    test_ordered["_tree_scan_code"] = test_encoded.codes.reset_index(drop=True).astype(object)
    test_ordered["block_id"] = _assign_equal_count_blocks(test_ordered, n_blocks).to_numpy()
    supported = node_table[
        node_table["conditional_support_ok"] & node_table["train_normal_conditional_probability"].notna()
    ].copy()
    if supported.empty:
        supported = node_table[node_table["depth"] > 1].sort_values(
            "train_normal_count", ascending=False
        ).head(1).copy()
    prime = int(train_encoded.spec.prime or 2)
    rows: list[dict[str, object]] = []
    for block_id, group in test_ordered.groupby("block_id", sort=True):
        total_rows = int(len(group))
        labels = group[config.label_column].astype(int)
        codes = [int(code) for code in group["_tree_scan_code"].tolist()]
        prefix_counts = _prefix_counts_by_depth(codes, prime, len(config.hierarchy))
        best: dict[str, object] | None = None
        for node in supported.itertuples(index=False):
            depth = int(getattr(node, "depth"))
            node_value = int(getattr(node, "node"))
            parent_node = int(getattr(node, "parent_node"))
            probability = float(getattr(node, "train_normal_conditional_probability"))
            parent_total = int(prefix_counts[depth - 1].get(parent_node, 0))
            observed = int(prefix_counts[depth].get(node_value, 0))
            llr = 0.0 if parent_total <= 0 else binomial_excess_llr(observed, parent_total, probability)
            candidate = {
                "conditional_tree_scan_llr": float(llr),
                "conditional_tree_scan_depth": depth,
                "conditional_tree_scan_node": node_value,
                "conditional_tree_scan_parent_node": parent_node,
                "conditional_tree_scan_observed": observed,
                "conditional_tree_scan_parent_observed": parent_total,
                "conditional_tree_scan_expected": float(parent_total * probability),
                "conditional_tree_scan_support_ok": bool(getattr(node, "conditional_support_ok")),
            }
            if best is None or float(candidate["conditional_tree_scan_llr"]) > float(
                best["conditional_tree_scan_llr"]
            ):
                best = candidate
        assert best is not None
        rows.append(
            {
                "block_id": int(block_id),
                "block_start_time": float(group[time_column].iloc[0]),
                "block_end_time": float(group[time_column].iloc[-1]),
                "rows": total_rows,
                "positive_count": int(labels.sum()),
                "positive_rate": float(labels.mean()),
                **best,
            }
        )
    return pd.DataFrame(rows)


def _safe_metric(func, y_true: pd.Series, scores: pd.Series) -> float:
    y = y_true.astype(int)
    s = scores.astype(float)
    if y.nunique(dropna=False) < 2 or s.nunique(dropna=False) <= 1:
        return float("nan")
    return float(func(y, s))


def _bootstrap_delta(y_true: pd.Series, proposed: pd.Series, control: pd.Series, n_bootstrap: int, seed: int = 41) -> dict[str, float]:
    y = y_true.astype(int).to_numpy()
    a = proposed.astype(float).to_numpy()
    b = control.astype(float).to_numpy()
    rng = np.random.default_rng(seed)
    deltas: list[float] = []
    for _ in range(int(n_bootstrap)):
        idx = rng.integers(0, len(y), len(y))
        if len(set(y[idx].tolist())) < 2:
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


def _category_entropy(frame: pd.DataFrame, columns: tuple[str, ...]) -> float:
    total = 0.0
    for column in columns:
        probs = frame[column].astype(str).value_counts(normalize=True)
        if len(probs):
            total += float(-(probs * np.log2(probs)).sum())
    return total


def _categorical_scan_blocks(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    columns: tuple[str, ...],
    label_column: str,
    time_column: str,
    n_blocks: int,
    min_support: int,
    alpha: float,
) -> pd.Series:
    normal = train[train[label_column].astype(int) == 0]
    train_keys = normal[list(columns)].astype(str).agg("|".join, axis=1)
    counts = train_keys.value_counts()
    supported = counts[counts >= min_support]
    if supported.empty:
        supported = counts.head(1)
    denominator = len(train_keys) + alpha * (len(counts) + 1)
    probabilities = {key: float((count + alpha) / denominator) for key, count in supported.items()}
    ordered = test.sort_values(time_column, kind="mergesort").reset_index(drop=True).copy()
    ordered["_scan_key"] = ordered[list(columns)].astype(str).agg("|".join, axis=1)
    ordered["block_id"] = _assign_equal_count_blocks(ordered, n_blocks).to_numpy()
    values = []
    for _, group in ordered.groupby("block_id", sort=True):
        total = len(group)
        block_counts = group["_scan_key"].value_counts()
        best = 0.0
        for key, probability in probabilities.items():
            llr = binomial_excess_llr(int(block_counts.get(key, 0)), total, probability)
            if llr > best:
                best = llr
        values.append(float(best))
    return pd.Series(values)


def _random_hierarchy(base: tuple[str, ...], seed: int) -> tuple[str, ...]:
    rng = np.random.default_rng(seed)
    arr = np.array(base, dtype=object)
    for _ in range(10):
        candidate_arr = arr.copy()
        rng.shuffle(candidate_arr)
        candidate = tuple(str(x) for x in candidate_arr.tolist())
        if candidate != base:
            return candidate
    return tuple(reversed(base))


def parse_cse_cic_timestamp_seconds(values: pd.Series) -> pd.Series:
    """Parse CSE-CIC-IDS2018 timestamps into Unix seconds without unit truncation.

    Pandas may store parsed timestamps as datetime64[us] on this environment;
    subtracting the Unix epoch and dividing by a Timedelta avoids the prior bug
    where microsecond ticks were divided by 1e9 and collapsed the scale.
    """

    parsed = pd.to_datetime(values.astype(str), format="%d/%m/%Y %H:%M:%S", errors="coerce")
    epoch = pd.Timestamp("1970-01-01")
    return ((parsed - epoch) // pd.Timedelta(seconds=1)).astype("Int64")


def _resolve_cse_cic_file(data_root: str | Path) -> Path:
    path = Path(data_root)
    if path.is_file():
        return path
    candidate = path / CSE_CIC_THURSDAY_FILE.name
    if candidate.exists():
        return candidate
    if path == CSE_CIC_THURSDAY_FILE.parent and CSE_CIC_THURSDAY_FILE.exists():
        return CSE_CIC_THURSDAY_FILE
    raise FileNotFoundError(
        f"Missing CSE-CIC-IDS2018 processed Thursday file: {candidate}. "
        "Download it from the official CSE-CIC-IDS2018 AWS Open Data location."
    )


def _dst_port_band(value: object) -> str:
    try:
        port = int(float(str(value).strip()))
    except (TypeError, ValueError):
        return "missing_or_nonstandard"
    if port < 0:
        return "missing_or_nonstandard"
    if port <= 1023:
        return "system"
    if port <= 49151:
        return "registered"
    if port <= 65535:
        return "dynamic"
    return "missing_or_nonstandard"


def load_cse_cic_processed_frame(
    data_root: str | Path,
    *,
    nrows: int | None = None,
) -> pd.DataFrame:
    """Load one official CSE-CIC-IDS2018 processed flow file.

    The hierarchy intentionally excludes target-derived attack-family labels.
    Labels are converted only to the binary evaluation field ``is_attack``.
    """

    path = _resolve_cse_cic_file(data_root)
    required = [
        "Dst Port",
        "Protocol",
        "Timestamp",
        "SYN Flag Cnt",
        "ACK Flag Cnt",
        "PSH Flag Cnt",
        "Label",
    ]
    frame = pd.read_csv(path, usecols=required, low_memory=False, nrows=nrows)
    frame = frame[frame["Label"].astype(str).str.strip().ne("Label")].copy()
    frame["timestamp_seconds"] = parse_cse_cic_timestamp_seconds(frame["Timestamp"])
    frame = frame[frame["timestamp_seconds"].notna()].copy()
    frame["timestamp_seconds"] = frame["timestamp_seconds"].astype("int64")
    frame["is_attack"] = frame["Label"].astype(str).str.strip().ne("Benign").astype(int)
    frame["dst_port_band"] = frame["Dst Port"].map(_dst_port_band)
    for column in CSE_CIC_HIERARCHY:
        frame[column] = frame[column].astype(str).fillna("missing")
    return frame.sort_values("timestamp_seconds", kind="mergesort").reset_index(drop=True)


def load_cse_cic_thursday_frame(data_root: str | Path = CSE_CIC_THURSDAY_FILE) -> pd.DataFrame:
    """Load the official CSE-CIC-IDS2018 Thursday processed flow file."""

    return load_cse_cic_processed_frame(data_root)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def run_tree_scan_claim_audit(
    train: pd.DataFrame,
    test: pd.DataFrame,
    config: TreeScanHierarchyConfig,
    *,
    time_column: str,
    n_blocks: int = 96,
    bootstrap_samples: int = 500,
    random_hierarchy_seeds: tuple[int, ...] = (11, 17, 23, 31, 47),
) -> dict[str, pd.DataFrame]:
    """Run proposed p-adic tree scan plus mandatory fail-closed controls."""

    blocks = run_fixed_block_tree_scan(train, test, config, time_column=time_column, n_blocks=n_blocks)
    blocks = blocks.rename(columns={"tree_scan_llr": "p_adic_tree_scan_llr"})
    conditional_blocks = run_fixed_block_conditional_tree_scan(
        train, test, config, time_column=time_column, n_blocks=n_blocks
    )
    blocks["p_adic_conditional_tree_scan_llr"] = conditional_blocks[
        "conditional_tree_scan_llr"
    ].to_numpy()
    for column in (
        "conditional_tree_scan_depth",
        "conditional_tree_scan_node",
        "conditional_tree_scan_parent_node",
        "conditional_tree_scan_observed",
        "conditional_tree_scan_parent_observed",
        "conditional_tree_scan_expected",
        "conditional_tree_scan_support_ok",
    ):
        blocks[column] = conditional_blocks[column].to_numpy()
    blocks["flat_tuple_scan_llr"] = _categorical_scan_blocks(
        train,
        test,
        columns=config.hierarchy,
        label_column=config.label_column,
        time_column=time_column,
        n_blocks=n_blocks,
        min_support=config.min_support,
        alpha=config.alpha,
    ).to_numpy()
    marginal_scores = []
    for column in config.hierarchy:
        marginal_scores.append(
            _categorical_scan_blocks(
                train,
                test,
                columns=(column,),
                label_column=config.label_column,
                time_column=time_column,
                n_blocks=n_blocks,
                min_support=config.min_support,
                alpha=config.alpha,
            ).to_numpy()
        )
    blocks["marginal_column_scan_llr"] = np.max(np.vstack(marginal_scores), axis=0) if marginal_scores else 0.0
    reversed_config = TreeScanHierarchyConfig(
        hierarchy=tuple(reversed(config.hierarchy)),
        label_column=config.label_column,
        min_support=config.min_support,
        alpha=config.alpha,
    )
    blocks["reversed_hierarchy_tree_scan_llr"] = run_fixed_block_tree_scan(
        train, test, reversed_config, time_column=time_column, n_blocks=n_blocks
    )["tree_scan_llr"].to_numpy()
    for seed in random_hierarchy_seeds:
        random_config = TreeScanHierarchyConfig(
            hierarchy=_random_hierarchy(config.hierarchy, seed),
            label_column=config.label_column,
            min_support=config.min_support,
            alpha=config.alpha,
        )
        blocks[f"random_hierarchy_tree_scan_llr_seed_{seed}"] = run_fixed_block_tree_scan(
            train, test, random_config, time_column=time_column, n_blocks=n_blocks
        )["tree_scan_llr"].to_numpy()
    ordered = test.sort_values(time_column, kind="mergesort").reset_index(drop=True).copy()
    ordered["block_id"] = _assign_equal_count_blocks(ordered, n_blocks).to_numpy()
    entropy = []
    count_signal = []
    for _, group in ordered.groupby("block_id", sort=True):
        entropy.append(_category_entropy(group, config.hierarchy))
        count_signal.append(float(len(group)))
    blocks["category_entropy_temporal"] = entropy
    blocks["transaction_count_signal"] = count_signal
    y = (blocks["positive_rate"] >= blocks["positive_rate"].quantile(0.75)).astype(int)
    method_families = {
        "p_adic_tree_scan_llr": "proposed",
        "p_adic_conditional_tree_scan_llr": "proposed",
        "flat_tuple_scan_llr": "flat_control",
        "marginal_column_scan_llr": "marginal_control",
        "reversed_hierarchy_tree_scan_llr": "hierarchy_order_control",
        "category_entropy_temporal": "entropy_control",
        "transaction_count_signal": "count_control",
    }
    for seed in random_hierarchy_seeds:
        method_families[f"random_hierarchy_tree_scan_llr_seed_{seed}"] = "hierarchy_order_control"
    rows = []
    for method, family in method_families.items():
        rows.append(
            {
                "method": method,
                "family": family,
                "auprc": _safe_metric(average_precision_score, y, blocks[method]),
                "roc_auc": _safe_metric(roc_auc_score, y, blocks[method]),
            }
        )
    claims = pd.DataFrame(rows)
    proposed = claims[claims["family"] == "proposed"].sort_values("auprc", ascending=False).iloc[0]
    control = claims[claims["family"] != "proposed"].sort_values("auprc", ascending=False).iloc[0]
    ci = _bootstrap_delta(y, blocks[str(proposed["method"])], blocks[str(control["method"])], bootstrap_samples)
    passed = float(proposed["auprc"]) > float(control["auprc"]) and ci["lower"] > 0 and ci["p_delta_le_zero"] <= 0.05
    claim_status = "q1_candidate_tree_scan_passed_controls" if passed else "diagnostic_only_failed_q1_tree_scan_gate"
    claims["best_proposed_method"] = str(proposed["method"])
    claims["best_control_method"] = str(control["method"])
    claims["best_proposed_auprc"] = float(proposed["auprc"])
    claims["best_control_auprc"] = float(control["auprc"])
    claims["delta_best_proposed_vs_best_control_auprc"] = float(proposed["auprc"] - control["auprc"])
    claims["bootstrap_delta_lower"] = ci["lower"]
    claims["bootstrap_delta_upper"] = ci["upper"]
    claims["bootstrap_p_delta_le_zero"] = ci["p_delta_le_zero"]
    claims["claim_status"] = claim_status
    return {"claims": claims, "blocks": blocks}


def _ensure_artifact_dirs(output_root: Path) -> None:
    for subdir in ("tables", "metrics", "figures", "manifests"):
        (output_root / subdir).mkdir(parents=True, exist_ok=True)


def _write_tree_scan_figure(blocks: pd.DataFrame, claims: pd.DataFrame, path: Path) -> tuple[float, float]:
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=False)
    axes[0].plot(blocks["block_id"], blocks["positive_rate"], color="black", linewidth=1.5, label="held-out block positive rate")
    axes[0].plot(blocks["block_id"], blocks["p_adic_tree_scan_llr"], color="#1f77b4", alpha=0.8, label="p-adic tree scan LLR")
    if "flat_tuple_scan_llr" in blocks:
        axes[0].plot(blocks["block_id"], blocks["flat_tuple_scan_llr"], color="#555555", alpha=0.7, label="flat tuple scan LLR")
    axes[0].set_ylabel("Block signal")
    axes[0].legend(fontsize=7, loc="best")
    top = claims.sort_values("auprc", ascending=True).tail(8)
    colors = ["#1f77b4" if family == "proposed" else "#666666" for family in top["family"]]
    axes[1].barh(top["method"], top["auprc"], color=colors)
    axes[1].tick_params(axis="y", labelsize=6)
    axes[1].set_xlabel("Block high-risk AUPRC")
    fig.suptitle("P-adic tree-scan CUSUM fail-closed gate", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=610)
    plt.close(fig)
    with Image.open(path) as image:
        return tuple(float(x) for x in image.info.get("dpi", (610.0, 610.0)))


def run_ieee_tree_scan_audit(
    data_root: str | Path = DEFAULT_OFFICIAL_ROOT,
    output_root: str | Path = "outputs/p_adic_ieee_cis_tree_scan",
    max_rows: int | None = None,
    n_blocks: int = 96,
    bootstrap_samples: int = 500,
    random_hierarchy_seeds: tuple[int, ...] = (11, 17, 23, 31, 47),
) -> dict[str, object]:
    """Run the official IEEE-CIS p-adic tree-scan audit and write artifacts."""

    output_root = Path(output_root)
    _ensure_artifact_dirs(output_root)
    transaction, identity = _load_ieee(Path(data_root))
    if max_rows is not None:
        transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(int(max_rows)).copy()
        identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    config = TreeScanHierarchyConfig(
        hierarchy=("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain"),
        label_column="isFraud",
        min_support=20,
        alpha=0.5,
    )
    result = run_tree_scan_claim_audit(
        train,
        test,
        config,
        time_column="TransactionDT",
        n_blocks=n_blocks,
        bootstrap_samples=bootstrap_samples,
        random_hierarchy_seeds=random_hierarchy_seeds,
    )
    claims = result["claims"]
    blocks = result["blocks"]
    dataset_name = "official_ieee_cis_tree_scan_surveillance"
    claims_path = output_root / "tables" / f"{dataset_name}_claims.csv"
    blocks_path = output_root / "metrics" / f"{dataset_name}_blocks.csv"
    figure_path = output_root / "figures" / f"{dataset_name}_gate.png"
    metadata_path = output_root / "manifests" / f"{dataset_name}_metadata.json"
    claims.to_csv(claims_path, index=False)
    claims.to_markdown(claims_path.with_suffix(".md"), index=False)
    blocks.to_csv(blocks_path, index=False)
    dpi = _write_tree_scan_figure(blocks, claims, figure_path)
    metadata = {
        "dataset": dataset_name,
        "data_root": str(data_root),
        "synthetic_data_used": False,
        "spec_doc": "docs/rebuild/23_P_ADIC_TREE_SCAN_CUSUM_Q1_SPEC_AND_DECISION.md",
        "rows": int(len(frame)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "n_blocks": int(n_blocks),
        "hierarchy": "|".join(config.hierarchy),
        "best_proposed_method": str(claims["best_proposed_method"].iloc[0]),
        "best_control_method": str(claims["best_control_method"].iloc[0]),
        "claim_status": str(claims["claim_status"].iloc[0]),
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


def run_cse_cic_thursday_tree_scan_audit(
    data_root: str | Path = CSE_CIC_THURSDAY_FILE,
    output_root: str | Path = "outputs/p_adic_cse_cic_thursday_tree_scan",
    max_rows: int | None = None,
    n_blocks: int = 96,
    bootstrap_samples: int = 500,
    random_hierarchy_seeds: tuple[int, ...] = (11, 17, 23, 31, 47),
) -> dict[str, object]:
    """Run the CSE-CIC-IDS2018 Thursday external tree-scan audit."""

    output_root = Path(output_root)
    _ensure_artifact_dirs(output_root)
    frame = load_cse_cic_thursday_frame(data_root)
    if max_rows is not None:
        frame = frame.head(int(max_rows)).copy()
    train, test = temporal_train_test_split(frame, "timestamp_seconds", train_fraction=0.7)
    config = TreeScanHierarchyConfig(
        hierarchy=CSE_CIC_HIERARCHY,
        label_column="is_attack",
        min_support=20,
        alpha=0.5,
    )
    result = run_tree_scan_claim_audit(
        train,
        test,
        config,
        time_column="timestamp_seconds",
        n_blocks=n_blocks,
        bootstrap_samples=bootstrap_samples,
        random_hierarchy_seeds=random_hierarchy_seeds,
    )
    claims = result["claims"]
    blocks = result["blocks"]
    dataset_name = "official_cse_cic_ids2018_thursday_tree_scan_surveillance"
    claims_path = output_root / "tables" / f"{dataset_name}_claims.csv"
    blocks_path = output_root / "metrics" / f"{dataset_name}_blocks.csv"
    figure_path = output_root / "figures" / f"{dataset_name}_gate.png"
    metadata_path = output_root / "manifests" / f"{dataset_name}_metadata.json"
    claims.to_csv(claims_path, index=False)
    claims.to_markdown(claims_path.with_suffix(".md"), index=False)
    blocks.to_csv(blocks_path, index=False)
    dpi = _write_tree_scan_figure(blocks, claims, figure_path)
    metadata = {
        "dataset": dataset_name,
        "data_root": str(data_root),
        "synthetic_data_used": False,
        "source_dataset_card": "docs/rebuild/dataset_cards/cse_cic_ids2018_thursday_2018_03_01.md",
        "source_urls": [
            "https://www.unb.ca/cic/datasets/ids-2018.html",
            "https://registry.opendata.aws/cse-cic-ids2018/",
        ],
        "rows": int(len(frame)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "n_blocks": int(n_blocks),
        "positive_label_rule": "Label != Benign",
        "hierarchy": "|".join(config.hierarchy),
        "label_leakage_guard": "attack labels are excluded from hierarchy and used only for final block metrics",
        "best_proposed_method": str(claims["best_proposed_method"].iloc[0]),
        "best_control_method": str(claims["best_control_method"].iloc[0]),
        "claim_status": str(claims["claim_status"].iloc[0]),
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


def run_cse_cic_wednesday_tree_scan_audit(
    data_root: str | Path = CSE_CIC_WEDNESDAY_FILE,
    output_root: str | Path = "outputs/p_adic_cse_cic_wednesday_tree_scan",
    max_rows: int | None = None,
    n_blocks: int = 96,
    bootstrap_samples: int = 500,
    random_hierarchy_seeds: tuple[int, ...] = (11, 17, 23, 31, 47),
) -> dict[str, object]:
    """Run the preregistered fresh Wednesday CSE-CIC tree-scan audit."""

    data_path = _resolve_cse_cic_file(data_root)
    source_sha256 = _sha256(data_path)
    if source_sha256 != CSE_CIC_WEDNESDAY_SHA256:
        raise ValueError(
            "CSE-CIC Wednesday file checksum mismatch: "
            f"expected {CSE_CIC_WEDNESDAY_SHA256}, observed {source_sha256}"
        )
    output_root = Path(output_root)
    _ensure_artifact_dirs(output_root)
    frame = load_cse_cic_processed_frame(data_path)
    if max_rows is not None:
        frame = frame.head(int(max_rows)).copy()
    train, test = temporal_train_test_split(frame, "timestamp_seconds", train_fraction=0.7)
    config = TreeScanHierarchyConfig(
        hierarchy=CSE_CIC_HIERARCHY,
        label_column="is_attack",
        min_support=20,
        alpha=0.5,
    )
    result = run_tree_scan_claim_audit(
        train,
        test,
        config,
        time_column="timestamp_seconds",
        n_blocks=n_blocks,
        bootstrap_samples=bootstrap_samples,
        random_hierarchy_seeds=random_hierarchy_seeds,
    )
    claims = result["claims"]
    blocks = result["blocks"]
    dataset_name = "official_cse_cic_ids2018_wednesday_2018_02_28_tree_scan_surveillance"
    claims_path = output_root / "tables" / f"{dataset_name}_claims.csv"
    blocks_path = output_root / "metrics" / f"{dataset_name}_blocks.csv"
    figure_path = output_root / "figures" / f"{dataset_name}_gate.png"
    metadata_path = output_root / "manifests" / f"{dataset_name}_metadata.json"
    claims.to_csv(claims_path, index=False)
    claims.to_markdown(claims_path.with_suffix(".md"), index=False)
    blocks.to_csv(blocks_path, index=False)
    dpi = _write_tree_scan_figure(blocks, claims, figure_path)
    metadata = {
        "dataset": dataset_name,
        "data_root": str(data_path),
        "source_file_sha256": source_sha256,
        "synthetic_data_used": False,
        "preregistered_fresh_external_validation": True,
        "preregistration_doc": "docs/rebuild/28_CSE_CIC_SECOND_DAY_PREREGISTRATION.md",
        "source_urls": [
            "https://www.unb.ca/cic/datasets/ids-2018.html",
            "https://registry.opendata.aws/cse-cic-ids2018/",
        ],
        "rows": int(len(frame)),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "n_blocks": int(n_blocks),
        "positive_label_rule": "Label != Benign",
        "hierarchy": "|".join(config.hierarchy),
        "label_leakage_guard": "attack labels are excluded from hierarchy and used only for final block metrics",
        "best_proposed_method": str(claims["best_proposed_method"].iloc[0]),
        "best_control_method": str(claims["best_control_method"].iloc[0]),
        "claim_status": str(claims["claim_status"].iloc[0]),
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run fail-closed p-adic tree-scan CUSUM audits on official real datasets."
    )
    parser.add_argument(
        "--dataset",
        choices=["ieee", "cse-cic-thursday", "cse-cic-wednesday"],
        default="ieee",
    )
    parser.add_argument("--data-root", default=str(DEFAULT_OFFICIAL_ROOT))
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--n-blocks", type=int, default=96)
    parser.add_argument("--bootstrap-samples", type=int, default=500)
    parser.add_argument("--random-hierarchy-seeds", default="11,17,23,31,47")
    args = parser.parse_args()
    seeds = tuple(int(part.strip()) for part in args.random_hierarchy_seeds.split(",") if part.strip())
    if args.dataset == "ieee":
        result = run_ieee_tree_scan_audit(
            data_root=args.data_root,
            output_root=args.output_root or "outputs/p_adic_ieee_cis_tree_scan",
            max_rows=args.max_rows,
            n_blocks=args.n_blocks,
            bootstrap_samples=args.bootstrap_samples,
            random_hierarchy_seeds=seeds,
        )
    elif args.dataset == "cse-cic-thursday":
        data_root = CSE_CIC_THURSDAY_FILE if args.data_root == str(DEFAULT_OFFICIAL_ROOT) else args.data_root
        result = run_cse_cic_thursday_tree_scan_audit(
            data_root=data_root,
            output_root=args.output_root or "outputs/p_adic_cse_cic_thursday_tree_scan",
            max_rows=args.max_rows,
            n_blocks=args.n_blocks,
            bootstrap_samples=args.bootstrap_samples,
            random_hierarchy_seeds=seeds,
        )
    else:
        data_root = CSE_CIC_WEDNESDAY_FILE if args.data_root == str(DEFAULT_OFFICIAL_ROOT) else args.data_root
        result = run_cse_cic_wednesday_tree_scan_audit(
            data_root=data_root,
            output_root=args.output_root or "outputs/p_adic_cse_cic_wednesday_tree_scan",
            max_rows=args.max_rows,
            n_blocks=args.n_blocks,
            bootstrap_samples=args.bootstrap_samples,
            random_hierarchy_seeds=seeds,
        )
    print(json.dumps(result["metadata"], indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
