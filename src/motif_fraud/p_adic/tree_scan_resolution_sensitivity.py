"""Prespecified secondary block-resolution sensitivity for tree-scan gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

import pandas as pd

from motif_fraud.p_adic.tree_scan_cusum import (
    CSE_CIC_THURSDAY_FILE,
    CSE_CIC_WEDNESDAY_FILE,
    DEFAULT_OFFICIAL_ROOT,
    run_cse_cic_thursday_tree_scan_audit,
    run_cse_cic_wednesday_tree_scan_audit,
    run_ieee_tree_scan_audit,
)


PRIMARY_BLOCK_COUNT = 96
SECONDARY_BLOCK_COUNTS = (48, 192)
PREREGISTRATION = (
    "docs/rebuild/30_TREE_SCAN_BLOCK_RESOLUTION_SENSITIVITY_PREREGISTRATION.md"
)
PRIMARY_CROSS_DATASET_STATUS = "diagnostic_only_failed_q1_cross_dataset_gate"


Runner = Callable[..., dict[str, object]]


DATASET_CONFIGS: dict[str, tuple[Runner, Path]] = {
    "official_ieee_cis": (run_ieee_tree_scan_audit, Path(DEFAULT_OFFICIAL_ROOT)),
    "cse_cic_ids2018_thursday": (
        run_cse_cic_thursday_tree_scan_audit,
        CSE_CIC_THURSDAY_FILE,
    ),
    "cse_cic_ids2018_wednesday_2018_02_28": (
        run_cse_cic_wednesday_tree_scan_audit,
        CSE_CIC_WEDNESDAY_FILE,
    ),
}


def summarize_resolution_result(
    dataset: str,
    n_blocks: int,
    result: dict[str, object],
) -> dict[str, object]:
    claims = result["claims"]
    if not isinstance(claims, pd.DataFrame) or claims.empty:
        raise ValueError("tree-scan result must contain a non-empty claims DataFrame")
    first = claims.iloc[0]
    raw = claims.loc[claims["method"] == "p_adic_tree_scan_llr"]
    conditional = claims.loc[claims["method"] == "p_adic_conditional_tree_scan_llr"]
    if raw.empty or conditional.empty:
        raise ValueError("claims table is missing required proposed methods")
    lower = float(first["bootstrap_delta_lower"])
    p_delta = float(first["bootstrap_p_delta_le_zero"])
    delta = float(first["delta_best_proposed_vs_best_control_auprc"])
    exploratory_pass = bool(delta > 0 and lower > 0 and p_delta <= 0.05)
    return {
        "dataset": dataset,
        "n_blocks": int(n_blocks),
        "primary_resolution": bool(n_blocks == PRIMARY_BLOCK_COUNT),
        "best_proposed_method": str(first["best_proposed_method"]),
        "best_control_method": str(first["best_control_method"]),
        "best_proposed_auprc": float(first["best_proposed_auprc"]),
        "best_control_auprc": float(first["best_control_auprc"]),
        "delta_best_proposed_vs_best_control_auprc": delta,
        "bootstrap_delta_lower": lower,
        "bootstrap_delta_upper": float(first["bootstrap_delta_upper"]),
        "bootstrap_p_delta_le_zero": p_delta,
        "conditional_minus_raw_auprc": float(
            conditional["auprc"].iloc[0] - raw["auprc"].iloc[0]
        ),
        "sensitivity_status": (
            "exploratory_pass_not_confirmatory"
            if exploratory_pass
            else "sensitivity_failed_superiority_gate"
        ),
        "primary_cross_dataset_status_unchanged": PRIMARY_CROSS_DATASET_STATUS,
    }


def run_block_resolution_sensitivity(
    output_root: str | Path = "outputs/p_adic_tree_scan_resolution_sensitivity",
    *,
    datasets: tuple[str, ...] = tuple(DATASET_CONFIGS),
    resolutions: tuple[int, ...] = SECONDARY_BLOCK_COUNTS,
    bootstrap_samples: int = 500,
    random_hierarchy_seeds: tuple[int, ...] = (11, 17, 23, 31, 47),
) -> dict[str, object]:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    artifacts: list[dict[str, object]] = []
    for dataset in datasets:
        if dataset not in DATASET_CONFIGS:
            raise ValueError(f"unknown dataset: {dataset}")
        runner, data_root = DATASET_CONFIGS[dataset]
        for n_blocks in resolutions:
            if n_blocks <= 1 or n_blocks == PRIMARY_BLOCK_COUNT:
                raise ValueError("secondary resolutions must exceed one and differ from 96")
            run_root = output_root / dataset / f"blocks_{n_blocks}"
            result = runner(
                data_root=data_root,
                output_root=run_root,
                n_blocks=n_blocks,
                bootstrap_samples=bootstrap_samples,
                random_hierarchy_seeds=random_hierarchy_seeds,
            )
            rows.append(summarize_resolution_result(dataset, n_blocks, result))
            artifacts.append(
                {
                    "dataset": dataset,
                    "n_blocks": int(n_blocks),
                    **dict(result["artifacts"]),
                }
            )

    summary = pd.DataFrame(rows).sort_values(["dataset", "n_blocks"]).reset_index(drop=True)
    summary_path = output_root / "tree_scan_block_resolution_sensitivity.csv"
    metadata_path = output_root / "tree_scan_block_resolution_sensitivity.json"
    summary.to_csv(summary_path, index=False)
    summary.to_markdown(summary_path.with_suffix(".md"), index=False)
    metadata = {
        "preregistration": PREREGISTRATION,
        "analysis_role": "secondary_sensitivity_not_confirmatory",
        "primary_block_count": PRIMARY_BLOCK_COUNT,
        "secondary_block_counts": [int(value) for value in resolutions],
        "bootstrap_samples": int(bootstrap_samples),
        "random_hierarchy_seeds": [int(seed) for seed in random_hierarchy_seeds],
        "synthetic_empirical_data_used": False,
        "primary_cross_dataset_status_unchanged": PRIMARY_CROSS_DATASET_STATUS,
        "exploratory_pass_count": int(
            summary["sensitivity_status"].eq("exploratory_pass_not_confirmatory").sum()
        ),
        "artifacts": artifacts,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {
        "summary": summary,
        "metadata": metadata,
        "artifacts": {
            "summary_csv": str(summary_path),
            "summary_md": str(summary_path.with_suffix(".md")),
            "metadata": str(metadata_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", default="outputs/p_adic_tree_scan_resolution_sensitivity")
    parser.add_argument("--dataset", choices=["all", *DATASET_CONFIGS], default="all")
    parser.add_argument("--resolutions", default="48,192")
    parser.add_argument("--bootstrap-samples", type=int, default=500)
    parser.add_argument("--random-hierarchy-seeds", default="11,17,23,31,47")
    args = parser.parse_args()
    datasets = tuple(DATASET_CONFIGS) if args.dataset == "all" else (args.dataset,)
    resolutions = tuple(int(part.strip()) for part in args.resolutions.split(",") if part.strip())
    seeds = tuple(
        int(part.strip()) for part in args.random_hierarchy_seeds.split(",") if part.strip()
    )
    result = run_block_resolution_sensitivity(
        args.output_root,
        datasets=datasets,
        resolutions=resolutions,
        bootstrap_samples=args.bootstrap_samples,
        random_hierarchy_seeds=seeds,
    )
    print(json.dumps(result["metadata"], indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
