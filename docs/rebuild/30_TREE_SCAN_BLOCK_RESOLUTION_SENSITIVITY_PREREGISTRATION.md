# Tree-scan block-resolution sensitivity preregistration

Date: 2026-06-12

Status: frozen before running the 48-block or 192-block analyses.

## Purpose

The primary tree-scan gate used 96 equal-count held-out blocks on IEEE-CIS and both CSE-CIC-IDS2018 days. This sensitivity audit tests whether the qualitative conclusion depends on that temporal resolution.

The 96-block analysis remains the sole confirmatory gate. Results at 48 or 192 blocks are secondary robustness evidence and cannot promote a failed primary claim.

## Frozen datasets

1. Official IEEE-CIS fraud detection training data.
2. CSE-CIC-IDS2018 Thursday, March 1, 2018 processed flow data.
3. CSE-CIC-IDS2018 Wednesday, February 28, 2018 processed flow data.

The Wednesday file remains checksum guarded by:

```text
F15E2A12304446058A0186C8AD67DE2BD15735A9BA5C70C9A1F4C4242AB06771
```

## Frozen sensitivity grid

```text
n_blocks = 48, 192
bootstrap_samples = 500
random_hierarchy_seeds = 11,17,23,31,47
```

All dataset preparation, temporal 70/30 splits, hierarchies, minimum support, smoothing, score directions, high-risk block-label rule, proposed methods, and mandatory controls remain identical to the frozen 96-block analyses.

## Reported quantities

For each dataset and resolution:

1. Best proposed method and AUPRC.
2. Best mandatory control and AUPRC.
3. Proposed-minus-control AUPRC difference.
4. Paired 95% bootstrap interval.
5. Bootstrap probability `p_delta_le_zero`.
6. Whether the conditional tree scan improves on the unconditional tree scan.

## Interpretation rules

The primary conclusion is robust only if no alternate resolution provides confirmatory evidence that contradicts the failed 96-block gate.

An alternate resolution is labelled `exploratory_pass_not_confirmatory` if its best proposed method beats all controls, its bootstrap lower bound is positive, and `p_delta_le_zero <= 0.05`. Such a result is hypothesis-generating only because the resolution audit was specified after observing the 96-block outcomes.

Otherwise the alternate resolution is labelled `sensitivity_failed_superiority_gate`.

The aggregate publication status remains:

```text
diagnostic_only_failed_q1_cross_dataset_gate
```

regardless of any alternate-resolution point estimate.

## Claim boundary

Allowed:

```text
The direction and uncertainty of the failed primary gate were audited at two prespecified secondary block resolutions.
```

Unsafe:

```text
An alternate block resolution rescues or replaces the failed preregistered primary result.
```
