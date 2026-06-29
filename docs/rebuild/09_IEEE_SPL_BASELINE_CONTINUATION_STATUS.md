# IEEE SPL continuation status after broader baselines

Date: 2026-06-08

## Current completion estimate

Estimated project completion: **84 / 100 = 84%**

This estimate is based on concrete completed artifacts, not optimism:

| Component | Points |
|---|---:|
| Official IEEE-CIS data provenance | 10 / 10 |
| Reproducible tests and pipeline | 15 / 15 |
| Core p-adic hierarchy method | 15 / 15 |
| Control gate + bootstrap evidence | 20 / 20 |
| 600 dpi figure artifacts | 10 / 10 |
| Broader baseline context | 8 / 10 |
| IEEE SPL signal-processing framing | 3 / 10 |
| Claim-to-artifact mapping | 3 / 5 |
| Submission packaging/manuscript | 0 / 5 |

## Commands actually run

```bash
pytest -q
```

Result:

```text
39 passed
```

```bash
python -m motif_fraud.p_adic.official_baselines
```

Result: broader official-data baselines written under:

`outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_baseline_comparison.csv`

```bash
python -m motif_fraud.p_adic.publication_figures
```

Result: 600 dpi publication figures written under:

`outputs/p_adic_ieee_cis_official/figures/`

## Broader baseline result

Artifact:

`outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_baseline_comparison.csv`

| Method | Family | AUPRC | ROC-AUC | Interpretation |
|---|---|---:|---:|---|
| p_adic_selected_hierarchy | proposed unsupervised signal | 0.08450 | 0.70111 | Primary unsupervised p-adic signal |
| logistic_frequency_supervised | supervised context baseline | 0.09747 | 0.72726 | Beats raw p-adic signal |
| logistic_frequency_plus_padic_signal | supervised + p-adic signal | 0.10067 | 0.72538 | Shows p-adic score adds AUPRC complementarity |
| isolation_forest_frequency_unsupervised | unsupervised context baseline | 0.07579 | 0.71514 | P-adic beats AUPRC, loses ROC-AUC |

## Brutal interpretation of broader baselines

The p-adic signal is **not** the strongest raw detector in the current table.

A simple supervised logistic-frequency baseline beats raw p-adic:

- p-adic AUPRC: 0.08450
- logistic AUPRC: 0.09747

But the p-adic signal is still useful as a complementary signal:

- logistic only AUPRC: 0.09747
- logistic + p-adic signal AUPRC: 0.10067
- AUPRC gain from adding p-adic: +0.00321 absolute

So the safe paper claim is **not**:

> p-adic fraud detection beats all standard fraud models.

The safe claim is:

> A train-selected non-Archimedean prefix-rarity signal beats hierarchy/rarity falsification controls and provides complementary AUPRC signal to a supervised frequency baseline on the official IEEE-CIS temporal split.

## 600 dpi figures generated and verified

All are verified at approximately 600 x 600 DPI.

| Figure | Path | Size | DPI |
|---|---|---:|---:|
| PR curve | `outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_pr_curve.png` | 3000 x 2400 | ~600 |
| Temporal p-adic signal | `outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_temporal_signal.png` | 4200 x 2400 | ~600 |
| Control ablation | `outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_control_ablation.png` | 4200 x 2400 | ~600 |
| Baseline context | `outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_baseline_context.png` | 4200 x 2400 | ~600 |

## New code added in this continuation

- `src/motif_fraud/p_adic/official_baselines.py`
- `src/motif_fraud/p_adic/publication_figures.py`
- `tests/test_p_adic_official_baselines.py`
- `tests/test_p_adic_publication_figures.py`

## Current level

Current level: **Q1/SPL candidate with baseline caveat**.

It is stronger than before because:

1. official IEEE-CIS provenance is fixed;
2. p-adic hierarchy beats flat and reversed-hierarchy controls;
3. bootstrap deltas are positive;
4. broader baselines are now present;
5. p-adic improves a supervised frequency baseline when used as an added signal;
6. 600 dpi paper figures now exist.

But it is still not final IEEE SPL submission-ready because the manuscript itself is not written and the claim needs careful positioning.

## What remains before IEEE SPL submission

1. Write the IEEE SPL-style method section:
   - transaction stream as categorical temporal signal;
   - p-adic prefix-rarity statistic;
   - train-only hierarchy selection;
   - temporal split and fixed-FPR evaluation.
2. Write the final results table:
   - internal controls;
   - broader baselines;
   - complementarity result.
3. Write the limitation paragraph explicitly:
   - raw p-adic does not beat supervised logistic frequency baseline;
   - claim is unsupervised/interpretable signal + complementarity, not SOTA detector superiority.
4. Build claim-to-artifact table:
   - every manuscript claim maps to a CSV/figure/command.
5. Draft the IEEE SPL paper package.

## Dataset note

No additional dataset is currently required for the next step. If we later need another official/reputed dataset for external validation, the user can manually download it and we should ask clearly rather than using unofficial mirrors.
