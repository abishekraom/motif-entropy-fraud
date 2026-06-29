# IEEE SPL literature and novelty positioning

Date: 2026-06-08

Purpose: define what the p-adic fraud manuscript can safely claim relative to prior work. This is not a broad survey; it is a reviewer-risk map for IEEE SPL submission.

## Primary paper position

Safe central claim:

> A train-selected non-Archimedean prefix-rarity signal improves over flat rarity and reversed-hierarchy controls on official IEEE-CIS, provides complementary AUPRC when added to a supervised frequency baseline, and shows supportive external behavior on a real/reputed vehicle insurance fraud dataset.

Do not claim:

- best overall fraud detector;
- SOTA fraud detection;
- universal p-adic superiority;
- numeric semantics of arbitrary digit labels inside categorical levels.

## Literature map

| Area | Representative source found | Year | Evidence / relevance | How it affects our claim |
|---|---|---:|---|---|
| p-adic / non-Archimedean ML | `p-adic statistical field theory and deep belief networks`, Physica A, DOI: 10.1016/j.physa.2023.128492 | 2023 | OpenAlex reports p-adic field theory applied to deep belief networks. | Shows p-adic ML exists; our novelty cannot be “first p-adic ML.” |
| p-adic neural models | `p-Adic statistical field theory and convolutional deep Boltzmann machines`, PTEP, DOI: 10.1093/ptep/ptad061 | 2023 | p-adic statistical field theory used for convolutional deep Boltzmann machines. | Supports mathematical lineage, but not fraud/transaction prefix-rarity. |
| ultrametric ML | `Learning in Ultrametric Committee Machines`, Journal of Statistical Physics, DOI: 10.1007/s10955-012-0636-1 | 2012 | Ultrametric structure used in learning theory/modeling. | Ultrametric learning is prior art; claim must be specific to transaction fraud signal. |
| categorical anomaly detection | `Anomaly Detection Methods for Categorical Data`, ACM Computing Surveys, DOI: 10.1145/3312739 | 2019 | Survey focused on categorical anomaly methods. | Requires us to compare against simple categorical rarity/frequency controls. We do. |
| auto-insurance fraud anomaly | `Auto insurance fraud detection using unsupervised spectral ranking for anomaly`, Journal of Finance and Data Science, DOI: 10.1016/j.jfds.2016.03.001 | 2016 | Unsupervised auto-insurance fraud detection exists. | Our vehicle-claim result is support, not novelty by itself. |
| credit-card fraud survey | `A Survey of Credit Card Fraud Detection Techniques: Data and Technique Oriented Perspective`, arXiv DOI: 10.48550/arxiv.1611.06439 | 2016 | Credit-card fraud detection literature is broad and mature. | Avoid broad fraud-superiority language. |
| e-commerce fraud ML | `Machine Learning for Fraud Detection in E-Commerce: A Research Agenda`, DOI: 10.1007/978-3-030-87839-9_2 | 2021 | ML fraud detection framed as ongoing research agenda. | Our contribution is a signal/statistic, not complete fraud system. |
| explainable fraud ML | `Explainable Machine Learning for Fraud Detection`, IEEE Computer, DOI: 10.1109/mc.2021.3081249 | 2021 | Explainability is an established fraud-detection concern. | Supports interpretable/complementary signal framing. |
| hierarchical anomaly detection | `Multivariate Time Series Anomaly Detection and Interpretation using Hierarchical Inter-Metric and Temporal Embedding`, KDD, 2021 | 2021 | Hierarchical/temporal anomaly detection is active prior art. | Our novelty must emphasize non-Archimedean prefix-rarity over transaction categories. |
| supervised tabular baseline | `XGBoost`, DOI: 10.1145/2939672.2939785 | 2016 | Very strong tabular baseline family. | We should eventually include or discuss tree-based baselines; current logistic context is not enough for final SOTA claims. |
| fraud learning-to-defer dataset | `FiFAR: A Fraud Detection Dataset for Learning to Defer`, arXiv:2312.13218 / DOI: 10.48550/arxiv.2312.13218 | 2023 | Recent fraud dataset around human-AI deferral. | Possible future external validation, but task differs from transaction prefix-rarity. |
| Bank Account Fraud dataset suite | Kaggle `sgpjesus/bank-account-fraud-dataset-neurips-2022` metadata | 2022 | Realistic, biased, imbalanced, dynamic tabular datasets, but Kaggle metadata says synthetic / privacy-preserving generated suite. | Do not use for research evidence under user’s no-synthetic rule. Can cite only as related benchmark family if needed. |

## Novelty boundary

Not novel:

1. p-adic / ultrametric ideas in ML generally.
2. categorical anomaly detection generally.
3. fraud detection with ML generally.
4. hierarchical/temporal anomaly detection generally.
5. supervised tabular fraud baselines.

Potentially novel enough for a letter:

1. Using a p-adic prefix-rarity statistic as a compact temporal categorical fraud signal.
2. Train-only hierarchy-order selection with reversed-hierarchy and flat-rarity falsification controls.
3. Showing that the p-adic signal is complementary to a supervised frequency baseline on official IEEE-CIS.
4. Providing a claim-audited reproducible artifact bundle with 600 dpi figures and external support.

## Reviewer-risk assessment

| Reviewer objection | Current answer | Remaining risk |
|---|---|---|
| “This is just categorical rarity.” | Proposed beats flat tuple rarity on IEEE-CIS and vehicle-claim external audit. | Need concise ablation table in manuscript. |
| “Hierarchy order was cherry-picked on test.” | Order selected on inner temporal validation split inside training set. | Must state this clearly and include artifact. |
| “Why p-adic? Digit labels are arbitrary.” | Claim is prefix/equality geometry; digit relabeling is expected invariance, not a semantic claim. | Must avoid digit-numeric wording. |
| “Does it beat standard ML?” | Raw p-adic does not beat supervised logistic frequency baseline; p-adic improves logistic AUPRC when added. | Cannot claim SOTA. Need frame as complementary/interpretable signal. |
| “Does it generalize?” | Vehicle insurance dataset passes controls but with modest effect size. | External support is weaker than primary IEEE-CIS. |
| “Where is signal processing?” | Temporal block p-adic signal and fixed-FPR metrics exist. | Need stronger SPL-style method prose and maybe a concise detection statistic equation. |

## Current recommended manuscript thesis

Use this thesis:

> Non-Archimedean prefix geometry provides a compact and interpretable categorical signal for fraud surveillance. On official IEEE-CIS, a train-selected p-adic prefix-rarity signal survives flat-rarity and hierarchy-order controls and provides complementary AUPRC to a supervised frequency baseline. A second vehicle insurance fraud dataset gives supportive, though weaker, external evidence.

Avoid this thesis:

> P-adic fraud detection is a new state-of-the-art fraud detector.

## Sources / lookup provenance

- OpenAlex API was used for DOI/title/citation reconnaissance.
- arXiv API was used for arXiv-indexed fraud and anomaly papers.
- Kaggle CLI metadata was used for dataset provenance checks.
- Current local empirical artifacts are under `outputs/p_adic_ieee_cis_official/` and `outputs/p_adic_vehicle_claim/`.
