# BLAST protocol

This document records the protocol implemented by the public code companion for the ICASSP 2027 submission.

## 1. Causal score generation

For an endpoint score `q_e`, BLAST with non-negative delay `d` assigns

```text
s_d(t) = q_(t+d)
```

while the evidence becomes available only at

```text
r_d(t) = t + d.
```

Consequently:

- `d = 0` is endpoint assignment;
- `d > 0` is bounded retrospective attribution;
- BLAST changes timestamp assignment only;
- no future observation is used before its release time;
- BLAST does not claim earlier computation, earlier alarms, or earlier intervention.

## 2. Primary causal score stream

The primary score is a trailing sample standard deviation with

```text
W = 256
```

and `ddof=1`.

For multivariate M70 series, each channel is normalized using statistics fitted only on the training prefix:

1. per-channel median;
2. `1.4826 * MAD` scale;
3. sample-standard-deviation fallback when MAD is unusable;
4. scale `1.0` fallback if both are unusable.

The scalar endpoint score is the mean of the per-channel trailing standard deviations.

## 3. U237 development selection

U237 is the development cohort. Evaluation begins at zero-based raw index

```text
767
```

The fixed delay grid is

```text
D = {0, 32, 64, 96, 127}
```

and the low-latency candidate set is

```text
{32, 64}.
```

For a candidate delay `d`, the development gates versus `d=0` are:

- mean paired VUS-PR gain at least `0.015`;
- median paired gain greater than `0`;
- strict win fraction at least `0.58`;
- two-sided Wilcoxon signed-rank `p < 0.01`.

The operating point is the **smallest passing low-latency delay**. The rule is a bounded-latency operating-point rule, not a search for the metric-maximizing delay.

## 4. Frozen M70 confirmation

The development-selected delay is frozen before M70 confirmation.

M70 processing is deliberately split into two stages.

### Stage A — label-free score generation

`score_m70_label_free.py`:

- reads feature columns only;
- keeps the final CSV label field opaque at byte level;
- fits normalization on the training prefix only;
- computes the causal endpoint score;
- stores `d=0` and frozen-delay score arrays;
- computes no anomaly metric.

### Stage B — confirmatory evaluation

`evaluate_m70_confirmatory.py` then reads labels and evaluates the already generated score artifacts. It does not search for a new delay and does not retune the score function.

## 5. Primary metric

The primary metric is VUS-PR from the pinned `vus==0.0.6` package.

For each entity, the evaluation buffer is

```text
L_e = max(1, round(median ground-truth anomaly-segment length)).
```

The public metric wrapper has no pointwise fallback: if the official VUS implementation cannot run, evaluation fails explicitly.

## 6. Full-length storage and formal support

The frozen pipeline stores full-length test arrays. For `d>0`, entries at the final `d` event timestamps do not have corresponding evidence inside the available sequence and are padded in the stored array.

The method's formal support is the validity mask returned by `blast.core.make_test_scores`. The public implementation also provides `common_support_pair` so matched-support sensitivity checks can explicitly exclude the invalid right boundary from both conditions.

## 7. Cross-detector interpretation

A delay selected on one causal score stream is not assumed to improve every detector. Any transfer experiment is interpreted as a transfer check, not as a second tuning stage.

## 8. Public-release boundary

The repository publishes method code, protocol, cohort manifests, environment pins, tests, and portable runners. It intentionally does not publish the manuscript, figures, generated paper results, pointwise score archives, raw datasets, model checkpoints, or the private audit bundle.
