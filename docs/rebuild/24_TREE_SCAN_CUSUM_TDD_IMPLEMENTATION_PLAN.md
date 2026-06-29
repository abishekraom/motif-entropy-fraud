# P-adic Tree-Scan CUSUM implementation plan

Date: 2026-06-09

Goal: implement the `P-adic Tree-Scan CUSUM for Hierarchical Categorical Event Streams` redesign under strict TDD and research-grade claim discipline.

Architecture: add a new module rather than mutating the failed prefix-rarity modules. The new module will compute train-only prefix-node probabilities, binomial/conditional tree-scan LLRs, mandatory controls, block/interval scores, fail-closed claims tables, and 600 dpi figures. The old prefix-rarity outputs remain archived as negative evidence.

No subagents. No synthetic empirical data for empirical claims. Unit tests may use official IEEE-CIS slices; if a tiny hand-constructed fixture is unavoidable for pure formula tests, it must be marked non-empirical and must not enter any claims table. To avoid ambiguity, this plan uses official IEEE-CIS/CSE rows for tests wherever possible.

## Files

Create:

- `src/motif_fraud/p_adic/tree_scan_cusum.py`
- `tests/test_p_adic_tree_scan_cusum.py`
- `docs/rebuild/dataset_cards/cse_cic_ids2018_full_processed.md` after external CSE preparation

Modify only if needed:

- `src/motif_fraud/p_adic/encoding.py` for robust unknown-category error handling.
- `src/motif_fraud/p_adic/__init__.py` only if public exports are required.

Do not modify:

- existing failed-result artifacts except to reference them.
- existing SPL manuscript until empirical/theoretical gate status is known.

## Task 1: RED test for train-only p-adic node table on official IEEE-CIS slice

Objective: prove that node counts/probabilities are computed only from normal training rows and include depth/node metadata.

Test file: `tests/test_p_adic_tree_scan_cusum.py`

Test behavior:

1. Load official IEEE-CIS data from `D:/motif-entropy-fraud/ieee-fraud-detection`.
2. Use first 30,000 temporal rows.
3. Prepare frame with `_prepare_ieee`.
4. Split temporally.
5. Call expected future function:

```python
from motif_fraud.p_adic.tree_scan_cusum import build_prefix_node_table
```

Expected assertions:

- table has columns: `depth`, `node`, `train_normal_count`, `train_normal_probability`, `support_ok`.
- probabilities per depth sum approximately 1 over observed/support nodes plus unknown handling.
- fraud rows in train do not contribute to `train_normal_count`.
- no test rows are required as input.

Run expected RED:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_build_prefix_node_table_uses_only_normal_train_rows_on_real_ieee_slice -q
```

Expected: fail with `ModuleNotFoundError` or missing function.

## Task 2: GREEN implementation for prefix node table

Create minimal `tree_scan_cusum.py` with:

- `TreeScanHierarchyConfig` dataclass:
  - `hierarchy: tuple[str, ...]`
  - `label_column: str`
  - `min_support: int = 20`
  - `alpha: float = 0.5`
- `build_prefix_node_table(train, config)`.

Use existing `HierarchySpec`, `encode_frame`, `next_prime_at_least`.

Implementation rules:

- Use normal train rows only: `label == 0`.
- For every depth `d`, compute `node = code % prime**d`.
- Add an unknown/other probability through smoothing, but do not invent synthetic rows.
- Mark `support_ok = train_normal_count >= min_support`.

Verification:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_build_prefix_node_table_uses_only_normal_train_rows_on_real_ieee_slice -q
```

Then:

```bash
pytest tests/test_p_adic_core.py tests/test_p_adic_multiresolution_operator.py -q
```

## Task 3: RED test for binomial excess LLR correctness on real-derived counts

Objective: verify the exact LLR formula without relying on flattering empirical results.

Test behavior:

1. Use node table from official IEEE-CIS slice.
2. Select a real prefix node with support.
3. Construct `observed`, `n_interval`, and `p_expected` from real block counts, not synthetic labels.
4. Compare future function:

```python
binomial_excess_llr(observed, n_interval, p_expected)
```

against direct formula in the test.

Assertions:

