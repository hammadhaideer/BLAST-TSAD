# Release Status

## Paper

**BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies** is submitted to **ICASSP 2027**.

This repository is the public code and reproducibility companion for that submission. Repository availability does **not** imply conference acceptance or publication.

## Release

**BLAST-TSAD v1.0.1** — 2026-09-16

The public scientific interface is considered stable for the submitted paper. Version 1.0.1 hardens provenance and reproduction while preserving the frozen scientific protocol and manuscript results.

### Included

- BLAST bounded-latency attribution and release-time semantics;
- exact primary causal Std256 score construction;
- exact M70 training-prefix normalization, including the frozen numerical scale floor and fallback logic;
- exact VUS-PR/VUS-ROC evaluation wrapper used by the study;
- U237 development-selection runner;
- M70 label-free scoring runner and frozen-delay confirmatory evaluator;
- post-freeze AP, AUROC, VUS-ROC, and common-support checks;
- frozen U237 and M70 cohort manifests;
- benchmark/cohort SHA256 provenance checks;
- an end-to-end paper-reproduction command and numerical result checker;
- unit tests and GitHub Actions CI;
- final manuscript result tables and paper-figure documentation assets;
- citation, data, protocol, baseline, reproducibility, and release documentation.

### Not distributed in this repository

- manuscript source or submitted PDF;
- raw benchmark datasets;
- generated per-series/pointwise result archives;
- third-party model checkpoints or caches;
- private audit/development records and preregistration files.

The final paper figures are included only as documentation assets; they are not consumed by the experiment code and do not affect numerical reproduction.

## Stability policy

During review, method semantics, cohort membership, causal information-access rules, frozen operating-point selection, metric definitions, and confirmation protocol should not change except to correct a genuine implementation or reproducibility error. Any such correction must be documented in `CHANGELOG.md`.

Documentation, citation metadata, and eventual proceedings metadata may be updated without changing the submitted scientific protocol. If the paper is accepted, proceedings metadata can be added to `CITATION.cff` while keeping the implementation versioned and traceable.
