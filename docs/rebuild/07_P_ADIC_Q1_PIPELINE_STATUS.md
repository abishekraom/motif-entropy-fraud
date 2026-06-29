# P-adic fraud Q1 reproducible pipeline status

Date: 2026-06-08

## Non-negotiable scientific rule

This pipeline is designed to fail closed. It does not upgrade a result to Q1-grade just because a p-adic score ran successfully. A Q1 candidate must pass:

1. real official/reputed dataset provenance;
2. temporal train/test split;
3. p-adic method beats flat categorical, random digit, and random hierarchy controls;
4. result is not synthetic-data-based;
5. figure exports are at least 600 dpi;
6. claims table explicitly records pass/fail status.

## What was built

New package:

- `src/motif_fraud/p_adic/metrics.py`
- `src/motif_fraud/p_adic/encoding.py`
- `src/motif_fraud/p_adic/scoring.py`
- `src/motif_fraud/p_adic/datasets.py`
- `src/motif_fraud/p_adic/splits.py`
- `src/motif_fraud/p_adic/real_pipeline.py`
- `src/motif_fraud/p_adic/ieee_pipeline.py`
- `src/motif_fraud/pipeline/p_adic_reproduce.py`

New tests:

- `tests/test_p_adic_core.py`
- `tests/test_p_adic_scoring.py`
- `tests/test_p_adic_reproducibility_contract.py`
- `tests/test_p_adic_real_pipeline.py`
- `tests/test_p_adic_ieee_pipeline.py`

New dataset cards:

- `docs/rebuild/dataset_cards/european_creditcard_kaggle.md`
- `docs/rebuild/dataset_cards/ieee_cis_kaggle_competition.md`

## Verified commands run

```bash
pytest -q
```

Result:

```text
30 passed
```

```bash
python -m motif_fraud.p_adic.real_pipeline
```

Result:

```json
{
  "dataset": "European Credit Card Fraud Detection (Kaggle mlg-ulb/creditcardfraud)",
  "rows": 284807,
  "train_rows": 199364,
  "test_rows": 85443,
  "fraud_rate": 0.001727485630620034,
  "train_fraction": 0.7,
  "quantile_bins": 10,
  "prime": 11,
  "claim_status": "diagnostic_only_failed_q1_gate"
}
```

```bash
python -m motif_fraud.p_adic.ieee_pipeline
```

Result:

```json
{
  "dataset": "IEEE-CIS Fraud Detection categorical audit",
  "rows": 590540,
  "train_rows": 413378,
  "test_rows": 177162,
  "fraud_rate": 0.03499000914417313,
  "prime": 61,
  "claim_status": "diagnostic_only_failed_q1_gate",
  "provenance_warning": "official Kaggle competition download was unauthorized in this environment; local mirror is development-only unless user accepts official competition rules"
}
```

## Actual empirical results

### European CCF diagnostic

Artifact:

- `outputs/p_adic_creditcard/tables/p_adic_creditcard_claims.csv`

Result:

| Method | AUPRC | ROC-AUC | Status |
|---|---:|---:|---|
| p-adic time/amount frequency | 0.00234 | 0.49882 | failed Q1 gate |
| amount-only baseline | 0.00165 | 0.41103 | diagnostic only |
| flat/random controls | 0.00234 | 0.49882 | matched proposed |

Interpretation:

- This dataset is real and official enough for a diagnostic, but it has PCA-anonymized features and no semantic hierarchy.
- The p-adic score does not beat controls.
- Correct claim: diagnostic failure / negative control, not Q1 evidence.

### IEEE-CIS categorical audit

Artifact:

- `outputs/p_adic_ieee_cis/tables/p_adic_ieee_cis_claims.csv`

Result:

| Method | AUPRC | ROC-AUC | Status |
|---|---:|---:|---|
| p-adic categorical prefix rarity | 0.06802 | 0.68613 | failed Q1 gate |
| flat categorical frequency control | 0.05747 | 0.66498 | control |
| random hierarchy order control | 0.06786 | 0.68757 | near-tie control |
| random digit-map controls | 0.06802 | 0.68613 | matched proposed |

Interpretation:

- Prefix rarity improved over flat exact categorical frequency.
- But random digit-map controls matched the proposed method, meaning the p-adic digit assignment itself is not carrying a validated semantic hierarchy signal.
- Official Kaggle competition download was unauthorized; the local mirror is development-only.
- Correct claim: promising diagnostic signal, not Q1-grade evidence.

## 600 dpi outputs

Generated 600 dpi figures:

- `outputs/p_adic_creditcard/figures/p_adic_creditcard_pr_curve.png`
- `outputs/p_adic_ieee_cis/figures/p_adic_ieee_cis_pr_curve.png`

## Current blocker to Q1-grade result

The current p-adic transaction-encoding hypothesis does not yet pass the required falsification controls.

The most important failure is not low AUPRC alone. The real blocker is that random digit-map controls match the proposed p-adic method. That means the current score is mostly a hierarchical/frequency rarity score, not evidence that p-adic arithmetic over a meaningful digit taxonomy adds unique fraud signal.

## What must change before Q1 targeting

1. Get official IEEE-CIS competition access or another official real transaction dataset with usable categorical hierarchy.
2. Replace arbitrary category digit assignment with externally justified taxonomies:
   - merchant/category taxonomy;
   - device/browser family taxonomy;
   - email domain grouping taxonomy;
   - geography/account hierarchy if available.
3. Add stronger baselines:
   - LightGBM/CatBoost supervised topline;
   - calibrated logistic regression;
   - rare-category/frequency baselines;
   - tree/hyperbolic baseline if hierarchy is central.
4. Keep the current negative controls mandatory:
   - random digit map;
   - random hierarchy order;
   - flat categorical frequency;
   - no-hierarchy real dataset.
5. Only call the result Q1-candidate if p-adic hierarchy beats all controls under temporal splits and bootstrap confidence intervals.

## Brutal final status

The reproducible pipeline is now built and fact-checked at the infrastructure level.

The empirical result is not Q1-grade yet.

I did not force a flattering result. The pipeline correctly rejects the current evidence as diagnostic-only.
