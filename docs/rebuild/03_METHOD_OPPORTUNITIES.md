# 03 Method Opportunities — Rebuild Design Space

Created: 2026-06-02T16:33:10Z

## Core design doctrine

The rebuild must not optimize for flattering results. It must optimize for claims that survive peer review.

Therefore every method must answer:

1. What confound does it beat?
2. What null model does it survive?
3. What dataset does it generalize to?
4. What negative result would falsify the claim?

## Primary method direction: local motif-null excess

### Hypothesis

Illicit entities/transactions exhibit local higher-order structure that exceeds what degree/activity alone predicts.

### Unit of analysis

Prefer local units over global timesteps:

- transaction node;
- address/account node;
- k-hop egonet;
- temporal ego-window;
- suspicious connected component;
- transaction burst window.

### Features

For each unit/window:

- raw local motif counts: cycles, feed-forward/chain patterns, fan-in/fan-out, reciprocation, 030C-like circular structures;
- normalized motif rates per edge/node count;
- degree-preserving local motif z-scores;
- ER/edge-count local motif z-scores;
- activity controls: degree, in/out degree, edge count, amount stats, time/block index;
- optional spectral summaries: local entropy, local Laplacian/VNE-like features;
- optional temporal deltas: feature_t+1 - feature_t.

### Null models

Required:

- activity/size residualization;
- degree-preserving edge swaps within relevant temporal window;
- label permutation;
- time-block permutation where valid;
- negative controls using random motif projections.

### Metrics

- AUROC and AUPRC for illicit unit ranking;
- precision@k for investigation workload;
- calibration if probabilities are produced;
- bootstrap CI;
- permutation p;
- paired delta against strongest simple baseline.

## Secondary direction: temporal transition / stochastic increment audit

### Hypothesis

Motif-null feature changes predict illicit-density increases or future illicit labels beyond activity drift.

### Avoid old failure

The old global Elliptic change-point task showed graph-size delta was stronger. New design must use local/entity transitions and rolling splits.

### Candidate targets

- next-window illicit-neighborhood increase;
- future suspicious transaction count around entity;
- transition from low-risk to high-risk local region;
- label emergence under time-sorted evaluation.

### Baselines

- activity delta;
- degree delta;
- amount delta;
- time-only trend;
- previous label density;
- graph-size/snapshot-size delta.

## Optional direction: convex-envelope audit

Use only if local motif-null features show signal.

Question:

> Do illicit local neighborhoods sit outside the convex envelope of licit/baseline motif-null neighborhoods?

Methods:

- low-dimensional PCA/UMAP only for visualization, not primary metric;
- convex-hull boundary exposure in 2D/3D audited feature space;
- distance-to-baseline-envelope;
- compare against graph-size/activity-only envelope.

Risk:

- high-dimensional hulls are unstable;
- outliers dominate;
- small samples can overfit.

## Optional direction: ultrametric / p-adic-inspired hierarchy audit

Use the word “ultrametric” unless a true p-adic construction is mathematically justified.

Question:

> Do illicit units form distinct branches in a hierarchy built from null-adjusted motif features?

Methods:

- build hierarchy from motif-null features, not arbitrary IDs;
- dendrogram-derived ultrametric distance;
- distance to licit baseline cluster;
- branch enrichment test;
- compare with Euclidean/cosine and graph-size-only hierarchies.

Risk:

- can look decorative;
- must be compared against ordinary clustering;
- no raw p-adic arithmetic on wallet IDs.

## Optional direction: stochastic process / SDE audit

Use interpretable stochastic diagnostics before neural SDEs.

Question:

> Are motif-null increments statistically surprising under a baseline stochastic process, and do those surprises align with future illicit activity?

Methods:

- rolling z-score of local motif-null increments;
- OU-like residual surprise;
- Brownian-bridge/hitting-threshold audit;
- neural SDE only if many temporal sequences exist.

Risk:

- Elliptic aggregate has too few timesteps for learned SDEs;
- stochastic calculus is not novelty by itself;
- can become ornament rather than evidence.

## Baseline suite required for any method

Simple baselines are not optional. They are the reviewer’s first blade.

- degree/in-degree/out-degree;
- edge count / local graph size;
- transaction amount/count features;
- time/block index;
- PageRank;
- k-core;
- clustering coefficient / reciprocity;
- GraphSAGE/GCN/GAT if feasible;
- Isolation Forest / logistic regression / XGBoost on baseline features;
- random labels and random features.

## Model hierarchy

Do not start with the most complex model.

1. Feature-only logistic regression / random forest / XGBoost.
2. Null-adjusted motif score models.
3. Temporal local feature models.
4. GNN baselines.
5. Optional neural/stochastic/geometric branches.

Q1 reviewers prefer a method that beats strong simple baselines over a deep model that hides confounds.

## Testing doctrine

Use strict TDD once building starts.

First tests should enforce:

- sorted temporal transitions;
- no leakage across future edges;
- local egonet extraction semantics;
- motif count correctness on tiny directed fixtures;
- degree-preserving null preserves degree sequence;
- artifact schemas and manifest registration;
- claim table marks negative results as valid, not failed.

## Build-start gate

Do not start implementation until these are ready:

1. dataset cards for selected datasets;
2. exact task definitions;
3. baseline list;
4. artifact schema;
5. TDD test plan;
6. paper claim table skeleton.
