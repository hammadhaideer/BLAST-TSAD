#!/usr/bin/env python3
"""Minimal method-level BLAST example using synthetic data.

This example demonstrates causal score construction and bounded-latency
attribution only.  It does not reproduce or disclose paper results.
"""

import numpy as np

from blast import bounded_latency_attribution, scalar_endpoint_score


rng = np.random.default_rng(7)
x = rng.normal(size=1024)

endpoint = scalar_endpoint_score(x, window=256)
valid_endpoint = endpoint[255:]

scores, valid, release = bounded_latency_attribution(valid_endpoint, delay=32)

print("endpoint scores:", valid_endpoint.shape)
print("BLAST scores:", scores.shape)
print("valid attributed timestamps:", int(valid.sum()))
print("first release index:", int(release[valid][0]))
print("last valid release index:", int(release[valid][-1]))
