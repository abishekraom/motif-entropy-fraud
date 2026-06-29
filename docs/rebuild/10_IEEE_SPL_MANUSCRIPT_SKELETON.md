# Draft IEEE SPL Manuscript Skeleton

Working title:
Non-Archimedean Prefix-Rarity Signals for Temporal Fraud Surveillance

Status: evidence-backed skeleton, not final submission text.

## Abstract draft

Fraud detection in transaction streams often depends on sparse categorical combinations whose hierarchy is lost under flat encodings. This letter studies a non-Archimedean representation of transaction categories, where coarse-to-fine categorical fields define a p-adic prefix signal and anomaly scores are derived from prefix rarity under a temporal training split. On the official IEEE-CIS fraud dataset, a train-selected hierarchy `DeviceType -> card6 -> card4 -> ProductCD -> P_emaildomain` yields an unsupervised p-adic prefix-rarity signal with AUPRC 0.0845 and ROC-AUC 0.7011 on the held-out temporal test set. The signal improves over flat categorical rarity (AUPRC 0.0575) and reversed-hierarchy control (AUPRC 0.0450), with positive bootstrap AUPRC-delta intervals. A broader baseline audit shows that the raw p-adic signal does not beat a supervised logistic frequency baseline (AUPRC 0.0975), but adding the p-adic score improves the supervised baseline to AUPRC 0.1007. These results support a narrow claim: p-adic prefix-rarity is an interpretable complementary temporal categorical signal, not a universal standalone fraud detector.

## I. Introduction and related positioning

Transaction fraud streams contain mixed categorical fields: device type, card type, product code, and email domain. Standard flat encodings treat these fields as independent or unordered symbols. This loses the possibility that categorical fields can form a coarse-to-fine hierarchy. Non-Archimedean metrics, especially p-adic prefix geometry, naturally encode hierarchical agreement: records sharing coarse prefixes remain close, while early disagreements become far.

The related literature already covers p-adic/ultrametric machine learning, categorical anomaly detection, hierarchical anomaly detection, and broad fraud-detection ML. Therefore, the manuscript must not claim general invention of p-adic ML or fraud detection. The novelty boundary is narrower: a p-adic prefix-rarity statistic for temporal categorical fraud surveillance, validated against flat-rarity and hierarchy-order controls and tested for complementarity with a supervised frequency baseline.

Positioning artifact:

`docs/rebuild/12_LITERATURE_NOVELTY_POSITIONING.md`

This letter asks whether a p-adic prefix-rarity statistic can serve as a compact temporal signal for fraud surveillance.

Contributions:

1. Define a p-adic prefix-rarity signal over transaction-category streams.
2. Select hierarchy order using only an inner temporal validation split.
3. Evaluate on official IEEE-CIS with temporal train/test split.
4. Compare against flat categorical rarity, reversed hierarchy, random digit-map invariance checks, unsupervised Isolation Forest, and supervised logistic frequency baselines.
5. Release reproducible artifacts with claim-to-artifact mapping and 600 dpi figures.

Do not claim:

- SOTA fraud detection.
- Universal p-adic superiority.
- Numeric semantics of arbitrary digit labels inside hierarchy levels.

## II. Method

### A. Temporal categorical stream

Let each transaction at time `t` be represented by categorical tuple:

`x_t = (c_{t,1}, c_{t,2}, ..., c_{t,d})`

where the selected IEEE-CIS hierarchy is:

`DeviceType -> card6 -> card4 -> ProductCD -> P_emaildomain`

The hierarchy order is selected on an inner temporal validation split within the training set only.

Evidence artifact:

`outputs/p_adic_ieee_cis_official/metrics/p_adic_ieee_cis_hierarchy_selection.csv`

### B. p-adic encoding

Each category at hierarchy level `j` is mapped to a digit in base `p`. A transaction receives code:

`z_t = sum_{j=0}^{d-1} a_{t,j} p^j`

where earlier hierarchy levels correspond to coarser agreement. The induced p-adic prefix structure makes shared hierarchy prefixes explicit.

Important caveat:

Within-level digit relabeling is treated as an invariance check. The method claims hierarchy-prefix structure, not numeric ordering among arbitrary category labels.

### C. Prefix-rarity score

The score estimates how rare a transaction's p-adic prefixes are relative to non-fraud training transactions. A weighted-deep prefix rarity statistic is used, giving signal to progressively finer hierarchy levels.

### D. Temporal signal aggregation

For interpretation, transaction scores are also aggregated into ordered temporal blocks. Each block records:

- row count;
- fraud count;
- fraud rate;
- mean p-adic score;
- max p-adic score.

Evidence artifact:

`outputs/p_adic_ieee_cis_official/metrics/p_adic_ieee_cis_temporal_blocks.csv`

## III. Experiments

Dataset:
Official IEEE-CIS Fraud Detection Kaggle competition files.

Local source:

`D:\motif-entropy-fraud\ieee-fraud-detection`

