# Final SoftwareX Readiness Audit

Date: 2026-06-29

## Status

```text
PASS
```

This status is the local SoftwareX mechanical readiness check after assigning the target GitHub URL and before/around public repository verification.

## Readiness checker metrics

| Metric | Value |
|---|---:|
| Abstract words | 122 |
| Keywords | 5 |
| Figures | 0 |
| Approximate TeX words | 1202 |
| Highlights | 4 |

Errors:

```text
none
```

Warnings:

```text
none
```

## Verified command log

Clean-install/targeted verification log:

```text
docs/softwarex/clean_install_verification.log
```

Observed final commands in that log:

```text
python -m pip install -e .[dev]                         PASS
python -m compileall -q src tests                       PASS
PYTHONPATH=src python -m motif_fraud.p_adic.reproduce_all --plan-only  PASS
pytest tests/test_p_adic_tree_scan_theory.py tests/test_ieee_spl_manuscript_draft.py tests/test_results_artifact_manifest.py tests/test_p_adic_reproduce_all.py -q  PASS: 11 passed
python scripts/softwarex_readiness_check.py              PASS
```

## Remaining author actions before Editorial Manager submission

1. Confirm MIT license choice in `LICENSE.txt`.
2. Confirm corresponding author e-mail and affiliations in `paper/softwarex/motif_entropy_fraud_softwarex.tex`.
3. Confirm competing-interest statement and generate Elsevier declaration file if required.
4. Review and accept the generative AI disclosure.
5. Verify public GitHub URL resolves after push: `https://github.com/abishekraom/motif-entropy-fraud`.
6. Run full `pytest -q` with a long/overnight timeout if the submission will claim a fresh full-suite pass. The current verified claim is targeted clean-install verification, not a full-suite pass.

## Claim boundary

The SoftwareX manuscript is ready only under the software/reproducibility framing. It must not claim SOTA fraud detection or statistically significant detector superiority.
