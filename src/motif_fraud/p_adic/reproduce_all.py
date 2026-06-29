"""One-command reproduction plan for p-adic IEEE SPL artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def build_reproduction_plan() -> list[dict[str, str]]:
    """Return ordered real-data reproduction commands and artifact checks."""
    return [
        {
            "name": "unit_and_artifact_tests",
            "command": "pytest -q",
            "argv": ["pytest", "-q"],
            "artifact_check": "test suite must pass",
        },
        {
            "name": "official_ieee_cis_padic_audit",
            "command": "python -m motif_fraud.p_adic.ieee_pipeline",
            "argv": ["python", "-m", "motif_fraud.p_adic.ieee_pipeline"],
            "artifact_check": "outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_claims.csv",
        },
        {
            "name": "official_ieee_cis_baseline_context",
            "command": "python -m motif_fraud.p_adic.official_baselines",
            "argv": ["python", "-m", "motif_fraud.p_adic.official_baselines"],
            "artifact_check": "outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_baseline_comparison.csv",
        },
        {
            "name": "official_ieee_cis_publication_figures",
            "command": "python -m motif_fraud.p_adic.publication_figures",
            "argv": ["python", "-m", "motif_fraud.p_adic.publication_figures"],
            "artifact_check": "outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_temporal_signal.png",
        },
        {
            "name": "official_ieee_cis_strong_baseline_audit",
            "command": "python -m motif_fraud.p_adic.strong_baselines",
            "argv": ["python", "-m", "motif_fraud.p_adic.strong_baselines"],
            "artifact_check": "outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_strong_baseline_comparison.csv",
        },
        {
            "name": "vehicle_claim_external_validation",
            "command": "python -m motif_fraud.p_adic.vehicle_claim_pipeline",
            "argv": ["python", "-m", "motif_fraud.p_adic.vehicle_claim_pipeline"],
            "artifact_check": "outputs/p_adic_vehicle_claim/tables/p_adic_vehicle_claim_claims.csv",
        },
        {
            "name": "official_ieee_cis_temporal_surveillance_gate",
            "command": "python -m motif_fraud.p_adic.temporal_surveillance",
            "argv": ["python", "-m", "motif_fraud.p_adic.temporal_surveillance"],
            "artifact_check": "outputs/p_adic_ieee_cis_temporal_surveillance/tables/p_adic_ieee_cis_temporal_surveillance_claims.csv",
        },
        {
            "name": "official_ieee_cis_rich_feature_gate",
            "command": "python -m motif_fraud.p_adic.rich_padic_features",
            "argv": ["python", "-m", "motif_fraud.p_adic.rich_padic_features"],
            "artifact_check": "outputs/p_adic_ieee_cis_rich_features/tables/p_adic_ieee_cis_rich_feature_claims.csv",
        },
        {
            "name": "official_ieee_cis_branch_signature_gate",
            "command": "python -m motif_fraud.p_adic.branch_signatures",
            "argv": ["python", "-m", "motif_fraud.p_adic.branch_signatures"],
            "artifact_check": "outputs/p_adic_ieee_cis_branch_signatures/tables/p_adic_ieee_cis_branch_signature_claims.csv",
        },
        {
            "name": "official_ieee_cis_multiresolution_gate",
            "command": "python -m motif_fraud.p_adic.multiresolution_operator",
            "argv": ["python", "-m", "motif_fraud.p_adic.multiresolution_operator"],
            "artifact_check": "outputs/p_adic_ieee_cis_preregistered_multiresolution/tables/official_ieee_cis_preregistered_multiresolution_surveillance_multiresolution_claims.csv",
        },
        {
            "name": "official_ieee_cis_tree_scan_fail_closed_gate",
            "command": "python -m motif_fraud.p_adic.tree_scan_cusum --dataset ieee --output-root outputs/p_adic_ieee_cis_tree_scan",
            "argv": [
                "python",
                "-m",
                "motif_fraud.p_adic.tree_scan_cusum",
                "--dataset",
                "ieee",
                "--output-root",
                "outputs/p_adic_ieee_cis_tree_scan",
            ],
            "artifact_check": "outputs/p_adic_ieee_cis_tree_scan/tables/official_ieee_cis_tree_scan_surveillance_claims.csv",
        },
        {
            "name": "official_cse_cic_thursday_tree_scan_external_gate",
            "command": "python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-thursday --data-root data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv --output-root outputs/p_adic_cse_cic_thursday_tree_scan",
            "argv": [
                "python",
                "-m",
                "motif_fraud.p_adic.tree_scan_cusum",
                "--dataset",
                "cse-cic-thursday",
                "--data-root",
                "data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv",
                "--output-root",
                "outputs/p_adic_cse_cic_thursday_tree_scan",
            ],
            "artifact_check": "outputs/p_adic_cse_cic_thursday_tree_scan/tables/official_cse_cic_ids2018_thursday_tree_scan_surveillance_claims.csv",
        },
        {
            "name": "official_cse_cic_wednesday_preregistered_external_gate",
            "command": "python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-wednesday --data-root data/cse_cic_ids2018/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv --output-root outputs/p_adic_cse_cic_wednesday_tree_scan --n-blocks 96 --bootstrap-samples 500 --random-hierarchy-seeds 11,17,23,31,47",
            "argv": [
                "python",
                "-m",
                "motif_fraud.p_adic.tree_scan_cusum",
                "--dataset",
                "cse-cic-wednesday",
                "--data-root",
                "data/cse_cic_ids2018/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv",
                "--output-root",
                "outputs/p_adic_cse_cic_wednesday_tree_scan",
                "--n-blocks",
                "96",
                "--bootstrap-samples",
                "500",
                "--random-hierarchy-seeds",
                "11,17,23,31,47",
            ],
            "artifact_check": "outputs/p_adic_cse_cic_wednesday_tree_scan/tables/official_cse_cic_ids2018_wednesday_2018_02_28_tree_scan_surveillance_claims.csv",
        },
        {
            "name": "tree_scan_theory_failure_diagnostics",
            "command": "python -m motif_fraud.p_adic.tree_scan_theory",
            "argv": ["python", "-m", "motif_fraud.p_adic.tree_scan_theory"],
            "artifact_check": "docs/rebuild/tree_scan_theory_diagnostics.csv",
        },
        {
            "name": "claim_audit",
            "command": "python -m motif_fraud.p_adic.claim_audit",
            "argv": ["python", "-m", "motif_fraud.p_adic.claim_audit"],
            "artifact_check": "docs/rebuild/ieee_spl_claim_audit.csv",
        },
    ]


def write_reproduction_plan(path: str | Path = "docs/rebuild/reproduce_ieee_spl_artifacts.json") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_reproduction_plan(), indent=2), encoding="utf-8")
    return path


def run_reproduction_plan(skip_tests: bool = False) -> int:
    """Run the reproduction plan. Returns 0 only when all commands and artifact checks pass."""
    plan = build_reproduction_plan()
    if skip_tests:
        plan = [step for step in plan if step["name"] != "unit_and_artifact_tests"]
    for step in plan:
        print(f"[reproduce] {step['name']}: {step['command']}", flush=True)
        completed = subprocess.run(step["argv"], check=False)
        if completed.returncode != 0:
            print(f"[reproduce] failed command: {step['name']}", flush=True)
            return completed.returncode
        artifact = step["artifact_check"]
        if artifact != "test suite must pass" and not Path(artifact).exists():
            print(f"[reproduce] missing artifact: {artifact}", flush=True)
            return 2
    write_reproduction_plan()
    print("[reproduce] all artifact checks passed", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Reproduce real-data p-adic IEEE SPL artifacts.")
    parser.add_argument("--plan-only", action="store_true", help="Write the JSON reproduction plan without running commands.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest when rerunning artifacts.")
    args = parser.parse_args()
    if args.plan_only:
        print(write_reproduction_plan())
        return 0
    return run_reproduction_plan(skip_tests=args.skip_tests)


if __name__ == "__main__":
    raise SystemExit(main())
