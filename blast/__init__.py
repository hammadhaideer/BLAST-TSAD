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
from .metrics import (
    anomaly_segment_lengths,
    entity_buffer_L,
    evaluation_metrics,
    official_vus_metrics,
    official_vus_pr,
    paired_summary,
)
from .provenance import (
    M70_COHORT_SHA256,
    TSB_AD_M_SHA256,
    TSB_AD_U_SHA256,
    U237_COHORT_SHA256,
    require_sha256,
    sha256_file,
)

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
    "evaluation_metrics",
    "official_vus_metrics",
    "official_vus_pr",
    "paired_summary",
    "TSB_AD_U_SHA256",
    "TSB_AD_M_SHA256",
    "U237_COHORT_SHA256",
    "M70_COHORT_SHA256",
    "require_sha256",
    "sha256_file",
]

__version__ = "1.0.2"