Split:
Temporal split by `TransactionDT`.

Rows:

- total: 590,540
- train: 413,378
- test: 177,162
- test fraud rate: 0.03457

Primary command:

```bash
python -m motif_fraud.p_adic.ieee_pipeline
```

Baseline command:

```bash
python -m motif_fraud.p_adic.official_baselines
```

Figure command:

```bash
python -m motif_fraud.p_adic.publication_figures
```

Test command:

```bash
pytest -q
```

Verified result:

`40 passed`

## IV. Results

### A. Control gate

Artifact:

`outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_claims.csv`

| Method | AUPRC | ROC-AUC | Recall @ approx 1% FPR | Interpretation |
|---|---:|---:|---:|---|
| p-adic selected hierarchy | 0.08450 | 0.70111 | 0.04800 | primary unsupervised signal |
| flat categorical rarity | 0.05747 | 0.66498 | 0.02204 | beaten control |
| reversed hierarchy | 0.04499 | 0.61341 | 0.00947 | beaten control |
| random digit-map checks | 0.08450 | 0.70111 | 0.04800 | expected invariance |

Bootstrap:

- vs reversed hierarchy AUPRC delta CI: [0.03672, 0.04279]
- p(delta <= 0): 0.0
- vs flat categorical rarity AUPRC delta CI: [0.02435, 0.02991]

### B. Broader baseline context

Artifact:

`outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_baseline_comparison.csv`

| Method | AUPRC | ROC-AUC | Interpretation |
|---|---:|---:|---|
| p-adic selected hierarchy | 0.08450 | 0.70111 | primary unsupervised p-adic signal |
| logistic frequency supervised | 0.09747 | 0.72726 | stronger raw supervised baseline |
| logistic frequency + p-adic signal | 0.10067 | 0.72538 | p-adic adds complementary AUPRC |
| Isolation Forest frequency unsupervised | 0.07579 | 0.71514 | lower AUPRC, higher ROC-AUC than p-adic |

Interpretation:

The p-adic signal does not beat the supervised logistic frequency baseline as a raw detector. Its stronger claim is complementarity and interpretable hierarchy-aware unsupervised signal structure.

## V. Figures

All current figures are approximately 600 dpi.

- PR curve:
  `outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_pr_curve.png`
- Temporal signal:
  `outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_temporal_signal.png`
- Control ablation:
  `outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_control_ablation.png`
- Baseline context:
  `outputs/p_adic_ieee_cis_official/figures/p_adic_ieee_cis_baseline_context.png`

## VI. External validation

A second real/reputed categorical fraud dataset was added as supporting evidence:

- Kaggle ref: `shivamb/vehicle-claim-fraud-detection`
- Title: Vehicle Insurance Claim Fraud Detection
- License: CC0-1.0
- Kaggle metadata source: Oracle Databases
- Rows: 15,420
- Fraud rate: 0.05986
- Temporal order: derived from `Year`, `Month`, and `WeekOfMonth`

Command:

```bash
python -m motif_fraud.p_adic.vehicle_claim_pipeline
```

Artifact:

`outputs/p_adic_vehicle_claim/tables/p_adic_vehicle_claim_claims.csv`

| Method | AUPRC | ROC-AUC | Interpretation |
|---|---:|---:|---|
| p-adic selected vehicle hierarchy | 0.06424 | 0.55028 | supportive external signal |
| flat vehicle tuple rarity | 0.05617 | 0.50352 | beaten control |
| reversed vehicle hierarchy | 0.04677 | 0.43879 | beaten control |

The selected external hierarchy is:

`AccidentArea -> PolicyType -> VehicleCategory -> BasePolicy -> Make -> Fault`

Interpretation:

This result supports the hierarchy-prefix control claim on a second real/reputed categorical fraud dataset, but the effect size is modest. It should be used as external support, not as a second primary benchmark.

## VII. Limitations

1. The raw p-adic signal is not the strongest detector in the broader IEEE-CIS baseline table.
2. The strongest evidence remains IEEE-CIS; vehicle-claim fraud is supportive but weaker.
3. The vehicle dataset has coarse temporal ordering rather than transaction-level timestamps.
4. The hierarchy is selected from available categorical fields, not from an externally provided merchant/device ontology.
5. Random digit relabeling invariance means the method should be described as prefix-structural, not digit-semantic.
6. The temporal block signal supports interpretation, not deployment readiness.

## VIII. Submission-readiness verdict

Current status:

Q1/SPL candidate with baseline caveat.

Not yet final submission-ready.

Remaining before submission:

1. Convert this skeleton into IEEE SPL format.
2. Add references/literature positioning.
3. Tighten method notation.
4. Decide whether to include only IEEE-CIS or ask user for another official dataset for external validation.
5. Finalize figure captions and table captions.
6. Run a final clean reproduction from scratch.

## Claim discipline

The claim audit is stored at:

`docs/rebuild/ieee_spl_claim_audit.csv`

This file marks defensible and unsafe claims before manuscript writing.
