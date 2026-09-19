# Frozen Experimental Protocol

This document records the public protocol for **BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies**, submitted to ICASSP 2027.

## 1. Causal score generation

At arrival index `e`, observations through `x_e` are available. For a causal detector using a trailing window of length `W`,

```text
q_e = f(x_{e-W+1:e}).
```

BLAST with non-negative integer delay `d` defines

```text
s_d(t) = q_{t+d}
r_d(t) = t + d
```

where `s_d(t)` is the score attributed to event timestamp `t` and `r_d(t)` is its evidence-availability index.

Therefore:

- `d=0` recovers conventional endpoint assignment;
- `d>0` is retrospective attribution under an explicit evidence delay;
- score generation is unchanged by BLAST;
- detector parameters are unchanged by BLAST;
- no observation is used before its declared release time;
- BLAST does **not** claim earlier computation, alarms, or intervention.

## 2. Primary causal score stream

The primary score is the trailing **sample** standard deviation with

```text
W = 256
```

and denominator `W-1` (`ddof=1`).

### U237

The statistic is applied directly to the raw univariate observations. No normalization, smoothing, or learned parameters are used.

### M70

Each channel is normalized using statistics fitted on the training prefix only. For channel `c`:

```text
m_c   = median(prefix_c)
a_c   = 1.4826 * median(|prefix_c - m_c|)
floor = 64 * eps_float64 * max(1, |m_c|)
```

If `a_c` is non-finite or `a_c <= floor`, use the prefix sample standard deviation (`ddof=1`) when that value is finite and greater than the same floor; otherwise use `1.0`.

The complete channel is standardized using the frozen prefix statistics, trailing sample standard deviation is computed independently per channel, and the channel scores are averaged with equal weight.

No anomaly labels, centered windows, temporal smoothing, channel selection, or learned aggregation are used in score generation.

## 3. U237 development selection

U237 contains 237 univariate TSB-AD-U series. Evaluation begins at zero-based raw index

```text
767
```

The frozen delay grid is

```text
D = {0, 32, 64, 96, 127}
```

with predeclared low-latency candidates

```text
D_low = {32, 64}.
```

For each `d`, per-series VUS-PR is compared with `d=0`. A low-latency candidate is eligible only if the four criteria stated in the manuscript all hold:

- absolute macro VUS-PR gain is at least `0.015`;
- median paired gain is positive;
- strict win fraction is at least `0.58`;
- two-sided Wilcoxon signed-rank `p < 0.01`.

The implementation also asserts that the candidate macro VUS-PR exceeds the `d=0` macro. This is a redundant consistency check because an absolute gain of at least `0.015` already implies macro superiority; it does not add a separate selection condition or change the selected operating point.

The operating point is the **smallest eligible delay in `D_low`**. Both 32 and 64 qualify, so the frozen choice is

```text
d* = 32.
```

This is a bounded-latency operating-point rule, not a search for the maximum development metric.

## 4. Frozen M70 confirmation

`W=256` and `d*=32` are frozen before M70 confirmation. M70 contains 70 TSB-AD-M series from 12 dataset families. Evaluation begins at the training boundary encoded in each filename.

The public pipeline deliberately separates scoring from labels.

### Stage A — label-free score generation

[`scripts/score_m70_label_free.py`](../scripts/score_m70_label_free.py):

- verifies the frozen dataset/cohort hashes;
- reads feature columns while leaving the final label field opaque at byte level;
- fits normalization only on the training prefix;
- computes the fixed causal endpoint score;
- creates `d=0` and frozen `d=32` score arrays;
- stores validity masks and a SHA256 manifest;
- computes no anomaly metric.

### Stage B — confirmatory evaluation

[`scripts/evaluate_m70_confirmatory.py`](../scripts/evaluate_m70_confirmatory.py) verifies the label-free package and pointwise SHA256 manifest **before** opening labels. It then evaluates only the already frozen operating point. It does not search for another delay or retune the score function.

M70 is **descriptive confirmation, not a second selection stage**. No pass/fail threshold, acceptance gate, or alternative-delay search is applied to M70. The reported macro score, paired statistics, family-balanced score, and family-wise gains are outputs of the frozen evaluation only.

## 5. Primary metric and paired statistics

The primary metric is VUS-PR from the pinned package:

```text
vus==0.0.6
```

The exact public metric call is equivalent to:

```python
get_metrics(
    scores,
    labels,
    metric="all",
    version="opt",
    slidingWindow=L_e,
    thre=250,
)
```

with per-entity temporal buffer

```text
L_e = max(1, round(median anomaly-segment length)).
```

The implementation fails explicitly if the expected VUS outputs are unavailable; it does not silently substitute another metric.

Paired tests use strict wins and the two-sided Wilcoxon signed-rank configuration:

```text
zero_method = "wilcox"
correction  = False
method      = "approx"
```

## 6. Right-boundary convention

For `d>0`, the final `d` event timestamps have no corresponding future endpoint score inside the observed sequence. The primary implementation stores a full-length array and zero-fills these invalid right-boundary positions while exposing an explicit validity mask.

The post-freeze boundary analysis evaluates both arms on identical support by removing the final 32 timestamps from each stream. This analysis reproduces the paper's common-support check.

## 7. Post-freeze robustness

After `d*=32` was frozen, the study additionally evaluates:

- average precision (AP);
- pointwise AUROC;
- VUS-ROC;
- common-support VUS-PR.

These metrics are **not** used to select `d*`. The M70 AUROC increase is numerical but not conventionally significant (`p=0.0657`), and the repository preserves that fact explicitly.

## 8. Interpretation

BLAST measures how timestamp attribution changes agreement between a fixed causal score stream and event labels at an explicitly declared evidence delay. A localization gain does not establish an earlier alarm.
