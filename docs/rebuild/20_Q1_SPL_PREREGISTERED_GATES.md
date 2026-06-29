# Pre-registered gates for Q1 / IEEE SPL p-adic multiresolution surveillance

Date: 2026-06-09

## Non-negotiable constraints

- No synthetic empirical data.
- Primary empirical evidence must use official or reputed real datasets.
- Current primary local dataset: official IEEE-CIS Fraud Detection files at `D:/motif-entropy-fraud/ieee-fraud-detection`.
- External datasets must come from official/reputed sources such as Kaggle competitions, UNSW, CIC/UNB, official institutional releases, or peer-reviewed dataset releases.
- If an external dataset is unavailable locally and cannot be downloaded through official tooling, stop and ask Lust to download it.
- All figures for manuscript-grade artifacts must be at least 300 dpi; target 600 dpi.
- Negative, null, or failed results are valid outcomes and must be recorded as failed/diagnostic, not polished into false claims.

## Current failed baseline facts that remain binding

On official IEEE-CIS:

- raw transaction-level p-adic AUPRC: 0.08450;
- raw transaction-level p-adic ROC-AUC: 0.70111;
- LightGBM compact tabular AUPRC: 0.49547;
- CatBoost compact tabular AUPRC: 0.46368;
- XGBoost compact tabular AUPRC: 0.48483;
- rich p-adic features did not improve the best strong model;
- temporal p-adic CUSUM had a small positive point estimate over flat CUSUM but bootstrap CI crossed zero;
- branch signatures had higher recall/coverage but lower precision/lift than flat tuple signatures.

Therefore, the paper cannot claim detector superiority, SOTA fraud detection, or general strong-model complementarity unless a new pre-registered result overturns these facts under stronger controls.

## Target SPL thesis

A permissible IEEE SPL thesis is:

> A non-Archimedean multiresolution statistic for categorical event-stream surveillance provides an interpretable hierarchy-aware temporal control signal, and under pre-specified controls it can be evaluated without detector-overclaiming.

The primary contribution must be a compact signal-processing operator, not post-hoc feature tweaking.

## Primary operator specification

Given a train-only hierarchy of categorical fields, each event maps to a rooted prefix path. The operator must output:

1. per-depth prefix surprise/rarity estimated from normal training events only;
2. per-depth residuals or centered scores using train-only references;
3. block-level multiresolution energy;
4. temporal CUSUM/EWMA variants over that energy;
5. flat tuple rarity controls;
6. entropy/count controls;
7. reversed hierarchy controls;
8. random hierarchy-order controls;
9. random digit-map invariance sanity controls.

No held-out test labels may be used for hierarchy selection, digit mapping, threshold selection, or model selection except for final metric evaluation.

## Dataset gates

### Dataset 1: IEEE-CIS Fraud Detection

Eligible because official local data exist.

Required split:

- temporal split by `TransactionDT`;
- train fraction may be fixed at 0.7 unless changed before any run;
- held-out test cannot influence hierarchy or parameters.

### Dataset 2: external official/reputed event-stream dataset

Candidate priority:

1. ToN_IoT from UNSW;
2. BoT-IoT from UNSW;
3. CSE-CIC-IDS2018 from CIC/UNB;
4. UNSW-NB15 from UNSW.

Before use, create a dataset card with source URL, local path, license/terms, row count, target labels, timestamp field, categorical hierarchy candidates, leakage columns, and claim eligibility.

## Primary metrics

For the Q1/SPL gate, the primary task is temporal block surveillance, not row-level classification.

Primary metric:

- AUPRC over held-out temporal blocks labeled high-risk/high-fraud/high-attack by pre-specified block-label rule.

Secondary metrics:

- ROC-AUC over blocks;
- precision at fixed alert budget;
- recall at fixed alert budget;
- precision/lift of selected alert blocks;
- bootstrap CI for proposed-minus-best-control AUPRC.

## Mandatory controls

The proposed p-adic multiresolution operator must be compared against:

- flat tuple rarity temporal score;
- flat tuple rarity EWMA/CUSUM;
- category entropy temporal score;
- transaction/flow count temporal score;
- reversed hierarchy order;
- random hierarchy-order controls;
- random digit-map invariance sanity checks;
- unsupervised block-feature context model such as Isolation Forest if feasible;
- supervised LightGBM block-level context if feasible.

Random digit-map equivalence is not by itself a failure for prefix/equality p-adic semantics; it is expected invariance unless numeric within-level digit semantics are claimed. Reversed/random hierarchy-order equivalence is a serious failure for hierarchy-depth claims.

## Q1/SPL pass condition

A headline Q1/SPL empirical claim is allowed only if all are true:

1. proposed p-adic multiresolution temporal method has higher AUPRC than every mandatory flat/hierarchy-order/control family on the held-out test blocks;
2. paired bootstrap 95% CI for proposed-minus-best-control AUPRC is strictly positive;
3. `p_delta_le_zero <= 0.05` when estimated;
4. figure DPI is verified >= 300, target 600;
5. artifact metadata says `synthetic_data_used: false`;
6. same gate passes on IEEE-CIS and at least one external official/reputed dataset, or the manuscript is rewritten as a theory-first paper with external data clearly marked diagnostic;
7. strong supervised row-level baselines are disclosed as context and not hidden.

## Failure statuses

Use these statuses exactly:

- `q1_candidate_multiresolution_signal_passed_controls`: all pre-registered empirical gates passed.
- `diagnostic_only_failed_q1_multiresolution_gate`: valid real-data run, but proposed method did not beat controls with strict positive CI.
- `external_dataset_unavailable_requires_user_download`: official/reputed external dataset is required but not locally available.
- `development_only_provenance_blocked`: dataset provenance is not official/reputed enough for primary claims.

## Unsafe claims banned unless gates pass

- state-of-the-art fraud detector;
- competitive transaction-level detector;
- general complementarity to LightGBM/CatBoost/XGBoost;
- statistically significant surveillance superiority;
- robust cross-dataset p-adic anomaly detection;
- IEEE SPL/Q1 ready empirical detector.

## Safe claims before gate pass

- reproducible hierarchy-aware diagnostic signal;
- multiresolution categorical event-stream surveillance audit;
- interpretable prefix-depth control signal;
- failure-aware benchmark showing where p-adic hierarchy helps or fails;
- control-discipline contribution.

## Immediate implementation protocol

1. Write tests before production code.
2. Use official IEEE-CIS data for empirical tests.
3. Allow tiny deterministic constructed fixtures only for mathematical invariance unit tests if unavoidable; never count them as empirical evidence. If the user prohibits even this, use only real IEEE-CIS slices for all tests.
4. Run targeted tests after each module.
5. Run full suite before claiming stability.
6. Inspect figure DPI programmatically.
7. If Q1 gates fail, record failure and do not tune on test recursively.
