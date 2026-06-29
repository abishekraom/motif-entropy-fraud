# Fault model and Q1 redesign — pre-implementation audit

Date: 2026-06-09

Scope: This document records the no-new-source-code audit requested before any further implementation. It identifies implementation and mathematical faults in the current p-adic/prefix-rarity route, records diagnostic evidence from official/reputed real data artifacts, and narrows the only defensible Q1/SPL redesign path.

No subagents were used. No synthetic empirical data were used. No source-code changes were made for this audit.

## 1. Current route is not Q1/SPL-grade

The current empirical record remains fail-closed:

- Raw IEEE-CIS p-adic AUPRC: 0.08450.
- LightGBM compact tabular AUPRC: 0.49547.
- Rich p-adic feature augmentation did not improve the best strong baseline.
- Temporal p-adic CUSUM had a small positive point estimate over flat CUSUM but its bootstrap confidence interval crossed zero.
- Branch signatures had higher recall/coverage but lower precision/lift than flat tuple branches.
- Preregistered multiresolution audit failed because a random hierarchy-order control beat the proposed score on IEEE-CIS.

Therefore, the existing method cannot support a Q1/SPL detector-superiority claim.

## 2. Mathematical fault: prefix rarity is not enough

The implemented statistic is essentially prefix support rarity:

```text
score_k(x) = 1 - count_train_normal(prefix_k(x)) / N_train_normal
```

then averaged/weighted over prefix depths and optionally transformed by EWMA/CUSUM.

This is not a strong non-Archimedean detection statistic. It is mainly a hierarchy-ordered frequency score. It does not encode:

- likelihood ratio or effect size;
- statistical confidence for branch excess;
- parent-child residual deviation;
- conditional dependence among fields;
- temporal interval optimization;
- branch-local contamination significance;
- multiple-testing correction over tree nodes;
- calibration under random/reversed hierarchy nulls.

The p-adic encoding is valid as a way to represent prefix paths, but the current scoring rule does not exploit enough mathematical structure to survive fair controls.

## 3. Diagnostic evidence: current score collapses to rarity/entropy

Official IEEE-CIS block diagnostics from existing artifacts:

```text
IEEE blocks: 96
Correlation with held-out block positive_rate:
positive_rate                            1.000000
p_adic_multiresolution_energy_cusum      0.220218
reversed_hierarchy_energy_cusum          0.209802
random_hierarchy_energy_cusum_seed_23    0.209672
flat_tuple_rarity_cusum                  0.205438
transaction_count_signal                 0.082670
category_entropy_temporal                0.012555
p_adic_multiresolution_energy           -0.054572
flat_tuple_rarity                       -0.154407

corr(p_adic_energy, flat_tuple_rarity)       = 0.9522249603
corr(p_adic_energy, category_entropy)        = 0.9451573447
corr(p_adic_energy, random_hierarchy_cusum)  = 0.3485536989
```

Brutal interpretation: raw p-adic multiresolution energy is almost the same information as flat tuple rarity and category entropy. The temporal CUSUM gives a small surveillance-like shape, but controls reproduce it.

## 4. Diagnostic evidence: hierarchy order selection is stable but not enough

The existing train-only hierarchy-selection artifact contains all 120 permutations of the five IEEE-CIS categorical columns.

Artifact:

```text
outputs/p_adic_ieee_cis_official/metrics/p_adic_ieee_cis_hierarchy_selection.csv
```

Summary:

```text
count 120
mean validation AUPRC 0.073753
std  validation AUPRC 0.016147
min  validation AUPRC 0.045266
max  validation AUPRC 0.104246
```

Top train-validation order:

```text
DeviceType|card6|card4|ProductCD|P_emaildomain
validation AUPRC 0.104246
outer test AUPRC 0.084503
outer test ROC-AUC 0.701107
```

A small outer-test check of the top and bottom validation orders showed strong correlation between inner validation and outer test across those inspected orders:

```text
correlation(inner_val_auprc, outer_test_auprc) = 0.9926738328
```

This means hierarchy order has some consistent effect. But the best order still produces weak test AUPRC and does not beat strong baselines or later hierarchy-order controls in the block-surveillance audit. Stable weak signal is not a Q1 claim.

## 5. Diagnostic evidence: the hierarchy is not a true semantic tree

Fast structural nesting diagnostics on the first 100,000 official IEEE-CIS temporal-train rows:

Best/current order:

```text
ORDER DeviceType|card6|card4|ProductCD|P_emaildomain

depth=1 DeviceType: categories=3, top_frac=0.597, entropy=1.334
depth=2 card6: parents=3, mean_children=3.67, max_children=4, H(child|parent)=0.811
depth=3 card4: parents=11, mean_children=2.82, max_children=5, H(child|parent)=1.085
depth=4 ProductCD: parents=31, mean_children=2.87, max_children=5, H(child|parent)=0.860
depth=5 P_emaildomain: parents=89, mean_children=14.67, max_children=46, H(child|parent)=2.624
```

