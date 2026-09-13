# Release Status

## Paper

**BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies** is submitted to **ICASSP 2027**.

This repository is the public code companion for that submission. The repository status does not imply acceptance or publication.

## Release

**BLAST-TSAD v1.0.0**

The public scientific interface is considered stable for the submitted paper.

### Included

- BLAST attribution implementation;
- primary causal score construction;
- training-prefix normalization used for M70;
- VUS-PR evaluation helpers;
- U237 development-selection runner;
- M70 label-free scoring runner;
- M70 frozen-delay confirmatory evaluator;
- frozen cohort manifests;
- environment pins;
- tests and continuous integration;
- citation and reproducibility documentation.

### Not distributed in this repository

- manuscript source or submitted PDF;
- paper figures or tables;
- generated numerical paper-result files;
- pointwise/intermediate score archives;
- raw benchmark datasets;
- model checkpoints or caches;
- internal audit/development records.

## Stability policy

The method/protocol surface should not change during review except for a genuine correctness, security, or reproducibility fix. Documentation, citation metadata, and eventual proceedings metadata may be updated without altering the submitted scientific protocol.

If the paper is accepted, proceedings metadata can be added to `CITATION.cff` while keeping the implementation versioned and traceable.
