# Fact-backed next steps toward an IEEE SPL/Q1-level p-adic fraud/surveillance paper

Date: 2026-06-09

## Executive verdict

The current IEEE-CIS p-adic empirical story is not IEEE SPL/Q1-ready. The package is reproducible, but the central empirical claim failed strong controls:

- raw p-adic IEEE-CIS AUPRC: 0.08450;
- LightGBM compact tabular AUPRC: 0.49547;
- rich p-adic features did not improve the best strong model;
- temporal p-adic CUSUM has a small positive point estimate over flat CUSUM, but the bootstrap CI crosses zero;
- branch signatures trade higher recall/coverage for lower precision/lift than flat tuple controls.

So the next work must create new evidence or new theory. Polishing the current manuscript will not make it Q1/SPL-grade.

## What IEEE SPL actually requires, based on retrieved IEEE pages

Source checked by local HTTP retrieval:

- `https://signalprocessingsociety.org/publications-resources/ieee-signal-processing-letters`
- `https://signalprocessingsociety.org/publications-resources/information-authors`

Relevant facts from the IEEE Signal Processing Society pages:

1. IEEE Signal Processing Letters is for rapid dissemination of original, cutting-edge ideas and timely, significant contributions in signal, image, speech, language, and audio processing.
2. A Signal Processing Letter is five pages in two-column format: at most four pages of technical content plus one page of references.
3. IEEE explicitly says the lean format is meant to promote ideas, not sacrifice rigor.
4. SPL allows supplementary material and an additional page for reproducibility information.
5. The author information page says manuscripts must be in scope and novel; a manuscript can be immediately rejected if it lacks novelty, for example if it is a straightforward combination of well-established repeatable theories/algorithms in a known field.
6. The author information page also flags insufficient experimental data as an immediate-rejection risk.
7. IEEE Xplore can publish supplemental datasets, code, and software or README links, and authors are encouraged to provide files that recreate figures.

Implication for this project:

- A weak detector benchmark cannot carry SPL.
- A compact signal-processing operator plus rigorous controls might.
- The paper must fit in four technical pages, so the central contribution has to be sharp: one operator, one theorem or proposition if possible, two real datasets max, clean figures/tables, and a reproducibility page.

## Prior-art / novelty facts from quick academic search

Local arXiv API searches performed:

- `p-adic fraud detection`
- `ultrametric anomaly detection`
- `hierarchical categorical anomaly detection`
- `categorical fraud detection hierarchy`
- `transaction fraud temporal surveillance anomaly detection`
- `prefix tree anomaly detection categorical data`
- `hierarchical anomaly detection categorical data`

Observed signal:

- Exact p-adic + fraud/anomaly work appears sparse/noisy in arXiv search results.
- However, adjacent anomaly/fraud work is active: tabular anomaly detection with LLMs, graph fraud detection, temporal transaction models, categorical anomaly detection, explainable healthcare-insurance anomaly detection, and network-intrusion datasets/methods.
- Semantic Scholar search surfaced a 2025 open-access BMC paper: `Explainable unsupervised anomaly detection for healthcare insurance data`, DOI `10.1186/s12911-024-02823-6`, using categorical embeddings, unsupervised anomaly detection, and SHAP for healthcare insurance anomaly/fraud workflows. Its data were not public; the PMC text says the data are available from Christian Health Insurance Fund under restrictions and are not publicly available.

Implication:

- Novelty cannot be claimed as simply `fraud anomaly detection with categories`.
- The defensible novelty has to be narrower and more mathematical/signal-processing-specific: e.g., a non-Archimedean multiresolution streaming statistic over categorical event streams with provable invariance/separation and empirical controls.

## Candidate real/reputed datasets checked

### 1. IEEE-CIS Fraud Detection

Source checked:

- `https://www.kaggle.com/c/ieee-fraud-detection`

Local official data already exists:

- `D:/motif-entropy-fraud/ieee-fraud-detection`

Status:

- Best for continuity and current artifacts.
- But current p-adic variants failed Q1 gates on it.
- Use it as Dataset 1 only if the new method is genuinely different, preferably theory-backed temporal signal processing.

