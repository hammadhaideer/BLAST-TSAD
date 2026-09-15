"""Core BLAST reference implementation.

This module contains the method-level operations used by the public code
companion for the ICASSP 2027 submission. The functions are intentionally
small and repository-relative; they do not depend on manuscript or result
artifacts.

BLAST separates event attribution time from evidence release time. For an
endpoint score q_e and non-negative delay d, the attributed score is

    s_d(t) = q_{t+d}

and that evidence is available only at release time t+d.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

MAD_NORMAL_SCALE = 1.4826
FLOAT64_SCALE_FLOOR_MULTIPLIER = 64.0


@dataclass(frozen=True)
class PrefixNormalization:
    """Robust statistics fitted on a training prefix only."""

    median: np.ndarray
    scale: np.ndarray


def _as_2d_float(x: np.ndarray) -> tuple[np.ndarray, bool]:
    arr = np.asarray(x, dtype=np.float64)
    was_1d = arr.ndim == 1
    if was_1d:
        arr = arr[:, None]
    if arr.ndim != 2:
        raise ValueError("expected a 1-D or 2-D time-series array")
    if not np.all(np.isfinite(arr)):
        raise ValueError("input contains non-finite values")
    return arr, was_1d


def fit_prefix_normalization(
    x: np.ndarray,
    train_index: int,
) -> PrefixNormalization:
    """Fit the exact M70 robust normalization on the training prefix.

    For each channel, the frozen study uses the prefix median and
    ``1.4826 * MAD``. A numerical floor is defined as

    ``64 * eps_float64 * max(1, abs(median))``.

    If the MAD scale is non-finite or does not exceed this floor, the prefix
    sample standard deviation (``ddof=1``) is used when it exceeds the same
    floor; otherwise the scale is set to ``1.0``. These statistics are then
    held fixed for the complete series.
    """

    arr, _ = _as_2d_float(x)
    if not 1 < train_index <= len(arr):
        raise ValueError("train_index must satisfy 1 < train_index <= len(x)")

    prefix = arr[:train_index]
    med = np.median(prefix, axis=0)
    mad = np.median(np.abs(prefix - med), axis=0)
    scale = MAD_NORMAL_SCALE * mad

    for c in range(arr.shape[1]):
        floor = (
            FLOAT64_SCALE_FLOOR_MULTIPLIER
            * np.finfo(np.float64).eps
            * max(1.0, abs(float(med[c])))
        )
        if not np.isfinite(scale[c]) or scale[c] <= floor:
            alt = float(np.std(prefix[:, c], ddof=1))
            if np.isfinite(alt) and alt > floor:
                scale[c] = alt
            else:
                scale[c] = 1.0

    return PrefixNormalization(median=med, scale=scale)


def apply_prefix_normalization(
    x: np.ndarray,
    stats: PrefixNormalization,
) -> np.ndarray:
    """Apply previously fitted training-prefix statistics."""

    arr, was_1d = _as_2d_float(x)
    if arr.shape[1] != stats.median.shape[0]:
        raise ValueError("channel count does not match fitted statistics")
    out = (arr - stats.median) / stats.scale
    if not np.all(np.isfinite(out)):
        raise ValueError("normalization produced non-finite values")
    return out[:, 0] if was_1d else out


def robust_prefix_normalize(
    x: np.ndarray,
    train_index: int,
) -> tuple[np.ndarray, PrefixNormalization]:
    """Fit training-prefix statistics and normalize the complete series."""

    stats = fit_prefix_normalization(x, train_index)
    return apply_prefix_normalization(x, stats), stats


def trailing_sample_std(x: np.ndarray, window: int) -> np.ndarray:
    """Causal trailing sample standard deviation with ``ddof=1``.

    The returned array has the same shape as the input. Positions before the
    first complete trailing window are ``NaN``. For multivariate input the
    statistic is computed independently for each channel.
    """

    arr, was_1d = _as_2d_float(x)
    if window < 2:
        raise ValueError("window must be at least 2")
    if window > len(arr):
        raise ValueError("window exceeds series length")

    n, c = arr.shape
    out = np.full((n, c), np.nan, dtype=np.float64)

    # Cumulative sums give an O(T*C) implementation while preserving the
    # sample-variance definition used in the study.
    cs = np.vstack([np.zeros((1, c)), np.cumsum(arr, axis=0)])
    cs2 = np.vstack([np.zeros((1, c)), np.cumsum(arr * arr, axis=0)])
    sums = cs[window:] - cs[:-window]
    sums2 = cs2[window:] - cs2[:-window]

    numer = sums2 - (sums * sums) / float(window)
    # Numerical cancellation may produce tiny negative values.
    numer = np.maximum(numer, 0.0)
    var = numer / float(window - 1)
    out[window - 1 :] = np.sqrt(var)

    return out[:, 0] if was_1d else out


def scalar_endpoint_score(
    x: np.ndarray,
    window: int = 256,
) -> np.ndarray:
    """Primary causal endpoint score used by the BLAST study.

    For a univariate series this is the trailing sample standard deviation.
    For a multivariate series it is the equal-weight mean of the per-channel
    trailing sample standard deviations at each endpoint.
    """

    std = trailing_sample_std(x, window)
    if std.ndim == 1:
        return std
    return np.mean(std, axis=1)


def make_test_scores(
    endpoint_score: np.ndarray,
    train_index: int,
    delay: int,
    *,
    pad_value: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Create event-time scores for a test region under bounded attribution.

    Parameters
    ----------
    endpoint_score:
        Full-series causal endpoint score ``q_e``.
    train_index:
        First test timestamp in the full series.
    delay:
        Non-negative BLAST delay ``d``.
    pad_value:
        Value stored where ``t+d`` falls beyond the available series. The
        frozen full-length implementation uses ``0.0``.

    Returns
    -------
    scores:
        Full-length test-region attribution array.
    valid:
        Boolean mask for the formal support where evidence exists.
    """

    endpoint = np.asarray(endpoint_score, dtype=np.float64).reshape(-1)
    if not 0 <= train_index < len(endpoint):
        raise ValueError("train_index is outside the endpoint score array")
    if delay < 0:
        raise ValueError("delay must be non-negative")

    n = len(endpoint) - train_index
    if delay > n:
        raise ValueError("delay exceeds test-region length")

    scores = np.full(n, pad_value, dtype=np.float64)
    valid = np.zeros(n, dtype=bool)
    usable = n - delay
    if usable:
        scores[:usable] = endpoint[train_index + delay :]
        valid[:usable] = True
    return scores, valid


def bounded_latency_attribution(
    endpoint_score: np.ndarray,
    delay: int,
    *,
    pad_value: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Attribute an endpoint score stream and expose release-time semantics.

    Returns ``(scores, valid, release_index)`` where ``release_index[t]=t+d``
    on the formal valid support. Invalid right-boundary entries are set to
    ``-1`` in ``release_index``.
    """

    scores, valid = make_test_scores(endpoint_score, 0, delay, pad_value=pad_value)
    release = np.full(len(scores), -1, dtype=np.int64)
    idx = np.flatnonzero(valid)
    release[idx] = idx + delay
    return scores, valid, release


def common_support_pair(
    endpoint_score: np.ndarray,
    delay: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return d=0 and d>0 scores on identical formal temporal support."""

    endpoint = np.asarray(endpoint_score, dtype=np.float64).reshape(-1)
    if delay < 0 or delay > len(endpoint):
        raise ValueError("invalid delay")
    if delay == 0:
        return endpoint.copy(), endpoint.copy()
    return endpoint[:-delay].copy(), endpoint[delay:].copy()
