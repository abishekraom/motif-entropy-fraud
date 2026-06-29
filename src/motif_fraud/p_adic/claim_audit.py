"""Claim-to-artifact audit table for IEEE SPL drafting."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path("outputs/p_adic_ieee_cis_official")
TREE_RESULTS = Path("results/q1_upgrade_failures/tree_scan_cusum")
CSE_THURSDAY_RESULTS = Path("results/q1_upgrade_failures/cse_cic_thursday_tree_scan")
CSE_WEDNESDAY_RESULTS = Path("results/q1_upgrade_failures/cse_cic_wednesday_tree_scan")
THEORY_ROOT = Path("docs/rebuild")


def _row(claim: str, status: str, artifact: str, command: str, position: str) -> dict[str, str]:
    return {
        "claim": claim,
        "status": status,
        "evidence_artifact": artifact,
        "command": command,
        "paper_position": position,
    }


def build_ieee_spl_claim_audit() -> pd.DataFrame:
    """Return defensible and unsafe manuscript claims with evidence mapping."""
    baselines_csv = str(ROOT / "tables" / "p_adic_ieee_cis_baseline_comparison.csv")
    control_fig = str(ROOT / "figures" / "p_adic_ieee_cis_control_ablation.png")
    ieee_tree_claims = str(TREE_RESULTS / "official_ieee_cis_tree_scan_surveillance_claims.csv")
    thursday_claims = str(
        CSE_THURSDAY_RESULTS / "official_cse_cic_ids2018_thursday_tree_scan_surveillance_claims.csv"
    )
    wednesday_claims = str(
        CSE_WEDNESDAY_RESULTS
        / "official_cse_cic_ids2018_wednesday_2018_02_28_tree_scan_surveillance_claims.csv"
    )
    wednesday_metadata = str(
        CSE_WEDNESDAY_RESULTS
        / "official_cse_cic_ids2018_wednesday_2018_02_28_tree_scan_surveillance_metadata.json"
    )
    diagnostics = str(THEORY_ROOT / "tree_scan_theory_diagnostics.csv")
    cross_gate = str(THEORY_ROOT / "tree_scan_cross_dataset_gate.json")
    rows = [
        _row(
            "The parent-conditional tree scan improves the raw p-adic tree-scan AUPRC on IEEE-CIS and both evaluated CSE-CIC days.",
            "defensible",
            diagnostics,
            "python -m motif_fraud.p_adic.tree_scan_theory",
            "Results / Conditional residual ablation",
        ),
        _row(
            "The IEEE-CIS conditional tree-scan point estimate exceeds the best registered simple control, but its paired confidence interval crosses zero.",
            "defensible",
            ieee_tree_claims,
            "python -m motif_fraud.p_adic.tree_scan_cusum --dataset ieee",
            "Results / IEEE-CIS gate",
        ),
        _row(
            "Category entropy beats the conditional p-adic tree scan on the CSE-CIC Thursday external day.",
            "defensible",
            thursday_claims,
            "python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-thursday",
            "Results / External Thursday failure",
        ),
        _row(
            "A fresh CSE-CIC Wednesday day was preregistered before download and also failed against category entropy.",
            "defensible",
            wednesday_claims,
            "python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-wednesday",
            "Results / Preregistered fresh-day failure",
        ),
        _row(
            "The preregistered Wednesday artifact uses the verified official source checksum and contains no synthetic empirical data.",
            "defensible",
            wednesday_metadata,
            "python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-wednesday",
            "Reproducibility / Provenance",
        ),
        _row(
            "The current aggregate cross-dataset empirical gate fails closed.",
            "defensible",
            cross_gate,
            "python -m motif_fraud.p_adic.tree_scan_theory",
            "Results / Aggregate claim status",
        ),
        _row(
            "The p-adic method is a competitive or state-of-the-art fraud detector on IEEE-CIS.",
            "unsafe",
            baselines_csv,
            "python -m motif_fraud.p_adic.official_baselines",
            "Do not claim; compact supervised gradient-boosted baselines are far stronger at row-level detection.",
        ),
        _row(
            "The conditional tree scan establishes statistically significant surveillance superiority.",
            "unsafe",
            cross_gate,
            "python -m motif_fraud.p_adic.tree_scan_theory",
            "Do not claim; all three dataset gates retain diagnostic failure status.",
        ),
        _row(
            "The method robustly generalizes across CSE-CIC days.",
            "unsafe",
            wednesday_claims,
            "python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-wednesday",
            "Do not claim; both CSE-CIC days are beaten by entropy control.",
        ),
        _row(
            "Within-level digit labels carry numeric semantic information.",
            "unsafe",
            control_fig,
            "python -m motif_fraud.p_adic.ieee_pipeline",
            "Do not claim; digit relabeling is an invariance check for prefix equality.",
        ),
        _row(
            "The current empirical detector evidence is IEEE SPL/Q1 ready.",
            "unsafe",
            cross_gate,
            "python -m motif_fraud.p_adic.tree_scan_theory",
            "Do not claim; the aggregate cross-dataset gate fails.",
        ),
    ]
    return pd.DataFrame(rows)


def write_ieee_spl_claim_audit(
    output_path: str | Path = Path("docs/rebuild/ieee_spl_claim_audit.csv"),
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    table = build_ieee_spl_claim_audit()
    table.to_csv(output_path, index=False)
    table.to_markdown(output_path.with_suffix(".md"), index=False)
    return output_path


if __name__ == "__main__":
    path = write_ieee_spl_claim_audit()
    print(path)
