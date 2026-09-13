<div align="center">

# BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies

**Official implementation for the ICASSP 2027 submission**

Hammad Ali Haider¹ · Marcin Pietroń² · Roberto Corizzo³ · Panpan Zheng¹

¹ Xinjiang University · ² AGH University of Krakow · ³ American University

[![CI](https://github.com/hammadhaideer/BLAST-TSAD/actions/workflows/ci.yml/badge.svg)](https://github.com/hammadhaideer/BLAST-TSAD/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/Paper-ICASSP%202027%20Submission-8A2BE2.svg)](#citation)

</div>

## Overview

**BLAST** is a causal score-attribution framework for streaming time-series anomaly detection. It addresses a simple but important timing question: a causal detector may only accumulate enough evidence for an event *after* the event begins, so the time described by a score and the time at which that score becomes available need not be the same.

For a causal endpoint score \(q_e\) and a non-negative delay \(d\), BLAST defines

\[
s_d(t)=q_{t+d}, \qquad r_d(t)=t+d,
\]

where \(s_d(t)\) is the score attributed to timestamp \(t\), while \(r_d(t)\) records when the supporting evidence is actually available.

> **BLAST changes score attribution, not evidence availability.** A positive delay enables retrospective localization under an explicit latency budget; it does not make the score available earlier, retrain the detector, or change the underlying causal score stream.

### Highlights

- **Causal by construction** — every score is computed only from observations available at its declared release time.
- **Bounded-latency attribution** — event attribution time and evidence-availability time are represented explicitly.
- **Detector-preserving** — BLAST changes timestamp assignment while leaving score generation and detector parameters unchanged.
- **Frozen development-to-confirmation protocol** — the operating delay is selected on development data and transferred unchanged to independent confirmation.
- **Label-free confirmatory scoring** — confirmation scores are generated before labels are used for evaluation.
- **Official VUS-PR evaluation** — the public implementation uses the pinned VUS metric implementation and the same per-entity tolerance definition used by the study.

**Code:** <https://github.com/hammadhaideer/BLAST-TSAD>

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
│   ├── evaluate_m70_confirmatory.py
│   └── verify_repository.py
├── tests/
│   ├── test_core.py
│   └── test_data.py
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

Verify the public release invariants:

```bash
python scripts/verify_repository.py
```

Run the unit tests:

```bash
python -m pip install pytest
pytest
```

Run the synthetic method example:

```bash
python examples/minimal_example.py
```

The example contains no paper results; it only verifies attribution/release semantics. These checks also run in GitHub Actions.

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
