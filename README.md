<div align="center">

# BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies

**Reference implementation and reproducibility companion for the ICASSP 2027 submission**

Hammad Ali Haider¹ · Marcin Pietroń² · Roberto Corizzo³ · Panpan Zheng¹

¹ Xinjiang University · ² AGH University of Krakow · ³ American University

[![CI](https://github.com/hammadhaideer/BLAST-TSAD/actions/workflows/ci.yml/badge.svg)](https://github.com/hammadhaideer/BLAST-TSAD/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg)](https://www.python.org/)
[![Release](https://img.shields.io/badge/release-v1.0.1-2ea44f.svg)](#release-status)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ICASSP 2027](https://img.shields.io/badge/ICASSP-2027%20Submission-6A5ACD.svg)](#citation)

[**Overview**](#overview) · [**Method**](#method-and-causal-semantics) · [**Results**](#main-results) · [**Reproduce**](#reproduce-the-paper) · [**Data**](#data-preparation) · [**Protocol**](docs/PROTOCOL.md) · [**Result Ledger**](docs/RESULTS.md) · [**Citation**](#citation)

</div>

---

## Overview

**BLAST** is a bounded-latency attribution framework for causal streaming time-series anomaly scores. It addresses a timing distinction that is easy to hide in sliding-window anomaly detection: the timestamp to which a score is attributed can differ from the time at which the evidence supporting that score actually becomes available.

For a causal endpoint score `q_e` and a non-negative delay `d`, BLAST defines

\[
s_d(t)=q_{t+d}, \qquad r_d(t)=t+d,
\]

where `s_d(t)` is the score attributed to event timestamp `t`, while `r_d(t)` records its evidence-availability index.

> **BLAST changes timestamp attribution only.** It does not retrain the detector, change the endpoint-score values, access observations before they arrive, or claim earlier alarm delivery.

<p align="center">
  <img src="assets/paper/Figure2_BLAST_final.png" width="900" alt="BLAST workflow: causal score generation, bounded-latency attribution, and frozen development-to-confirmation protocol">
</p>

<p align="center"><em>BLAST workflow: a fixed causal endpoint score is reattributed under an explicit evidence delay; the operating point is selected on U237 and frozen before M70 confirmation.</em></p>

### Research artifact status

| Item | Status |
|---|---|
| Paper | ICASSP 2027 submission |
| Public code release | **v1.0.1** |
| Primary implementation | Python 3.11 |
| Primary detector stream | causal trailing sample standard deviation (`W=256`) |
| Frozen operating delay | `d*=32` samples |
| Primary metric | VUS-PR |
| CI | GitHub Actions |
| License | MIT |

## Method and causal semantics

At arrival index `e`, only observations through `x_e` are available. The primary experiment uses the causal endpoint statistic

\[
q_e = \operatorname{Std}_{\mathrm{sample}}(x_{e-W+1:e}), \qquad W=256.
\]

BLAST then attributes the already computed endpoint score to an earlier event timestamp while retaining its actual release time. The detector, score values, window, preprocessing, and model parameters remain fixed across `d=0` and `d>0`.

<p align="center">
  <img src="assets/paper/Figure1.png" width="430" alt="Endpoint assignment versus BLAST attribution">
</p>

<p align="center"><em>Endpoint assignment versus BLAST attribution. For `d>0`, the score assigned to `t` remains available only at `t+d`.</em></p>

The submitted study uses a frozen development → confirmation protocol:

1. **U237 development:** evaluate `D={0,32,64,96,127}` using the fixed Std256 stream;
2. **low-latency candidates:** only `{32,64}` are eligible for operating-point selection;
3. **selection rule:** choose the smallest candidate satisfying every predeclared development gate;
4. **freeze:** `d*=32` is selected and frozen;
5. **M70 confirmation:** generate scores without parsing anomaly labels, then evaluate the already frozen configuration.

The exact causal semantics, five selection gates, normalization rule, label-access protocol, VUS call, and right-boundary convention are documented in [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

## Main results

The controlled comparison changes only temporal attribution of the same causal Std256 endpoint-score stream.

| Cohort | `d=0` VUS-PR | `d=32` VUS-PR | Absolute gain | Wins | Wilcoxon `p` |
|---|---:|---:|---:|---:|---:|
| U237 development | 0.3043 | **0.3300** | +0.0257 | 183 / 237 | 3.85e-22 |
| M70 confirmation | 0.1705 | **0.2089** | +0.0384 | 54 / 70 | 2.65e-7 |

On M70, the frozen setting yields a **22.6% relative macro VUS-PR increase** without retuning. Family-balanced VUS-PR changes from **0.2427 to 0.2784**, and all 12 family mean VUS-PR gains are positive.

<p align="center">
  <img src="assets/paper/Figure3_M70_family_gain_FINAL.png" width="520" alt="Family-wise M70 mean VUS-PR gains at the frozen delay d*=32">
</p>

<p align="center"><em>Family-wise M70 confirmation at the frozen `d*=32`; all 12 family mean VUS-PR gains are positive.</em></p>

Post-freeze checks also evaluate AP, AUROC, VUS-ROC, and common temporal support. The M70 AUROC increase is reported transparently as **not statistically significant** (`p=0.0657`). The complete final tables, including the U237 latency sweep and right-edge sensitivity check, are in [`docs/RESULTS.md`](docs/RESULTS.md).

## Installation

Clone the repository and create the reference environment:

```bash
git clone https://github.com/hammadhaideer/BLAST-TSAD.git
cd BLAST-TSAD
conda env create -f environment.yml
conda activate blast-tsad
python -m pip install -e .
```

A pip-only installation is also supported:

```bash
python -m pip install -e .
```

Reference stack:

```text
Python          3.11
NumPy           2.4.4
SciPy           1.17.1
pandas          3.0.3
scikit-learn    1.9.0
vus             0.0.6
```

## Quick verification

The repository includes invariant checks, unit tests, CI, and a synthetic example that requires no benchmark data:

```bash
python -m pip install pytest
python scripts/verify_repository.py
pytest
python examples/minimal_example.py
```

A successful invariant check ends with:

```text
BLAST_PUBLIC_REPOSITORY_VERIFICATION: PASS
```

## Data preparation

The experiments use the public [TSB-AD](https://github.com/TheDatumOrg/TSB-AD) benchmark. Raw datasets are **not** redistributed here.

Place independently obtained archives at:

```text
data/
└── tsb_ad/
    ├── TSB-AD-U.zip
    └── TSB-AD-M.zip
```

The public runners verify the frozen SHA256 values before computation. Exact archive hashes, cohort hashes, filename-defined M70 training boundaries, and label-handling rules are documented in [`docs/DATA.md`](docs/DATA.md).

## Reproduce the paper

After the two verified TSB-AD archives are in place, the controlled manuscript experiment and robustness checks can be regenerated with one command:

```bash
python scripts/reproduce_paper.py
```

The pipeline executes:

```text
repository/provenance verification
        ↓
U237 delay selection
        ↓
M70 label-free score generation
        ↓
M70 frozen confirmatory evaluation
        ↓
post-freeze metric + common-support checks
        ↓
exact manuscript-number audit
```

A successful complete reproduction ends with:

```text
BLAST_MANUSCRIPT_NUMBERS: PASS
BLAST_PAPER_REPRODUCTION: PASS
```

For a stage-by-stage walkthrough and generated-output layout, see [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

### Manual stages

```bash
python scripts/select_u237_delay.py
python scripts/score_m70_label_free.py
python scripts/evaluate_m70_confirmatory.py
python scripts/evaluate_postfreeze_robustness.py
python scripts/check_paper_results.py
```

Each experiment script exposes path options through `--help`.

## Reproducibility safeguards

The public implementation deliberately fails instead of silently changing the submitted protocol:

- benchmark and cohort SHA256 mismatches abort execution;
- M70 scoring keeps the final label field opaque until the confirmatory stage;
- M70 pointwise score artifacts are SHA256-manifested before labels are opened;
- VUS evaluation uses the pinned public `vus==0.0.6` implementation;
- invalid/non-finite scores abort rather than falling back to another metric;
- generated paper numbers are checked against a frozen numerical ledger;
- the final `d` right-boundary positions are represented explicitly and a common-support sensitivity analysis is reproduced separately.

## Repository structure

```text
BLAST-TSAD/
├── assets/paper/                  # final paper figures used for documentation
├── blast/
│   ├── core.py                    # attribution, Std256, exact M70 normalization
│   ├── data.py                    # TSB-AD readers and label-free feature access
│   ├── metrics.py                 # VUS/AP/AUROC and paired statistics
│   └── provenance.py              # frozen archive/cohort checksums
├── configs/                       # exact U237 and M70 cohort manifests
├── docs/
│   ├── BASELINES.md
│   ├── DATA.md
│   ├── PROTOCOL.md
│   ├── REPRODUCIBILITY.md
│   ├── RELEASE_STATUS.md
│   └── RESULTS.md                 # final result tables / numerical ledger
├── examples/
│   └── minimal_example.py
├── scripts/
│   ├── select_u237_delay.py
│   ├── score_m70_label_free.py
│   ├── evaluate_m70_confirmatory.py
│   ├── evaluate_postfreeze_robustness.py
│   ├── check_paper_results.py
│   ├── reproduce_paper.py
│   └── verify_repository.py
├── tests/
├── .github/workflows/ci.yml
├── CHANGELOG.md
├── CITATION.cff
├── CONTRIBUTING.md
├── LICENSE
├── environment.yml
├── pyproject.toml
└── requirements.txt
```

## Documentation

- [`docs/PROTOCOL.md`](docs/PROTOCOL.md) — method semantics, exact score construction, delay selection, label access, metrics, and right-boundary handling.
- [`docs/DATA.md`](docs/DATA.md) — TSB-AD provenance, archive/cohort hashes, layout, and M70 training boundaries.
- [`docs/RESULTS.md`](docs/RESULTS.md) — frozen manuscript numbers, main/latency/robustness tables, and interpretation.
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) — one-command and manual reproduction paths.
- [`docs/BASELINES.md`](docs/BASELINES.md) — controlled-vs-contextual comparison policy and information-access assumptions.
- [`docs/RELEASE_STATUS.md`](docs/RELEASE_STATUS.md) — public scope and stability policy.

## Scientific scope

BLAST establishes a controlled improvement in **temporal localization** for the tested causal Std256 score stream under an explicit evidence delay. It does **not** claim:

- earlier computation or earlier access to future observations;
- earlier alarm delivery or earlier intervention;
- that `d*=32` is universally optimal for other detectors or datasets;
- that contextual methods with different information-access protocols are interchangeable causal baselines.

## Public release scope

This repository publishes the implementation, frozen cohort manifests, protocol documentation, final numerical result tables, and final paper figures needed to understand and reproduce the controlled BLAST study.

The manuscript source/PDF, raw benchmark datasets, generated pointwise/per-series result archives, third-party checkpoints, and the private frozen audit/preregistration record are intentionally not distributed.

## Release status

The current public implementation is **v1.0.1**. This release aligns the public code with the frozen audited manuscript protocol and adds end-to-end reproduction/verification without changing the reported scientific results. See [`CHANGELOG.md`](CHANGELOG.md) and [`docs/RELEASE_STATUS.md`](docs/RELEASE_STATUS.md).

## Citation

This repository accompanies the **ICASSP 2027 submission**. Until proceedings metadata are available, please use [`CITATION.cff`](CITATION.cff):

```text
Hammad Ali Haider, Marcin Pietroń, Roberto Corizzo, and Panpan Zheng,
"BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies,"
submitted to ICASSP 2027, 2026.
```

## Contributing

Reproducibility reports and implementation-focused issues are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening an issue or proposing a change.

## License

Code and documentation authored for this repository are released under the [MIT License](LICENSE). TSB-AD, its underlying datasets, `vus`, and other third-party software retain their original licenses.
