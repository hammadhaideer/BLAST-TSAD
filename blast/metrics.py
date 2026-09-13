"""Evaluation helpers used by the BLAST public code companion."""

from __future__ import annotations

import numpy as np


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


def official_vus_pr(labels: np.ndarray, scores: np.ndarray) -> float:
    """Compute VUS-PR with the pinned public ``vus`` implementation.

    No pointwise fallback is used: if the official metric is unavailable or
    returns an invalid value, the function raises instead of silently changing
    the metric.
    """

    y = np.asarray(labels).astype(int).reshape(-1)
    s = np.asarray(scores, dtype=np.float64).reshape(-1)
    if len(y) != len(s):
        raise ValueError("labels and scores must have equal length")
    if not np.all(np.isfinite(s)):
        raise ValueError("scores contain non-finite values")

    from vus.metrics import get_metrics

    L_e = entity_buffer_L(y)
    result = get_metrics(s, y, metric="all", slidingWindow=L_e)
    if "VUS_PR" not in result:
        raise RuntimeError("official VUS result contains no VUS_PR")
    value = float(result["VUS_PR"])
    if not np.isfinite(value):
        raise RuntimeError("official VUS returned non-finite VUS_PR")
    return value


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
