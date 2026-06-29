import pandas as pd

from motif_fraud.p_adic.statistics import bootstrap_metric_delta_ci


def test_bootstrap_metric_delta_ci_reports_reproducible_delta_interval():
    y = pd.Series([0, 0, 1, 1, 0, 1])
    proposed = pd.Series([0.1, 0.2, 0.8, 0.7, 0.3, 0.9])
    control = pd.Series([0.9, 0.8, 0.6, 0.5, 0.7, 0.4])

    ci1 = bootstrap_metric_delta_ci(y, proposed, control, metric="auprc", n_bootstrap=200, seed=5)
    ci2 = bootstrap_metric_delta_ci(y, proposed, control, metric="auprc", n_bootstrap=200, seed=5)

    assert ci1 == ci2
    assert ci1["delta_mean"] > 0
    assert ci1["lower"] <= ci1["delta_mean"] <= ci1["upper"]
    assert 0 <= ci1["p_delta_le_zero"] <= 1
