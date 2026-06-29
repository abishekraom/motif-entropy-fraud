# P-adic Tree-Scan CUSUM Q1 specification and go/no-go decision

Date: 2026-06-09

Status: pre-implementation research/specification. No production source code has been changed by this document.

Constraints honored:

- No subagents.
- No synthetic empirical data for claims.
- Official/reputed datasets only.
- Negative results remain valid and must be marked diagnostic/failed.
- No post-hoc test tuning.

## 1. Decision summary

The current prefix-rarity p-adic method is not salvageable as a Q1/SPL empirical detector claim.

A defensible Q1/SPL path exists only if we pivot the contribution to a calibrated scan-statistic formulation:

```text
P-adic Tree-Scan CUSUM for Hierarchical Categorical Event Streams
```

This is not a minor tweak. It is a replacement of the scoring core.

The p-adic object becomes the tree/prefix-ball index. The actual detection statistic becomes a statistically calibrated likelihood-ratio / posterior-surprise scan over p-adic balls and temporal intervals.

## 2. Why this path is better than prefix rarity

Prefix rarity asks:

```text
Was this event prefix rare in normal training data?
```

The proposed tree-scan asks:

```text
Did any p-adic ball/prefix node accumulate significantly more mass in a held-out temporal interval than expected from normal training, after controlling for tree search, flat rarity, entropy, and random hierarchy order?
```

That is a materially stronger signal-processing/statistical problem.

It gives:

- an explicit alternative hypothesis;
- effect size through log-likelihood ratio;
- branch localization;
- interval localization;
- calibrated null controls;
- a possible theorem;
- a cleaner SPL-style compact method section.

## 3. Related work anchors

The redesign is positioned against these established methods, not invented in isolation.

### 3.1 Maximally divergent intervals

```text
Rodner et al., "Maximally Divergent Intervals for Anomaly Detection"
arXiv:1610.06761
```

Uses KL divergence between interval distribution and outside/background distribution. Our p-adic tree scan adapts this idea to categorical prefix balls and normal-train expectations.

### 3.2 Mixed graphical model CUSUM localization

```text
Laby, Roueff, Gramfort,
"Anomaly Detection and Localisation using Mixed Graphical Models"
arXiv:1607.05974
```

Uses conditional likelihood ratios and CUSUM for heterogeneous categorical/quantitative data. Our method must compete with or at least cite this because it addresses conditional structure ignored by prefix rarity.

### 3.3 Bayesian online changepoint detection

```text
Adams and MacKay,
"Bayesian Online Changepoint Detection"
arXiv:0710.3742
```

Gives the online changepoint framing. Optional extension: Dirichlet-multinomial predictive likelihood over tree-node counts.

### 3.4 Fast subset / scan statistics

```text
Neill, "Fast Subset Scan for Spatial Pattern Detection"
JRSS-B, 2012, DOI: 10.1111/j.1467-9868.2011.01014.x

Neill, McFowland, Zheng,
"Fast subset scan for multivariate event detection"
Statistics in Medicine, 2013, DOI: 10.1002/sim.5675

Wang, Neill, Chen,
"Calibrated Nonparametric Scan Statistics for Anomalous Pattern Detection in Graphs"
AAAI, 2022, DOI: 10.1609/aaai.v36i4.20339
```

These justify the subset/tree scan framing and calibration requirements.

## 4. Formal setup

Let events be ordered by time:

```text
e_1, e_2, ..., e_n
```

Each event has categorical fields:

```text
x_i = (x_i^{(1)}, ..., x_i^{(D)})
```

An ordered hierarchy `H = (h_1, ..., h_D)` maps each event to a path in a rooted tree. Equivalently, using p-adic digits:

```text
z_i = a_i0 + a_i1 p + ... + a_i,D-1 p^{D-1}
```

where each digit is a category code for one hierarchy level. A prefix node / p-adic ball at depth `d` is:

```text
B(v, d) = { z : z mod p^d = v }
```

Training data are split temporally. Normal training rows define the background distribution.

No held-out test labels are used for hierarchy selection, smoothing choice, thresholds, or model selection.

