# Q1-upgrade recursion results: failed gates and honest pivot decision

Date: 2026-06-09 19:51 IST

## Scope

This document records the post-IEEE-SPL-draft Q1-upgrade recursion on the official IEEE-CIS fraud dataset. It is deliberately claim-safe: the empirical upgrades were falsification attempts, not polish passes. They did not produce detector-grade or IEEE SPL/Q1-grade evidence.

Project root:

- `D:/motif-entropy-fraud/motif-entropy-fraud`

Official real dataset used:

- `D:/motif-entropy-fraud/ieee-fraud-detection`
- Source/provenance: IEEE-CIS Fraud Detection competition data.
- No synthetic empirical data were used for these reported results.

## Validation run in this continuation

Targeted tests:

```bash
pytest tests/test_p_adic_temporal_surveillance.py tests/test_p_adic_rich_features.py tests/test_p_adic_branch_signatures.py -q
```

Observed result:

```text
...                                                                      [100%]
```

Full suite:

```bash
pytest -q
```

Observed result:

```text
...............................................                          [100%]
============================== warnings summary ===============================
tests/test_p_adic_strong_baselines.py::test_strong_baseline_audit_writes_tree_boosting_results_on_real_data
tests/test_p_adic_strong_baselines.py::test_strong_baseline_audit_writes_tree_boosting_results_on_real_data
  D:\motif-entropy-fraud\motif-entropy-fraud\src\motif_fraud\p_adic\strong_baselines.py:115: Pandas4Warning: Constructing a Categorical with a dtype and values containing non-null entries not in that dtype's categories is deprecated and will raise in a future version.
    x_test[col] = pd.Categorical(x_test[col].astype(str), categories=categories)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```

Interpretation: after the earlier interrupted full-suite run, this continuation verified that the current suite passes. The warning is a forward-compatibility Pandas warning, not a test failure.

## Baseline scientific floor: raw p-adic detector failed strong-baseline gate

Artifact:

- `outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_strong_baseline_comparison.md`

Official IEEE-CIS temporal split:

- Train rows: 413,378
- Test rows: 177,162
- Test fraud rate: 0.0345729
- Categorical hierarchy: `ProductCD|card4|card6|P_emaildomain|R_emaildomain|DeviceType`

Key results:

| Method | AUPRC | ROC-AUC | Honest interpretation |
|---|---:|---:|---|
| p-adic selected hierarchy | 0.0845032 | 0.701107 | far below strong supervised baselines |
| LightGBM compact tabular | 0.495468 | 0.904873 | strongest compact supervised baseline |
| CatBoost compact tabular | 0.463679 | 0.886808 | strong supervised baseline |
| XGBoost compact tabular | 0.484829 | 0.900638 | strong supervised baseline |
| LightGBM + single p-adic scalar | 0.495106 | 0.906095 | hurts AUPRC slightly |
| CatBoost + single p-adic scalar | 0.470917 | 0.892445 | modest model-specific gain |
| XGBoost + single p-adic scalar | 0.483342 | 0.898541 | hurts AUPRC slightly |

Claim status in artifact:

- `strong_baselines_expose_detector_superiority_failure`
- `p_adic_augmented_strong_baseline_checked`

Brutal conclusion: the original p-adic detector is not competitive as a fraud detector on official IEEE-CIS. The single scalar p-adic feature does not provide general complementarity to strong tree-boosting models.

## Upgrade route 1: multi-resolution temporal p-adic surveillance

Files:

- Module: `src/motif_fraud/p_adic/temporal_surveillance.py`
- Test: `tests/test_p_adic_temporal_surveillance.py`
- Output directory: `outputs/p_adic_ieee_cis_temporal_surveillance/`
- Claims table: `outputs/p_adic_ieee_cis_temporal_surveillance/tables/p_adic_ieee_cis_temporal_surveillance_claims.md`
- Figure: `outputs/p_adic_ieee_cis_temporal_surveillance/figures/p_adic_ieee_cis_temporal_surveillance.png`

Figure verification:

- Size: 4320 x 2880 px
- DPI: approximately 600 x 600

Best proposed temporal signal:

- Method: `p_adic_cusum_temporal`
- AUPRC: 0.383115
- ROC-AUC: 0.589859
- Top fraction: 0.1
- Precision at top fraction: 0.5
- Recall at top fraction: 0.2

Best flat/control temporal signal:

- Method: `flat_cusum_temporal`
- AUPRC: 0.369727
- ROC-AUC: 0.523099
- Top fraction: 0.1
- Precision at top fraction: 0.4
- Recall at top fraction: 0.16

