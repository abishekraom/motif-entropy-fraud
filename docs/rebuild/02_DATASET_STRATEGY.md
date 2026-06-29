# 02 Dataset Strategy — Q1 Rebuild

Created: 2026-06-02T16:33:10Z

## Dataset principle

For Q1-level publication, the rebuild needs more than Elliptic global timestep ranking. It needs multiple datasets/tasks, clean splits, robust baselines, and external validation.

Minimum target:

1. One Bitcoin/cryptocurrency transaction dataset with public labels.
2. One non-Bitcoin or non-identical financial transaction graph dataset.
3. One external/generalization dataset or synthetic-but-realistic AML dataset for controlled ablations.

Do not tune a method on one dataset and then call the second dataset “external” after post-hoc score inversion or threshold tuning.

## Existing preserved data

Currently active in root:

- `data/elliptic_plusplus/`
  - `elliptic_bitcoin_dataset/elliptic_txs_features.csv`
  - `elliptic_bitcoin_dataset/elliptic_txs_edgelist.csv`
  - `elliptic_bitcoin_dataset/elliptic_txs_classes.csv`
  - `elliptic-data-set.zip`
  - `elliptic_plusplus.zip`
  - partial `Elliptic++ Dataset/AddrAddr_edgelist.csv...part`

Archived as old derived artifacts:

- `archive/legacy_pre_rebuild_20260602T163135Z/data/r_ready/`
- `archive/legacy_pre_rebuild_20260602T163135Z/data/dgraph_triad_data.npz`
- empty old placeholders for DGraph/ethereum/synthetic.

## Candidate datasets

### 1. Elliptic Bitcoin Dataset / Elliptic++

Status: already partially/mostly present.

Use case:

- node/transaction classification;
- temporal blocks;
- local neighborhood motif excess;
- rolling-origin validation;
- global aggregate only as a cautionary baseline, not the main task.

Strengths:

- canonical public crypto illicit-transaction dataset;
- temporal structure;
- already available locally;
- good for reproducibility and comparison.

Risks:

- known class imbalance;
- many unknown labels;
- global timestep illicit count is contaminated early;
- old global CMS was graph-size/degree confounded.

Rebuild use:

- Primary development dataset, but not sole evidence.
- Focus on local/entity-level features and temporal splits.

### 2. DGraph / DGraphFin

Status: old derived audit was archived; active dataset folder was empty. Need reacquisition or verified source.

Use case:

- financial fraud node classification / graph anomaly benchmark;
- external validation outside Bitcoin.

Strengths:

- large directed financial transaction graph benchmark;
- good for external validation if access is clean.

Risks:

- need to verify exact official source/license/access;
- old pre-specified motif aggregate was negative on DGraph snapshots;
- may not expose rich temporal/amount fields depending on version.

Rebuild use:

- External validation dataset.
- Use node/local features rather than global snapshot CMS.

### 3. Ethereum phishing / scam / illicit-address datasets

Potential sources to scout:

- XBlock Ethereum phishing/scam datasets;
- Ethereum transaction-network fraud datasets on Kaggle/GitHub;
- PhishTank/Etherscam-labeled address sets cross-linked with transaction graphs.

Use case:

- address-level illicit/phishing detection;
- local motif/flow features around addresses;
- cross-chain generalization from Bitcoin to Ethereum.

Strengths:

- different blockchain mechanics from Bitcoin;
- address-level local neighborhoods are natural;
- strong domain relevance.

Risks:

- label noise;
- crawling transaction graphs can be expensive;
- API/rate limits if not prepackaged;
- many datasets are stale, scraped, or license-unclear.

Rebuild use:

- Candidate third dataset if a clean package is found.

### 4. IBM / synthetic AML transaction monitoring datasets

Potential sources:

- IBM AML / anti-money-laundering transaction simulation datasets;
- AMLSim-derived datasets;
- SAML-D or other synthetic AML graph datasets.

Use case:

- controlled laundering typologies;
- motif specificity positive controls;
- ablation of laundering patterns, amounts, roles, and time.

Strengths:

- may include explicit laundering typologies;
- enables controlled ground truth;
- good for explaining motif types.

Risks:

- synthetic-only cannot carry final Q1 claim;
- must not replace real-data validation;
- dataset access/licensing must be verified.

Rebuild use:

- Controlled ablation and mechanistic positive control.

### 5. PaySim / IEEE-CIS / credit-card tabular fraud datasets

Use case:

- weak graph reconstruction only if sender/receiver or entity links exist.

Strengths:

- accessible;
- common fraud benchmarks.

Risks:

- often tabular rather than graph-native;
- graph construction may be artificial;
- weaker fit for motif/null graph paper.

Rebuild use:

- Lower priority. Use only if graph-native fields are available or as a non-graph baseline appendix.

## Recommended Q1 dataset plan

### Tier A — Must-have

1. Elliptic/Elliptic++ local node/transaction task.
2. DGraph/DGraphFin or equivalent real financial graph external validation.
3. Ethereum phishing/scam address graph OR AML synthetic typology dataset.

### Tier B — Stronger paper

4. Controlled AML synthetic typology benchmark with known motifs.
5. Cross-dataset transfer: train/tune on Elliptic, evaluate feature/baseline behavior on Ethereum/DGraph without post-hoc inversion.

## Split/evaluation requirements

Use these rules before any model is built:

1. Temporal splits when timestamps exist.
2. Rolling-origin validation for early-warning/change-point claims.
3. Node/edge leakage prevention: no future edges, no labels in features, no neighborhood leakage across temporal boundary.
4. Compare against simple baselines:
   - degree/in-degree/out-degree;
   - transaction count/activity volume;
   - amount statistics if available;
   - PageRank/k-core/clustering;
   - time/block index;
   - graph size/snapshot size;
   - GNN baseline if feasible.
5. Statistical reporting:
   - bootstrap confidence intervals;
   - label permutation p-values;
   - paired comparisons vs confound baselines;
   - multiple seeds for stochastic models;
   - external dataset table with negative results allowed.

## Dataset acquisition TODO before build

1. Verify DGraphFin official download/source/license.
2. Verify Ethereum graph dataset candidates and choose one with:
   - public labels;
   - transaction edges;
   - timestamps if possible;
   - clear license or academic use permission;
   - enough labeled positives.
3. Verify AML synthetic dataset availability and schema.
4. Write `docs/rebuild/dataset_cards/*.md` once sources are confirmed.
5. Only then create data loaders.

## Current dataset decision

The active rebuild starts with Elliptic/Elliptic++ only because it is already local. It must not end there. Q1 path requires at least one real external graph dataset and preferably one controlled typology dataset.
