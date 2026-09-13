import numpy as np

from blast import (
    bounded_latency_attribution,
    common_support_pair,
    entity_buffer_L,
    fit_prefix_normalization,
    make_test_scores,
    trailing_sample_std,
)


def test_trailing_sample_std_matches_numpy():
    x = np.arange(1.0, 9.0)
    w = 4
    got = trailing_sample_std(x, w)
    assert np.isnan(got[: w - 1]).all()
    expected = [np.std(x[i - w + 1 : i + 1], ddof=1) for i in range(w - 1, len(x))]
    np.testing.assert_allclose(got[w - 1 :], expected, rtol=1e-12, atol=1e-12)


def test_prefix_normalization_uses_prefix_only():
    x = np.array([[1.0], [2.0], [3.0], [1000.0]])
    stats = fit_prefix_normalization(x, train_index=3)
    np.testing.assert_allclose(stats.median, [2.0])
    # A future outlier must not affect prefix-fitted statistics.
    x2 = x.copy()
    x2[-1, 0] = 1e9
    stats2 = fit_prefix_normalization(x2, train_index=3)
    np.testing.assert_allclose(stats.median, stats2.median)
    np.testing.assert_allclose(stats.scale, stats2.scale)


def test_bounded_latency_shift_and_release_semantics():
    q = np.arange(10.0)
    s, valid, release = bounded_latency_attribution(q, delay=3)
    np.testing.assert_allclose(s[:7], q[3:])
    np.testing.assert_allclose(s[7:], 0.0)
    assert valid.tolist() == [True] * 7 + [False] * 3
    np.testing.assert_array_equal(release[:7], np.arange(3, 10))
    np.testing.assert_array_equal(release[7:], [-1, -1, -1])


def test_make_test_scores_matches_frozen_full_length_convention():
    endpoint = np.arange(20.0)
    scores, valid = make_test_scores(endpoint, train_index=5, delay=4)
    np.testing.assert_allclose(scores[:11], endpoint[9:])
    np.testing.assert_allclose(scores[11:], 0.0)
    assert valid.sum() == 11


def test_common_support_pair():
    q = np.arange(8.0)
    d0, d2 = common_support_pair(q, delay=2)
    np.testing.assert_allclose(d0, [0, 1, 2, 3, 4, 5])
    np.testing.assert_allclose(d2, [2, 3, 4, 5, 6, 7])


def test_entity_buffer_median_segment_length():
    y = np.array([0, 1, 1, 0, 0, 1, 1, 1, 1, 0])
    # Segment lengths are 2 and 4; median is 3.
    assert entity_buffer_L(y) == 3
