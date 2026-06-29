"""Theory and failure-mode diagnostics for p-adic tree-scan gates."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd


DEFAULT_CLAIM_TABLES = {
    "official_ieee_cis": Path(
        "results/q1_upgrade_failures/tree_scan_cusum/"
        "official_ieee_cis_tree_scan_surveillance_claims.csv"
    ),
    "cse_cic_ids2018_thursday": Path(
        "results/q1_upgrade_failures/cse_cic_thursday_tree_scan/"
        "official_cse_cic_ids2018_thursday_tree_scan_surveillance_claims.csv"
    ),
    "cse_cic_ids2018_wednesday_2018_02_28": Path(
        "results/q1_upgrade_failures/cse_cic_wednesday_tree_scan/"
        "official_cse_cic_ids2018_wednesday_2018_02_28_tree_scan_surveillance_claims.csv"
    ),
}


def bernoulli_kl(q: float, p: float) -> float:
    """Return KL(Bernoulli(q) || Bernoulli(p))."""

    q = float(q)
    p = float(p)
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be in [0, 1]")
    eps = 1e-15
    q_safe = min(max(q, eps), 1.0 - eps)
    p_safe = min(max(p, eps), 1.0 - eps)
    return float(
        q_safe * math.log(q_safe / p_safe)
        + (1.0 - q_safe) * math.log((1.0 - q_safe) / (1.0 - p_safe))
    )


def branch_local_expected_llr(interval_rows: int, normal_probability: float, delta: float) -> float:
    """Expected one-node excess LLR under a branch-local probability increase."""

    if interval_rows <= 0:
        raise ValueError("interval_rows must be positive")
    p = float(normal_probability)
    delta = float(delta)
    if delta <= 0:
        raise ValueError("delta must be positive")
    q = p + delta
    if q >= 1.0:
        raise ValueError("normal_probability + delta must be below 1")
    return float(interval_rows * bernoulli_kl(q, p))


def branch_local_small_delta_approx(interval_rows: int, normal_probability: float, delta: float) -> float:
    """Second-order approximation for branch-local excess LLR."""

    if interval_rows <= 0:
        raise ValueError("interval_rows must be positive")
    p = float(normal_probability)
    delta = float(delta)
    if not 0.0 < p < 1.0:
        raise ValueError("normal_probability must be in (0, 1)")
    if delta <= 0:
        raise ValueError("delta must be positive")
    return float(interval_rows * delta * delta / (2.0 * p * (1.0 - p)))


def flat_tuple_dilution_factor(
    exact_tuple_count_under_prefix: int,
    normal_prefix_probability: float,
) -> float:
    """Small-shift prefix-to-best-tuple LLR ratio under equal descendants.

    Assume a prefix has normal probability p, consists of M equally likely
    exact tuples, and a total branch shift delta is distributed equally among
    those tuples. The second-order prefix-to-one-tuple expected LLR ratio is

        M * (1 - p / M) / (1 - p).

    It is approximately M for a rare prefix, not M squared.
    """

    if exact_tuple_count_under_prefix < 1:
        raise ValueError("exact_tuple_count_under_prefix must be positive")
    p = float(normal_prefix_probability)
    if not 0.0 < p < 1.0:
        raise ValueError("normal_prefix_probability must be in (0, 1)")
    m = float(exact_tuple_count_under_prefix)
    return float(m * (1.0 - p / m) / (1.0 - p))


def flat_tuple_exact_llr_advantage(
    normal_prefix_probability: float,
    delta: float,
    exact_tuple_count_under_prefix: int,
) -> float:
    """Exact prefix-to-best-tuple expected LLR ratio for equal descendants."""

    if exact_tuple_count_under_prefix < 1:
        raise ValueError("exact_tuple_count_under_prefix must be positive")
    p = float(normal_prefix_probability)
    delta = float(delta)
    if not 0.0 < p < 1.0:
        raise ValueError("normal_prefix_probability must be in (0, 1)")
    if delta <= 0.0 or p + delta >= 1.0:
        raise ValueError("delta must be positive and keep p + delta below 1")
    m = float(exact_tuple_count_under_prefix)
    prefix_kl = bernoulli_kl(p + delta, p)
    tuple_kl = bernoulli_kl((p + delta) / m, p / m)
    return float(prefix_kl / tuple_kl)


def _require_method(table: pd.DataFrame, method: str) -> pd.Series:
    rows = table[table["method"] == method]
    if rows.empty:
        raise ValueError(f"missing required method: {method}")
    return rows.iloc[0]


def summarize_claim_table(dataset: str, path: str | Path) -> dict[str, object]:
    """Summarize a real fail-closed tree-scan claim table."""

    path = Path(path)
    table = pd.read_csv(path)
    required = {
        "method",
        "family",
        "auprc",
        "roc_auc",
        "best_proposed_method",
        "best_control_method",
        "best_proposed_auprc",
        "best_control_auprc",
        "delta_best_proposed_vs_best_control_auprc",
        "bootstrap_delta_lower",
        "bootstrap_delta_upper",
        "bootstrap_p_delta_le_zero",
        "claim_status",
    }
    missing = required.difference(table.columns)
    if missing:
        raise ValueError(f"{path} missing required columns: {sorted(missing)}")
    raw = _require_method(table, "p_adic_tree_scan_llr")
    conditional = _require_method(table, "p_adic_conditional_tree_scan_llr")
    entropy_rows = table[table["method"] == "category_entropy_temporal"]
    entropy_auprc = float(entropy_rows["auprc"].iloc[0]) if not entropy_rows.empty else float("nan")
    first = table.iloc[0]
    best_control_method = str(first["best_control_method"])
    delta = float(first["delta_best_proposed_vs_best_control_auprc"])
    ci_lower = float(first["bootstrap_delta_lower"])
    p_delta = float(first["bootstrap_p_delta_le_zero"])
    claim_status = str(first["claim_status"])
    if claim_status.startswith("q1_candidate") and delta > 0 and ci_lower > 0 and p_delta <= 0.05:
        failure_mode = "passed_empirical_gate"
    elif best_control_method == "category_entropy_temporal":
        failure_mode = "entropy_dominance"
    elif delta > 0 and ci_lower <= 0:
        failure_mode = "uncertain_positive_delta"
    else:
        failure_mode = "control_dominance"
    return {
        "dataset": dataset,
        "claim_table": path.as_posix(),
        "raw_tree_scan_auprc": float(raw["auprc"]),
        "conditional_tree_scan_auprc": float(conditional["auprc"]),
        "conditional_minus_raw_auprc": float(conditional["auprc"] - raw["auprc"]),
        "entropy_control_auprc": entropy_auprc,
        "best_proposed_method": str(first["best_proposed_method"]),
        "best_control_method": best_control_method,
        "best_proposed_auprc": float(first["best_proposed_auprc"]),
        "best_control_auprc": float(first["best_control_auprc"]),
        "delta_best_proposed_vs_best_control_auprc": delta,
        "bootstrap_delta_lower": ci_lower,
        "bootstrap_delta_upper": float(first["bootstrap_delta_upper"]),
        "bootstrap_p_delta_le_zero": p_delta,
        "failure_mode": failure_mode,
        "claim_status": claim_status,
    }


def build_theory_reference_table() -> pd.DataFrame:
    """Return compact analytic propositions used by the diagnostic report."""

    rows = [
        {
            "proposition": "branch_local_expected_llr",
            "statement": "A branch-local probability shift produces expected LLR n * KL(Bernoulli(p+delta) || Bernoulli(p)).",
            "q1_implication": "Power should grow with interval length and squared local shift when the anomaly is branch-local.",
        },
        {
            "proposition": "flat_tuple_dilution",
            "statement": "For M equal descendants under a prefix of normal probability p, the small-shift prefix-to-best-tuple LLR ratio is M(1-p/M)/(1-p), approximately M for rare prefixes.",
            "q1_implication": "Prefix scans are theoretically useful only when affected exact tuples share a meaningful parent prefix.",
        },
        {
            "proposition": "entropy_dominance_failure",
            "statement": "When high-risk blocks are broad category-diversity shifts rather than branch-local concentration, entropy can beat p-adic scans.",
            "q1_implication": "Entropy dominance is a diagnostic failure mode, not a detector superiority result.",
        },
    ]
    return pd.DataFrame(rows)


def build_tree_scan_theory_diagnostics(
    claim_tables: dict[str, Path] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build real-artifact summaries plus compact theory reference rows."""

    claim_tables = claim_tables or DEFAULT_CLAIM_TABLES
    summary = pd.DataFrame(
        [summarize_claim_table(dataset, path) for dataset, path in claim_tables.items()]
    )
    return summary, build_theory_reference_table()


