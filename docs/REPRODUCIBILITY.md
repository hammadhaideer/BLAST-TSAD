# Reproducibility

This document describes the public reproduction surface of the BLAST code companion.

## Reference software environment

The frozen study was executed with:

```text
Python          3.11
NumPy           2.4.4
SciPy           1.17.1
pandas          3.0.3
scikit-learn    1.9.0
vus             0.0.6
```

Create the public environment with:

```bash
conda env create -f environment.yml
conda activate blast-tsad
```

or:

```bash
python -m pip install -r requirements.txt
```

## Data preparation

Obtain the benchmark archives independently and place them as described in [`DATA.md`](DATA.md).

## Current public execution surface

The current public snapshot exposes the M70 label-free scorer and confirmatory analysis scripts. These scripts preserve the frozen protocol semantics, including the distinction between score generation and confirmatory label evaluation.

The scientific source-of-truth for the submitted study is a separately frozen audit bundle containing exact scripts, manifests, pointwise artifacts, environment records, and checksums. That archive is intentionally not published in this repository during manuscript preparation.

## Why generated results are absent

The repository intentionally does not track generated result tables, score arrays, figures, or manuscript text. This keeps the code companion separate from the paper's frozen evidence package and avoids treating committed output files as the source of truth.

## Exact-reproduction status

The public repository is being brought into dependency closure from the frozen audit record. A release should be treated as **exactly reproducible** only when:

1. every imported local helper is present;
2. all referenced freeze manifests are present;
3. repository-relative paths resolve without machine-specific assumptions;
4. the dataset archive checksums match the frozen record;
5. the public verifier passes from a clean environment.

Until those conditions are satisfied, use this repository as the public code companion rather than as the authoritative frozen evidence archive.

## Integrity principle

Scientific logic should not be rewritten merely to make the repository cleaner. Portability fixes may change paths or packaging, but they must not change detector scores, attribution semantics, cohort membership, frozen operating points, metric definitions, or statistical tests.
