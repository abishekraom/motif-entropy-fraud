# Preregistered CSE-CIC Wednesday gate result

Date: 2026-06-12

## Scope

This document records the frozen fresh-day validation specified before download in:

```text
docs/rebuild/28_CSE_CIC_SECOND_DAY_PREREGISTRATION.md
```

No hierarchy, parameter, split, metric, score direction, or control was changed after observing the Wednesday result.

## Command

```bash
python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-wednesday --data-root data/cse_cic_ids2018/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv --output-root outputs/p_adic_cse_cic_wednesday_tree_scan --n-blocks 96 --bootstrap-samples 500 --random-hierarchy-seeds 11,17,23,31,47
```

Initial runtime observed:

```text
approximately 108 minutes
```

After replacing repeated node-by-row scans with one prefix counter per depth and block, the exact same frozen run completed in:

```text
392.002 seconds (approximately 6.53 minutes)
```

Approximate speedup:

```text
16.6x
```

Scientific-output equivalence check:

```text
shape_equal: true
columns_equal: true
exact_values_equal: true
max_numeric_abs_diff: 0.0
```

The optimization changed computation strategy only. It did not change any claim-table value, method, control, parameter, or gate rule.

## Provenance and split

```text
source SHA-256: F15E2A12304446058A0186C8AD67DE2BD15735A9BA5C70C9A1F4C4242AB06771
rows: 613071
train_rows: 429149
test_rows: 183922
n_blocks: 96
synthetic_data_used: false
preregistered_fresh_external_validation: true
figure_dpi: 610.0064 x 610.0064
```

## Result

| Method | Family | AUPRC | ROC-AUC |
|---|---|---:|---:|
| p_adic_tree_scan_llr | proposed | 0.195955 | 0.339410 |
| p_adic_conditional_tree_scan_llr | proposed | 0.215253 | 0.402199 |
| flat_tuple_scan_llr | flat_control | 0.214694 | 0.405382 |
| marginal_column_scan_llr | marginal_control | 0.195866 | 0.335938 |
| reversed_hierarchy_tree_scan_llr | hierarchy_order_control | 0.195133 | 0.320891 |
| category_entropy_temporal | entropy_control | 0.249078 | 0.394676 |
| transaction_count_signal | count_control | 0.235518 | 0.458333 |

Best proposed:

```text
p_adic_conditional_tree_scan_llr
AUPRC: 0.215253
```

Best control:

```text
category_entropy_temporal
AUPRC: 0.249078
```

Paired delta:

```text
proposed - best control AUPRC: -0.033825
bootstrap CI: [-0.141594, 0.039650]
p_delta_le_zero: 0.820
```

Claim status:

```text
diagnostic_only_failed_q1_tree_scan_gate
```

## Interpretation

The parent-conditional scan improved the raw p-adic tree scan by `+0.019298` AUPRC and narrowly exceeded flat tuple scan by point estimate. It did not beat entropy or transaction-count controls and its paired confidence interval crossed zero.

This fresh preregistered failure strengthens the entropy-dominance diagnosis from Thursday. The CSE-CIC evidence does not support a Q1/SPL empirical superiority claim.

## Claim boundary

Allowed:

```text
The frozen parent-conditional tree scan was evaluated on a fresh official CSE-CIC day and failed closed under entropy/count controls.
```

Unsafe:

```text
The p-adic tree scan generalizes across CSE-CIC days or provides statistically significant surveillance superiority.
```

## Decision

No further tuning on the Wednesday or Thursday held-out results is permitted. The remaining publication route is theory/diagnostic unless a separately preregistered independent dataset is acquired.