Original pipeline order:

```text
ORDER ProductCD|card4|card6|P_emaildomain|DeviceType

depth=1 ProductCD: categories=5, top_frac=0.569, entropy=1.764
depth=2 card4: parents=5, mean_children=3.80, max_children=5, H(child|parent)=1.092
depth=3 card6: parents=19, mean_children=2.05, max_children=3, H(child|parent)=0.747
depth=4 P_emaildomain: parents=39, mean_children=19.18, max_children=46, H(child|parent)=2.642
depth=5 DeviceType: parents=748, mean_children=1.75, max_children=3, H(child|parent)=0.467
```

Worst inspected order:

```text
ORDER P_emaildomain|card4|card6|ProductCD|DeviceType

depth=1 P_emaildomain: categories=60, top_frac=0.363, entropy=3.007
depth=2 card4: parents=60, mean_children=3.17, max_children=5, H(child|parent)=1.153
depth=3 card6: parents=190, mean_children=1.70, max_children=3, H(child|parent)=0.831
depth=4 ProductCD: parents=323, mean_children=2.32, max_children=4, H(child|parent)=1.255
depth=5 DeviceType: parents=748, mean_children=1.75, max_children=3, H(child|parent)=0.467
```

Brutal interpretation: these are nested categorical combinations, not an externally justified taxonomy. A reviewer can reasonably say the p-adic tree is arbitrary. The method needs either an external hierarchy/taxonomy dataset or a statistical tree-scan formulation that treats the tree as an auditable candidate structure, not as a semantic truth.

## 6. Implementation/data-flow faults found

### 6.1 CSE-CIC timestamp unit bug

The CSE-CIC external diagnostic parsed timestamps as `datetime64[us]`, then divided raw integer values by `1e9`, which produced timestamps around `1519892` instead of Unix seconds around `1519892231`.

Observed:

```text
Timestamp: 01/03/2018 08:17:11
astype int64 raw: 1519892231000000
seconds by //1e9: 1519892
correct timestamp(): 1519892231
```

Ordering was preserved, so chronological block assignment was likely not invalidated, but any manuscript-grade CSE run must fix timestamp conversion and rerun from raw official files.

### 6.2 Transductive control issue in CSE block context

The CSE `isolation_forest_block_context` control was fit on held-out block features. That is acceptable only if explicitly labeled as a transductive unsupervised context baseline. It is not a leakage-free train-only baseline. Future gates must separate:

- train-calibrated unsupervised baseline;
- held-out/transductive context baseline;
- supervised baseline.

### 6.3 `encode_frame` custom unknown-category error is partially unreachable

In `encoding.py`, `digits = digits.astype(int)` occurs before the later `digits.isna()` custom error branch. With standard maps this is usually avoided by `OTHER_TOKEN`, but if a caller provides a digit map without an `OTHER_TOKEN`, pandas can raise before the intended custom diagnostic. This is a robustness issue, not the reason Q1 gates failed.

### 6.4 Hierarchy-order control naming inconsistency

In `ieee_pipeline.py`, `random_hierarchy_order_control` actually uses `reversed_spec`, not a random order. This is a naming/audit clarity issue in the older raw transaction-level audit. Later multiresolution audit has explicit reversed and random hierarchy-order controls. Not a rescue path.

## 7. No-code exploratory alternatives already tested on IEEE-CIS

These were diagnostic terminal experiments only; no source code was written and no manuscript claim is allowed from them.

### 7.1 Prefix log-likelihood / branch excess scan

Best exploratory variants:

```text
supervised_prefix_lift_mean_d4: AUPRC 0.338303, ROC-AUC 0.618028
supervised_prefix_lift_mean_d5: AUPRC 0.331915, ROC-AUC 0.607887
prefix_llr_top10_d4:            AUPRC 0.259827, ROC-AUC 0.532958
```

These did not beat existing p-adic temporal CUSUM or strong controls. Simple branch LLR is not enough by itself.

### 7.2 Distributional change statistics

Best exploratory variants:

```text
cusum_js_train_d5: AUPRC 0.341972, ROC-AUC 0.584225
cusum_js_train_d4: AUPRC 0.325432, ROC-AUC 0.557746
cusum_js_train_d2: AUPRC 0.321009, ROC-AUC 0.519718
```

Again, not enough.

## 8. Relevant research alternatives found

### 8.1 Maximally divergent intervals

Paper:

```text
Erik Rodner et al., "Maximally Divergent Intervals for Anomaly Detection"
arXiv:1610.06761
```

Abstract-relevant point: detect anomalous intervals in multivariate time series by maximizing KL divergence between the distribution inside and outside an interval. This is much closer to a signal-processing contribution than per-event prefix rarity.

