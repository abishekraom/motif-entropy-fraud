from motif_fraud.p_adic.reproduce_all import build_reproduction_plan


def test_build_reproduction_plan_contains_real_dataset_commands_only():
    plan = build_reproduction_plan()

    assert plan
    joined = "\n".join(step["command"] for step in plan)
    assert "ieee_pipeline" in joined
    assert "official_baselines" in joined
    assert "vehicle_claim_pipeline" in joined
    assert "temporal_surveillance" in joined
    assert "rich_padic_features" in joined
    assert "branch_signatures" in joined
    assert "multiresolution_operator" in joined
    assert "tree_scan_cusum" in joined
    assert "cse-cic-thursday" in joined
    assert "cse-cic-wednesday" in joined
    assert "tree_scan_theory" in joined
    assert "official_ieee_cis_tree_scan_surveillance_claims.csv" in "\n".join(
        step["artifact_check"] for step in plan
    )
    assert "official_cse_cic_ids2018_thursday_tree_scan_surveillance_claims.csv" in "\n".join(
        step["artifact_check"] for step in plan
    )
    assert "official_cse_cic_ids2018_wednesday_2018_02_28_tree_scan_surveillance_claims.csv" in "\n".join(
        step["artifact_check"] for step in plan
    )
    assert "tree_scan_theory_diagnostics.csv" in "\n".join(
        step["artifact_check"] for step in plan
    )
    assert "synthetic" not in joined.lower()
    for step in plan:
        assert {"name", "command", "artifact_check"}.issubset(step)
