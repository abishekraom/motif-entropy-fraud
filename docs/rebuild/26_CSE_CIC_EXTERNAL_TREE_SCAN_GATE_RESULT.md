# CSE-CIC external tree-scan gate result

Date: 2026-06-10

## Scope

This document records the first external official/reputed event-stream tree-scan audit after the failed IEEE-CIS tree-scan gate. It was updated after implementing the preregistered parent-child residual variant.

Dataset:

- CSE-CIC-IDS2018 processed Thursday 2018-03-01 flow file.
- Local file: `data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv`.
- Dataset card: `docs/rebuild/dataset_cards/cse_cic_ids2018_thursday_2018_03_01.md`.

The run uses the same fail-closed tree-scan claim logic as the IEEE-CIS audit.

## Code changes

Added CSE-CIC external support to:

- `src/motif_fraud/p_adic/tree_scan_cusum.py`

Added tests for:

- timestamp parsing;
- non-leaking CSE-CIC event-stream preparation;
- CSE-CIC external tree-scan artifact writing;
- parent-conditional residual scan outputs;
- reproduction-plan inclusion.

The CSE-CIC hierarchy is:

```text
Protocol -> dst_port_band -> Dst Port -> SYN Flag Cnt -> ACK Flag Cnt -> PSH Flag Cnt
```

The label rule is:

```text
is_attack = Label != Benign
```

Attack labels are not used inside the hierarchy.

## Full external run after parent-conditional residual extension

Command:

```bash
python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-thursday --data-root data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv --output-root outputs/p_adic_cse_cic_thursday_tree_scan --n-blocks 96 --bootstrap-samples 500
```

Observed metadata:

```text
rows: 331100
train_rows: 231769
test_rows: 99331
n_blocks: 96
synthetic_data_used: false
figure_dpi: 610.0064 x 610.0064
```

## Key result

| Method | Family | AUPRC | ROC-AUC |
|---|---|---:|---:|
| p_adic_tree_scan_llr | proposed | 0.509695 | 0.824653 |
| p_adic_conditional_tree_scan_llr | proposed | 0.524222 | 0.834491 |
| flat_tuple_scan_llr | flat_control | 0.361348 | 0.659433 |
| marginal_column_scan_llr | marginal_control | 0.478823 | 0.823495 |
| reversed_hierarchy_tree_scan_llr | hierarchy_order_control | 0.453795 | 0.797454 |
| category_entropy_temporal | entropy_control | 0.540129 | 0.719907 |
| transaction_count_signal | count_control | 0.226057 | 0.423611 |

Best proposed:

```text
p_adic_conditional_tree_scan_llr
AUPRC: 0.524222
```

Best control:

```text
category_entropy_temporal
AUPRC: 0.540129
```

Delta:

```text
proposed - best control AUPRC: -0.015906
bootstrap CI: [-0.185953, 0.156353]
p_delta_le_zero: 0.506
```

Claim status:

```text
diagnostic_only_failed_q1_tree_scan_gate
```

## Interpretation

The parent-conditional p-adic tree scan beats the raw p-adic tree scan, flat tuple scan, marginal scan, reversed hierarchy, transaction-count control, and all registered random hierarchy controls on this single CSE-CIC Thursday file. It still fails the Q1/SPL gate because category entropy has higher AUPRC and the bootstrap interval for proposed-minus-best-control crosses zero.

This is not an IEEE SPL empirical pass. It is useful diagnostic evidence that the p-adic tree scan can carry signal on an external cybersecurity event stream, but it does not yet establish statistically controlled superiority.

## Current status after this run

The project remains:

```text
reproducible diagnostic / failed Q1 empirical gate
```

The best next Q1-grade path is now theory-led:

1. add a formal proposition explaining when prefix aggregation should beat flat tuple scan and when entropy controls can dominate;
2. add a formal entropy-dominance failure analysis so the SPL contribution is theory/diagnostic rather than detector superiority;
3. evaluate on the full multi-day CSE-CIC benchmark or a pre-registered second external dataset only after the method and gates are frozen.

Do not claim IEEE SPL/Q1 empirical readiness from this result.
