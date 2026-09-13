"""BLAST public reference implementation."""

from .core import (
    PrefixNormalization,
    apply_prefix_normalization,
    bounded_latency_attribution,
    common_support_pair,
    fit_prefix_normalization,
    make_test_scores,
    robust_prefix_normalize,
    scalar_endpoint_score,
    trailing_sample_std,
)
from .metrics import anomaly_segment_lengths, entity_buffer_L, official_vus_pr, paired_summary

__all__ = [
    "PrefixNormalization",
    "apply_prefix_normalization",
    "bounded_latency_attribution",
    "common_support_pair",
    "fit_prefix_normalization",
    "make_test_scores",
    "robust_prefix_normalize",
    "scalar_endpoint_score",
    "trailing_sample_std",
    "anomaly_segment_lengths",
    "entity_buffer_L",
    "official_vus_pr",
    "paired_summary",
]

__version__ = "1.0.0"
