# Public release status

## Status

**BLAST-TSAD v1.0.0 — stable public code companion for the ICASSP 2027 submission.**

This repository is public and may be linked directly from the submitted manuscript.

## Public scope

Included:

- self-contained BLAST reference implementation;
- primary causal score construction;
- robust training-prefix normalization;
- VUS-PR evaluation helpers;
- U237 development-selection runner;
- M70 label-free scoring runner;
- M70 frozen-delay confirmatory evaluator;
- frozen cohort manifests;
- environment pins, tests, CI, citation metadata, and documentation.

Intentionally not included:

- manuscript source or submitted PDF;
- figures or paper tables;
- generated paper-result files;
- pointwise/intermediate score archives;
- raw benchmark datasets;
- model checkpoints/caches;
- private audit bundle and internal development logs.

## Stability policy

The public method/protocol surface is frozen for the submission. Changes should be limited to genuine correctness fixes, security fixes, or bibliographic metadata updates. If the paper receives final proceedings metadata, `CITATION.cff` may be updated without changing the scientific implementation.

## Paper status

Submitted to ICASSP 2027. This repository does not imply acceptance or publication.