Paired/bootstrap comparison:

- Delta AUPRC: +0.0133874
- Bootstrap delta lower: -0.0289923
- Bootstrap delta upper: +0.0717835
- Bootstrap `p_delta_le_zero`: 0.194

Claim status:

- `diagnostic_only_failed_q1_temporal_gate`

Brutal conclusion: this is the only upgrade route with a positive point estimate over the best flat temporal control, but the confidence interval crosses zero. It is promising as a diagnostic surveillance signal, not statistically strong enough for a Q1/SPL empirical detector claim.

## Upgrade route 2: rich p-adic feature-family augmentation

Files:

- Module: `src/motif_fraud/p_adic/rich_padic_features.py`
- Test: `tests/test_p_adic_rich_features.py`
- Output directory: `outputs/p_adic_ieee_cis_rich_features/`
- Claims table: `outputs/p_adic_ieee_cis_rich_features/tables/p_adic_ieee_cis_rich_feature_claims.md`
- Figure: `outputs/p_adic_ieee_cis_rich_features/figures/p_adic_ieee_cis_rich_feature_comparison.png`

Figure verification:

- Size: 4320 x 2880 px
- DPI: approximately 600 x 600

Feature setup:

- Rich p-adic feature count: 13
- Strong baselines: LightGBM, CatBoost, XGBoost
- Dataset: official IEEE-CIS
- Train rows: 413,378
- Test rows: 177,162
- Test fraud rate: 0.0345729
- Iterations: 200

Key results:

| Method | AUPRC | ROC-AUC |
|---|---:|---:|
| LightGBM compact tabular | 0.495468 | 0.904873 |
| LightGBM + rich p-adic | 0.494321 | 0.903164 |
| CatBoost compact tabular | 0.463679 | 0.886808 |
| CatBoost + rich p-adic | 0.462758 | 0.889395 |
| XGBoost compact tabular | 0.484829 | 0.900638 |
| XGBoost + rich p-adic | 0.482513 | 0.899590 |

Gate comparison:

- Best strong AUPRC: 0.495468
- Best rich augmented AUPRC: 0.494321
- Delta: -0.00114669

Claim status:

- `diagnostic_only_failed_q1_rich_feature_gate`

Brutal conclusion: the richer p-adic feature family did not improve the best strong baseline. It also failed to improve CatBoost and XGBoost in AUPRC in the latest rich-feature audit. This route is dead for a strong-model-complementarity claim on IEEE-CIS unless a genuinely new, pre-registered hypothesis is introduced.

## Upgrade route 3: train-only branch-signature interpretability audit

Files:

- Module: `src/motif_fraud/p_adic/branch_signatures.py`
- Test: `tests/test_p_adic_branch_signatures.py`
- Output directory: `outputs/p_adic_ieee_cis_branch_signatures/`
- Claims table: `outputs/p_adic_ieee_cis_branch_signatures/tables/p_adic_ieee_cis_branch_signature_claims.md`
- Selected branches: `outputs/p_adic_ieee_cis_branch_signatures/tables/p_adic_ieee_cis_selected_branch_signatures.csv`
- Figure: `outputs/p_adic_ieee_cis_branch_signatures/figures/p_adic_ieee_cis_branch_signature_lift.png`

Figure verification:

- Size: 4320 x 1920 px
- DPI: approximately 600 x 600

Train-only selector constraints:

- `min_depth = 2`
- `max_train_support_fraction = 0.25`
- `min_train_lift = 1.1`
- Matched-coverage flat control added.

Key results:

| Method | Selected train branches | Test alert rows | Test alert coverage | Test alert fraud count | Test alert fraud rate | Lift | Fraud recall in alerts |
|---|---:|---:|---:|---:|---:|---:|---:|
| p-adic prefix branch signatures | 30 | 56,113 | 0.316733 | 4,137 | 0.0737262 | 2.13249 | 0.675429 |
| flat tuple branch signatures | 30 | 27,165 | 0.153334 | 2,671 | 0.0983251 | 2.84399 | 0.436082 |
| flat tuple matched-coverage signatures | 71 | 33,658 | 0.189984 | 3,129 | 0.0929645 | 2.68894 | 0.510857 |

Best flat control:

- `flat_tuple_branch_signatures`

Paired/bootstrap precision comparison:

- Delta p-adic vs best flat alert fraud rate: -0.0245988
- Bootstrap delta precision lower: -0.0283955
- Bootstrap delta precision upper: -0.0202253
- Bootstrap `p_delta_precision_le_zero`: 1.0

Claim status:

- `diagnostic_only_failed_q1_interpretability_gate`

Brutal conclusion: p-adic branch signatures cover more rows and recall more fraud, but they do so by firing broader alerts with lower precision/lift than flat tuple branches. This is not a Q1 interpretability win. It is a diagnostic description of hierarchy-aware coverage tradeoffs.

## Aggregate Q1-gate verdict

Three principled Q1-upgrade routes were tried on official IEEE-CIS and failed their gates:

1. Temporal surveillance:
   - Point estimate positive but statistically weak.
   - CI crosses zero.
   - Status: `diagnostic_only_failed_q1_temporal_gate`.
2. Rich feature-family augmentation:
   - Best rich augmented model underperforms best strong baseline.
   - Status: `diagnostic_only_failed_q1_rich_feature_gate`.
3. Branch-signature interpretability:
   - p-adic signatures have higher coverage/recall but lower precision/lift than flat tuple branches.
   - Precision delta CI is strictly negative.
   - Status: `diagnostic_only_failed_q1_interpretability_gate`.

The current scientifically safe contribution is therefore:

> an interpretable hierarchy-aware p-adic categorical surveillance/control signal with reproducible evidence and useful diagnostic structure, but not a competitive fraud detector, not a general strong-model complement, and not an IEEE SPL/Q1 empirical win on official IEEE-CIS.

## Unsafe claims that must not appear in the manuscript

Do not claim:

- state-of-the-art fraud detection;
- competitive detector performance versus strong supervised tabular baselines;
- general p-adic complementarity to strong models;
- statistically significant temporal surveillance superiority;
- superior interpretability precision/lift versus flat tuple controls;
- IEEE SPL/Q1 readiness based on the current empirical evidence.

## Safe claims that remain defensible

The evidence supports only narrow wording such as:

- reproducible audit of a hierarchy-aware p-adic categorical fraud signal;
- interpretable non-Archimedean/prefix-rarity signal on official IEEE-CIS;
- diagnostic temporal surveillance behavior with a non-significant positive point estimate over flat CUSUM;
- branch-signature recall/coverage tradeoff versus flatter categorical signatures;
- control-discipline case study showing why strong baselines and flat controls are necessary.

## Recommended decision

Do not keep recursively tweaking IEEE-CIS p-adic variants without a new principled hypothesis. The current recursion has already tested the obvious empirical rescue routes and failed them honestly.

Recommended options, in order of scientific honesty:

A. Retarget as a Q3 / low-Q2 reproducibility and control-discipline paper.
   - Best fit if the goal is to publish the artifact without fake detector claims.
   - Frame around falsification discipline, hierarchy-aware diagnostics, and negative/neutral results.

B. Search for another official/reputed dataset where hierarchical categorical structure is central.
   - Pre-register gates before running.
   - Do not tune on test.
   - If Kaggle/API access blocks, ask Lust to download the dataset.
   - Candidate domains: network intrusion, cyber logs, click/ad fraud, healthcare claims with diagnosis/procedure/provider hierarchy.

C. Develop a real theoretical contribution.
   - Example direction: prove prefix-rarity as an ultrametric KDE/control statistic and derive a separation condition where hierarchical anomalies are detectable by prefix-depth statistics but hidden from flat marginals.
   - Empirical IEEE-CIS results would become diagnostic validation, not the central detector claim.

D. Abandon IEEE SPL for this particular empirical result.
   - This is the cleanest decision if the target must remain Q1/IEEE SPL and no new theory/dataset route is acceptable.

## Manuscript/PDF status

Existing draft files:

- `paper/ieee_spl/p_adic_prefix_rarity_spl.tex`
- `paper/ieee_spl/references.bib`
- `paper/ieee_spl/p_adic_prefix_rarity_spl.pdf`

Do not update the manuscript yet. The compiled PDF was previously visually acceptable as a 3-page package, but the new upgrade experiments weaken the Q1/SPL detector story rather than strengthen it. A rewrite should happen only after choosing one of the decision routes above.

## Next action if continuing empirically

Before any new dataset run:

1. Research official/reputed dataset candidates.
2. Choose one where categorical hierarchy is real and central.
3. Write pre-registered gates in a status doc before experiments.
4. Add tests for artifact schemas and claim-status failure modes before running expensive audits.
5. Ask Lust to download any dataset that cannot be accessed through official/Kaggle tooling.
6. Preserve negative results as negative results.

Bottom line: the project is reproducible and disciplined; the central IEEE-CIS p-adic detector claim is scientifically weak. The honest move is to retarget, switch datasets with pre-registered gates, add theory, or stop the SPL push.
