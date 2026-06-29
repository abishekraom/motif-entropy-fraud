# P-adic Tree-Scan CUSUM implementation and IEEE-CIS gate result

Date: 2026-06-09

## Scope

This document records the first TDD implementation and full official IEEE-CIS audit for the p-adic tree-scan redesign specified in:

- `docs/rebuild/23_P_ADIC_TREE_SCAN_CUSUM_Q1_SPEC_AND_DECISION.md`
- `docs/rebuild/24_TREE_SCAN_CUSUM_TDD_IMPLEMENTATION_PLAN.md`

No subagents were used.

No synthetic empirical data were used.

## Files added

- `src/motif_fraud/p_adic/tree_scan_cusum.py`
- `tests/test_p_adic_tree_scan_cusum.py`
- `docs/rebuild/23_P_ADIC_TREE_SCAN_CUSUM_Q1_SPEC_AND_DECISION.md`
- `docs/rebuild/24_TREE_SCAN_CUSUM_TDD_IMPLEMENTATION_PLAN.md`

## Research/design decision

The existing prefix-rarity p-adic method was not patched further. The new implementation uses a p-adic prefix-ball tree scan with one-sided binomial excess LLR and mandatory fail-closed controls.

Implemented core pieces:

- train-normal prefix node table;
- one-sided binomial excess LLR;
- fixed-block p-adic tree scan;
- flat tuple scan control;
- marginal column scan control;
- reversed hierarchy tree-scan control;
- random hierarchy tree-scan controls;
- entropy/count controls;
- CSE-CIC timestamp parser fix;
- fail-closed claims table;
- 610 dpi figure writer.

## TDD validation

Initial RED failures were observed before implementation for missing module/functions:

- missing `motif_fraud.p_adic.tree_scan_cusum`;
- missing `binomial_excess_llr`;
- missing `run_fixed_block_tree_scan`;
- missing `run_tree_scan_claim_audit`;
- missing `parse_cse_cic_timestamp_seconds`;
- missing `run_ieee_tree_scan_audit`.

Final targeted new test command:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py -q
```

Observed result:

```text
......                                                                   [100%]
```

Targeted p-adic upgrade suite:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py tests/test_p_adic_temporal_surveillance.py tests/test_p_adic_rich_features.py tests/test_p_adic_branch_signatures.py tests/test_p_adic_multiresolution_operator.py -q
```

Observed result:

```text
...........                                                              [100%]
```

Full suite:

```bash
pytest -q
```

Observed result:

```text
.......................................................                  [100%]
```

Warnings:

- existing `Pandas4Warning` from `src/motif_fraud/p_adic/strong_baselines.py:115`.

## CSE timestamp bug fixed

