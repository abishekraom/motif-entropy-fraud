# Multiresolution operator implementation and preregistered audit status

Date: 2026-06-09

## Scope

This document records the first implementation pass for the pre-registered Q1 / IEEE SPL multiresolution p-adic surveillance route.

The implementation followed the failure-safe gate in:

- `docs/rebuild/20_Q1_SPL_PREREGISTERED_GATES.md`

No subagents were used.

## Files added

- `src/motif_fraud/p_adic/multiresolution_operator.py`
- `tests/test_p_adic_multiresolution_operator.py`
- `docs/rebuild/20_Q1_SPL_PREREGISTERED_GATES.md`
- `docs/rebuild/dataset_cards/cse_cic_ids2018_thursday_2018_03_01.md`

## Operator implemented

The module implements a train-only p-adic/prefix multiresolution event-stream operator:

- per-depth prefix surprise from normal training rows;
- weighted multiresolution energy;
- EWMA and positive CUSUM temporal variants;
- flat tuple rarity controls;
- entropy and count controls;
- reversed hierarchy-order control;
- random hierarchy-order controls;
- Isolation Forest block-feature context control;
- strict pass/fail claim statuses;
- 610 dpi saved figures so PNG metadata verifies above the 600 dpi manuscript target.

The code deliberately allows negative results. It does not require the proposed method to win in tests.

## TDD / validation commands run

RED test was observed first:

```bash
pytest tests/test_p_adic_multiresolution_operator.py -q
```

Initial failure:

```text
ModuleNotFoundError: No module named 'motif_fraud.p_adic.multiresolution_operator'
```

After implementation and DPI fix:

```bash
pytest tests/test_p_adic_multiresolution_operator.py -q
```

Observed result:

```text
..                                                                       [100%]
```

Targeted p-adic upgrade suite:

```bash
pytest tests/test_p_adic_temporal_surveillance.py tests/test_p_adic_rich_features.py tests/test_p_adic_branch_signatures.py tests/test_p_adic_multiresolution_operator.py -q
```

Observed result:

```text
.....                                                                    [100%]
```

Full suite:

```bash
pytest -q
```

Observed result:

```text
.................................................                        [100%]
```

Warning remains:

- `Pandas4Warning` in `src/motif_fraud/p_adic/strong_baselines.py:115` about future categorical dtype behavior.

## Full official IEEE-CIS preregistered multiresolution audit

Command:

```bash
python -m motif_fraud.p_adic.multiresolution_operator
```

Dataset:

- official IEEE-CIS Fraud Detection
- data root: `D:/motif-entropy-fraud/ieee-fraud-detection`
- rows: 590,540
- train rows: 413,378
- test rows: 177,162
- blocks: 96
- synthetic data used: false

Artifacts:

- Claims table: `outputs/p_adic_ieee_cis_preregistered_multiresolution/tables/official_ieee_cis_preregistered_multiresolution_surveillance_multiresolution_claims.csv`
- Markdown table: `outputs/p_adic_ieee_cis_preregistered_multiresolution/tables/official_ieee_cis_preregistered_multiresolution_surveillance_multiresolution_claims.md`
- Block features: `outputs/p_adic_ieee_cis_preregistered_multiresolution/metrics/official_ieee_cis_preregistered_multiresolution_surveillance_multiresolution_blocks.csv`
- Metadata: `outputs/p_adic_ieee_cis_preregistered_multiresolution/manifests/official_ieee_cis_preregistered_multiresolution_surveillance_multiresolution_metadata.json`
- Figure: `outputs/p_adic_ieee_cis_preregistered_multiresolution/figures/official_ieee_cis_preregistered_multiresolution_surveillance_multiresolution_gate.png`

Figure verification:

- Size: 4392 x 2928 px
- DPI: 610.0064 x 610.0064

Key results:

| Method | Family | AUPRC | ROC-AUC |
|---|---|---:|---:|
| p_adic_multiresolution_energy | proposed | 0.293386 | 0.563944 |
| p_adic_multiresolution_energy_ewma | proposed | 0.278962 | 0.553239 |
| p_adic_multiresolution_energy_cusum | proposed | 0.383115 | 0.589859 |
| flat_tuple_rarity_cusum | flat_control | 0.369727 | 0.523099 |
| reversed_hierarchy_energy_cusum | hierarchy_order_control | 0.370135 | 0.524507 |
| random_hierarchy_energy_cusum_seed_23 | hierarchy_order_control | 0.387234 | 0.622535 |

Best proposed:

- `p_adic_multiresolution_energy_cusum`
- AUPRC: 0.3831146884

Best control:

- `random_hierarchy_energy_cusum_seed_23`
- AUPRC: 0.3872335538

Delta:

- proposed minus best control AUPRC: -0.0041188654
- bootstrap CI: [-0.1031885671, 0.1104164635]
- bootstrap `p_delta_le_zero`: 0.462

