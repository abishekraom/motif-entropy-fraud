import json
from pathlib import Path

import pandas as pd
import pytest

from motif_fraud.p_adic.datasets import DatasetCard, validate_real_dataset_card
from motif_fraud.p_adic.splits import temporal_train_test_split
from motif_fraud.pipeline.p_adic_reproduce import build_q1_manifest


def test_dataset_cards_reject_synthetic_sources_and_missing_official_provenance():
    card = DatasetCard(
        name="PaySim",
        source_type="synthetic",
        official_url="https://www.kaggle.com/datasets/ealaxi/paysim1",
        local_paths=("data/paysim/PS_20174392719_1491204439457_log.csv",),
        target_column="isFraud",
        temporal_column="step",
        allowed_for_primary_claims=False,
        leakage_columns=("oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"),
    )
    result = validate_real_dataset_card(card)
    assert not result.is_valid_for_primary_claims
    assert "synthetic" in " ".join(result.reasons).lower()


def test_temporal_split_is_ordered_disjoint_and_refuses_random_shuffle():
    frame = pd.DataFrame({"time": [3, 1, 2, 4, 5], "label": [0, 0, 1, 0, 1]})
    train, test = temporal_train_test_split(frame, temporal_column="time", train_fraction=0.6)

    assert train["time"].max() <= test["time"].min()
    assert set(train.index).isdisjoint(set(test.index))
    assert len(train) == 3
    assert len(test) == 2

    with pytest.raises(ValueError):
        temporal_train_test_split(frame, temporal_column="time", train_fraction=1.0)


def test_q1_manifest_requires_negative_controls_real_datasets_and_high_dpi_figures(tmp_path):
    artifacts = {
        "dataset_cards": ["docs/rebuild/dataset_cards/ieee_cis.md", "docs/rebuild/dataset_cards/ccf.md"],
        "negative_controls": ["random_digit_map", "random_hierarchy", "flat_categorical"],
        "figures": [{"path": "outputs/figures/fig1.png", "dpi": 600}],
        "claims_table": "outputs/tables/p_adic_claims_table.csv",
    }
    manifest = build_q1_manifest(artifacts=artifacts, output_path=tmp_path / "manifest.json")
    saved = json.loads(Path(manifest["manifest_path"]).read_text())

    assert saved["quality_gate"] == "q1_research_grade_candidate"
    assert set(saved["required_negative_controls_present"]) == {
        "random_digit_map",
        "random_hierarchy",
        "flat_categorical",
    }
    assert saved["minimum_figure_dpi"] == 600