### 8.2 Mixed graphical model anomaly localization

Paper:

```text
Romain Laby, François Roueff, Alexandre Gramfort,
"Anomaly Detection and Localisation using Mixed Graphical Models"
arXiv:1607.05974
```

Abstract-relevant point: heterogeneous categorical/quantitative model learned on normal data; temporal CUSUM using conditional likelihood ratio per variable; localizes variables involved in anomalies. This directly addresses a core fault of current prefix rarity: it ignores conditional structure.

### 8.3 Bayesian online changepoint detection

Paper:

```text
Ryan P. Adams, David J. C. MacKay,
"Bayesian Online Changepoint Detection"
arXiv:0710.3742
```

Useful as a temporal evidence/calibration route, especially if categorical branch counts are modeled with Dirichlet-multinomial predictive likelihoods.

### 8.4 Fast subset scan / tree scan statistics

Crossref returned reputed scan-statistic literature:

```text
Neill, "Fast Subset Scan for Spatial Pattern Detection"
Journal of the Royal Statistical Society Series B, 2012
DOI: 10.1111/j.1467-9868.2011.01014.x

"Fast subset scan for multivariate event detection"
Statistics in Medicine, 2013
DOI: 10.1002/sim.5675

"Calibrated Nonparametric Scan Statistics for Anomalous Pattern Detection in Graphs"
AAAI, 2022
DOI: 10.1609/aaai.v36i4.20339
```

These support the redesign direction: scan over candidate subsets/nodes/intervals with calibrated likelihood or nonparametric scores.

## 9. Only defensible redesign path

The current prefix-rarity method should be deprecated as the main contribution.

The best Q1/SPL route is:

```text
P-adic Tree-Scan CUSUM for Hierarchical Categorical Event Streams
```

The p-adic encoding remains only as a compact index for tree prefixes. The actual statistic must be a scan statistic over p-adic balls/prefix nodes and time intervals.

### Proposed mathematical object

Given train-normal categorical event stream and hierarchy/path encoding, define for every prefix node `v` and temporal block or interval `I`:

```text
O(I, v) = observed count of test events in interval I falling under prefix node v
E(I, v) = |I| * train_normal_probability(v)
```

Then compute a one-sided log-likelihood ratio or Dirichlet-multinomial posterior surprise:

```text
LLR(I, v) = max_{q > p_v} [ O log(q/p_v) + (|I|-O) log((1-q)/(1-p_v)) ]
```

where `p_v` is estimated from train-normal data with smoothing.

The surveillance statistic is a penalized scan:

```text
S(I) = max_{v in p-adic tree} [ LLR(I, v) - penalty(depth(v), support(v)) ]
```

or a calibrated sum over significant nodes:

```text
S(I) = sum_{v: p_value(I,v) <= alpha_tree} residual_LLR(I,v)
```

Then run CUSUM/EWMA over `S(I)` or directly scan intervals.

### Required controls

Must beat all of:

- flat tuple scan statistic;
- entropy/count signal;
- random hierarchy-order tree scan;
- reversed hierarchy tree scan;
- per-column marginal scan;
- train-calibrated Isolation Forest or simple unsupervised context baseline;
- strong supervised row-level baselines disclosed as context.

### Required theoretical contribution

At minimum, prove/provide:

1. Within-level digit relabeling invariance.
2. Branch-local contamination separation: if contamination raises probability mass in a true prefix branch by `delta`, then the p-adic tree scan has expected LLR growth `Omega(n delta^2 / p_v)` under standard approximations.
3. Flat rarity failure mode under dilution: if anomalous mass is spread across many exact tuples sharing a prefix, exact tuple rarity loses power while prefix-node scan aggregates power.
4. Random hierarchy failure mode: if contamination respects the true tree, random hierarchy spreads the affected mass across many nodes, lowering max scan power in expectation.

Without this theory, the method is just another empirical detector and will not be Q1.

## 10. Current decision

Do not write more production code for prefix rarity.

Before implementation, the next concrete step should be a mathematical specification and preregistered protocol for `P-adic Tree-Scan CUSUM`, including exact formulas, controls, pass/fail gates, and tests to write first.

Implementation should start only after this spec is fixed.

## 11. Blockers / needs

No user input is needed for the next step if we continue on IEEE-CIS + existing CSE-CIC data.

User input will be needed if we require ToN_IoT or BoT-IoT from official UNSW sources, because official download access may require browser/session/manual steps.

## 12. Brutal bottom line

The implementation has some fixable audit bugs, but the main failure is mathematical: prefix rarity is too weak and too close to flat rarity/entropy. A Q1 route requires replacing it with a calibrated tree/interval scan statistic plus a theorem. If that redesign fails controls too, this project should be retargeted or abandoned for SPL/Q1 detector claims.