Claim status:

- `diagnostic_only_failed_q1_multiresolution_gate`

Brutal interpretation:

The stricter hierarchy-order controls remove the small temporal advantage. The proposed p-adic CUSUM is not Q1/SPL-grade on IEEE-CIS under the pre-registered multiresolution gate.

## External official/reputed dataset attempt: CSE-CIC-IDS2018 Thursday file

Official source:

- `https://registry.opendata.aws/cse-cic-ids2018`
- `https://www.unb.ca/cic/datasets/ids-2018.html`

Downloaded file:

- `data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv`
- Size: 107,842,858 bytes

Rows after removing repeated header rows:

- 331,100

Positive label rule:

- `Label != Benign`

Positive rate:

- 0.2810721836

Hierarchy used:

- `Protocol|dst_port_band|Dst Port|SYN Flag Cnt|ACK Flag Cnt|PSH Flag Cnt`

Artifacts:

- Claims table: `outputs/cse_cic_ids2018_thursday_multiresolution/tables/cse_cic_ids2018_thursday_2018_03_01_preregistered_multiresolution_surveillance_multiresolution_claims.csv`
- Markdown table: `outputs/cse_cic_ids2018_thursday_multiresolution/tables/cse_cic_ids2018_thursday_2018_03_01_preregistered_multiresolution_surveillance_multiresolution_claims.md`
- Block features: `outputs/cse_cic_ids2018_thursday_multiresolution/metrics/cse_cic_ids2018_thursday_2018_03_01_preregistered_multiresolution_surveillance_multiresolution_blocks.csv`
- Metadata: `outputs/cse_cic_ids2018_thursday_multiresolution/manifests/cse_cic_ids2018_thursday_2018_03_01_preregistered_multiresolution_surveillance_multiresolution_metadata.json`
- Figure: `outputs/cse_cic_ids2018_thursday_multiresolution/figures/cse_cic_ids2018_thursday_2018_03_01_preregistered_multiresolution_surveillance_multiresolution_gate.png`

Figure verification:

- Size: 4392 x 2928 px
- DPI: 610.0064 x 610.0064

Key results:

| Method | Family | AUPRC | ROC-AUC |
|---|---|---:|---:|
| p_adic_multiresolution_energy | proposed | 0.411664 | 0.675347 |
| p_adic_multiresolution_energy_ewma | proposed | 0.427348 | 0.749421 |
| p_adic_multiresolution_energy_cusum | proposed | 0.337912 | 0.574074 |
| flat_tuple_rarity_ewma | flat_control | 0.428225 | 0.749421 |
| category_entropy_temporal | entropy_control | 0.540129 | 0.719907 |
| isolation_forest_block_context | unsupervised_context | 0.570283 | 0.740741 |

Best proposed:

- `p_adic_multiresolution_energy_ewma`
- AUPRC: 0.427348

Best control:

- `isolation_forest_block_context`
- AUPRC: 0.570283

Delta:

- proposed minus best control AUPRC: -0.142935
- bootstrap CI: [-0.314079, 0.053605]
- bootstrap `p_delta_le_zero`: 0.912

Claim status:

- `diagnostic_only_failed_q1_multiresolution_gate`

Brutal interpretation:

This external official/reputed benchmark does not rescue the empirical route. On this processed CSE-CIC-IDS2018 day, p-adic multiresolution scores are below entropy and Isolation Forest context controls.

## Aggregate verdict after this implementation pass

The implementation is cleaner and stricter, but the Q1/SPL empirical gate failed on:

1. full official IEEE-CIS;
2. an official CSE-CIC-IDS2018 processed-flow external benchmark file.

This is not a Q1/SPL empirical win. It is stronger evidence that the current p-adic prefix-rarity family is diagnostic/control-useful but not detector-grade.

## What not to do next

Do not keep tuning the hierarchy, block labels, CUSUM parameters, or feature list on these test outputs. That would be post-hoc test tuning and would invalidate Q1/SPL claims.

## Honest next branch

Only two routes remain scientifically defensible:

A. Theory-first route:

- Prove a clean separation/invariance theorem for the non-Archimedean operator.
- Use IEEE-CIS and CSE-CIC results as diagnostic examples, not as superiority evidence.
- The paper becomes a compact theory/control-discipline signal-processing note.

B. New external dataset route:

- Obtain ToN_IoT or BoT-IoT from official UNSW SharePoint links.
- Write a dataset card before running.
- Pre-register the hierarchy and gate before the first run.
- If it fails, stop the empirical SPL route.

Current local status:

- ToN_IoT not found locally.
- BoT-IoT not found locally.
- UNSW-NB15 not found locally.
- CSE-CIC-IDS2018 one official file downloaded and tested; failed gate.

If Lust wants to continue empirical Q1/SPL pursuit, the next needed user action is to download ToN_IoT or BoT-IoT from the official UNSW links into the project data directory.
