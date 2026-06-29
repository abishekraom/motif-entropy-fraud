# 06 Build Validation Status

Created: 2026-06-02

## Build phase completed

Initial Q1 rebuild skeleton is implemented and validated.

This is not yet a full Q1 experiment. It is the first strict-TDD build slice:

- Elliptic data contract;
- temporal edge cutoff without future-node leakage;
- local egonet extraction;
- scalar motif fixtures;
- ER and degree-preserving local null primitives;
- paired permutation statistic;
- claim-discipline table;
- initial smoke-scale local motif-null audit pipeline.

## Validation commands actually run

```bash
pytest tests/test_claim_discipline.py -q && pytest -q && python -m motif_fraud.pipeline.reproduce_all
```

Verified output:

```text
tests/test_claim_discipline.py: 3 passed
full suite: 20 passed
reproduce_all: completed successfully
```

## Generated artifacts

```text
outputs/manifests/rebuild_manifest.json
outputs/metrics/sampled_local_features.csv
outputs/tables/table1_dataset_summary.csv/md
outputs/tables/table2_simple_baselines.csv/md
outputs/tables/table3_local_motif_null_results.csv/md
outputs/tables/table4_claim_discipline.csv/md
```

## Smoke audit result

From `outputs/tables/table3_local_motif_null_results.csv`:

- dataset: Elliptic Bitcoin
- task: sampled local node ranking
- effective sample nodes: 100
- null permutations: 8
- method: ER-null local motif score
- AUC: 0.7016
- AUPRC: 0.6565
- best simple baseline: center total degree
- best baseline AUC: 0.3684
- delta vs best simple baseline: 0.3332
- paired permutation p: 0.00498

Claim discipline:

`outputs/tables/table4_claim_discipline.csv` deliberately marks this as:

```text
diagnostic_or_insufficient_gain
```

Reason: it is only a single-dataset smoke sample. It is encouraging, but not publication-grade evidence yet.

## Brutal interpretation

This first local/egonet direction shows a promising smoke signal, unlike the old global CMS collapse. But it is not yet Q1 evidence.

Do not claim detector superiority yet.

The next build slice must add:

1. cached/scalable egonet extraction;
2. full-scale Elliptic local audit, not smoke sample;
3. bootstrap confidence intervals;
4. degree-preserving null local scores integrated into the pipeline;
5. precision@k / AUPRC reporting;
6. dataset cards and external dataset loader contract for DGraphFin or Ethereum scam/phishing data.
