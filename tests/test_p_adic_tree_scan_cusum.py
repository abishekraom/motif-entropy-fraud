from pathlib import Path
import math

import pytest

from motif_fraud.p_adic.ieee_pipeline import _load_ieee, _prepare_ieee
from motif_fraud.p_adic.splits import temporal_train_test_split
from motif_fraud.p_adic.tree_scan_cusum import (
    CSE_CIC_HIERARCHY,
    CSE_CIC_WEDNESDAY_FILE,
    TreeScanHierarchyConfig,
    binomial_excess_llr,
    build_prefix_node_table,
    load_cse_cic_processed_frame,
    load_cse_cic_thursday_frame,
    parse_cse_cic_timestamp_seconds,
    run_cse_cic_thursday_tree_scan_audit,
    run_cse_cic_wednesday_tree_scan_audit,
    run_fixed_block_conditional_tree_scan,
    run_fixed_block_tree_scan,
    run_ieee_tree_scan_audit,
    run_tree_scan_claim_audit,
)


OFFICIAL_ROOT = Path(r"D:/motif-entropy-fraud/ieee-fraud-detection")
CSE_THURSDAY_FILE = Path(r"D:/motif-entropy-fraud/motif-entropy-fraud/data/cse_cic_ids2018/Thursday-01-03-2018_TrafficForML_CICFlowMeter.csv")
CSE_WEDNESDAY_FILE = Path(r"D:/motif-entropy-fraud/motif-entropy-fraud/data/cse_cic_ids2018/Wednesday-28-02-2018_TrafficForML_CICFlowMeter.csv")


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required; no synthetic empirical data allowed.",
)
def test_build_prefix_node_table_uses_only_normal_train_rows_on_real_ieee_slice():
    transaction, identity = _load_ieee(OFFICIAL_ROOT)
    transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(30000).copy()
    identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    train, _ = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    hierarchy = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain")
    config = TreeScanHierarchyConfig(hierarchy=hierarchy, label_column="isFraud", min_support=20, alpha=0.5)

    table, encoded = build_prefix_node_table(train, config)

    assert {"depth", "node", "train_normal_count", "train_normal_probability", "support_ok"}.issubset(table.columns)
    assert encoded.spec.columns == hierarchy
    assert table["depth"].min() == 1
    assert table["depth"].max() == len(hierarchy)
    assert (table["train_normal_count"] >= 0).all()
    assert table["train_normal_probability"].between(0, 1).all()
    assert table["support_ok"].equals(table["train_normal_count"] >= config.min_support)

    normal_train_rows = int((train["isFraud"].astype(int) == 0).sum())
    depth_totals = table.groupby("depth")["train_normal_count"].sum()
    assert (depth_totals == normal_train_rows).all()

    probability_totals = table.groupby("depth")["train_normal_probability"].sum()
    assert (probability_totals < 1.0).all()
    assert (probability_totals > 0.95).all()


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required; no synthetic empirical data allowed.",
)
def test_prefix_node_table_includes_train_only_parent_conditional_probabilities():
    transaction, identity = _load_ieee(OFFICIAL_ROOT)
    transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(30000).copy()
    identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    train, _ = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    hierarchy = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain")
    config = TreeScanHierarchyConfig(hierarchy=hierarchy, label_column="isFraud", min_support=20, alpha=0.5)

    table, _ = build_prefix_node_table(train, config)
    child_rows = table[table["depth"] > 1]

    assert {"parent_node", "train_normal_parent_count", "train_normal_conditional_probability"}.issubset(
        table.columns
    )
    assert child_rows["parent_node"].notna().all()
    assert child_rows["train_normal_parent_count"].notna().all()
    assert child_rows["train_normal_conditional_probability"].between(0, 1).all()
    assert (child_rows["train_normal_parent_count"] >= child_rows["train_normal_count"]).all()
    assert child_rows["conditional_support_ok"].equals(
        (child_rows["train_normal_count"] >= config.min_support)
        & (child_rows["train_normal_parent_count"] >= config.min_support)
    )


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required; no synthetic empirical data allowed.",
)
def test_binomial_excess_llr_matches_direct_formula_on_real_derived_counts():
    transaction, identity = _load_ieee(OFFICIAL_ROOT)
    transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(30000).copy()
    identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    hierarchy = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain")
    config = TreeScanHierarchyConfig(hierarchy=hierarchy, label_column="isFraud", min_support=20, alpha=0.5)
    table, encoded_train = build_prefix_node_table(train, config)

    encoded_test = __import__("motif_fraud.p_adic.encoding", fromlist=["encode_frame"]).encode_frame(
        test, encoded_train.spec, digit_maps=encoded_train.digit_maps
    )
    node = table.sort_values("train_normal_count", ascending=False).iloc[0]
    depth = int(node["depth"])
    modulus = int(encoded_train.spec.prime or 2) ** depth
    total = min(2000, len(test))
    observed = int((encoded_test.codes.reset_index(drop=True).head(total).astype(int) % modulus == int(node["node"])).sum())
    expected_probability = float(node["train_normal_probability"])

    value = binomial_excess_llr(observed, total, expected_probability)
    if observed <= total * expected_probability:
        assert value == 0.0
    else:
        q = observed / total
        expected = observed * math.log(q / expected_probability) + (total - observed) * math.log(
            (1.0 - q) / (1.0 - expected_probability)
        )
        assert value == pytest.approx(expected, rel=1e-12, abs=1e-12)

    assert binomial_excess_llr(0, total, expected_probability) == 0.0


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required; no synthetic empirical data allowed.",
)
def test_fixed_block_tree_scan_outputs_localized_scores_on_real_ieee_slice():
    transaction, identity = _load_ieee(OFFICIAL_ROOT)
    transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(40000).copy()
    identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    hierarchy = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain")
    config = TreeScanHierarchyConfig(hierarchy=hierarchy, label_column="isFraud", min_support=20, alpha=0.5)

    blocks = run_fixed_block_tree_scan(train, test, config, time_column="TransactionDT", n_blocks=12)

    assert len(blocks) == 12
    required = {
        "block_id",
        "rows",
        "positive_rate",
        "tree_scan_llr",
        "tree_scan_depth",
        "tree_scan_node",
        "tree_scan_observed",
        "tree_scan_expected",
        "tree_scan_support_ok",
    }
    assert required.issubset(blocks.columns)
    assert (blocks["rows"] > 0).all()
    assert blocks["positive_rate"].between(0, 1).all()
    assert (blocks["tree_scan_llr"] >= 0).all()
    assert blocks["tree_scan_support_ok"].all()
    assert (blocks["tree_scan_observed"] >= 0).all()
    assert (blocks["tree_scan_expected"] >= 0).all()


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required; no synthetic empirical data allowed.",
)
def test_fixed_block_conditional_tree_scan_outputs_parent_residual_scores_on_real_ieee_slice():
    transaction, identity = _load_ieee(OFFICIAL_ROOT)
    transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(40000).copy()
    identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    hierarchy = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain")
    config = TreeScanHierarchyConfig(hierarchy=hierarchy, label_column="isFraud", min_support=20, alpha=0.5)

    blocks = run_fixed_block_conditional_tree_scan(train, test, config, time_column="TransactionDT", n_blocks=12)

    assert len(blocks) == 12
    required = {
        "block_id",
        "rows",
        "positive_rate",
        "conditional_tree_scan_llr",
        "conditional_tree_scan_depth",
        "conditional_tree_scan_node",
        "conditional_tree_scan_parent_node",
        "conditional_tree_scan_observed",
        "conditional_tree_scan_parent_observed",
        "conditional_tree_scan_expected",
        "conditional_tree_scan_support_ok",
    }
    assert required.issubset(blocks.columns)
    assert (blocks["conditional_tree_scan_llr"] >= 0).all()
    assert (blocks["conditional_tree_scan_depth"] > 1).all()
    assert (
        blocks["conditional_tree_scan_parent_observed"] >= blocks["conditional_tree_scan_observed"]
    ).all()
    assert (blocks["conditional_tree_scan_expected"] >= 0).all()


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required; no synthetic empirical data allowed.",
)
def test_tree_scan_claim_audit_registers_mandatory_controls_and_fails_closed():
    transaction, identity = _load_ieee(OFFICIAL_ROOT)
    transaction = transaction.sort_values("TransactionDT", kind="mergesort").head(50000).copy()
    identity = identity[identity["TransactionID"].isin(transaction["TransactionID"])].copy()
    frame = _prepare_ieee(transaction, identity).sort_values("TransactionDT", kind="mergesort")
    train, test = temporal_train_test_split(frame, "TransactionDT", train_fraction=0.7)
    hierarchy = ("DeviceType", "card6", "card4", "ProductCD", "P_emaildomain")
    config = TreeScanHierarchyConfig(hierarchy=hierarchy, label_column="isFraud", min_support=20, alpha=0.5)

    result = run_tree_scan_claim_audit(
        train,
        test,
        config,
        time_column="TransactionDT",
        n_blocks=16,
        bootstrap_samples=30,
        random_hierarchy_seeds=(11, 17, 23),
    )

    claims = result["claims"]
    blocks = result["blocks"]
    methods = set(claims["method"])
    assert "p_adic_tree_scan_llr" in methods
    assert "p_adic_conditional_tree_scan_llr" in methods
    assert "flat_tuple_scan_llr" in methods
    assert "marginal_column_scan_llr" in methods
    assert "reversed_hierarchy_tree_scan_llr" in methods
    assert "category_entropy_temporal" in methods
    assert "transaction_count_signal" in methods
    assert sum(method.startswith("random_hierarchy_tree_scan_llr_seed_") for method in methods) == 3
    assert set(claims["claim_status"]).issubset(
        {"q1_candidate_tree_scan_passed_controls", "diagnostic_only_failed_q1_tree_scan_gate"}
    )
    assert "best_control_method" in claims.columns
    assert "bootstrap_delta_lower" in claims.columns
    assert len(blocks) == 16


