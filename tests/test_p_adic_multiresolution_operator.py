from pathlib import Path

import pandas as pd
import pytest

from motif_fraud.p_adic.multiresolution_operator import (
    compute_prefix_surprise_scores,
    run_ieee_multiresolution_preregistered_audit,
)
from motif_fraud.p_adic.ieee_pipeline import _load_ieee, _prepare_ieee
from motif_fraud.p_adic.splits import temporal_train_test_split


OFFICIAL_ROOT = Path(r"D:/motif-entropy-fraud/ieee-fraud-detection")


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required; no synthetic empirical data allowed.",
)
def test_prefix_surprise_scores_are_invariant_to_within_level_relabeling_on_real_ieee_slice():
    transaction, identity = _load_ieee(OFFICIAL_ROOT)
    transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(30000).copy()
    identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    hierarchy = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain")

    original = compute_prefix_surprise_scores(train, test, hierarchy=hierarchy, label_column="isFraud")

    relabeled_train = train.copy()
    relabeled_test = test.copy()
    for column in hierarchy:
        observed = pd.concat([relabeled_train[column], relabeled_test[column]], ignore_index=True).astype(str).unique()
        mapping = {value: f"real_ieee_relabel_{column}_{idx}" for idx, value in enumerate(sorted(observed))}
        relabeled_train[column] = relabeled_train[column].astype(str).map(mapping)
        relabeled_test[column] = relabeled_test[column].astype(str).map(mapping)

    relabeled = compute_prefix_surprise_scores(relabeled_train, relabeled_test, hierarchy=hierarchy, label_column="isFraud")

    depth_columns = [column for column in original.columns if column.startswith("prefix_depth_")]
    assert depth_columns
    pd.testing.assert_frame_equal(original[depth_columns], relabeled[depth_columns], check_exact=False, atol=1e-12)


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required; no synthetic empirical data allowed.",
)
def test_preregistered_multiresolution_audit_writes_research_grade_failure_safe_artifacts_on_real_ieee_data():
    result = run_ieee_multiresolution_preregistered_audit(
        data_root=OFFICIAL_ROOT,
        output_root="outputs/test_p_adic_multiresolution_operator",
        max_rows=90000,
        n_blocks=24,
        bootstrap_samples=40,
        random_hierarchy_seeds=(11, 17),
    )

    claims = result["claims"]
    metadata = result["metadata"]
    artifacts = result["artifacts"]

    assert metadata["dataset"] == "official_ieee_cis_preregistered_multiresolution_surveillance"
    assert metadata["synthetic_data_used"] is False
    assert metadata["pre_registered_gates_doc"].endswith("20_Q1_SPL_PREREGISTERED_GATES.md")
    assert metadata["claim_status"] in {
        "q1_candidate_multiresolution_signal_passed_controls",
        "diagnostic_only_failed_q1_multiresolution_gate",
    }
    assert metadata["figure_dpi"][0] >= 600
    assert metadata["figure_dpi"][1] >= 600

    required_methods = {
        "p_adic_multiresolution_energy_cusum",
        "flat_tuple_rarity_cusum",
        "category_entropy_temporal",
        "transaction_count_signal",
        "reversed_hierarchy_energy_cusum",
    }
    assert required_methods.issubset(set(claims["method"]))
    assert any(str(method).startswith("random_hierarchy_energy_cusum_seed_") for method in claims["method"])
    assert "bootstrap_delta_lower" in claims.columns
    assert "best_control_method" in claims.columns
    assert set(claims["claim_status"]).issubset(
        {"q1_candidate_multiresolution_signal_passed_controls", "diagnostic_only_failed_q1_multiresolution_gate"}
    )

    for key in ("claims_table", "block_features", "metadata", "figure"):
        assert Path(artifacts[key]).exists(), key
