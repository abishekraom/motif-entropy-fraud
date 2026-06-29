# 04 Rebuild Blueprint — Start Point Before Coding

Created: 2026-06-02T16:33:10Z

## Current workspace state

Archived legacy project:

- `archive/legacy_pre_rebuild_20260602T163135Z/`

Active root after cleanup:

- `README.md`
- `pyproject.toml` retained temporarily
- `data/elliptic_plusplus/`
- `docs/rebuild/`
- `archive/`

The active root is intentionally clean. The old `src/`, `tests/`, `outputs/`, `paper/`, `R/`, `results/`, and generated clutter are archived.

## Rebuild mission

Build a Q1-grade, reproducible, confounding-aware fraud-graph surveillance framework centered on local/temporal higher-order structure, not global CMS detector superiority.

## Paper-grade contribution target

Primary contribution:

- local and temporal motif-null fraud-graph audit framework;
- explicit confound ladder;
- multi-dataset validation;
- negative-result-safe claim discipline;
- reproducible artifact pipeline.

Secondary contribution if evidence supports it:

- local motif-null excess improves illicit ranking beyond degree/activity baselines.

Fallback contribution if evidence is negative:

- rigorous benchmark showing where motif/higher-order graph signals collapse under realistic controls.

## Proposed new repository structure

```text
motif-entropy-fraud/
  README.md
  pyproject.toml
  data/
    elliptic_plusplus/
    external/                 # downloaded/scouted datasets, not committed if repo later initialized
  docs/
    rebuild/
    dataset_cards/
    literature/
  src/
    motif_fraud/
      data/
      motifs/
      nulls/
      features/
      baselines/
      evaluation/
      pipeline/
      publication/
  tests/
    test_data_contracts.py
    test_local_egonets.py
    test_motif_fixtures.py
    test_null_models.py
    test_temporal_splits.py
    test_artifact_manifest.py
    test_claim_discipline.py
  outputs/
    manifests/
    tables/
    figures/
    metrics/
  paper/
    tables/
    figures/
```

## Build phase 1 — Data contracts and task definitions

Strict TDD tests first:

1. Elliptic loader returns nodes/transactions/edges/classes/time without leakage.
2. Unknown labels are handled explicitly.
3. Temporal splits are sorted and future edges do not leak into train features.
4. Local egonet extraction is deterministic and bounded.
5. Dataset card metadata is loaded into manifest.

Deliverables:

- `docs/dataset_cards/elliptic.md`
- `src/motif_fraud/data/elliptic.py`
- first manifest schema

## Build phase 2 — Motif fixtures and local feature extraction

Strict TDD tests first:

1. Tiny directed graph with known cycle/chain/fan motifs.
2. Local egonet motif counts match scalar reference implementation.
3. Feature normalization by edge/node count works.
4. Output schema is stable.

Deliverables:

- local motif feature table for Elliptic units;
- fixture-based correctness tests.

## Build phase 3 — Null models and confound baselines

Strict TDD tests first:

1. Degree-preserving null preserves in/out degree.
2. ER null preserves edge count in window.
3. Null z-score handles zero variance without fake signal.
4. Baseline feature table includes degree/activity/time controls.

Deliverables:

- null-adjusted local motif features;
- baseline comparison table.

## Build phase 4 — Evaluation and claims

Strict TDD tests first:

1. AUROC/AUPRC/precision@k computed correctly.
2. Bootstrap confidence intervals reproducible by seed.
3. Permutation p-values valid and seed-stable.
4. Claim table accepts negative results.
5. Artifact manifest records all metrics/tables/figures.

Deliverables:

- table1_dataset_summary;
- table2_baselines;
- table3_local_motif_null_results;
- table4_external_validation once second dataset is acquired.

## Build phase 5 — External datasets

Before implementation:

- verify DGraph/DGraphFin source;
- verify Ethereum/AML dataset source;
- create dataset cards;
- write loader tests from dataset contracts.

No post-hoc tuning across external datasets.

## Immediate pre-build tasks still open

1. Verify official DGraphFin download/access/license.
2. Verify Ethereum phishing/scam graph dataset source.
3. Verify AML synthetic typology dataset source.
4. Create dataset card docs.
5. Decide exact first task:
   - entity/node illicit ranking on Elliptic;
   - local egonet motif excess;
   - temporal rolling split.

## Non-negotiables

- No detector-superiority claim without beating degree/activity baselines with statistical support.
- No early-warning claim without clean temporal onset definition.
- No neural SDE/GNN-first approach before simple baselines and null models.
- No hidden post-hoc score inversion.
- No fabricated git state; current folder is not a git repository.
- No code changes in build phase without failing tests first.