- LLR is zero when `observed <= n * p_expected`.
- LLR matches direct formula when excess exists.
- handles probabilities clipped away from 0/1.

Run RED:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_binomial_excess_llr_matches_direct_formula_on_real_derived_counts -q
```

## Task 4: GREEN implementation for LLR formula

Add:

- `binomial_excess_llr(observed, total, expected_probability)`.

Rules:

- no sklearn dependency needed.
- return `0.0` if observed is not an excess.
- clip probability with small epsilon.
- raise clean `ValueError` for invalid counts.

Verification:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_binomial_excess_llr_matches_direct_formula_on_real_derived_counts -q
```

## Task 5: RED test for fixed-block tree scan schema on official IEEE-CIS slice

Objective: compute block-level proposed tree-scan scores without using held-out labels except for evaluation columns.

Expected future function:

```python
run_fixed_block_tree_scan(train, test, config, n_blocks=24)
```

Assertions:

- output has one row per block.
- columns include:
  - `block_id`
  - `rows`
  - `positive_rate`
  - `tree_scan_llr`
  - `tree_scan_depth`
  - `tree_scan_node`
  - `tree_scan_observed`
  - `tree_scan_expected`
- `tree_scan_llr >= 0`.
- selected nodes have `support_ok == True` unless no supported node exists.
- no exception on real IEEE-CIS slice.

Run RED:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_fixed_block_tree_scan_outputs_localized_scores_on_real_ieee_slice -q
```

## Task 6: GREEN implementation for fixed-block tree scan

Add:

- equal-count block assignment helper or reuse existing helper pattern.
- `run_fixed_block_tree_scan`.

Implementation rules:

- Sort held-out test by time before block assignment.
- For each block and each supported prefix node, compute LLR.
- Choose max LLR node.
- Keep positive_rate for evaluation only; do not use it in scoring.

Verification:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_fixed_block_tree_scan_outputs_localized_scores_on_real_ieee_slice -q
```

## Task 7: RED test for mandatory controls registration

Objective: prevent a fake Q1 claim by requiring controls from the beginning.

Expected future function:

```python
run_tree_scan_claim_audit(...)
```

Assertions on claims table methods:

- `p_adic_tree_scan_llr`
- `flat_tuple_scan_llr`
- `marginal_column_scan_llr`
- `reversed_hierarchy_tree_scan_llr`
- at least 3 `random_hierarchy_tree_scan_llr_seed_*`
- `category_entropy_temporal`
- `transaction_count_signal`

Assertions on status:

- claim status is one of:
  - `q1_candidate_tree_scan_passed_controls`
  - `diagnostic_only_failed_q1_tree_scan_gate`
- no empirical test asserts the proposed method wins.

Run RED:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_tree_scan_claim_audit_registers_mandatory_controls_and_fails_closed -q
```

## Task 8: GREEN implementation for controls and claim audit

Add:

- `run_tree_scan_claim_audit`.
- flat tuple scan: exact tuple nodes.
- marginal scan: per-column value excess.
- reversed/random hierarchy scan: same tree scan with different order.
- entropy/count controls.
- bootstrap delta vs best control.

Claim pass rule:

```text
proposed AUPRC > best_control AUPRC
and bootstrap_delta_lower > 0
and p_delta_le_zero <= 0.05
```

Otherwise fail closed.

Verification:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_tree_scan_claim_audit_registers_mandatory_controls_and_fails_closed -q
```

## Task 9: RED test for CSE-CIC timestamp parsing correctness on real CSE rows

Objective: fix known CSE timestamp unit bug before any external manuscript-grade run.

Use existing local real file:

```text
data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv
```

Expected future function:

```python
parse_cse_cic_timestamp_seconds(series)
```

Assertions:

- first timestamp `01/03/2018 08:17:11` parses to Unix seconds around `1519892231`.
- parsed seconds are greater than `1_500_000_000`, not `1_519_892`.
- sorting by parsed timestamp preserves chronological order.

