from pathlib import Path

import pytest

from motif_fraud.p_adic.tree_scan_theory import (
    branch_local_expected_llr,
    branch_local_small_delta_approx,
    build_tree_scan_theory_diagnostics,
    flat_tuple_exact_llr_advantage,
    flat_tuple_dilution_factor,
    summarize_claim_table,
    write_tree_scan_theory_diagnostics,
)


IEEE_TREE_SCAN_CLAIMS = Path(
    "results/q1_upgrade_failures/tree_scan_cusum/"
    "official_ieee_cis_tree_scan_surveillance_claims.csv"
)
CSE_TREE_SCAN_CLAIMS = Path(
    "results/q1_upgrade_failures/cse_cic_thursday_tree_scan/"
    "official_cse_cic_ids2018_thursday_tree_scan_surveillance_claims.csv"
)
CSE_WEDNESDAY_TREE_SCAN_CLAIMS = Path(
    "results/q1_upgrade_failures/cse_cic_wednesday_tree_scan/"
    "official_cse_cic_ids2018_wednesday_2018_02_28_tree_scan_surveillance_claims.csv"
)


def test_branch_local_expected_llr_matches_small_delta_approximation():
    exact = branch_local_expected_llr(interval_rows=10_000, normal_probability=0.08, delta=0.002)
    approx = branch_local_small_delta_approx(interval_rows=10_000, normal_probability=0.08, delta=0.002)

    assert exact > 0
    assert approx > 0
    assert exact == pytest.approx(approx, rel=0.03)


def test_flat_tuple_dilution_factor_has_correct_linear_small_shift_scaling():
    p = 0.08

    assert flat_tuple_dilution_factor(1, p) == 1.0
    assert flat_tuple_dilution_factor(4, p) == pytest.approx(4 * (1 - p / 4) / (1 - p))
    assert flat_tuple_dilution_factor(10, p) == pytest.approx(10 * (1 - p / 10) / (1 - p))
    assert flat_tuple_dilution_factor(10, 0.001) == pytest.approx(10.009, rel=0.001)


def test_exact_equal_descendant_llr_ratio_converges_to_small_shift_factor():
    p = 0.08
    m = 6
    exact = flat_tuple_exact_llr_advantage(p, delta=1e-5, exact_tuple_count_under_prefix=m)
    approximation = flat_tuple_dilution_factor(m, p)

    assert exact == pytest.approx(approximation, rel=0.001)


def test_flat_tuple_advantage_rejects_invalid_probability_models():
    with pytest.raises(ValueError):
        flat_tuple_dilution_factor(0, 0.1)
    with pytest.raises(ValueError):
        flat_tuple_dilution_factor(4, 1.0)
    with pytest.raises(ValueError):
        flat_tuple_exact_llr_advantage(0.9, 0.2, 4)


@pytest.mark.skipif(
    not IEEE_TREE_SCAN_CLAIMS.exists(),
    reason="Curated IEEE-CIS tree-scan claims are required for artifact-backed diagnostics.",
)
def test_summarize_ieee_claim_table_marks_uncertain_positive_delta():
    row = summarize_claim_table("official_ieee_cis", IEEE_TREE_SCAN_CLAIMS)

    assert row["best_proposed_method"] == "p_adic_conditional_tree_scan_llr"
    assert row["conditional_minus_raw_auprc"] > 0
    assert row["delta_best_proposed_vs_best_control_auprc"] > 0
    assert row["bootstrap_delta_lower"] <= 0
    assert row["failure_mode"] == "uncertain_positive_delta"
    assert row["claim_status"] == "diagnostic_only_failed_q1_tree_scan_gate"


@pytest.mark.skipif(
    not CSE_TREE_SCAN_CLAIMS.exists(),
    reason="Curated CSE-CIC tree-scan claims are required for artifact-backed diagnostics.",
)
def test_summarize_cse_claim_table_marks_entropy_dominance():
    row = summarize_claim_table("cse_cic_ids2018_thursday", CSE_TREE_SCAN_CLAIMS)

    assert row["best_proposed_method"] == "p_adic_conditional_tree_scan_llr"
    assert row["best_control_method"] == "category_entropy_temporal"
    assert row["conditional_minus_raw_auprc"] > 0
    assert row["best_control_auprc"] > row["best_proposed_auprc"]
    assert row["failure_mode"] == "entropy_dominance"
    assert row["claim_status"] == "diagnostic_only_failed_q1_tree_scan_gate"


@pytest.mark.skipif(
    not CSE_WEDNESDAY_TREE_SCAN_CLAIMS.exists(),
    reason="Curated fresh Wednesday CSE-CIC claims are required.",
)
def test_summarize_fresh_wednesday_claim_table_marks_entropy_dominance():
    row = summarize_claim_table(
        "cse_cic_ids2018_wednesday_2018_02_28", CSE_WEDNESDAY_TREE_SCAN_CLAIMS
    )

    assert row["best_proposed_method"] == "p_adic_conditional_tree_scan_llr"
    assert row["best_control_method"] == "category_entropy_temporal"
    assert row["conditional_minus_raw_auprc"] > 0
    assert row["delta_best_proposed_vs_best_control_auprc"] < 0
    assert row["failure_mode"] == "entropy_dominance"
    assert row["claim_status"] == "diagnostic_only_failed_q1_tree_scan_gate"


def test_write_tree_scan_theory_diagnostics_outputs_summary_and_reference_tables(tmp_path):
    if (
        not IEEE_TREE_SCAN_CLAIMS.exists()
        or not CSE_TREE_SCAN_CLAIMS.exists()
        or not CSE_WEDNESDAY_TREE_SCAN_CLAIMS.exists()
    ):
        pytest.skip("Curated tree-scan claims are required for artifact-backed diagnostics.")

    artifacts = write_tree_scan_theory_diagnostics(tmp_path)
    summary, theory = build_tree_scan_theory_diagnostics()

    assert Path(artifacts["summary_csv"]).exists()
    assert Path(artifacts["summary_md"]).exists()
    assert Path(artifacts["theory_csv"]).exists()
    assert Path(artifacts["theory_md"]).exists()
    assert Path(artifacts["metadata"]).exists()
    assert Path(artifacts["cross_dataset_gate"]).exists()
    assert set(summary["dataset"]) == {
        "official_ieee_cis",
        "cse_cic_ids2018_thursday",
        "cse_cic_ids2018_wednesday_2018_02_28",
    }
    assert {"branch_local_expected_llr", "flat_tuple_dilution", "entropy_dominance_failure"}.issubset(
        set(theory["proposition"])
    )

    import json

    cross_gate = json.loads(Path(artifacts["cross_dataset_gate"]).read_text(encoding="utf-8"))
    assert cross_gate["observed_dataset_count"] == 3
    assert cross_gate["all_dataset_gates_passed"] is False
    assert cross_gate["cross_dataset_status"] == "diagnostic_only_failed_q1_cross_dataset_gate"
