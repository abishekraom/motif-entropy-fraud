# 05 Build Start Plan — Strict TDD

Created: 2026-06-02T16:33:10Z

This is the point where coding should begin after Lust approves or edits the research direction.

## First build target

Build the Elliptic local-egonet motif-null pipeline.

Why first:

- Elliptic data is already local.
- Old global aggregate failed under confounds.
- Local motif-null excess is the strongest scientific opportunity.
- It creates reusable components for DGraph/Ethereum later.

## First TDD cycle

### RED 1: data contract

Create `tests/test_data_contracts.py` with tests that require:

- loader reads Elliptic classes/features/edges;
- exposes time/block field;
- maps labels into licit/illicit/unknown;
- returns directed edges without future leakage for a given cutoff;
- reports counts in a dataset summary object.

Run:

```bash
pytest tests/test_data_contracts.py -q
```

Expected: fail because no new loader exists.

### GREEN 1: minimal loader

Create:

- `src/motif_fraud/data/elliptic.py`
- `src/motif_fraud/data/contracts.py`

Implement only enough to pass the data-contract tests.

### RED 2: local egonet extraction

Create `tests/test_local_egonets.py` with tiny directed fixture:

- one center node;
- incoming/outgoing neighbors;
- edge direction preserved;
- time cutoff removes future edges;
- max-hop behavior deterministic.

### RED 3: motif scalar fixtures

Create `tests/test_motif_fixtures.py` with independent scalar oracle fixtures for:

- 3-cycle / 030C-like pattern;
- chain motif;
- fan-in/fan-out;
- reciprocal pair if used.

No vectorized implementation until scalar oracle tests exist.

### RED 4: null model preservation

Create `tests/test_null_models.py`:

- ER null preserves edge count;
- degree-preserving swap preserves in/out degree;
- invalid swaps rejected;
- null z-score handles zero variance as neutral, not infinite fake signal.

### RED 5: evaluation and claim discipline

Create `tests/test_claim_discipline.py`:

- table rows include method, baseline, AUC/AUPRC, CI, p-value, delta vs best simple baseline, claim_status;
- negative results are serialized as valid results;
- no method can be marked `defensible_detector_gain` unless it beats best simple baseline with paired support.

## First validation commands after build starts

```bash
pytest tests/test_data_contracts.py -q
pytest tests/test_local_egonets.py -q
pytest tests/test_motif_fixtures.py -q
pytest tests/test_null_models.py -q
pytest -q
```

Then, when the pipeline exists:

```bash
python -m motif_fraud.pipeline.reproduce_all
```

## First paper artifact target

Do not produce a fancy figure first. Produce these:

1. `outputs/tables/table1_dataset_summary.csv/md/tex`
2. `outputs/tables/table2_simple_baselines.csv/md/tex`
3. `outputs/tables/table3_local_motif_null_results.csv/md/tex`
4. `outputs/manifests/rebuild_manifest.json`

## First stopping rule

If local motif-null features do not beat degree/activity baselines on Elliptic, do not tune blindly. Report collapse and move to:

- alternate task definition only if scientifically justified;
- external dataset audit;
- manuscript as diagnostic confound benchmark.

## Second dataset gate

Before external validation code:

- confirm official dataset URL/source;
- write dataset card;
- write loader contract tests;
- freeze scoring direction from Elliptic before evaluating external data.
