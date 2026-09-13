# BLAST protocol

This document records the public protocol semantics for BLAST without publishing the manuscript, figures, or generated result package.

## 1. Causal score generation

BLAST operates on a score stream produced causally from observations available up to the physical release time. The attribution rule must never be interpreted as future information becoming available early.

For a detector endpoint score `q_e`, BLAST with delay `d` assigns that score to event time

```text
t = e - d
```

while the supporting evidence is still available only at release time

```text
r_d(t) = t + d.
```

Therefore:

- `d = 0` is endpoint assignment;
- `d > 0` is bounded retrospective attribution;
- BLAST changes timestamp assignment only;
- BLAST does not imply earlier computation, earlier alarms, or earlier intervention.

## 2. Primary score stream

The frozen BLAST study uses a trailing sample-standard-deviation score with window length

```text
W = 256
```

for the primary development and confirmation protocol.

For multivariate data, channel normalization is fitted only on the training prefix before scoring. The frozen implementation uses robust prefix statistics and does not inspect labels during score generation.

## 3. Development selection

The U237 development cohort is used to evaluate a fixed delay grid and choose a bounded-latency operating point. The selection decision is made on development data only.

The development cohort file is tracked under `configs/` in the current public snapshot.

The operating-point selection protocol is frozen before the independent M70 confirmation step.

## 4. M70 confirmation

M70 score generation is performed before confirmatory label evaluation. The scorer intentionally treats the label field as unavailable during score construction.

The M70 analysis then evaluates the already generated score artifacts using the frozen delay selected during development.

The confirmation stage must not search for a new delay or retune the detector on M70 labels.

## 5. Metrics

The primary paper metric is VUS-PR, evaluated with the pinned `vus` package used by the frozen study. Secondary metrics are treated as post-freeze robustness checks rather than as criteria for choosing the operating point.

## 6. Boundary handling

The frozen implementation stores full-length score arrays for downstream evaluation. The final manuscript distinguishes the formal valid support of bounded attribution from implementation-level boundary padding. A separate common-support sensitivity analysis was performed after the primary result was frozen.

## 7. Cross-detector transfer

A frozen-delay transfer check is used to test whether the selected attribution delay generalizes automatically to another causal score stream. This is a transfer test, not a second tuning stage.

## 8. Public-release scope

This repository intentionally excludes generated result files, figures, manuscript source, raw datasets, model checkpoints, and the internal audit archive. Those exclusions do not change the protocol above.
