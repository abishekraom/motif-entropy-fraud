# Dataset card: European Credit Card Fraud Detection

Status: downloaded and used for diagnostic real-data pipeline.

Source: Kaggle dataset `mlg-ulb/creditcardfraud`
URL: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
License reported by Kaggle CLI on 2026-06-08: DbCL-1.0
Rows: 284,807
Frauds: 492
Fraud rate: 0.172% according to Kaggle metadata and verified pipeline metadata.
Time span: two days of September 2013 European cardholder transactions.
Features: V1-V28 PCA-anonymized numerical features; `Time`; `Amount`; `Class`.
Primary metric recommended by dataset metadata: AUPRC due extreme imbalance.

Use in this project:

- Real-data diagnostic and negative-control dataset only.
- Not valid as primary evidence for p-adic hierarchical transaction encoding because original categorical hierarchy is not available; V1-V28 are PCA components.
- Any strong p-adic result here would need extra scrutiny because no semantic hierarchy exists.

Local file:

- `data/creditcardfraud/creditcard.csv`

Reproduction command:

```bash
kaggle datasets download -d mlg-ulb/creditcardfraud -p data/creditcardfraud --unzip
python -m motif_fraud.p_adic.real_pipeline
```
