# Brutal Q1 / IEEE SPL reassessment after Claude's critique

Date: 2026-06-09

## Inputs checked

- Claude critique: `D:/motif-entropy-fraud/claude's response.txt`
- Strong-baseline audit: `docs/rebuild/15_STRONG_BASELINE_AUDIT_STATUS.md`
- PDF compile/final package status: `docs/rebuild/16_IEEE_SPL_PDF_COMPILE_STATUS.md`
- IEEE SPL public scope page, retrieved 2026-06-09:
  - SPL is for rapid dissemination of original, cutting-edge and timely significant contributions in signal/image/speech/language/audio processing.
  - SPL format is five pages: at most four pages of technical content plus one page of references.
  - The short format is meant to promote ideas, not sacrifice rigor.
  - It allows additional reproducibility information pages.
- arXiv API spot checks:
  - `p-adic` + `fraud`: 0 returned entries.
  - `p-adic` + `anomaly detection`: 0 returned entries.
  - `ultrametric` + `anomaly detection`: 0 returned entries.
  - categorical/hierarchical anomaly detection has existing related work.

## Verdict

Claude is mostly right about the scientific venue level **as the paper is currently framed**.

The project engineering/package level is high:

- compiled IEEE-style PDF exists;
- 44 tests pass;
- reproduction runner passes;
- 600 dpi figures exist;
- claim audit exists;
- LightGBM/CatBoost/XGBoost baselines exist.

But the scientific contribution level is not currently Q1/IEEE SPL strong.

Current honest paper level:

- **as detector paper:** Q3 / reject-risk high;
- **as narrow interpretable categorical surveillance note:** low Q2 possible, maybe SPL only if rewritten around a sharper signal-processing contribution;
- **as IEEE SPL/Q1:** not ready scientifically, despite package readiness.

## Why the current paper is capped

The decisive fact is the strong-baseline audit on official IEEE-CIS:

| Method | AUPRC | ROC-AUC |
|---|---:|---:|
| p-adic selected hierarchy | 0.08450 | 0.70111 |
| LightGBM compact tabular | 0.49547 | 0.90487 |
| CatBoost compact tabular | 0.46368 | 0.88681 |
| XGBoost compact tabular | 0.48483 | 0.90064 |

The raw p-adic method is roughly 5.9x lower AUPRC than LightGBM.

Augmentation does not rescue the detector story:

| Baseline | Baseline AUPRC | + p-adic AUPRC | Result |
|---|---:|---:|---|
| Logistic frequency | 0.09747 | 0.10067 | helps slightly |
| CatBoost | 0.46368 | 0.47092 | helps modestly |
| LightGBM | 0.49547 | 0.49511 | hurts slightly |
| XGBoost | 0.48483 | 0.48334 | hurts slightly |

Therefore, the paper cannot honestly claim:

- competitive detector;
- SOTA fraud detection;
- general complementarity;
- strong applied fraud utility.

The surviving current contribution is:

> a reproducible, interpretable, hierarchy-aware non-Archimedean categorical signal that beats flat rarity and reversed-hierarchy controls, but does not compete with strong supervised tabular models.

That is scientifically honest, but usually not enough for IEEE SPL unless the method contribution is sharpened substantially.

## What would make it Q1 / IEEE SPL level

Polishing the current draft is not enough. We need at least one of the following upgrades.

### Route A — strongest practical route: convert to a real signal-processing method

Current p-adic score is a single prefix-rarity statistic. For SPL, make the contribution a compact temporal signal-processing operator over categorical transaction streams:

1. Build a **multi-resolution p-adic temporal signal**, not one scalar rarity score.
   - prefix depth channels: level 1..d;
   - blockwise rates over time;
   - exponentially weighted prefix surprise;
   - p-adic tree/Haar/wavelet energy by depth;
   - change scores: derivative/CUSUM/EWMA over prefix-rarity channels.
2. Evaluate a surveillance task, not only transaction classification.
   - temporal block anomaly detection;
   - alert precision@k blocks;
   - recall at fixed alert budget;
   - lead-time / early warning if labels allow;
   - review-cost curves.
3. Compare against proper signal/anomaly baselines:
   - flat frequency time-series EWMA/CUSUM;
   - entropy-only block signal;
   - count-only/density-only block signal;
   - Isolation Forest/LOF/OneClassSVM on block features;
   - change-point methods on scalar rarity;
   - LightGBM block-level baseline as context.
4. The required win is not necessarily against LightGBM transaction classification; it must show the p-adic operator does something the scalar/flat temporal controls do not.

Pass condition for Q1/SPL route:

- p-adic temporal operator significantly beats flat temporal rarity/entropy/change baselines on at least official IEEE-CIS;
- result is robust across temporal blocks / bootstrap / seeds;
- the paper's method section contains a genuinely new compact operator, not just a rare-category score.

### Route B — feature-engineering route: make p-adic features help strong models robustly

Current single p-adic score helps CatBoost but not LightGBM/XGBoost. To claim useful complementarity, build richer p-adic features:

- per-depth prefix rarity vector;
- per-depth normal/fraud contrast learned only from training;
- temporal EWMA of prefix rarity;
- prefix novelty since last seen;
- p-adic nearest-normal prefix depth;
- tree-level density residual after marginal category frequency;
- interaction features with transaction amount/time/card/device.

Then rerun:

- LightGBM, CatBoost, XGBoost;
- with/without p-adic feature families;
- repeated seeds or stable temporal folds;
- paired bootstrap CI over AUPRC delta.

Pass condition:

- p-adic feature family improves the strongest baseline, not just CatBoost, with nontrivial and statistically stable AUPRC gain.

If LightGBM remains unchanged or worse, do not use this as the Q1 route.

### Route C — theory route: prove something real

If empirical detector utility stays weak, build the paper around theory:

- show prefix-rarity is an ultrametric kernel density estimator on a rooted categorical tree;
- derive invariance to within-level digit relabeling;
- prove when hierarchical anomalies are detectable by prefix-depth statistics but hidden from flat marginal rarity;
- derive sample complexity or a separation condition under a hierarchical contamination model;
- validate the theoretical condition on real IEEE-CIS blocks.

Pass condition:

- theorem + empirical validation becomes the novelty, not raw detector performance.

This could fit IEEE SPL if concise and signal/statistical enough.

### Route D — interpretability/deployment route: make explanation the product

Use p-adic score as an explainable monitoring layer:

- every alert decomposes by prefix level;
- show stable human-readable fraud signatures such as DeviceType/card6/card4/ProductCD/email-domain branches;
- compare explanation stability against SHAP for LightGBM/CatBoost;
- quantify explanation compactness, stability, and alert triage utility.

Pass condition:

- p-adic explanations reveal stable temporal branch anomalies missed or obscured by strong black-box baselines;
- evaluation is quantitative, not only anecdotal.

This is probably less SPL and more KBS/ESWA/interpretable-ML, unless expressed as a signal representation.

## Immediate next steps I recommend

Do not spend the next cycle polishing the current PDF. Build a falsifiable Q1-upgrade experiment.

### Step 1 — implement p-adic multi-resolution temporal operator

Add a module that outputs time-block features:

- block ID by TransactionDT quantile/time window;
- per-block fraud rate for evaluation only;
- p-adic depth rarity means/quantiles;
- p-adic tree-Haar or prefix-depth energy;
- flat rarity/entropy/count controls;
- EWMA/CUSUM change statistics.

### Step 2 — evaluate block-level surveillance

Metrics:

- AUPRC over blocks;
- precision@k blocks;
- recall at top 1%, 5%, 10% alert budget;
- paired bootstrap CI versus flat temporal rarity and entropy controls.

### Step 3 — compare with temporal/anomaly baselines

Baselines:

- block transaction count;
- block fraud prevalence prior from training;
- flat tuple rarity block mean;
- category entropy block signal;
- Isolation Forest on block features;
- LOF/OneClassSVM if feasible;
- LightGBM block-level model as context, not necessarily target.

### Step 4 — only then reassess IEEE SPL

If the p-adic temporal operator wins materially against flat temporal controls, IEEE SPL becomes plausible.

If it loses or ties, Claude's Q3/low-Q2 assessment stands and we should retarget rather than force SPL.

## Updated target-level estimate

Current compiled package:

- engineering/reproducibility: **94% complete**;
- scientific Q1 readiness: **55-60%**;
- IEEE SPL submission readiness after honest venue filtering: **not ready**.

Current level:

- **Q3 as detector paper**;
- **low Q2 as an interpretable categorical anomaly note**;
- **IEEE SPL candidate only after a stronger temporal signal-processing operator or theory result.**

## Bottom line

Claude's critique is not an insult; it is basically the same conclusion the LightGBM/CatBoost/XGBoost audit forced.

The package is polished, but the central empirical payoff is too weak for Q1/SPL as-is.

To climb to IEEE SPL level, the next work must create new evidence, not prettier writing:

1. multi-resolution p-adic temporal signal operator;
2. block-level surveillance task;
3. strong temporal/flat/entropy/anomaly baselines;
4. bootstrap confidence over alert metrics;
5. claim-safe rewrite only if the new operator wins.