### 2. UNSW-NB15

Source checked:

- `https://research.unsw.edu.au/projects/unsw-nb15-dataset`

Retrieved facts:

- Created at UNSW Canberra Cyber Range using IXIA PerfectStorm.
- Hybrid of real modern normal activities and synthetic contemporary attack behaviours.
- Captured 100 GB raw traffic.
- Nine attack types: Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode, Worms.
- 49 features plus class label.
- Total records: 2,540,044 across four CSV files.
- Official train/test partition: 175,341 training records and 82,332 testing records.

Assessment:

- Reputed and official academic source.
- Has categorical network fields, attack taxonomy, service/protocol/state structure.
- But some attack traffic is synthetic/generated. It is acceptable as a cybersecurity benchmark if described honestly, but it is not pure real-world fraud.
- Strong candidate for external validation if the paper pivots from transaction fraud to categorical event-stream intrusion/anomaly surveillance.

### 3. CSE-CIC-IDS2018

Source checked:

- `https://www.unb.ca/cic/datasets/ids-2018.html`

Retrieved facts:

- Canadian Institute for Cybersecurity / Communications Security Establishment dataset.
- Built to evaluate intrusion-detection systems with diverse and comprehensive benchmark data.
- Includes attack profiles such as brute force, DoS/DDoS, web attack, infiltration, botnet, etc.
- License text on page allows redistribution/republishing/mirroring with citation and AWS link.
- Official page provides AWS sync download instructions.

Assessment:

- Reputed official cybersecurity benchmark.
- Signal-processing fit is stronger than card-fraud because it is event/traffic surveillance.
- Hierarchical labels/attack families exist, but raw flow features may not naturally encode a clean external categorical taxonomy unless we define one carefully.
- Candidate Dataset 2 if we want robust cross-domain surveillance evidence.

### 4. CIC-IDS2017

Source checked:

- `https://www.unb.ca/cic/datasets/ids-2017.html`

Retrieved facts:

- Public CIC dataset with benign and common attacks resembling real-world data.
- Includes PCAPs and CSV machine-learning files.
- Page notes labeled flows with timestamps, source/destination IPs, ports, protocols, and attack labels.

Assessment:

- Reputed, but older and heavily benchmarked.
- Useful as secondary validation but probably weaker than CSE-CIC-IDS2018 or CICIoT2023 for novelty.

### 5. ToN_IoT

Source checked:

- `https://research.unsw.edu.au/projects/toniot-datasets`

Retrieved facts:

- New generation Industry 4.0 / IoT / IIoT datasets from UNSW Canberra.
- Heterogeneous data sources: IoT/IIoT telemetry, OS datasets, network traffic datasets.
- Realistic large-scale network designed at UNSW Canberra Cyber Range and IoT labs.
- Includes raw datasets, processed datasets, train/test datasets, feature descriptions/statistics, and security-event ground truth timestamps.
- Proposed uses include intrusion detection, threat intelligence, malware detection, fraud detection, privacy preservation, digital forensics, adversarial ML, and threat hunting.

Assessment:

- Strongest dataset candidate if we pivot from transaction fraud to hierarchical categorical event-stream surveillance.
- Heterogeneous sources and security-event timestamps are attractive for a multiresolution temporal signal-processing paper.
- Need download and schema audit before claiming suitability.

### 6. BoT-IoT

Source checked:

- `https://research.unsw.edu.au/projects/bot-iot-dataset`

Retrieved facts:

- Created in UNSW Cyber Range Lab.
- Realistic network environment with normal and botnet traffic.
- Includes original PCAP, generated argus files, and CSV files.
- Files separated by attack category and subcategory.
- PCAP size: 69.3 GB; more than 72 million records.
- Extracted flow traffic CSV size: 16.7 GB.
- Includes DDoS, DoS, OS/service scan, keylogging, and data-exfiltration attacks.
- 5% subset: about 3 million records and about 1.07 GB.
- Free use for academic research purposes noted on source page.

Assessment:

