# Baselines and Information Access

The submitted paper separates the controlled BLAST comparison from contextual detector comparisons. This document records that distinction without publishing numerical paper results.

## Controlled BLAST comparison

The primary causal comparison holds the underlying endpoint score stream fixed and changes only timestamp attribution:

```text
d = 0        endpoint assignment
d = d*       BLAST bounded-latency attribution
```

For the primary Std256 stream, score generation, window length, preprocessing, and detector parameters are identical across the two attribution conditions.

## Information-access protocol codes

The broader M70 comparison contains methods with different information-access assumptions. They are therefore contextual detector references rather than strictly interchangeable causal competitors.

| Code | Protocol | Methods used in the submitted comparison |
|---|---|---|
| `B` | Pinned TSB-AD benchmark-wrapper protocol | PCA, KMeansAD, IForest, EIF, COPOD, HBOS, LOF |
| `P` | Training on the normal prefix with full-query score-vector standardization | PaAno-PAI |
| `S` | Training on the normal prefix and scoring the test region; not presented as sample-causal evidence | STREAM-VAE |
| `F` | Full-series zero-shot inference | Time-RCD |
| `C` | Causal score generation with explicitly declared BLAST attribution delay | Std256 / BLAST |

Because these access protocols differ, the paper treats the broader benchmark as context. The controlled scientific claim is the paired attribution comparison on the same fixed causal score stream.

## Pinned TSB-AD reference

Classical benchmark wrappers and the HSF causal transfer check were tied to the TSB-AD repository snapshot recorded by the submission:

```text
repository: https://github.com/TheDatumOrg/TSB-AD
commit:     e0975a5f7d3e65ab77e9fab24d1b5b51acda8f48
```

This repository does not vendor TSB-AD or third-party baseline implementations. Their original licenses and repositories remain authoritative.

## Cross-detector transfer

The submitted study also transfers the development-selected BLAST delay to a second fixed causal score stream (HSF causal) without running a rescue-delay search. This is a transfer check of the attribution rule, not a second operating-point tuning stage.

## Reproduction guidance

For BLAST itself, use the public runners in this repository and the frozen cohort manifests in `configs/`. For third-party methods, use the corresponding original implementation or the pinned TSB-AD snapshot under its own licensing terms, while preserving the information-access protocol described above.