@pytest.mark.skipif(
    not CSE_THURSDAY_FILE.exists(),
    reason="Official CSE-CIC-IDS2018 processed file is required; no synthetic empirical data allowed.",
)
def test_cse_cic_timestamp_parser_uses_seconds_not_microsecond_truncation_on_real_rows():
    rows = __import__("pandas").read_csv(CSE_THURSDAY_FILE, usecols=["Timestamp"], nrows=5)

    seconds = parse_cse_cic_timestamp_seconds(rows["Timestamp"])

    assert int(seconds.iloc[0]) == 1519892231
    assert seconds.iloc[0] > 1_500_000_000
    assert seconds.iloc[0] != 1519892
    assert seconds.notna().all()


@pytest.mark.skipif(
    not CSE_THURSDAY_FILE.exists(),
    reason="Official CSE-CIC-IDS2018 processed file is required; no synthetic empirical data allowed.",
)
def test_cse_cic_loader_builds_nonleaking_external_event_stream():
    frame = load_cse_cic_thursday_frame(CSE_THURSDAY_FILE).head(5000)

    assert {"timestamp_seconds", "is_attack", "dst_port_band", *CSE_CIC_HIERARCHY}.issubset(frame.columns)
    assert "Label" not in CSE_CIC_HIERARCHY
    assert "is_attack" not in CSE_CIC_HIERARCHY
    assert frame["timestamp_seconds"].notna().all()
    assert frame["timestamp_seconds"].is_monotonic_increasing
    assert set(frame["is_attack"].unique()).issubset({0, 1})
    assert set(frame["dst_port_band"]).issubset(
        {"system", "registered", "dynamic", "missing_or_nonstandard"}
    )


