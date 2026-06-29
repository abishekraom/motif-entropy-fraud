# SoftwareX Scope-Fit / Kill-Gate Decision

## Decision

Current decision: `SCOPE_FIT_PASSES_FOR_SOFTWAREX_IF_PUBLIC_GITHUB_PUSH_VERIFIES`.

The project can fit SoftwareX only if framed as a software article about a reproducible, fail-closed audit pipeline for hierarchy-aware fraud/event-stream surveillance hypotheses. It should not be framed as a conventional research-results paper claiming a superior detector.

## Why scope can pass

SoftwareX asks for a descriptive paper plus open-source software distribution. This project has:

- a Python package under `src/motif_fraud/`;
- tests under `tests/`;
- curated results under `results/`;
- documented claim discipline under `docs/rebuild/` and `understanding/`;
- reproducibility commands and manifests;
- a clear scientific use case: future researchers can evaluate p-adic/hierarchy-aware fraud-surveillance claims without overclaiming.

## Why detector-paper scope fails

The current evidence does not support a superior fraud detector claim:

- raw p-adic IEEE-CIS AUPRC 0.08450 is far below LightGBM 0.49547;
- tree-scan IEEE-CIS positive point delta has CI crossing zero;
- both CSE-CIC days are beaten by category entropy;
- aggregate status remains `diagnostic_only_failed_q1_cross_dataset_gate`.

## Kill criterion status

| Kill criterion | Status |
|---|---|
| Claims cannot be proved | NOT KILLED if claims remain diagnostic/software-focused; KILLED if manuscript claims detector superiority. |
| SoftwareX scope fails | NOT KILLED if the assigned public GitHub repository resolves before submission. |

## Required scope wording

Safe title family:

```text
Motif Entropy Fraud: A Fail-Closed Audit Pipeline for Hierarchy-Aware Fraud Surveillance
```

Unsafe title family:

```text
A State-of-the-Art P-adic Fraud Detector
```