- Good hierarchy candidate because attacks are organized by category/subcategory/protocol.
- Large enough to be credible; subset manageable.
- Cybersecurity/signal-processing fit is better than fraud-only framing.

### 7. Public healthcare claims anomaly/fraud

Source checked:

- `https://pmc.ncbi.nlm.nih.gov/articles/PMC11720628/`

Retrieved facts:

- Healthcare insurance anomaly detection is active and high-stakes.
- The BMC 2025 paper uses categorical embeddings, unsupervised anomaly detection, and SHAP.
- Data are restricted/not publicly available from the Christian Health Insurance Fund.

Assessment:

- Scientifically attractive because diagnosis/procedure/provider hierarchy is real.
- Not currently usable unless a public official claims dataset is found or Lust obtains access.
- Do not build primary empirical claims on inaccessible/private data.

## The honest route to Q1/SPL

There are only two credible routes. Everything else is polishing.

### Route 1: Theory-led SPL paper, with IEEE-CIS + one cyber dataset as validation

This is the route I recommend.

Core thesis:

> A p-adic/ultrametric categorical event stream can be represented as a rooted prefix tree, and fraud/intrusion surveillance can be done with a compact multiresolution prefix-energy or prefix-CUSUM operator. The contribution is the operator and its control discipline, not raw transaction-level SOTA detection.

What must be new:

1. Define a real operator, not a collection of features:
   - event `x_t` maps to hierarchy path `h(x_t)`;
   - train-only prefix measure `P_train(prefix)`;
   - per-depth surprise/residual signal `s_l(t)`;
   - block-level multiresolution energy `E_b = sum_l w_l phi(s_l in block b)`;
   - streaming CUSUM/EWMA over residualized multiresolution signal;
   - optional p-adic Haar/wavelet contrast over tree nodes.

2. Add a theorem/proposition:
   - invariance to within-level category relabeling;
   - separation condition where a branch-local contamination changes prefix-depth energy more than flat marginal rarity;
   - or equivalence/nonequivalence to flat tuple rarity under stated assumptions.

3. Make negative results part of the story:
   - show why scalar p-adic rarity fails against LightGBM;
   - show why flat controls are mandatory;
   - show where the new operator is and is not useful.

Required empirical gates:

- Dataset 1: official IEEE-CIS, already local.
- Dataset 2: ToN_IoT, BoT-IoT, UNSW-NB15, or CSE-CIC-IDS2018, after schema/provenance audit.
- Pre-register hierarchy and metrics before external-dataset test.
- Proposed operator must beat best flat/reversed/random hierarchy temporal control on both datasets or pass a narrower theorem-validation criterion.
- Bootstrap CI for proposed-minus-best-control must be strictly positive for the headline metric on at least the primary surveillance task.
- If one dataset fails, claim becomes diagnostic/generalization-limited, not Q1 empirical win.

Why this can fit SPL:

- It is compact.
- It is signal-processing framed: categorical event stream -> multiresolution tree signal -> temporal surveillance statistic.
- It can include a theorem and two concise empirical figures.
- It uses reproducibility pages/code artifacts.

Risk:

- If the theorem is weak or the second dataset fails, SPL is still unlikely.

### Route 2: New official/reputed dataset where hierarchy is central, then pre-registered empirical win

This is the empirical route, but it is riskier because we cannot tune until success.

Best dataset candidates to audit first:

1. ToN_IoT
   - Strong heterogeneous source/timestamp structure.
   - Good for temporal surveillance.
2. BoT-IoT
   - Attack category/subcategory hierarchy is explicit.
   - Large, with manageable 5% subset.
3. CSE-CIC-IDS2018
   - Reputed benchmark, AWS download, redistribution/citation rules clear.
4. UNSW-NB15
   - Smaller official train/test CSVs, easier first external benchmark.

Pre-registered empirical gates before downloading/running:

- Primary task: temporal block alerting, not transaction/flow classification.
- Primary metric: AUPRC over temporal blocks or precision@fixed alert budget; choose one before test.
- Required controls:
  - flat tuple rarity CUSUM/EWMA;
  - entropy/count temporal controls;
  - reversed hierarchy order;
  - random hierarchy order;
  - random digit-map invariance sanity check;
  - Isolation Forest / LOF / OneClassSVM block-feature context if feasible;
  - supervised LightGBM block-level context, not necessarily the target to beat if the thesis is unsupervised surveillance.
