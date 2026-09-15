# Comparison Scope and Information Access

The ICASSP 2027 submission makes one primary controlled comparison and one explicitly contextual external comparison. Keeping those roles separate is important for interpreting BLAST correctly.

## Controlled BLAST comparison

The scientific claim holds the causal endpoint-score stream fixed and changes only timestamp attribution:

```text
d = 0        conventional endpoint assignment
d = 32       frozen BLAST attribution
```

For the primary Std256 score stream, the following are identical across the two arms:

- source time series;
- preprocessing;
- window `W = 256`;
- endpoint-score values `q_e`;
- detector/scoring parameters;
- information available at each endpoint.

Only the timestamp attached to the endpoint score changes. For `d>0`, the score remains available only at its original endpoint time.

## Contextual TimeRCD comparison

The manuscript additionally reports a reproduced TimeRCD VUS-PR value of **0.2101** on the M70 evaluation region. TimeRCD uses a different **full-series zero-shot inference** protocol. It is therefore included only as context and must not be described as an interchangeable causal baseline for BLAST.

The primary BLAST claim remains the paired comparison against the same Std256 stream at `d=0`.

## Third-party provenance

The TSB-AD benchmark repository used for dataset provenance is:

```text
https://github.com/TheDatumOrg/TSB-AD
```

Third-party methods and datasets retain their own licenses and repositories. BLAST-TSAD does not vendor them.

## Interpretation rule

A better VUS-PR after attribution means improved temporal agreement with anomaly intervals under the declared evidence delay. It does **not** establish an earlier alarm or faster information access.
