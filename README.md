# Motif Entropy Fraud

Research-grade reproducible audit pipeline for p-adic / motif-style fraud surveillance on official real datasets.

This repository is intentionally honest: the strongest p-adic empirical detector claims failed the official IEEE-CIS Q1/SPL gates. The code and artifacts are kept reproducible so the negative result is auditable rather than polished into a fake claim.

## Current scientific status

Claim status: diagnostic / failed Q1 empirical detector gate.

Official IEEE-CIS results show that the p-adic variants do not beat strong or simple controls:

- Raw p-adic prefix rarity is far below strong supervised tabular baselines.
- Temporal p-adic CUSUM has a small positive delta over flat CUSUM, but its bootstrap CI crosses zero.
- Rich p-adic feature augmentation does not improve the best strong baseline.
- Branch-signature interpretability loses precision/lift to flat tuple controls.
- The cleaner p-adic tree-scan LLR redesign failed the official IEEE-CIS gate; the parent-conditional residual extension improves the point estimate but still fails the strict CI gate.
- A first external CSE-CIC-IDS2018 Thursday tree-scan audit shows useful p-adic signal; the parent-conditional residual extension improves the point estimate, but the result still fails because entropy control has higher AUPRC and the bootstrap CI crosses zero.
- A preregistered fresh Wednesday CSE-CIC day independently fails against entropy control, so the cross-day evidence strengthens the diagnostic limitation rather than a superiority claim.

The repository is therefore GitHub-ready as a reproducible negative/diagnostic research artifact, not as a SOTA fraud detector.

Aggregate cross-dataset tree-scan status:

```text
diagnostic_only_failed_q1_cross_dataset_gate
```

## Repository layout

```text
src/motif_fraud/             Python package
  p_adic/                    P-adic fraud experiments, controls, and audits
  data/, evaluation/, ...    Older motif/rebuild support modules

tests/                       Reproducibility and claim-discipline tests
docs/rebuild/                Research logs, preregistered gates, failure analysis
results/                     Curated GitHub-ready final artifacts
paper/ieee_spl/              Historical SPL draft/bundle; not current after failed gates
data/README.md               Dataset acquisition notes; raw data is not committed
```

Ignored local-only directories:

- `data/*` except `data/README.md`
- `outputs/`
- `archive/`
- caches and build byproducts

## Install

Use Python 3.11+.

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash on Windows
python -m pip install -U pip
python -m pip install -e ".[dev,strong-baselines]"
```

If you only need lightweight tests, `python -m pip install -e ".[dev]"` is enough for most modules. Strong supervised baselines need LightGBM/CatBoost/XGBoost.

## Data

Raw datasets are not included.

For full official IEEE-CIS reproduction, download Kaggle IEEE-CIS Fraud Detection and place files at:

```text
D:/motif-entropy-fraud/ieee-fraud-detection/train_transaction.csv
D:/motif-entropy-fraud/ieee-fraud-detection/train_identity.csv
```

The code uses this path as the default on Lust's Windows/Git Bash environment. You can also call audit functions with a custom `data_root`.

## Verify the repo

```bash
pytest -q
```

Last verified locally:

```text
55 passed, 2 warnings
```

## Reproduce key artifacts

Write the reproduction plan:

```bash
python -m motif_fraud.p_adic.reproduce_all --plan-only
```

Run the fail-closed tree-scan gate on official IEEE-CIS:

```bash
python -m motif_fraud.p_adic.tree_scan_cusum --dataset ieee --output-root outputs/p_adic_ieee_cis_tree_scan
```

Run the broader p-adic artifact plan:

```bash
python -m motif_fraud.p_adic.reproduce_all
```

This may take a long time and requires official datasets and optional strong-baseline packages.

## Curated result index

See:

- `results/README.md`
- `docs/rebuild/25_TREE_SCAN_IMPLEMENTATION_AND_IEEE_GATE_RESULT.md`
- `docs/rebuild/26_CSE_CIC_EXTERNAL_TREE_SCAN_GATE_RESULT.md`
- `docs/rebuild/28_CSE_CIC_SECOND_DAY_PREREGISTRATION.md`
- `docs/rebuild/29_CSE_CIC_PREREGISTERED_WEDNESDAY_GATE_RESULT.md`
- `docs/rebuild/18_Q1_UPGRADE_RECURSION_RESULTS.md`

## Best verified headline numbers

Raw p-adic prefix rarity on official IEEE-CIS:

```text
AUPRC: 0.08450
ROC-AUC: 0.70111
```

Strong supervised compact baselines on official IEEE-CIS:

```text
LightGBM AUPRC: 0.49547
CatBoost AUPRC: 0.46368
XGBoost AUPRC: 0.48483
```

Tree-scan CUSUM full official IEEE-CIS gate, after parent-conditional residual extension:

```text
Best proposed: p_adic_conditional_tree_scan_llr, AUPRC 0.297719
Best control: transaction_count_signal, AUPRC 0.285952
Delta: +0.011766
Bootstrap CI: [-0.070532, 0.122167]
p_delta_le_zero: 0.330
Claim status: diagnostic_only_failed_q1_tree_scan_gate
```

CSE-CIC-IDS2018 Wednesday fresh preregistered gate:

```text
Best proposed: p_adic_conditional_tree_scan_llr, AUPRC 0.215253
Best control: category_entropy_temporal, AUPRC 0.249078
Delta: -0.033825
Bootstrap CI: [-0.141594, 0.039650]
p_delta_le_zero: 0.820
Claim status: diagnostic_only_failed_q1_tree_scan_gate
```

CSE-CIC-IDS2018 Thursday external tree-scan gate, after parent-conditional residual extension:

```text
Best proposed: p_adic_conditional_tree_scan_llr, AUPRC 0.524222
Best control: category_entropy_temporal, AUPRC 0.540129
Delta: -0.015906
Bootstrap CI: [-0.185953, 0.156353]
p_delta_le_zero: 0.506
Claim status: diagnostic_only_failed_q1_tree_scan_gate
```


## SoftwareX paper preparation

SoftwareX submission materials are being prepared under:

```text
paper/softwarex/
docs/softwarex/
scripts/softwarex_readiness_check.py
```

The SoftwareX framing is a reproducible research-software article about the fail-closed audit pipeline and curated diagnostic artifacts. It must not claim state-of-the-art fraud detection or statistically significant detector superiority.

Run the local SoftwareX readiness checker with:

```bash
python scripts/softwarex_readiness_check.py
```

## Citation / claim discipline

Do not cite this code as evidence for a superior p-adic fraud detector. The correct interpretation is:

```text
A reproducible, control-disciplined audit found that multiple p-adic hierarchy-aware fraud surveillance variants failed to outperform strong/simple controls on official IEEE-CIS.
```

Allowed claim:

```text
The repository provides a research-grade fail-closed pipeline for evaluating p-adic hierarchy-aware fraud surveillance hypotheses.
```

Banned claim:

```text
P-adic fraud detection is Q1/SOTA on IEEE-CIS.
```
