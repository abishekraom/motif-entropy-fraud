"""Publication artifacts for the current p-adic tree-scan diagnostic letter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from motif_fraud.p_adic.tree_scan_theory import DEFAULT_CLAIM_TABLES, summarize_claim_table


DISPLAY_NAMES = {
    "official_ieee_cis": "IEEE-CIS",
    "cse_cic_ids2018_thursday": "CSE Thu",
    "cse_cic_ids2018_wednesday_2018_02_28": "CSE Wed (fresh)",
}


def build_publication_summary() -> pd.DataFrame:
    rows = [summarize_claim_table(dataset, path) for dataset, path in DEFAULT_CLAIM_TABLES.items()]
    table = pd.DataFrame(rows)
    table["display_name"] = table["dataset"].map(DISPLAY_NAMES).fillna(table["dataset"])
    table["ci_excludes_zero"] = table["bootstrap_delta_lower"].astype(float) > 0
    table["fresh_preregistered"] = table["dataset"].eq("cse_cic_ids2018_wednesday_2018_02_28")
    return table


def write_cross_dataset_gate_figure(path: str | Path) -> tuple[float, float]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    table = build_publication_summary()
    x = np.arange(len(table), dtype=float)
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.bar(
        x - width / 2,
        table["best_proposed_auprc"],
        width,
        label="Best proposed",
        color="#2878B5",
    )
    ax.bar(
        x + width / 2,
        table["best_control_auprc"],
        width,
        label="Best control",
        color="#D95F02",
    )
    for index, row in table.reset_index(drop=True).iterrows():
        delta = float(row["delta_best_proposed_vs_best_control_auprc"])
        marker = "CI>0" if bool(row["ci_excludes_zero"]) else "CI crosses 0"
        y = max(float(row["best_proposed_auprc"]), float(row["best_control_auprc"])) + 0.025
        ax.text(index, y, f"$\\Delta$={delta:+.3f}\n{marker}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x, table["display_name"])
    ax.set_ylabel("Block-level AUPRC")
    ax.set_ylim(0, max(table["best_proposed_auprc"].max(), table["best_control_auprc"].max()) + 0.13)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.grid(axis="y", linewidth=0.4, alpha=0.35)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=610)
    plt.close(fig)
    with Image.open(path) as image:
        return tuple(float(value) for value in image.info.get("dpi", (610.0, 610.0)))


def write_tree_scan_publication_artifacts(
    output_root: str | Path = "paper/ieee_spl/tree_scan_artifacts",
) -> dict[str, object]:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    table = build_publication_summary()
    table_path = output_root / "cross_dataset_gate_summary.csv"
    figure_path = output_root / "cross_dataset_gate_auprc.png"
    metadata_path = output_root / "cross_dataset_gate_artifacts.json"
    table.to_csv(table_path, index=False)
    table.to_markdown(table_path.with_suffix(".md"), index=False)
    dpi = write_cross_dataset_gate_figure(figure_path)
    metadata = {
        "synthetic_empirical_data_used": False,
        "source_claim_tables": {
            dataset: path.as_posix() for dataset, path in DEFAULT_CLAIM_TABLES.items()
        },
        "dataset_count": int(len(table)),
        "all_dataset_gates_passed": bool(table["claim_status"].str.startswith("q1_candidate").all()),
        "figure_dpi": list(dpi),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {
        "summary_csv": str(table_path),
        "summary_md": str(table_path.with_suffix(".md")),
        "figure": str(figure_path),
        "metadata": str(metadata_path),
        "figure_dpi": dpi,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Write current tree-scan publication artifacts.")
    parser.add_argument("--output-root", default="paper/ieee_spl/tree_scan_artifacts")
    args = parser.parse_args()
    print(json.dumps(write_tree_scan_publication_artifacts(args.output_root), indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