Test:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_cse_cic_timestamp_parser_uses_seconds_not_microsecond_truncation_on_real_rows -q
```

Observed result:

```text
.                                                                        [100%]
```

Verified first real CSE timestamp:

```text
01/03/2018 08:17:11 -> 1519892231
```

This prevents the prior microsecond truncation bug where timestamps collapsed to values around `1519892`.

## Smoke IEEE-CIS tree-scan audit

Command:

```bash
python - <<'PY'
from motif_fraud.p_adic.tree_scan_cusum import run_ieee_tree_scan_audit
r = run_ieee_tree_scan_audit(
    output_root='outputs/p_adic_ieee_cis_tree_scan_smoke',
    max_rows=120000,
    n_blocks=32,
    bootstrap_samples=80,
    random_hierarchy_seeds=(11,17,23),
)
print(r['metadata'])
print(r['claims'])
PY
```

Observed metadata:

```text
rows: 120000
train_rows: 84000
test_rows: 36000
n_blocks: 32
best proposed: p_adic_tree_scan_llr
best control: category_entropy_temporal
claim_status: diagnostic_only_failed_q1_tree_scan_gate
figure_dpi: 610.0064 x 610.0064
```

Smoke result:

```text
p_adic_tree_scan_llr AUPRC: 0.242242
category_entropy_temporal AUPRC: 0.452272
delta: -0.210030
bootstrap CI: [-0.521934, 0.089393]
p_delta_le_zero: 0.900
```

## Full official IEEE-CIS tree-scan audit

Command:

```bash
python - <<'PY'
from motif_fraud.p_adic.tree_scan_cusum import run_ieee_tree_scan_audit
r = run_ieee_tree_scan_audit(
    output_root='outputs/p_adic_ieee_cis_tree_scan',
    n_blocks=96,
    bootstrap_samples=500,
    random_hierarchy_seeds=(11,17,23,31,47),
)
print(r['metadata'])
print(r['claims'])
PY
```

Dataset:

```text
official IEEE-CIS Fraud Detection
rows: 590540
train_rows: 413378
test_rows: 177162
n_blocks: 96
synthetic_data_used: false
figure_dpi: 610.0064 x 610.0064
```

Artifacts:

- `outputs/p_adic_ieee_cis_tree_scan/tables/official_ieee_cis_tree_scan_surveillance_claims.csv`
- `outputs/p_adic_ieee_cis_tree_scan/tables/official_ieee_cis_tree_scan_surveillance_claims.md`
- `outputs/p_adic_ieee_cis_tree_scan/metrics/official_ieee_cis_tree_scan_surveillance_blocks.csv`
- `outputs/p_adic_ieee_cis_tree_scan/manifests/official_ieee_cis_tree_scan_surveillance_metadata.json`
- `outputs/p_adic_ieee_cis_tree_scan/figures/official_ieee_cis_tree_scan_surveillance_gate.png`

Key results:

| Method | Family | AUPRC | ROC-AUC |
|---|---|---:|---:|
| p_adic_tree_scan_llr | proposed | 0.190753 | 0.313803 |
| flat_tuple_scan_llr | flat_control | 0.279863 | 0.566761 |
| marginal_column_scan_llr | marginal_control | 0.203252 | 0.349296 |
| reversed_hierarchy_tree_scan_llr | hierarchy_order_control | 0.280443 | 0.575775 |
| category_entropy_temporal | entropy_control | 0.271563 | 0.522817 |
| transaction_count_signal | count_control | 0.285952 | 0.555775 |
| random_hierarchy_tree_scan_llr_seed_11 | hierarchy_order_control | 0.260300 | 0.536620 |
| random_hierarchy_tree_scan_llr_seed_17 | hierarchy_order_control | 0.254319 | 0.509296 |
| random_hierarchy_tree_scan_llr_seed_23 | hierarchy_order_control | 0.241647 | 0.472676 |
| random_hierarchy_tree_scan_llr_seed_31 | hierarchy_order_control | 0.276973 | 0.564507 |
| random_hierarchy_tree_scan_llr_seed_47 | hierarchy_order_control | 0.183979 | 0.283662 |

Best proposed:

```text
p_adic_tree_scan_llr
AUPRC: 0.190753
```

Best control:

```text
transaction_count_signal
AUPRC: 0.285952
```

Delta:

```text
proposed - best control AUPRC: -0.095200
bootstrap CI: [-0.167412, -0.020197]
p_delta_le_zero: 0.988
```

Claim status:

```text
diagnostic_only_failed_q1_tree_scan_gate
```

## Brutal interpretation

The redesigned p-adic tree-scan statistic is mathematically cleaner than prefix rarity, but it still fails the official IEEE-CIS Q1/SPL empirical gate.

This is a stronger failure than the earlier temporal CUSUM failure because the confidence interval is strictly negative against the best control:

```text
CI lower/upper: [-0.167412, -0.020197]
```

The proposed tree scan loses to:

- flat tuple scan;
- reversed hierarchy scan;
- several random hierarchy scans;
- entropy/count controls.

This means the current IEEE-CIS categorical hierarchy does not support a Q1 empirical p-adic/tree-scan detector claim.

## What not to do

Do not tune hierarchy order, support threshold, alpha, block count, or scoring direction on this held-out result to make it flattering. That would be post-hoc test tuning.

Do not claim Q1/SPL empirical detector readiness.

## Remaining defensible options

1. Theory-first paper only:
   - retain p-adic tree-scan theorem/proof as the contribution;
   - use IEEE-CIS as an honest failure/diagnostic case;
   - target may no longer be IEEE SPL unless the theoretical novelty is strong enough.

2. External dataset route only with pre-registered hypothesis:
   - official CSE-CIC full processed set is downloadable and feasible on disk;
   - ToN_IoT/BoT-IoT may require Lust to download from UNSW;
   - but external success cannot erase IEEE-CIS failure if the paper claims robust cross-dataset fraud surveillance.

3. Abandon p-adic empirical detector claim:
   - current evidence now includes failures for prefix rarity, temporal surveillance, rich features, branch signatures, multiresolution, and tree-scan LLR.

## Bottom line

The implementation is research-grade and passes tests. The result is not Q1/SPL-grade on official IEEE-CIS. The honest status is failed/diagnostic.

## Follow-up parent-conditional residual rerun

Date: 2026-06-10

The preregistered parent-child residual variant from Section 6 of
`docs/rebuild/23_P_ADIC_TREE_SCAN_CUSUM_Q1_SPEC_AND_DECISION.md` was implemented
as `p_adic_conditional_tree_scan_llr` and evaluated under the same fail-closed
IEEE-CIS gate.

Command:

```bash
python -m motif_fraud.p_adic.tree_scan_cusum --dataset ieee --output-root outputs/p_adic_ieee_cis_tree_scan --n-blocks 96 --bootstrap-samples 500
```

Updated key result:

| Method | Family | AUPRC | ROC-AUC |
|---|---|---:|---:|
| p_adic_tree_scan_llr | proposed | 0.190753 | 0.313803 |
| p_adic_conditional_tree_scan_llr | proposed | 0.297719 | 0.595493 |
| transaction_count_signal | count_control | 0.285952 | 0.555775 |
| reversed_hierarchy_tree_scan_llr | hierarchy_order_control | 0.280443 | 0.575775 |
| flat_tuple_scan_llr | flat_control | 0.279863 | 0.566761 |

Best proposed:

```text
p_adic_conditional_tree_scan_llr
AUPRC: 0.297719
```

Best control:

```text
transaction_count_signal
AUPRC: 0.285952
```

Delta:

```text
proposed - best control AUPRC: +0.011766
bootstrap CI: [-0.070532, 0.122167]
p_delta_le_zero: 0.330
```

Claim status:

```text
diagnostic_only_failed_q1_tree_scan_gate
```

Interpretation:

The parent-conditional residual scan materially improves the IEEE-CIS point
estimate and makes the proposed method the best point-estimate method in this
tree-scan family. It still does not pass the Q1/SPL gate because the paired
bootstrap CI crosses zero and `p_delta_le_zero` is far above 0.05.