## 5. Primary statistic: p-adic tree likelihood-ratio scan

For a held-out temporal block or interval `I` and prefix node `v`:

```text
n_I      = number of events in interval I
O_{I,v} = number of events in interval I whose code lies in prefix ball v
p_v      = smoothed normal-train probability of prefix node v
E_{I,v} = n_I p_v
```

Use a one-sided binomial log-likelihood ratio for excess mass:

```text
LLR(I,v) = 0, if O_{I,v} <= E_{I,v}

LLR(I,v) = O_{I,v} log((O_{I,v}/n_I) / p_v)
         + (n_I - O_{I,v}) log(((n_I - O_{I,v})/n_I) / (1 - p_v)), otherwise.
```

Smoothing:

```text
p_v = (N_v + alpha_d) / (N_train_normal + alpha_d * K_d)
```

where:

- `N_v` is normal-train count of node `v`;
- `K_d` is number of observed train nodes at depth `d` plus an unknown bucket;
- `alpha_d` is fixed before test evaluation, default `alpha_d = 0.5` or `1.0`.

Candidate score for interval `I`:

```text
S_raw(I) = max_{v in T} LLR(I,v)
```

Depth/support-penalized version:

```text
S_pen(I) = max_{v in T} [ LLR(I,v) - lambda_depth log(K_d) - lambda_support 1{N_v < m_min} ]
```

Initial pre-registered recommendation:

```text
lambda_depth = 1.0
lambda_support = infinity for N_v < m_min
m_min = 20 normal-train events
```

This avoids spurious tiny-node wins.

## 6. Parent-child residual variant

To avoid simply rediscovering high-level volume shifts, define parent-conditioned excess:

```text
p_{v|parent(v)} = (N_v + alpha) / (N_parent(v) + alpha * children(parent(v)))
O_parent = O_{I,parent(v)}
E_cond = O_parent * p_{v|parent(v)}
```

Then compute the same one-sided LLR for child excess conditional on parent mass.

Conditional residual score:

```text
S_cond(I) = max_v LLR_cond(I,v)
```

This is important because reviewers will ask whether the method is only detecting volume/entropy changes rather than hierarchy-specific branch redistribution.

## 7. Interval scan / CUSUM layer

Two pre-registered temporal modes:

### Mode A: fixed equal-count blocks

Use equal-count held-out blocks, e.g. `B = 96` or `B = 128`, fixed before running.

For block `b`:

```text
s_b = S_pen(block_b)
```

CUSUM:

```text
C_b = max(0, C_{b-1} + s_b - median_train_calibration)
```

But because held-out test labels cannot calibrate the baseline, the CUSUM reference must be estimated from an inner validation split of training or from normal-train pseudo-blocks.

### Mode B: interval scan

For candidate intervals over held-out blocks:

```text
I = [b_start, b_end]
```

with length constraints:

```text
L_min <= |I| <= L_max
```

score:

```text
S_interval(I) = max_v LLR(I,v) - penalty(length, depth)
```

Recommended initial gate:

```text
L_min = 1 block
L_max = 8 blocks
```

No tuning after held-out evaluation.

## 8. Optional Bayesian/MDL variant

Dirichlet-multinomial posterior predictive surprise for depth `d`:

```text
- log P(counts_I,d | alpha + counts_train_normal,d)
```

Then compare this with:

- flat tuple Dirichlet-multinomial surprise;
- per-column marginal Dirichlet-multinomial surprise;
- random hierarchy depth surprise.

This can be framed as MDL/code-length excess:

```text
excess_code_length = L(block under train-normal tree model) - L(block under locally adapted tree model)
```

This is mathematically clean but may be slower and harder to fit into SPL. Keep it as secondary unless the LLR scan fails.

## 9. Primary claims allowed only if gates pass

A Q1/SPL empirical claim is allowed only if:

1. Proposed tree-scan AUPRC beats every mandatory control on official IEEE-CIS held-out temporal blocks.
2. Proposed tree-scan AUPRC beats every mandatory control on at least one external official/reputed dataset.
3. Bootstrap CI for proposed-minus-best-control AUPRC is strictly positive on both datasets.
4. `p_delta_le_zero <= 0.05` on both datasets.
5. The method also improves precision@alert-budget or recall@fixed-alert-budget, not only AUPRC.
6. Figures verify at >=600 dpi for manuscript artifacts.
7. Artifacts explicitly state `synthetic_data_used: false`.
8. Strong supervised row-level baselines are disclosed and not hidden.

If any of these fail, the claim status is diagnostic only.

## 10. Mandatory controls

Every implementation must include these controls before a Q1 claim:

### 10.1 Flat tuple scan

Use exact full-tuple categories as the candidate subset universe. Compute the same scan statistic. This tests whether p-adic aggregation adds anything beyond exact rare combinations.

### 10.2 Per-column marginal scan

Scan each categorical column independently. This tests whether the method is just marginal drift.

### 10.3 Reversed hierarchy tree scan

Reverse the hierarchy order and rerun the same tree scan.

### 10.4 Random hierarchy-order tree scan

Use at least 5 random permutations of hierarchy order, fixed seeds pre-registered.

### 10.5 Random digit-map invariance sanity check

Within-level digit relabeling should not change equality/prefix tree results. This is a sanity check, not a failure.

### 10.6 Entropy/count controls

Include category entropy, event/flow count, and simple rolling prevalence-like unsupervised proxies if labels are not used.

### 10.7 Train-calibrated unsupervised context baseline

Isolation Forest or robust covariance must be trained/calibrated on train/validation block features, not fit on held-out test blocks unless explicitly labeled transductive.

### 10.8 Strong supervised context baseline

For context only, not necessarily as the main unsupervised surveillance competitor:

- LightGBM/CatBoost/XGBoost row-level baseline on IEEE-CIS;
- block-aggregated supervised baseline if label budget is allowed.

## 11. Dataset plan

### Dataset A: official IEEE-CIS

Local official data exist:

```text
D:/motif-entropy-fraud/ieee-fraud-detection
```

Use:

- `TransactionDT` temporal order;
- `isFraud` labels only for evaluation and train-normal filtering;
- categorical hierarchy candidates from ProductCD, card4, card6, P_emaildomain, DeviceType;
- no Vxxx high-dimensional engineered features in the p-adic method, except supervised baseline context.

### Dataset B: CSE-CIC-IDS2018 from AWS Open Data / UNB-CIC

Official source:

```text
https://registry.opendata.aws/cse-cic-ids2018/
https://www.unb.ca/cic/datasets/ids-2018.html
```

Public S3 bucket:

```text
s3://cse-cic-ids2018/
```

Processed ML CSV files available from official AWS listing:

```text
352,368,373  Friday-02-03-2018_TrafficForML_CICFlowMeter.csv
333,723,605  Friday-16-02-2018_TrafficForML_CICFlowMeter.csv
382,840,456  Friday-23-02-2018_TrafficForML_CICFlowMeter.csv
4,054,925,350 Thuesday-20-02-2018_TrafficForML_CICFlowMeter.csv
107,842,858  Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv
375,945,899  Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv
382,636,202  Thursday-22-02-2018_TrafficForML_CICFlowMeter.csv
358,223,333  Wednesday-14-02-2018_TrafficForML_CICFlowMeter.csv
328,893,673  Wednesday-21-02-2018_TrafficForML_CICFlowMeter.csv
209,249,758  Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv
```

Total processed CSV size: ~6.89 GB. Local D: has ~454 GB free, so download is feasible.

Important fix required before any CSE run:

- convert timestamp using `.timestamp()` or divide raw datetime64 microseconds by `1e6`, not `1e9`.

CSE hierarchy candidates:

```text
Protocol -> dst_port_band -> Dst Port -> flow_flag_profile -> service/attack-family proxy if available
```

Do not use label-derived attack names inside the hierarchy for detection if that leaks target labels.

### Dataset C: ToN_IoT / BoT-IoT

Official UNSW pages confirm CSV/log availability but download links may require browser/manual access.