@pytest.mark.skipif(
    not CSE_WEDNESDAY_FILE.exists(),
    reason="Official CSE-CIC-IDS2018 Wednesday processed file is required.",
)
def test_generic_cse_cic_loader_prepares_preregistered_wednesday_without_label_leakage():
    frame = load_cse_cic_processed_frame(CSE_CIC_WEDNESDAY_FILE, nrows=5000)

    assert len(frame) <= 5000
    assert {"timestamp_seconds", "is_attack", "dst_port_band", *CSE_CIC_HIERARCHY}.issubset(frame.columns)
    assert "Label" not in CSE_CIC_HIERARCHY
    assert "is_attack" not in CSE_CIC_HIERARCHY
    assert frame["timestamp_seconds"].notna().all()
    assert frame["timestamp_seconds"].is_monotonic_increasing
    assert set(frame["is_attack"].unique()).issubset({0, 1})


@pytest.mark.skipif(
    not CSE_WEDNESDAY_FILE.exists(),
    reason="Official CSE-CIC-IDS2018 Wednesday processed file is required.",
)
def test_cse_cic_wednesday_audit_writes_preregistered_fail_closed_artifacts():
    result = run_cse_cic_wednesday_tree_scan_audit(
        data_root=CSE_WEDNESDAY_FILE,
        output_root="outputs/test_p_adic_cse_cic_wednesday_tree_scan",
        max_rows=90000,
        n_blocks=18,
        bootstrap_samples=30,
        random_hierarchy_seeds=(11, 17, 23),
    )

    metadata = result["metadata"]
    claims = result["claims"]

    assert metadata["dataset"] == "official_cse_cic_ids2018_wednesday_2018_02_28_tree_scan_surveillance"
    assert metadata["synthetic_data_used"] is False
    assert metadata["preregistered_fresh_external_validation"] is True
    assert metadata["preregistration_doc"].endswith("28_CSE_CIC_SECOND_DAY_PREREGISTRATION.md")
    assert metadata["source_file_sha256"] == "F15E2A12304446058A0186C8AD67DE2BD15735A9BA5C70C9A1F4C4242AB06771"
    assert metadata["figure_dpi"][0] >= 600
    assert metadata["figure_dpi"][1] >= 600
    assert metadata["claim_status"] in {
        "q1_candidate_tree_scan_passed_controls",
        "diagnostic_only_failed_q1_tree_scan_gate",
    }
    assert set(claims["claim_status"]).issubset(
        {"q1_candidate_tree_scan_passed_controls", "diagnostic_only_failed_q1_tree_scan_gate"}
    )


