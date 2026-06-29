# SoftwareX Verification Log

This log records commands actually run during SoftwareX preparation. It must not be edited to claim success for commands that did not finish.

## Planned minimal verification set

```bash
python -m compileall -q src tests
PYTHONPATH=src python -m motif_fraud.p_adic.reproduce_all --plan-only
pytest tests/test_p_adic_tree_scan_theory.py tests/test_ieee_spl_manuscript_draft.py tests/test_results_artifact_manifest.py tests/test_p_adic_reproduce_all.py -q
python scripts/softwarex_readiness_check.py
```

Full `pytest -q` is known to be slow in this repo because some real-data tests run long. It should be run overnight or with a longer process manager before final public release, but the manuscript must not claim a fresh full-suite pass unless a final summary is captured.


## Clean install verification result

Command batch saved to:

```text
docs/softwarex/clean_install_verification.log
```

Observed result:

```text
python -m pip install -e .[dev]                         PASS
python -m compileall -q src tests                       PASS
PYTHONPATH=src python -m motif_fraud.p_adic.reproduce_all --plan-only  PASS
pytest targeted SoftwareX/source-backed tests            PASS: 11 passed
python scripts/softwarex_readiness_check.py              PASS
```

Full `pytest -q` was not claimed as passed in this SoftwareX audit because previous full-suite attempts exceeded the interactive wait window.

## Public GitHub and CI verification

Verified public repository:

```text
https://github.com/abishekraom/motif-entropy-fraud
visibility: PUBLIC
default branch: master
latest pushed commit: f4eb11f
```

Verified GitHub Actions run:

```text
workflow: tests
run id: 28359319014
status: success
job: pytest in 38s
observed test line: ...ssss..........s.......ssss.....s....s...sssssssssssss.............sss [ 96%] ... [100%]
```

Public CI intentionally skips raw-data tests when restricted datasets are absent. Raw-data tests still run locally when the corresponding raw dataset files are present.