def write_tree_scan_theory_diagnostics(
    output_root: str | Path = "docs/rebuild",
    claim_tables: dict[str, Path] | None = None,
) -> dict[str, str]:
    """Write diagnostic theory and failure-mode artifacts."""

    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    summary, theory = build_tree_scan_theory_diagnostics(claim_tables)
    summary_path = output_root / "tree_scan_theory_diagnostics.csv"
    theory_path = output_root / "tree_scan_theory_reference.csv"
    metadata_path = output_root / "tree_scan_theory_diagnostics_metadata.json"
    cross_dataset_path = output_root / "tree_scan_cross_dataset_gate.json"
    summary.to_csv(summary_path, index=False)
    summary.to_markdown(summary_path.with_suffix(".md"), index=False)
    theory.to_csv(theory_path, index=False)
    theory.to_markdown(theory_path.with_suffix(".md"), index=False)
    all_dataset_gates_passed = bool(
        len(summary) >= 2
        and summary["claim_status"].astype(str).str.startswith("q1_candidate").all()
        and (summary["bootstrap_delta_lower"].astype(float) > 0).all()
        and (summary["bootstrap_p_delta_le_zero"].astype(float) <= 0.05).all()
    )
    cross_dataset_status = (
        "q1_candidate_cross_dataset_gate_passed"
        if all_dataset_gates_passed
        else "diagnostic_only_failed_q1_cross_dataset_gate"
    )
    metadata = {
        "synthetic_empirical_data_used": False,
        "claim_tables": {dataset: path.as_posix() for dataset, path in (claim_tables or DEFAULT_CLAIM_TABLES).items()},
        "summary_rows": int(len(summary)),
        "theory_rows": int(len(theory)),
        "claim_statuses": sorted(set(summary["claim_status"].astype(str))),
        "failure_modes": sorted(set(summary["failure_mode"].astype(str))),
        "cross_dataset_status": cross_dataset_status,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    cross_dataset = {
        "required_dataset_count_minimum": 2,
        "observed_dataset_count": int(len(summary)),
        "all_dataset_gates_passed": all_dataset_gates_passed,
        "dataset_statuses": dict(
            zip(summary["dataset"].astype(str), summary["claim_status"].astype(str))
        ),
        "cross_dataset_status": cross_dataset_status,
        "synthetic_empirical_data_used": False,
    }
    cross_dataset_path.write_text(json.dumps(cross_dataset, indent=2), encoding="utf-8")
    return {
        "summary_csv": str(summary_path),
        "summary_md": str(summary_path.with_suffix(".md")),
        "theory_csv": str(theory_path),
        "theory_md": str(theory_path.with_suffix(".md")),
        "metadata": str(metadata_path),
        "cross_dataset_gate": str(cross_dataset_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Write p-adic tree-scan theory diagnostics.")
    parser.add_argument("--output-root", default="docs/rebuild")
    args = parser.parse_args()
    artifacts = write_tree_scan_theory_diagnostics(args.output_root)
    print(json.dumps(artifacts, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