Use only if accessible from official UNSW source. If blocked, ask Lust to download.

## 12. Theorem sketch required for Q1/SPL

### Proposition 1: digit relabeling invariance

Any statistic depending only on equality of prefixes `z mod p^d` is invariant to bijective relabeling of digits within a fixed hierarchy level, provided the relabeling is applied consistently to train and test.

Reviewer implication: random digit-map equality is expected and must not be oversold as numeric p-adic digit semantics.

### Proposition 2: branch-local contamination separation

Assume normal probability of prefix node `v` is `p_v`, and in anomalous interval `I` the probability becomes `p_v + delta` with `delta > 0`.

For interval length `n_I`, expected LLR grows approximately:

```text
E[LLR(I,v)] ≈ n_I * KL(Bernoulli(p_v + delta) || Bernoulli(p_v))
           ≈ n_I * delta^2 / (2 p_v (1 - p_v))
```

Thus detection improves with interval length and contamination strength, and rare-but-supported branches can be detectable when sample size is sufficient.

### Proposition 3: exact tuple dilution failure mode

If contamination spreads over `M` exact tuples under the same prefix node `v`, each exact tuple has shift about `delta/M`. A flat tuple scan sees per-tuple LLR scaling approximately:

```text
n_I * (delta/M)^2
```

while the prefix scan aggregates mass and sees:

```text
n_I * delta^2
```

up to probability normalization. This is the theoretical reason p-adic prefix balls can beat flat tuple rarity.

### Proposition 4: random hierarchy power loss

If the true contamination is coherent under hierarchy `H`, random hierarchy permutations split the affected branch across multiple prefix nodes. Under mild dispersion assumptions, the maximum node-level delta is reduced, reducing expected max LLR.

This is the theorem needed to justify why random hierarchy controls should lose when the hierarchy is meaningful.

## 13. Go/no-go decision for implementation

Proceed to implementation only for the tree-scan redesign, not for prefix-rarity tweaking.

Implementation is scientifically justified if and only if the code is built to answer this pre-registered question:

```text
Does a calibrated p-adic prefix-ball tree scan detect branch-local temporal concentration better than flat tuple, marginal, entropy/count, and random/reversed hierarchy scan controls on official real event-stream datasets?
```

This is a legitimate Q1/SPL research question.

It is not guaranteed to pass. If it fails, the correct outcome is a diagnostic/failure paper or abandonment of SPL/Q1 detector claims.

## 14. Implementation start criteria

Before production implementation:

1. Write tests first.
2. Tests may use tiny constructed fixtures only for mathematical/unit invariance if labeled non-empirical. If avoiding all synthetic fixtures, tests must use small official IEEE-CIS slices.
3. Empirical tests must use official/reputed real data only.
4. The implementation must produce claims tables where failure is valid output.
5. No test may assert that the method wins empirically.
6. Tests must assert:
   - correct LLR formula;
   - train-only node probability estimation;
   - no held-out label leakage;
   - controls are registered;
   - figure DPI >=600 for manuscript figures;
   - claim status fails closed when controls win.

## 15. Immediate next implementation plan

Use strict TDD:

1. Add tests for tree-node count/probability estimation on official IEEE-CIS slice.
2. Add tests for binomial LLR numerical correctness.
3. Add tests for prefix-ball scan output schema.
4. Add tests for flat/reversed/random hierarchy controls registration.
5. Add tests for CSE timestamp conversion correctness using real downloaded CSE rows.
6. Implement minimal tree-scan module.
7. Run smoke audit on IEEE-CIS max_rows slice.
8. Run full IEEE-CIS audit.
9. Download/prepare full official CSE-CIC processed CSV set or ask Lust for ToN_IoT/BoT-IoT if CSE is insufficient.
10. Run external dataset audit.
11. Only then decide manuscript claim status.

## 16. Brutal conclusion

This is the best available Q1/SPL path. It is mathematically defensible because it has a real scan statistic and theorem sketch. It is empirically honest because it can fail closed under controls. It is not a guaranteed flattering result, but it is the only path that would not be scientifically fake.
