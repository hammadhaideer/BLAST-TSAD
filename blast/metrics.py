"""Evaluation helpers used by the BLAST public code companion."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


VUS_VERSION = "opt"
VUS_THRESHOLD_COUNT = 250


def anomaly_segment_lengths(labels: np.ndarray) -> list[int]:
    """Lengths of maximal contiguous anomaly runs in a binary label array."""

    y = np.asarray(labels).astype(int).reshape(-1)
    if not np.all((y == 0) | (y == 1)):
        raise ValueError("labels must be binary")
    if y.sum() == 0:
        return []
    padded = np.concatenate([[0], y, [0]])
    diff = np.diff(padded)
    starts = np.where(diff == 1)[0]
    ends = np.where(diff == -1)[0]
    return list((ends - starts).astype(int))


def entity_buffer_L(labels: np.ndarray) -> int:
    """Per-entity VUS buffer used in the submitted study.

    ``L_e = max(1, round(median anomaly-segment length))``.
    """

    segs = anomaly_segment_lengths(labels)
    if not segs:
        return 1
    return int(max(1, round(float(np.median(segs)))))


def _validated_pair(labels: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    y = np.asarray(labels).astype(int).reshape(-1)
    s = np.asarray(scores, dtype=np.float64).reshape(-1)
    if len(y) != len(s):
        raise ValueError("labels and scores must have equal length")
    if not np.all((y == 0) | (y == 1)):
        raise ValueError("labels must be binary")
    if not np.all(np.isfinite(s)):
        raise ValueError("scores contain non-finite values")
    return y, s


def official_vus_metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    """Compute VUS-PR/VUS-ROC with the exact pinned public VUS call.

    The frozen audit used ``vus==0.0.6`` with ``version='opt'`` and
    ``thre=250``. No pointwise or alternative fallback is permitted.
    """

    y, s = _validated_pair(labels, scores)
    from vus.metrics import get_metrics

    L_e = entity_buffer_L(y)
    result = get_metrics(
        s,
        y,
        metric="all",
        version=VUS_VERSION,
        slidingWindow=L_e,
        thre=VUS_THRESHOLD_COUNT,
    )
    missing = {"VUS_PR", "VUS_ROC"} - set(result)
    if missing:
        raise RuntimeError(f"official VUS result missing keys: {sorted(missing)}")
    values = {
        "vus_pr": float(result["VUS_PR"]),
        "vus_roc": float(result["VUS_ROC"]),
        "L_e": int(L_e),
    }
    if not np.isfinite(values["vus_pr"]) or not np.isfinite(values["vus_roc"]):
        raise RuntimeError("official VUS returned a non-finite value")
    return values


def official_vus_pr(labels: np.ndarray, scores: np.ndarray) -> float:
    """Return VUS-PR from the exact frozen VUS configuration."""

    return official_vus_metrics(labels, scores)["vus_pr"]


def evaluation_metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    """Return the post-freeze metric set used in the manuscript."""

    y, s = _validated_pair(labels, scores)
    vus = official_vus_metrics(y, s)
    classes = set(np.unique(y).tolist())
    if classes != {0, 1}:
        raise ValueError(f"AUROC requires both classes, found {sorted(classes)}")
    values = {
        "vus_pr": vus["vus_pr"],
        "vus_roc": vus["vus_roc"],
        "ap": float(average_precision_score(y, s)),
        "auroc": float(roc_auc_score(y, s)),
        "L_e": int(vus["L_e"]),
    }
    if not all(np.isfinite(v) for k, v in values.items() if k != "L_e"):
        raise RuntimeError(f"non-finite metric result: {values}")
    return values


def paired_summary(candidate: np.ndarray, baseline: np.ndarray) -> dict[str, float | int]:
    """Paired descriptive statistics plus two-sided Wilcoxon test."""

    from scipy.stats import wilcoxon

    a = np.asarray(candidate, dtype=np.float64).reshape(-1)
    b = np.asarray(baseline, dtype=np.float64).reshape(-1)
    if a.shape != b.shape or a.size == 0:
        raise ValueError("paired arrays must be non-empty and equal-sized")
    delta = a - b
    wins = int(np.sum(delta > 0))
    losses = int(np.sum(delta < 0))
    ties = int(np.sum(delta == 0))

    if np.all(delta == 0):
        stat, p = 0.0, 1.0
    else:
        stat, p = wilcoxon(
            delta,
            alternative="two-sided",
            zero_method="wilcox",
            correction=False,
            method="approx",
        )
        stat, p = float(stat), float(p)

    return {
        "mean_delta": float(np.mean(delta)),
        "median_delta": float(np.median(delta)),
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "strict_win_fraction": float(wins / len(delta)),
        "wilcoxon_stat": stat,
        "wilcoxon_p": p,
    }
