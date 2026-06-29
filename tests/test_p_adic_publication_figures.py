from pathlib import Path

import pytest

from motif_fraud.p_adic.publication_figures import generate_ieee_publication_figures


BLOCKS = Path("outputs/p_adic_ieee_cis_official/metrics/p_adic_ieee_cis_temporal_blocks.csv")
CLAIMS = Path("outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_claims.csv")
BASELINES = Path("outputs/p_adic_ieee_cis_official/tables/p_adic_ieee_cis_baseline_comparison.csv")


@pytest.mark.skipif(
    not (BLOCKS.exists() and CLAIMS.exists() and BASELINES.exists()),
    reason="official IEEE-CIS run artifacts are required; synthetic figures are forbidden",
)
def test_generate_ieee_publication_figures_from_official_artifacts(tmp_path):
    result = generate_ieee_publication_figures(
        temporal_blocks_path=BLOCKS,
        claims_path=CLAIMS,
        baseline_path=BASELINES,
        output_root=tmp_path,
    )

    assert result["temporal_signal"].exists()
    assert result["control_ablation"].exists()
    assert result["baseline_comparison"].exists()
    for dpi in result["dpi"].values():
        assert dpi[0] >= 300
        assert dpi[1] >= 300