@pytest.mark.skipif(
    not CSE_THURSDAY_FILE.exists(),
    reason="Official CSE-CIC-IDS2018 processed file is required; no synthetic empirical data allowed.",
)
def test_cse_cic_tree_scan_audit_writes_external_fail_closed_artifacts_on_real_slice():
    result = run_cse_cic_thursday_tree_scan_audit(
        data_root=CSE_THURSDAY_FILE,
        output_root="outputs/test_p_adic_cse_cic_tree_scan",
        max_rows=90000,
        n_blocks=18,
        bootstrap_samples=30,
        random_hierarchy_seeds=(11, 17, 23),
    )

    metadata = result["metadata"]
    artifacts = result["artifacts"]
    claims = result["claims"]

    assert metadata["dataset"] == "official_cse_cic_ids2018_thursday_tree_scan_surveillance"
    assert metadata["synthetic_data_used"] is False
    assert metadata["source_dataset_card"].endswith("cse_cic_ids2018_thursday_2018_03_01.md")
    assert metadata["positive_label_rule"] == "Label != Benign"
    assert "Label" not in metadata["hierarchy"]
    assert "is_attack" not in metadata["hierarchy"]
    assert metadata["figure_dpi"][0] >= 600
    assert metadata["figure_dpi"][1] >= 600
    assert metadata["claim_status"] in {"q1_candidate_tree_scan_passed_controls", "diagnostic_only_failed_q1_tree_scan_gate"}
    assert set(claims["claim_status"]).issubset(
        {"q1_candidate_tree_scan_passed_controls", "diagnostic_only_failed_q1_tree_scan_gate"}
    )
    for key in ("claims_table", "block_features", "metadata", "figure"):
        assert Path(artifacts[key]).exists(), key


@pytest.mark.skipif(
    not (OFFICIAL_ROOT / "train_transaction.csv").exists(),
    reason="Official IEEE-CIS files are required; no synthetic empirical data allowed.",
)
def test_ieee_tree_scan_audit_writes_600dpi_fail_closed_artifacts_on_real_slice():
    result = run_ieee_tree_scan_audit(
        data_root=OFFICIAL_ROOT,
        output_root="outputs/test_p_adic_tree_scan_cusum",
        max_rows=70000,
        n_blocks=16,
        bootstrap_samples=30,
        random_hierarchy_seeds=(11, 17, 23),
    )

    metadata = result["metadata"]
    artifacts = result["artifacts"]
    claims = result["claims"]

    assert metadata["dataset"] == "official_ieee_cis_tree_scan_surveillance"
    assert metadata["synthetic_data_used"] is False
    assert metadata["spec_doc"].endswith("23_P_ADIC_TREE_SCAN_CUSUM_Q1_SPEC_AND_DECISION.md")
    assert metadata["figure_dpi"][0] >= 600
    assert metadata["figure_dpi"][1] >= 600
    assert metadata["claim_status"] in {"q1_candidate_tree_scan_passed_controls", "diagnostic_only_failed_q1_tree_scan_gate"}
    assert set(claims["claim_status"]).issubset(
        {"q1_candidate_tree_scan_passed_controls", "diagnostic_only_failed_q1_tree_scan_gate"}
    )
    for key in ("claims_table", "block_features", "metadata", "figure"):
        assert Path(artifacts[key]).exists(), key
