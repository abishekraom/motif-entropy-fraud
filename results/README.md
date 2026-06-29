# Curated final results

This folder contains the GitHub-ready artifact subset copied from the full local `outputs/` tree.

The full `outputs/` directory is ignored because it contains smoke/test runs and regenerated intermediates. This `results/` folder keeps the best final artifacts needed to audit the scientific outcome.

## Scientific conclusion

The project is a reproducible negative/diagnostic result, not a Q1/SOTA fraud detector.

The official IEEE-CIS experiments show repeated p-adic empirical detector failures under increasingly strict controls.

## Folder map

```text
official_ieee_cis/raw_prefix_rarity/
  Raw p-adic prefix-rarity claims and figures.

official_ieee_cis/strong_baselines/
  LightGBM/CatBoost/XGBoost compact tabular baselines and p-adic augmentation comparison.

q1_upgrade_failures/temporal_surveillance/
  Multi-resolution temporal p-adic CUSUM vs flat temporal control.

q1_upgrade_failures/rich_features/
  Strong supervised baselines with rich p-adic feature-family augmentation.

q1_upgrade_failures/branch_signatures/
  Train-only branch-signature interpretability audit vs flat tuple branches.

q1_upgrade_failures/multiresolution/
  Preregistered multiresolution p-adic operator gate.

q1_upgrade_failures/tree_scan_cusum/
  P-adic tree-scan and parent-conditional residual gate; failed official IEEE-CIS CI gate.

q1_upgrade_failures/cse_cic_thursday_tree_scan/
  External CSE-CIC-IDS2018 Thursday tree-scan and parent-conditional residual gate; failed against entropy control.

q1_upgrade_failures/cse_cic_wednesday_tree_scan/
  Fresh preregistered CSE-CIC-IDS2018 Wednesday gate; failed against entropy control.

docs/rebuild/tree_scan_theory_diagnostics.csv
  Theory/failure-mode summary for current IEEE-CIS and CSE-CIC tree-scan gates.
```

## Key final result: tree-scan CUSUM

Source file:

```text
results/q1_upgrade_failures/tree_scan_cusum/official_ieee_cis_tree_scan_surveillance_claims.csv
```

Result:

```text
Best proposed: p_adic_conditional_tree_scan_llr, AUPRC 0.297719
Best control: transaction_count_signal, AUPRC 0.285952
Delta: +0.011766
Bootstrap CI: [-0.070532, 0.122167]
p_delta_le_zero: 0.330
Claim status: diagnostic_only_failed_q1_tree_scan_gate
```

## External CSE-CIC tree-scan result

Source file:

```text
results/q1_upgrade_failures/cse_cic_thursday_tree_scan/official_cse_cic_ids2018_thursday_tree_scan_surveillance_claims.csv
```

Result:

```text
Best proposed: p_adic_conditional_tree_scan_llr, AUPRC 0.524222
Best control: category_entropy_temporal, AUPRC 0.540129
Delta: -0.015906
Bootstrap CI: [-0.185953, 0.156353]
p_delta_le_zero: 0.506
Claim status: diagnostic_only_failed_q1_tree_scan_gate
```

## Artifact manifest

## Fresh Wednesday CSE-CIC Result

Source file:

```text
results/q1_upgrade_failures/cse_cic_wednesday_tree_scan/official_cse_cic_ids2018_wednesday_2018_02_28_tree_scan_surveillance_claims.csv
```

Result:

```text
Best proposed: p_adic_conditional_tree_scan_llr, AUPRC 0.215253
Best control: category_entropy_temporal, AUPRC 0.249078
Delta: -0.033825
Bootstrap CI: [-0.141594, 0.039650]
p_delta_le_zero: 0.820
Claim status: diagnostic_only_failed_q1_tree_scan_gate
```

## Theory Diagnostics

Source file:

```text
docs/rebuild/tree_scan_theory_diagnostics.csv
```

Current diagnosis:

```text
official_ieee_cis: uncertain_positive_delta
cse_cic_ids2018_thursday: entropy_dominance
cse_cic_ids2018_wednesday_2018_02_28: entropy_dominance
claim_statuses: diagnostic_only_failed_q1_tree_scan_gate
```

Machine-readable copied-file manifest:

```text
results/artifact_manifest.json
```

## Rebuild source

To regenerate rather than inspect copied artifacts, run from repo root after installing dependencies and placing official IEEE-CIS data:

```bash
pytest -q
python -m motif_fraud.p_adic.tree_scan_cusum --dataset ieee --output-root outputs/p_adic_ieee_cis_tree_scan
python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-thursday --data-root data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv --output-root outputs/p_adic_cse_cic_thursday_tree_scan
python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-wednesday --data-root data/cse_cic_ids2018/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv --output-root outputs/p_adic_cse_cic_wednesday_tree_scan --n-blocks 96 --bootstrap-samples 500 --random-hierarchy-seeds 11,17,23,31,47
```
