import numpy as np

from blast.metrics import evaluation_metrics, official_vus_pr, paired_summary


def test_official_vus_pr_is_finite():
    y = np.array([0, 0, 1, 1, 0, 0, 1, 0], dtype=int)
    s = np.array([0.05, 0.1, 0.8, 0.9, 0.2, 0.1, 0.7, 0.1])
    value = official_vus_pr(y, s)
    assert np.isfinite(value)


def test_evaluation_metrics_contains_postfreeze_set():
    y = np.array([0, 0, 1, 1, 0, 0, 1, 0], dtype=int)
    s = np.array([0.05, 0.1, 0.8, 0.9, 0.2, 0.1, 0.7, 0.1])
    result = evaluation_metrics(y, s)
    assert set(result) == {"vus_pr", "vus_roc", "ap", "auroc", "L_e"}
    assert all(np.isfinite(result[k]) for k in ("vus_pr", "vus_roc", "ap", "auroc"))


def test_paired_summary_uses_strict_wins():
    base = np.array([1.0, 2.0, 3.0, 4.0])
    cand = np.array([2.0, 2.0, 2.0, 5.0])
    result = paired_summary(cand, base)
    assert result["wins"] == 2
    assert result["losses"] == 1
    assert result["ties"] == 1
    assert result["strict_win_fraction"] == 0.5
