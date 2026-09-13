# Protocol

This document records the public experimental protocol for **BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies**, submitted to ICASSP 2027.

## 1. Causal score generation

At arrival index `e`, observations through `x_e` are available. For a detector using a trailing window of length `W`, the endpoint score is

```text
q_e = f(x_{e-W+1:e}).
```

BLAST with non-negative delay `d` attributes

```text
s_d(t) = q_{t+d}
r_d(t) = t + d
```

where `s_d(t)` is the score assigned to event timestamp `t`, while `r_d(t)` is the evidence-availability index.

Therefore:

- `d = 0` recovers endpoint assignment;
- `d > 0` is retrospective attribution under an explicit evidence delay;
- score generation is unchanged by BLAST;
- detector parameters are unchanged by BLAST;
- no observation is used before its declared release time;
- BLAST does **not** claim earlier computation, earlier alarms, or earlier intervention.

## 2. Primary causal score stream

The primary score is a trailing sample standard deviation with

```text
W = 256
```

and sample-standard-deviation denominator `W - 1` (`ddof=1`).

### U237

The statistic is applied directly to the raw univariate observations.

### M70

Each channel is normalized using statistics fitted on the training prefix only:

1. per-channel median;
2. scale `1.4826 × MAD`;
3. sample-standard-deviation fallback if the MAD scale is unusable;
4. fallback scale `1.0` if both previous scales are unusable.

The trailing sample standard deviation is computed per channel and then averaged across channels to obtain the scalar endpoint score.

No anomaly labels, centered windows, or temporal smoothing are used in score generation.

## 3. U237 development selection

U237 contains 237 univariate TSB-AD-U series. Evaluation begins at zero-based raw index

```text
767
```

The frozen delay grid is

```text
D = {0, 32, 64, 96, 127}
```

with low-latency candidates

```text
D_low = {32, 64}.
```

For each candidate `d`, paired VUS-PR gains are computed relative to `d = 0`. A candidate is eligible only if all four development conditions hold:

- mean paired gain `>= 0.015`;
- median paired gain `> 0`;
- strict win fraction `>= 0.58`;
- two-sided Wilcoxon signed-rank `p < 0.01`.

The operating point is the **smallest eligible delay in `D_low`**. This is a bounded-latency operating-point rule, not a search for the maximum development metric.

## 4. Frozen M70 confirmation

The selected delay and `W = 256` are frozen before M70 confirmation. M70 contains 70 TSB-AD-M series from 12 dataset families; the evaluation start for each series is the training boundary encoded in its filename.

The public pipeline separates score generation from label-based evaluation.

### Stage A — label-free score generation

`scripts/score_m70_label_free.py`:

- reads feature columns only;
- keeps the final CSV label field opaque at byte level;
- fits normalization only on the training prefix;
- computes the causal endpoint score;
- creates endpoint-assigned and frozen-delay score arrays;
- computes no anomaly metric.

### Stage B — confirmatory evaluation

`scripts/evaluate_m70_confirmatory.py` then reads labels and evaluates the already generated score package. It does not search for another delay and does not retune the score function.

## 5. Primary metric and paired statistics

The primary metric is **VUS-PR** from the pinned `vus==0.0.6` package.

For each series, the temporal tolerance buffer is

```text
L_e = max(1, round(median ground-truth anomaly-segment length)).
```

The public wrapper calls the official VUS implementation directly. If VUS cannot be computed, evaluation fails explicitly rather than falling back to a different metric.

Paired comparisons use strict wins and a two-sided Wilcoxon signed-rank test with:

```text
zero_method = "wilcox"
correction  = False
method      = "approx"
```

## 6. Formal support and right boundary

For delay `d > 0`, the final `d` event timestamps have no corresponding endpoint score inside the observed sequence. The frozen implementation stores full-length arrays and pads those invalid right-boundary entries with zero.

The formal support is returned explicitly by `blast.core.make_test_scores`. The helper `blast.core.common_support_pair` evaluates `d = 0` and `d > 0` on identical valid support when a common-support sensitivity analysis is required.

## 7. Interpretation

BLAST measures how timestamp attribution changes agreement between a fixed causal score stream and event labels at an explicitly declared evidence delay. A localization gain does not establish an earlier alarm.

A delay selected on one score stream is not assumed to improve every detector. Cross-detector evaluation is therefore interpreted as a transfer check, not as a second tuning stage.
