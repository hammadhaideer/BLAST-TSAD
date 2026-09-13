# BLAST-TSAD

**Bounded-Latency Attribution of Streaming Time-Series Anomalies**

BLAST is a causal score-attribution framework for streaming time-series anomaly detection. It separates the timestamp an anomaly score is intended to describe from the later time at which the evidence supporting that attribution becomes available.

The central design goal is simple: preserve causal information access while allowing a bounded amount of retrospective attribution. BLAST changes timestamp assignment only; it does not retrain the detector, alter the underlying score stream, or claim earlier alarm delivery.

> **Paper status:** manuscript in preparation for ICASSP 2027.
>
> **Repository status:** public code companion. The frozen experimental record is maintained separately from this repository. Manuscript files, figures, generated results, raw datasets, checkpoints, and internal audit artifacts are intentionally not tracked here.

## Method at a glance

For a causal detector score \(q_e\) released at endpoint \(e\), BLAST attributes the score to an earlier event time \(t=e-d\), where \(d\) is an explicitly bounded delay. The evidence remains available only at release time \(t+d\).

This distinction is important:

- **attribution time** describes which event timestamp receives the score;
- **release time** describes when the causal evidence actually exists;
- BLAST does **not** use future information before release;
- BLAST does **not** claim faster computation, earlier alerts, or earlier intervention.

The experimental protocol uses development data to select a bounded operating point and freezes that choice before independent confirmation.

## Public repository scope

Included here:

- core BLAST scoring and confirmatory-analysis scripts;
- frozen cohort configuration files;
- environment/dependency specifications;
- protocol and data-layout documentation;
- software citation metadata.

Intentionally excluded:

- manuscript source and submitted PDF;
- figures and paper tables;
- generated numerical results;
- pointwise/intermediate score arrays;
- raw benchmark datasets;
- model checkpoints and caches;
- private machine paths and internal audit material.

The exclusion of generated outputs is deliberate: this repository is intended to expose the implementation and protocol without publishing the manuscript or its result package before the submission workflow is complete.

## Repository layout

```text
.
├── configs/                         frozen cohort lists
├── docs/
│   ├── DATA.md                      expected dataset layout
│   ├── PROTOCOL.md                  BLAST protocol and causal semantics
│   ├── REPRODUCIBILITY.md           environment and execution notes
│   └── RELEASE_STATUS.md            public-release status
├── scripts/
│   ├── analyze_latency_alignment_tsbadm_confirmatory.py
│   └── score_latency_alignment_tsbadm_labelfree.py
├── CITATION.cff
├── environment.yml
└── requirements.txt
```

## Environment

Reference environment used for the frozen study:

- Python 3.11
- NumPy 2.4.4
- SciPy 1.17.1
- pandas 3.0.3
- scikit-learn 1.9.0
- `vus` 0.0.6

Create the lightweight public environment with Conda:

```bash
conda env create -f environment.yml
conda activate blast-tsad
```

or install the Python dependencies directly:

```bash
python -m pip install -r requirements.txt
```

See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) for the exact release status and dependency notes.

## Data

BLAST uses the public TSB-AD benchmark archives in the frozen study. The datasets are **not redistributed** in this repository. Place locally obtained benchmark archives under the layout documented in [`docs/DATA.md`](docs/DATA.md).

## Protocol

The public protocol documentation records the separation between development selection and frozen confirmation, the bounded-delay semantics, and the label-free M70 scoring requirement. See [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

## Citation

If you use this repository, please cite the BLAST paper once a final bibliographic record is available. Software citation metadata is provided in [`CITATION.cff`](CITATION.cff).

## Code availability

Public repository:

<https://github.com/hammadhaideer/BLAST-TSAD>

## License

A repository-wide software license will be added only after the final source-provenance audit is complete. Third-party datasets, metrics packages, models, and external implementations retain their own licenses and are not redistributed here.