Run RED:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_cse_cic_timestamp_parser_uses_seconds_not_microsecond_truncation_on_real_rows -q
```

## Task 10: GREEN implementation for CSE parser and loader helper

Add:

- `parse_cse_cic_timestamp_seconds(series)`.
- `prepare_cse_cic_processed_flows(frame)` minimal helper if needed.

Rules:

- remove repeated header rows.
- label positive as `Label != Benign`.
- do not use label-derived attack category as hierarchy feature.

Verification:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py::test_cse_cic_timestamp_parser_uses_seconds_not_microsecond_truncation_on_real_rows -q
```

## Task 11: RED test for 600 dpi artifacts and metadata

Objective: manuscript artifacts must be research-grade even on failure.

Expected audit on small real IEEE-CIS slice:

```python
run_ieee_tree_scan_audit(... max_rows=90000, n_blocks=24, bootstrap_samples=40)
```

Assertions:

- claims CSV exists.
- block metrics CSV exists.
- metadata JSON exists.
- figure exists and DPI >=600.
- metadata says `synthetic_data_used: false`.
- metadata links to spec doc `23_P_ADIC_TREE_SCAN_CUSUM_Q1_SPEC_AND_DECISION.md`.

## Task 12: GREEN implementation for audit runner and figure

Add:

- `run_ieee_tree_scan_audit`.
- CLI `main()` in module.
- `_write_tree_scan_figure` with dpi=610 to avoid PNG rounding below 600.

Verification:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py -q
```

## Task 13: Run targeted p-adic suite

Command:

```bash
pytest tests/test_p_adic_tree_scan_cusum.py tests/test_p_adic_temporal_surveillance.py tests/test_p_adic_rich_features.py tests/test_p_adic_branch_signatures.py tests/test_p_adic_multiresolution_operator.py -q
```

Expected: all pass. If old modules fail because of shared helper changes, fix through TDD.

## Task 14: Smoke empirical audit on IEEE-CIS slice

Command:

```bash
python -m motif_fraud.p_adic.tree_scan_cusum --dataset ieee --max-rows 120000 --n-blocks 32 --bootstrap-samples 80
```

Expected:

- artifacts written under `outputs/p_adic_ieee_cis_tree_scan_smoke/`.
- claim status may pass or fail; test does not require a win.

## Task 15: Full IEEE-CIS tree-scan audit

Command:

```bash
python -m motif_fraud.p_adic.tree_scan_cusum --dataset ieee --n-blocks 96 --bootstrap-samples 500
```

Expected:

- full official IEEE-CIS artifacts.
- honest claim status.

If it fails controls, do not tune on test. Analyze failure and decide whether theory-only or external dataset continuation remains justified.

## Task 16: Full CSE-CIC processed dataset preparation

Download official CSE-CIC processed ML CSVs from AWS Open Data if not already present.

Potential direct URL pattern:

```text
https://cse-cic-ids2018.s3.ca-central-1.amazonaws.com/Processed%20Traffic%20Data%20for%20ML%20Algorithms/<filename>
```

Local target:

```text
data/cse_cic_ids2018/full_processed/
```

Do not download if disk check fails. Current D: free space was ~454 GB, so the ~6.89 GB processed set is feasible.

## Task 17: Full external CSE-CIC audit

Command shape:

```bash
python -m motif_fraud.p_adic.tree_scan_cusum --dataset cse-cic-ids2018-full --n-blocks 128 --bootstrap-samples 500
```

Expected:

- official source metadata.
- timestamp parser fixed.
- no label-derived hierarchy leakage.
- pass/fail claim status.

## Task 18: Go/no-go after full empirical audits

If both IEEE-CIS and CSE-CIC pass:

- proceed to paper update and IEEE SPL packaging.

If IEEE-CIS passes but CSE fails:

- ask Lust for ToN_IoT or BoT-IoT official download, or pivot theory-first.

If IEEE-CIS fails:

- do not keep empirical tweaking on IEEE-CIS.
- use failure to refine theorem or abandon empirical SPL/Q1 claim.

## Task 19: Full suite

Command:

```bash
pytest -q
```

Only claim stability after this passes with real output.

## Non-negotiable claim language

Allowed before gates pass:

```text
candidate p-adic tree-scan statistic
research-grade implementation
fail-closed empirical audit
branch-local diagnostic signal
```

Banned before gates pass:

```text
Q1-ready result
SOTA detector
statistically significant superiority
robust cross-dataset p-adic detector
```