- Required uncertainty:
  - paired bootstrap CI for proposed-minus-best-control;
  - time-block resampling or day/session resampling where appropriate.
- Pass gate:
  - proposed p-adic temporal operator beats all flat/hierarchy-order controls with strictly positive 95% CI on primary metric;
  - result repeats on IEEE-CIS and at least one external dataset;
  - figures 600 dpi;
  - claims table marks failures honestly.

If the dataset is not accessible through official/Kaggle/public links, stop and ask Lust to download it. Do not use unofficial mirrors for primary claims unless clearly marked development-only.

## Concrete next actions

### Step 0 — freeze current negative evidence

Already done in:

- `docs/rebuild/18_Q1_UPGRADE_RECURSION_RESULTS.md`

Do not rewrite it into positive prose.

### Step 1 — write a pre-registration doc before any new experiment

Create:

- `docs/rebuild/20_Q1_SPL_PREREGISTERED_GATES.md`

It should define:

- exact thesis;
- datasets eligible for primary claims;
- hierarchy construction rules;
- train/validation/test split rules;
- primary metric;
- controls;
- bootstrap procedure;
- pass/fail claim statuses;
- unsafe claims banned from manuscript.

### Step 2 — implement theory/operator test scaffolding first

Add tests before implementation:

- `tests/test_p_adic_multiresolution_operator.py`

Must test:

- within-level digit relabeling invariance;
- reversed hierarchy changes the statistic when hierarchy semantics matter;
- synthetic unit fixtures only for mathematical correctness, not empirical claims;
- artifact schema includes proposed, controls, CI, and claim_status;
- failure case is valid output.

### Step 3 — build the actual operator

Add:

- `src/motif_fraud/p_adic/multiresolution_operator.py`

Minimum operator outputs:

- per-depth prefix surprise;
- per-depth residual against train-only expected frequency;
- block-level p-adic energy;
- p-adic CUSUM/EWMA;
- flat tuple CUSUM/EWMA control;
- entropy/count controls;
- reversed/random hierarchy controls.

### Step 4 — rerun IEEE-CIS only once under the new preregistered gate

If it fails, stop the SPL empirical route and use the result as theorem/diagnostic support only.

If it passes, proceed to external dataset.

### Step 5 — pick one external dataset and ask Lust for download if needed

Recommended order:

1. ToN_IoT if the schema has usable timestamps and categorical event source/type/device fields.
2. BoT-IoT if attack category/subcategory/protocol hierarchy can be cleanly represented.
3. CSE-CIC-IDS2018 if AWS download is easiest and schema supports temporal block surveillance.
4. UNSW-NB15 if we need a smaller fast external check.

### Step 6 — only after two-dataset evidence, rewrite the SPL manuscript

The new paper should be titled/framed around signal processing, not fraud SOTA. Example safe title direction:

- `A Non-Archimedean Multiresolution Statistic for Categorical Event-Stream Surveillance`

Suggested 4-page technical layout:

1. Introduction: problem + why categorical hierarchy needs multiresolution stream statistics.
2. Method: p-adic prefix tree signal + operator + proposition.
3. Experiments: IEEE-CIS + cyber dataset, controls, metrics.
4. Discussion/limitations: where it beats controls, where supervised models still win, reproducibility.

## Bottom line

The fastest honest path to IEEE SPL/Q1 is not more IEEE-CIS tweaking. It is:

1. make the contribution a compact non-Archimedean multiresolution temporal operator;
2. support it with one small theorem/proposition;
3. pre-register controls and failure statuses;
4. validate on IEEE-CIS plus one official/reputed cybersecurity event-stream dataset;
5. require statistically positive control deltas before writing any strong claim.

If those gates fail, the result should be retargeted to a lower venue as a reproducibility/control-discipline paper. That is not defeat; it is honest science.
