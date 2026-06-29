# Strong baseline audit correction

Date: 2026-06-09

## Why this was needed

The earlier baseline context included logistic regression and Isolation Forest, but it did **not** include the stronger tree-boosting baselines I had explicitly said were necessary: LightGBM, CatBoost, and XGBoost.

That was an incomplete verification step. The concern was valid: without these baselines, the project could overstate detector competitiveness.

## Packages checked / installed

Initial availability check showed:

```text
lightgbm False
catboost False
xgboost False
sklearn True
```

Installed with:

```bash
python -m pip install lightgbm catboost xgboost
```

Installed versions available through package wheels:

- LightGBM 4.6.0
- CatBoost 1.2.10
- XGBoost 3.2.0

## New code and tests

Created:

- `src/motif_fraud/p_adic/strong_baselines.py`
- `tests/test_p_adic_strong_baselines.py`

The test uses official IEEE-CIS data with a small `max_rows` setting to verify the module writes real-data tree-boosting baseline artifacts.

Targeted test result:

```bash
pytest tests/test_p_adic_strong_baselines.py -q
```

```text
1 passed
```

## Official IEEE-CIS strong baseline audit

Command run on full official IEEE-CIS temporal split:

```bash
python -m motif_fraud.p_adic.strong_baselines
```

Dataset:

- Official IEEE-CIS
- rows: 590,540
- train rows: 413,378
- test rows: 177,162
- test fraud rate: 0.03457
- iterations: 200
- categorical features: ProductCD, card4, card6, P_emaildomain, R_emaildomain, DeviceType
- numeric feature count: 31

Artifact:

`outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_strong_baseline_comparison.csv`

Figure:

`outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_strong_baseline_comparison.png`

Verified figure:

- 4320 x 2880 px
- approximately 600 dpi

## Results

| Method | AUPRC | ROC-AUC | Interpretation |
|---|---:|---:|---|
| p_adic_selected_hierarchy | 0.08450 | 0.70111 | primary unsupervised p-adic signal |
| lightgbm_compact_tabular | 0.49547 | 0.90487 | strongest compact supervised baseline |
| lightgbm_compact_tabular_plus_padic | 0.49511 | 0.90609 | adding p-adic slightly lowers AUPRC, raises ROC-AUC |
| catboost_compact_tabular | 0.46368 | 0.88681 | strong supervised baseline |
| catboost_compact_tabular_plus_padic | 0.47092 | 0.89244 | adding p-adic improves CatBoost AUPRC and ROC-AUC |
| xgboost_compact_tabular | 0.48483 | 0.90064 | strong supervised baseline |
| xgboost_compact_tabular_plus_padic | 0.48334 | 0.89854 | adding p-adic slightly lowers AUPRC and ROC-AUC |

Metadata summary:

- best strong AUPRC: 0.49547
- best augmented AUPRC: 0.49511
- p-adic AUPRC: 0.08450
- p-adic minus best strong AUPRC: -0.41096
- best augmented minus best strong AUPRC: -0.00036

## Brutal interpretation

The strong baselines decisively prove that the raw p-adic method is **not competitive as a standalone detector** against modern supervised tabular baselines.

The earlier warning was correct.

The p-adic result still has value, but the paper must be narrowed further:

Defensible:

> A non-Archimedean prefix-rarity statistic is an interpretable unsupervised categorical signal that survives hierarchy controls and can provide model-specific auxiliary value.

Not defensible:

> The p-adic method is competitive with strong supervised fraud detectors.

Not defensible:

> The p-adic method is SOTA.

Complementarity is now weaker than before:

- With logistic frequency features, p-adic improved AUPRC from 0.09747 to 0.10067.
- With CatBoost, p-adic improved AUPRC from 0.46368 to 0.47092.
- With LightGBM, p-adic slightly reduced AUPRC from 0.49547 to 0.49511.
- With XGBoost, p-adic reduced AUPRC from 0.48483 to 0.48334.

So the safe claim is **not general complementarity**. It is:

> p-adic scores provide an interpretable hierarchy-aware signal and show positive complementarity for some baselines, but not for the strongest LightGBM result.

## Impact on IEEE SPL readiness

This reduces the detector-performance claim, but improves honesty and reviewer robustness.

Current paper positioning should shift from:

> p-adic signal improves fraud detection

To:

> p-adic prefix-rarity is a compact interpretable non-Archimedean categorical surveillance signal; it survives hierarchy controls but is not a replacement for supervised gradient-boosted tabular models.

## Current project status

The project is more scientifically honest now, but less performance-impressive.

Estimated completion remains high for a reproducible submission package, but the target venue/story must be more careful:

- IEEE SPL possible if framed as signal/statistic + interpretability + control discipline.
- Not acceptable if framed as detector superiority.
