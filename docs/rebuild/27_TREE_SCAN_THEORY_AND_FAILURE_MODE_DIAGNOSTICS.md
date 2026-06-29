# Tree-scan theory and failure-mode diagnostics

Date: 2026-06-10

## Scope

This note records the theory-led follow-up after the parent-conditional p-adic tree-scan reruns on IEEE-CIS and CSE-CIC-IDS2018 Thursday.

The purpose is not to tune the held-out empirical gates. The purpose is to make the SPL/Q1 story sharper and more falsifiable:

- when p-adic prefix aggregation should help;
- when flat tuple scans are diluted;
- when entropy controls can dominate;
- why current evidence remains diagnostic rather than an empirical pass.

## Added artifacts

New module:

```text
src/motif_fraud/p_adic/tree_scan_theory.py
```

New tests:

```text
tests/test_p_adic_tree_scan_theory.py
```

Generated artifacts:

```text
docs/rebuild/tree_scan_theory_diagnostics.csv
docs/rebuild/tree_scan_theory_diagnostics.md
docs/rebuild/tree_scan_theory_reference.csv
docs/rebuild/tree_scan_theory_reference.md
docs/rebuild/tree_scan_theory_diagnostics_metadata.json
```

Reproduction command:

```bash
python -m motif_fraud.p_adic.tree_scan_theory
```

## Theory reference

The diagnostic artifact records three compact propositions:

1. Branch-local expected LLR:

```text
E[LLR] = n * KL(Bernoulli(p + delta) || Bernoulli(p))
```

For small `delta`, this is approximately:

```text
n * delta^2 / (2 p (1 - p))
```

2. Flat tuple dilution:

If a prefix-level shift is spread across `M` exact tuples, a best single flat tuple scan has an approximate `M^2` disadvantage.

3. Entropy-dominance failure:

If high-risk blocks are broad category-diversity shifts rather than branch-local concentration, category entropy can beat p-adic prefix scans. This is a valid diagnostic failure mode, not a detector superiority result.

## Current artifact-backed diagnosis

Source:

```text
docs/rebuild/tree_scan_theory_diagnostics.csv
```

| Dataset | Failure mode | Conditional minus raw AUPRC | Best proposed | Best control | Delta | CI | p(delta <= 0) |
|---|---|---:|---|---|---:|---|---:|
| official_ieee_cis | uncertain_positive_delta | +0.106966 | p_adic_conditional_tree_scan_llr | transaction_count_signal | +0.011766 | [-0.070532, 0.122167] | 0.330 |
| cse_cic_ids2018_thursday | entropy_dominance | +0.014528 | p_adic_conditional_tree_scan_llr | category_entropy_temporal | -0.015906 | [-0.185953, 0.156353] | 0.506 |
| cse_cic_ids2018_wednesday_2018_02_28 | entropy_dominance | +0.019298 | p_adic_conditional_tree_scan_llr | category_entropy_temporal | -0.033825 | [-0.141594, 0.039650] | 0.820 |

## Interpretation

The parent-conditional residual scan moved the method in the right theoretical direction:

- IEEE-CIS: raw tree scan AUPRC improved from 0.190753 to 0.297719.
- CSE-CIC Thursday: raw tree scan AUPRC improved from 0.509695 to 0.524222.
- Fresh preregistered CSE-CIC Wednesday: raw tree scan AUPRC improved from 0.195955 to 0.215253.

But neither dataset passes the strict Q1/SPL empirical gate:

- IEEE-CIS has a positive point-estimate delta, but the confidence interval crosses zero.
- CSE-CIC Thursday is still beaten by category entropy.
- Fresh CSE-CIC Wednesday is also beaten by category entropy.

## Consequence for IEEE SPL/Q1

The empirical detector-superiority route is still closed.

The remaining viable SPL direction is a theory/diagnostic letter:

```text
A Non-Archimedean Tree-Scan Diagnostic for Hierarchical Categorical Event Streams
```

That paper would need to claim:

- a compact p-adic prefix/conditional scan operator;
- formal branch-local and flat-dilution propositions;
- reproducible failure-aware gates on IEEE-CIS and CSE-CIC;
- explicit entropy-dominance limitations.

It must not claim:

- state-of-the-art fraud detection;
- statistically significant superiority;
- robust cross-dataset p-adic anomaly detection.

## Next gate

Before another empirical run, freeze a manuscript-grade theory section and add an entropy-vs-branch-local diagnostic criterion to the claim table. Only then evaluate a fresh multi-day CSE-CIC or UNSW dataset under a pre-registered protocol.
