# CSE-CIC second-day external validation preregistration

Date: 2026-06-12

Status: frozen before download, schema inspection, label counts, or empirical scoring of the selected day.

## Purpose

The first external CSE-CIC audit used Thursday, March 1, 2018 and produced an entropy-dominance failure. This preregistration selects a fresh official processed day to test the already-frozen parent-conditional p-adic tree-scan without tuning on its labels or results.

## Official source

Dataset:

```text
CSE-CIC-IDS2018
```

Official sources:

```text
https://registry.opendata.aws/cse-cic-ids2018/
https://www.unb.ca/cic/datasets/ids-2018.html
```

The AWS registry identifies the public bucket as:

```text
s3://cse-cic-ids2018/
```

The UNB attack schedule identifies two infiltration periods on Wednesday, February 28, 2018:

```text
10:50-12:05
13:42-14:40
```

## Frozen file

Selected processed file:

```text
Processed Traffic Data for ML Algorithms/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv
```

Planned local path:

```text
data/cse_cic_ids2018/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv
```

This day was selected before inspecting its local label distribution or running any model because it is the smallest listed untested processed day and gives a fresh same-attack, different-day generalization check.

## Frozen preparation

Time field:

```text
Timestamp
```

Binary evaluation label:

```text
is_attack = Label != Benign
```

The label is used only for final block metrics and normal-training reference filtering. It is excluded from the hierarchy.

Hierarchy:

```text
Protocol -> dst_port_band -> Dst Port -> SYN Flag Cnt -> ACK Flag Cnt -> PSH Flag Cnt
```

Port bands remain unchanged:

```text
system: 0-1023
registered: 1024-49151
dynamic: 49152-65535
missing_or_nonstandard: all other values
```

## Frozen split and operator

Split:

```text
temporal sort by parsed Timestamp
first 70% train
last 30% held-out test
```

Operator parameters:

```text
min_support = 20
alpha = 0.5
n_blocks = 96
bootstrap_samples = 500
random_hierarchy_seeds = 11,17,23,31,47
```

Proposed methods:

```text
p_adic_tree_scan_llr
p_adic_conditional_tree_scan_llr
```

Mandatory controls:

```text
flat_tuple_scan_llr
marginal_column_scan_llr
reversed_hierarchy_tree_scan_llr
five fixed random hierarchy scans
category_entropy_temporal
transaction_count_signal
```

## Frozen primary metric

Primary task:

```text
temporal block surveillance
```

Primary metric:

```text
AUPRC over blocks labeled high-risk by the frozen upper-quartile block attack-rate rule
```

Secondary metric:

```text
ROC-AUC over the same blocks
```

Uncertainty:

```text
paired 500-sample bootstrap for best proposed minus best control AUPRC
```

## Pass condition

The fresh-day gate passes only if all are true:

1. Best proposed AUPRC is higher than every mandatory control.
2. Bootstrap 95% CI lower bound is strictly positive.
3. `p_delta_le_zero <= 0.05`.
4. Artifact metadata states `synthetic_data_used: false`.
5. Figure DPI is at least 600.
6. No hierarchy, split, parameter, score direction, or control is changed after seeing Wednesday results.

Pass status:

```text
q1_candidate_tree_scan_passed_controls
```

Failure status:

```text
diagnostic_only_failed_q1_tree_scan_gate
```

## Claim boundary

Even a Wednesday pass would not erase the Thursday entropy-dominance failure or establish universal superiority. It would support a narrower cross-day result that the frozen conditional tree scan can succeed in at least one fresh same-benchmark day.

If Wednesday fails, no further CSE-CIC hierarchy or parameter tuning is permitted on these held-out days. The project remains theory/diagnostic unless a separately preregistered dataset is acquired.
