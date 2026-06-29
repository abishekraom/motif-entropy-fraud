# External validation continuation: Vehicle Insurance Claim Fraud

Date: 2026-06-08

## Purpose

The next IEEE SPL strengthening step was external validation on a second real/reputed fraud dataset with categorical hierarchy. I did not use synthetic data.

Dataset downloaded automatically via Kaggle CLI:

- Kaggle ref: `shivamb/vehicle-claim-fraud-detection`
- Title: Vehicle Insurance Claim Fraud Detection
- License: CC0-1.0
- Kaggle metadata source field: `Oracle Databases`
- Local path: `D:\motif-entropy-fraud\vehicle-claim-fraud-detection\fraud_oracle.csv`

This is not as strong as official IEEE-CIS competition provenance, but it is a real/reputed external categorical fraud dataset and is usable as external support, not as the primary claim.

## Commands actually run

```bash
kaggle datasets download -d shivamb/vehicle-claim-fraud-detection -p ../vehicle-claim-fraud-detection --unzip
```

```bash
pytest tests/test_p_adic_vehicle_claim_pipeline.py -q
```

Result:

```text
1 passed
```

```bash
python -m motif_fraud.p_adic.vehicle_claim_pipeline
```

Result summary:

```json
{
  "dataset": "Vehicle Insurance Claim Fraud Detection",
  "source": "Kaggle shivamb/vehicle-claim-fraud-detection; CC0-1.0; userSpecifiedSources=Oracle Databases",
  "rows": 15420,
  "train_rows": 10794,
  "test_rows": 4626,
  "fraud_rate": 0.05985732814526589,
  "selected_hierarchy_order": [
    "AccidentArea",
    "PolicyType",
    "VehicleCategory",
    "BasePolicy",
    "Make",
    "Fault"
  ],
  "prime": 23,
  "claim_status": "external_support_passed_controls"
}
```

```bash
pytest -q
```

Result:

```text
41 passed
```

## External validation result

Artifact:

`outputs/p_adic_vehicle_claim/tables/p_adic_vehicle_claim_claims.csv`

| Method | AUPRC | ROC-AUC | Delta vs best control | Status |
|---|---:|---:|---:|---|
| p_adic_vehicle_selected_hierarchy | 0.06424 | 0.55028 | +0.00808 | external_support_passed_controls |
| flat_vehicle_tuple_rarity | 0.05617 | 0.50352 | 0.00000 | control |
| reversed_vehicle_hierarchy | 0.04677 | 0.43879 | -0.00940 | control |

Bootstrap p-adic vs reversed hierarchy:

- AUPRC delta lower: 0.01248
- AUPRC delta upper: 0.02535

## Figure

Artifact:

`outputs/p_adic_vehicle_claim/figures/p_adic_vehicle_claim_pr_curve.png`

Verified:

- dimensions: 3000 x 2400 px
- DPI: approximately 600 x 600

## New files

- `src/motif_fraud/p_adic/vehicle_claim_pipeline.py`
- `tests/test_p_adic_vehicle_claim_pipeline.py`

## Brutal interpretation

This external validation is supportive but not spectacular.

Good:

1. It uses a second real/reputed categorical fraud dataset.
2. The p-adic selected hierarchy beats flat tuple rarity and reversed hierarchy.
3. The external result passes the local control gate.
4. It supports the paper's narrow hierarchy-prefix signal claim.

Weak:

1. ROC-AUC is only 0.55028.
2. AUPRC is only 0.06424 at a fraud rate of 0.05986, so the absolute lift is small.
3. The dataset has coarser temporal ordering (`Year`, `Month`, `WeekOfMonth`) rather than transaction timestamp.
4. Provenance is less strong than IEEE-CIS competition data because it is a Kaggle dataset with source listed as Oracle Databases, not a competition-hosted benchmark.

Therefore, this should be used as **external supporting evidence**, not as a second primary benchmark.

## Updated project level

Current estimated completion: **84.5%**

Current level:

**IEEE SPL / Q1 candidate with baseline and external-validation caveats.**

The external validation improves the story, but does not eliminate the biggest limitation: raw p-adic signal is not stronger than a simple supervised logistic frequency baseline on IEEE-CIS.

## Revised safe paper claim

Safe claim now:

> A train-selected non-Archimedean prefix-rarity signal improves over flat rarity and reversed-hierarchy controls on official IEEE-CIS, provides complementary AUPRC when added to a supervised frequency baseline, and shows supportive external behavior on a real/reputed vehicle insurance fraud dataset.

Still unsafe:

> The p-adic method is the best overall fraud detector.

> The p-adic method is SOTA.

> The p-adic method universally generalizes across fraud domains.

## Remaining before final submission

1. Update the manuscript skeleton with this external-validation section.
2. Add literature references and novelty positioning.
3. Convert skeleton into IEEE SPL-style concise paper.
4. Perform final clean reproduction from scratch.
5. If the user wants stronger external validation, request a manually downloaded official/reputed dataset with:
   - fraud label;
   - timestamp or temporal ordering;
   - categorical transaction fields;
   - clear license/source.
