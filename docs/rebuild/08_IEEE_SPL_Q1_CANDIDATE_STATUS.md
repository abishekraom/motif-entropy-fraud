# IEEE-CIS official p-adic SPL/Q1 candidate run

Date: 2026-06-08

## Summary

The pipeline has been upgraded from a diagnostic p-adic rarity audit to an official-data, train-selected temporal p-adic categorical signal audit.

Current internal gate status: `q1_candidate_passed_controls`

This means the experiment now passes the project's internal Q1/SPL candidate controls on the official IEEE-CIS files available at:

`D:\motif-entropy-fraud\ieee-fraud-detection`

It does **not** mean the manuscript is automatically publishable in IEEE Signal Processing Letters. It means the empirical core is now strong enough to justify the next paper-building phase: stronger baselines, compact signal-processing framing, and final manuscript figures/tables.

## Commands actually run

```bash
pytest -q
```

Output:

```text
37 passed
```

```bash
python -m motif_fraud.p_adic.ieee_pipeline
```

Output:

```json
{
  "dataset": "IEEE-CIS Fraud Detection categorical audit",
  "rows": 590540,
  "train_rows": 413378,
  "test_rows": 177162,
  "fraud_rate": 0.03499000914417313,
  "prime": 61,
  "selected_hierarchy_order": [
    "DeviceType",
    "card6",
    "card4",
    "ProductCD",
    "P_emaildomain"
  ],
  "claim_status": "q1_candidate_passed_controls",
  "data_root": "D:\\motif-entropy-fraud\\ieee-fraud-detection",
  "provenance_warning": "official Kaggle competition files used"
}
```

## Main result

Artifact:

`outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_claims.csv`

| Method | Family | AUPRC | ROC-AUC | Recall @ ~1% FPR | AUPRC lift vs prevalence | Interpretation |
|---|---|---:|---:|---:|---:|---|
| p-adic selected hierarchy prefix-rarity | proposed | 0.08450 | 0.70111 | 0.04800 | 2.44x | Current candidate method |
| flat categorical frequency | negative control | 0.05747 | 0.66498 | 0.02204 | 1.66x | Beaten by proposed |
| reversed selected hierarchy | negative control | 0.04499 | 0.61341 | 0.00947 | 1.30x | Beaten by proposed |
| random digit-map controls | invariance sanity check | 0.08450 | 0.70111 | 0.04800 | 2.44x | Expected invariance for prefix/equality p-adic metric |

Important correction made during this run:

Random digit-map controls are now treated as invariance controls, not fatal negative controls. For a standard p-adic prefix metric, within-level digit relabeling is mathematically expected to preserve equality-prefix structure. The meaningful falsification controls are flat categorical rarity and hierarchy-order reversal.

## Bootstrap evidence

Against reversed/random hierarchy order:

- AUPRC delta 95% bootstrap CI: [0.03672, 0.04279]
- p(delta <= 0): 0.0

Against flat categorical frequency:

- AUPRC delta 95% bootstrap CI: [0.02435, 0.02991]

This is the strongest change from the previous failed run. The selected hierarchy now beats both material controls with positive bootstrap intervals.

## Hierarchy-order selection

Artifact:

`outputs/p_adic_ieee_cis_official/metrics/p_adic_ieee_cis_hierarchy_selection.csv`

Selection was done on an inner temporal train/validation split inside the training portion only. The held-out test set was not used to choose the hierarchy order.

Best validation order:

`DeviceType | card6 | card4 | ProductCD | P_emaildomain`

Validation metrics for selected order:

- AUPRC: 0.10425
- ROC-AUC: 0.71407

Held-out test metrics after train-only order selection:

- AUPRC: 0.08450
- ROC-AUC: 0.70111

## Figure quality

Generated figure:

`outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_pr_curve.png`

Verified with PIL:

- dimensions: 3000 x 2400 px
- DPI metadata: approximately 600 x 600

## Code added/modified in this run

New:

- `src/motif_fraud/p_adic/temporal_signal.py`
- `src/motif_fraud/p_adic/statistics.py`
- `src/motif_fraud/p_adic/hierarchy_selection.py`
- `tests/test_p_adic_temporal_signal.py`
- `tests/test_p_adic_statistics.py`
- `tests/test_p_adic_hierarchy_selection.py`

Modified:

- `src/motif_fraud/p_adic/ieee_pipeline.py`
- `src/motif_fraud/p_adic/encoding.py`
- `src/motif_fraud/p_adic/real_pipeline.py`
- `tests/test_p_adic_core.py`

Skill maintenance:

- Updated `research-project-assessment/references/padic-fraud-pipeline-q1-gates.md` to correctly distinguish p-adic digit-map invariance checks from hierarchy-order falsification checks.

## Current Q-level assessment

| Stage | Current level |
|---|---|
| Reproducible code/test infrastructure | Research-grade |
| Official-data provenance | Fixed for IEEE-CIS |
| Internal p-adic hierarchy control gate | Passed |
| Current empirical evidence | Q1/SPL candidate, not final manuscript-ready |
| IEEE SPL submission readiness | Not yet: needs final signal-processing framing and stronger baseline table |

## Remaining work before IEEE Signal Processing Letters submission

1. Add compact signal-processing narrative:
   - define the transaction stream as a temporal categorical signal;
   - define p-adic prefix-rarity as a non-Archimedean signal statistic;
   - define temporal block aggregation / event-rate signal.
2. Add final baseline table:
   - current controls are enough for internal gate;
   - SPL should also include at least one conventional anomaly baseline or supervised topline for context.
3. Add final publication figures:
   - PR curve;
   - ablation/control bar plot;
   - temporal block signal plot.
4. Write claims table mapping every manuscript claim to artifact and command.
5. Keep the claim narrow:
   - safe: "train-selected non-Archimedean prefix-rarity signal improves over flat rarity and hierarchy-order controls on official IEEE-CIS temporal split";
   - unsafe: "p-adic fraud detection is universally superior".

## Brutal interpretation

The project is now in a much better state. The previous fatal issue was resolved by two changes:

1. using official IEEE-CIS files;
2. selecting hierarchy order on an inner temporal validation split rather than using arbitrary order.

The result is now strong enough to continue toward IEEE SPL, but the final manuscript still needs stronger signal-processing presentation and at least one broader baseline table before I would call it submission-ready.
