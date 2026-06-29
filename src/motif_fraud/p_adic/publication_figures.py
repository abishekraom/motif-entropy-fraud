"""Publication-grade 600 dpi figures from official IEEE-CIS artifacts."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image


def _dpi(path: Path) -> tuple[float, float]:
    image = Image.open(path)
    info = image.info.get("dpi", (600, 600))
    return float(info[0]), float(info[1])


def _save_temporal_signal(blocks: pd.DataFrame, path: Path, dpi: int = 600) -> tuple[float, float]:
    fig, ax1 = plt.subplots(figsize=(7.0, 4.0))
    ax1.plot(blocks["block_id"], blocks["mean_score"], color="#7c3aed", linewidth=1.8, label="mean p-adic score")
    ax1.set_xlabel("Temporal block")
    ax1.set_ylabel("Mean p-adic prefix-rarity score", color="#7c3aed")
    ax1.tick_params(axis="y", labelcolor="#7c3aed")
    ax2 = ax1.twinx()
    ax2.plot(blocks["block_id"], blocks["fraud_rate"], color="#ef4444", linewidth=1.4, label="fraud rate")
    ax2.set_ylabel("Fraud rate", color="#ef4444")
    ax2.tick_params(axis="y", labelcolor="#ef4444")
    plt.title("Official IEEE-CIS temporal p-adic signal")
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    return _dpi(path)


def _save_control_ablation(claims: pd.DataFrame, path: Path, dpi: int = 600) -> tuple[float, float]:
    rows = claims[claims["control_family"].isin(["proposed", "negative_control"])]
    rows = rows.sort_values("auprc", ascending=True)
    colors = ["#7c3aed" if f == "proposed" else "#64748b" for f in rows["control_family"]]
    plt.figure(figsize=(7.0, 4.0))
    plt.barh(rows["method"], rows["auprc"], color=colors)
    plt.xlabel("AUPRC")
    plt.title("P-adic hierarchy control ablation")
    plt.tight_layout()
    plt.savefig(path, dpi=dpi)
    plt.close()
    return _dpi(path)


def _save_baseline_comparison(baselines: pd.DataFrame, path: Path, dpi: int = 600) -> tuple[float, float]:
    rows = baselines.sort_values("auprc", ascending=True)
    colors = ["#7c3aed" if role == "primary_method" else "#475569" for role in rows["claim_role"]]
    plt.figure(figsize=(7.0, 4.0))
    plt.barh(rows["method"], rows["auprc"], color=colors)
    plt.xlabel("AUPRC")
    plt.title("Official IEEE-CIS broader baseline context")
    plt.tight_layout()
    plt.savefig(path, dpi=dpi)
    plt.close()
    return _dpi(path)


def generate_ieee_publication_figures(
    temporal_blocks_path: str | Path = Path("outputs/p_adic_ieee_cis_official/metrics/p_adic_ieee_cis_temporal_blocks.csv"),
    claims_path: str | Path = Path("outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_claims.csv"),
    baseline_path: str | Path = Path("outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_baseline_comparison.csv"),
    output_root: str | Path = Path("outputs/p_adic_ieee_cis_official/figures"),
) -> dict[str, object]:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    blocks = pd.read_csv(temporal_blocks_path)
    claims = pd.read_csv(claims_path)
    baselines = pd.read_csv(baseline_path)
    temporal_path = output_root / "p_adic_ieee_cis_temporal_signal.png"
    control_path = output_root / "p_adic_ieee_cis_control_ablation.png"
    baseline_fig_path = output_root / "p_adic_ieee_cis_baseline_context.png"
    dpi = {
        "temporal_signal": _save_temporal_signal(blocks, temporal_path),
        "control_ablation": _save_control_ablation(claims, control_path),
        "baseline_comparison": _save_baseline_comparison(baselines, baseline_fig_path),
    }
    return {
        "temporal_signal": temporal_path,
        "control_ablation": control_path,
        "baseline_comparison": baseline_fig_path,
        "dpi": dpi,
    }


if __name__ == "__main__":
    result = generate_ieee_publication_figures()
    for key in ("temporal_signal", "control_ablation", "baseline_comparison"):
        print(key, result[key], result["dpi"][key])
