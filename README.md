# BLAST-TSAD

**BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies**

[![CI](https://github.com/hammadhaideer/BLAST-TSAD/actions/workflows/ci.yml/badge.svg)](https://github.com/hammadhaideer/BLAST-TSAD/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Public code companion for the paper **“BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies,” submitted to ICASSP 2027**.

BLAST is a causal score-attribution framework for streaming time-series anomaly detection. It separates the timestamp an anomaly score describes from the later time at which the causal evidence supporting that attribution becomes available.

For an endpoint score \(q_e\) and a non-negative bounded delay \(d\), BLAST attributes

\[
s_d(t) = q_{t+d},
\]

while the evidence is available only at release time

\[
r_d(t) = t+d.
\]

BLAST therefore changes **timestamp attribution only**. It does not retrain the detector, alter the underlying endpoint score stream, use future information before release, or claim earlier alarms or faster intervention.

> **Paper status:** submitted to ICASSP 2027.
>
> **Release status:** stable public code companion, version 1.0.0. Generated paper results, figures, manuscript files, raw datasets, checkpoints, and the private frozen audit bundle are intentionally not published here.

## What is included

This repository is complete for the public implementation/protocol scope of the submission:

- self-contained BLAST attribution implementation;
- causal trailing sample-standard-deviation scoring used by the primary study;
- training-prefix robust normalization used for the multivariate confirmation cohort;
- official VUS-PR evaluation wrapper and per-entity buffer definition;
- U237 development delay-selection runner;
- label-free M70 score-generation runner;
- frozen-delay M70 confirmatory evaluator;
- frozen cohort membership files;
- environment specifications, unit tests, CI, and reproducibility documentation.

Not included:

- manuscript source or submitted PDF;
- paper figures and tables;
- generated numerical result files;
- pointwise score artifacts;
- raw benchmark datasets;
- model checkpoints/caches;
- private audit/provenance bundle.

Those exclusions are deliberate and do not change the public method implementation or protocol.

## Repository layout

```text
.
├── blast/
│   ├── core.py                  BLAST attribution and causal score construction
│   ├── data.py                  TSB-AD readers and label-free data access
│   └── metrics.py               VUS-PR and paired evaluation helpers
├── configs/
│   ├── rangerank_tsbad_confirmatory_237.txt
│   └── rangerank_tsbad_m_confirmatory_70.txt
├── docs/
│   ├── DATA.md
│   ├── PROTOCOL.md
│   ├── REPRODUCIBILITY.md
│   └── RELEASE_STATUS.md
├── examples/
│   └── minimal_example.py
├── scripts/
│   ├── select_u237_delay.py
│   ├── score_m70_label_free.py
│   └── evaluate_m70_confirmatory.py
├── tests/
│   └── test_core.py
├── .github/workflows/ci.yml
├── CITATION.cff
├── LICENSE
├── environment.yml
├── pyproject.toml
└── requirements.txt
```

## Environment

The reference software stack used for the submitted study is:

```text
Python          3.11
NumPy           2.4.4
SciPy           1.17.1
pandas          3.0.3
scikit-learn    1.9.0
vus             0.0.6
```

Create the environment with Conda:

```bash
conda env create -f environment.yml
conda activate blast-tsad
python -m pip install -e .
```

or with pip:

```bash
python -m pip install -e .
```

## Quick verification

Run the unit tests:

```bash
python -m pip install pytest
pytest
```

Run the synthetic method example:

```bash
python examples/minimal_example.py
```

The example contains no paper results; it only verifies attribution/release semantics.

## Data preparation

The study uses the public TSB-AD univariate and multivariate archives. The datasets are not redistributed.

Place independently obtained archives at:

```text
data/
└── tsb_ad/
    ├── TSB-AD-U.zip
    └── TSB-AD-M.zip
```

See [`docs/DATA.md`](docs/DATA.md) for cohort and checksum information.

## Reproduce the public protocol

### 1. U237 development selection

```bash
python scripts/select_u237_delay.py
```

This evaluates the frozen delay grid and applies the development-only operating-point rule documented in [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

### 2. M70 label-free score generation

```bash
python scripts/score_m70_label_free.py
```

The scorer reads feature columns while leaving the label field opaque. It fits normalization on the training prefix only and writes local score artifacts under `results/`.

### 3. M70 confirmation

```bash
python scripts/evaluate_m70_confirmatory.py
```

Only after label-free scores exist does this stage read M70 labels and evaluate the already frozen delay. It does not search for a new delay or retune the score function.

Generated outputs are intentionally ignored by Git.

## Evaluation semantics

The primary metric is **VUS-PR** from the pinned `vus` package. The per-entity buffer is

\[
L_e = \max\left(1,\operatorname{round}(\operatorname{median}\{\text{GT anomaly-run lengths}\})\right).
\]

The public wrapper raises if the official VUS implementation is unavailable instead of silently substituting a different metric.

## Boundary convention

For a delay \(d>0\), formal BLAST support contains only timestamps for which \(t+d\) exists. Full-length stored arrays use right-tail padding for compatibility with the frozen evaluation pipeline. The repository exposes both the formal validity mask and a common-support helper so boundary-sensitive analyses can explicitly exclude invalid tail positions.

## Reproducibility and provenance

The submitted paper was audited against a separately frozen evidence bundle containing scripts, result artifacts, manifests, hashes, environment records, and the manuscript snapshot. That private audit bundle is not part of this public repository.

This repository is the stable public code companion. Scientific semantics, cohort membership, operating-point rules, metric definitions, and causal information-access constraints are documented in [`docs/PROTOCOL.md`](docs/PROTOCOL.md) and [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Citation

Until final proceedings metadata are available, cite the submitted manuscript and repository using [`CITATION.cff`](CITATION.cff). The citation record will require only bibliographic metadata updates if the paper is accepted; the code release itself is intended to remain stable.

## Code availability

<https://github.com/hammadhaideer/BLAST-TSAD>

## License

Code and documentation authored for this repository are released under the [MIT License](LICENSE). TSB-AD, underlying benchmark datasets, the `vus` package, and all other third-party software retain their original licenses and are not redistributed here.
