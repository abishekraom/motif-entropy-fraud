# Reproduction and literature continuation status

Date: 2026-06-08

## What was completed in this continuation

1. Literature and novelty positioning was added.
2. Manuscript skeleton was updated with related-work boundaries.
3. A one-command reproduction runner was added and verified.

## Literature / novelty artifact

Created:

`docs/rebuild/12_LITERATURE_NOVELTY_POSITIONING.md`

Key conclusion:

The project must not claim general invention of p-adic machine learning, ultrametric learning, categorical anomaly detection, or fraud detection. Those areas already exist. The defensible novelty is narrower:

> A train-selected non-Archimedean prefix-rarity signal for temporal categorical fraud surveillance, validated against flat-rarity and hierarchy-order controls, shown complementary to a supervised frequency baseline, and externally supported on a vehicle insurance fraud dataset.

## Literature risks identified

| Risk | Evidence | Manuscript response |
|---|---|---|
| p-adic ML already exists | p-adic statistical field theory / deep belief networks, Physica A 2023; p-adic convolutional deep Boltzmann machines, PTEP 2023 | Do not claim first p-adic ML method. |
| ultrametric learning exists | Learning in Ultrametric Committee Machines, Journal of Statistical Physics 2012 | Claim transaction-specific prefix-rarity signal only. |
| categorical anomaly detection exists | ACM Computing Surveys 2019 categorical anomaly methods survey | Keep flat categorical rarity control mandatory. |
| fraud ML is broad and mature | fraud detection surveys and explainable fraud ML papers | Do not claim SOTA detector. |
| tabular supervised baselines are strong | XGBoost and logistic/tree baselines are standard | Claim complementarity, not raw superiority. |

## Manuscript skeleton update

Updated:

`docs/rebuild/10_IEEE_SPL_MANUSCRIPT_SKELETON.md`

Changed section:

`I. Introduction` -> `I. Introduction and related positioning`

Added:

- related-work boundary;
- safe novelty statement;
- pointer to `12_LITERATURE_NOVELTY_POSITIONING.md`.

## Reproduction runner

Created:

`src/motif_fraud/p_adic/reproduce_all.py`

Created test:

`tests/test_p_adic_reproduce_all.py`

Created plan artifact:

`docs/rebuild/reproduce_ieee_spl_artifacts.json`

The runner executes the real-data artifact commands and checks that expected artifacts exist. It avoids `shell=True` and uses argv lists for subprocess safety.

## Commands run

### Plan-only generation

```bash
python -m motif_fraud.p_adic.reproduce_all --plan-only
```

Result:

```text
docs\rebuild\reproduce_ieee_spl_artifacts.json
```

### Full test suite

```bash
pytest -q
```

Result:

```text
42 passed
```

### Real-data artifact reproduction without re-running tests

```bash
python -m motif_fraud.p_adic.reproduce_all --skip-tests
```

Result:

```text
[reproduce] all artifact checks passed
```

The reproduction runner re-ran:

1. `python -m motif_fraud.p_adic.ieee_pipeline`
2. `python -m motif_fraud.p_adic.official_baselines`
3. `python -m motif_fraud.p_adic.publication_figures`
4. `python -m motif_fraud.p_adic.vehicle_claim_pipeline`
5. `python -m motif_fraud.p_adic.claim_audit`

## Current state

The project now has:

- official IEEE-CIS primary audit;
- broader baseline context;
- p-adic complementarity result;
- 600 dpi figures;
- claim audit;
- manuscript skeleton;
- external vehicle-claim validation;
- literature/novelty positioning;
- reproducibility runner;
- 42 passing tests;
- real-data artifact reproduction verified.

## Remaining before final IEEE SPL submission

The next concrete step is to convert the skeleton into a concise IEEE SPL-style manuscript draft with references and final table/figure captions.

Current blocker is not code infrastructure. The blocker is manuscript polish and final positioning.

## Current estimated completion

Estimated completion: **88%**

Why not 100%:

- final IEEE-formatted manuscript not written;
- reference list not formatted as IEEE BibTeX;
- figure captions not finalized;
- final clean reproduction including tests takes time but artifact reproduction passed;
- raw p-adic still does not beat supervised logistic frequency baseline, so claims must remain narrow.
