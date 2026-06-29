# Dataset card: IEEE-CIS Fraud Detection

Status: official competition download blocked in this environment; local mirror downloaded for development-only audit.

Official source: Kaggle competition `ieee-fraud-detection`
Official URL: https://www.kaggle.com/competitions/ieee-fraud-detection
Official access status on 2026-06-08: `kaggle competitions download -c ieee-fraud-detection` returned HTTP 401 Unauthorized. User must accept competition rules / enable access before this can be used as official primary evidence.

Development mirror used:

- Kaggle dataset: `lnasiri007/ieeecis-fraud-detection`
- URL: https://www.kaggle.com/datasets/lnasiri007/ieeecis-fraud-detection
- Kaggle CLI-reported license on 2026-06-08: unknown
- Local files:
  - `data/ieee_cis_mirror/train_transaction.csv`
  - `data/ieee_cis_mirror/train_identity.csv`
  - `data/ieee_cis_mirror/test_transaction.csv`
  - `data/ieee_cis_mirror/test_identity.csv`

Verified train rows in local mirror pipeline: 590,540.
Verified fraud rate in local mirror pipeline: 3.499%.

Use in this project:

- Suitable for development and diagnostic audit only until official competition access is fixed.
- Candidate hierarchy columns used by current p-adic audit:
  - `ProductCD`
  - `card4`
  - `card6`
  - `P_emaildomain`
  - `DeviceType`
- These are categorical fields, but not a fully validated merchant/account taxonomy. Q1 primary claims require stronger semantic hierarchy justification or additional real datasets.

Reproduction commands:

```bash
# Official source; currently unauthorized in this environment
kaggle competitions download -c ieee-fraud-detection -p data/ieee_cis --unzip

# Development mirror actually used in this session
kaggle datasets download -d lnasiri007/ieeecis-fraud-detection -p data/ieee_cis_mirror --unzip
python -m motif_fraud.p_adic.ieee_pipeline
```
