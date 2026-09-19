# Reproducibility

This repository is the public implementation accompanying **BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies**, submitted to ICASSP 2027.

The goal of this document is to make the manuscript's controlled BLAST experiment reproducible from the public TSB-AD archives without relying on hidden result files.

## 1. Reference environment

The reference software stack is:

```text
Python          3.11
NumPy           2.4.4
SciPy           1.17.1
pandas          3.0.3
scikit-learn    1.9.0
vus             0.0.6
```

Recommended setup:

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

## 2. Verify the code artifact

Install the test dependency and run:

```bash
python -m pip install pytest
python scripts/verify_repository.py
pytest
python examples/minimal_example.py
```

The verification script checks package/version metadata, author order, cohort hashes, required reproduction files, and the checksums of the browser-friendly documentation figures. GitHub Actions executes the same code-level checks for pull requests and for `main`.

## 3. Prepare TSB-AD

Obtain the public TSB-AD archives independently from the benchmark source and place them at:

```text
data/
└── tsb_ad/
    ├── TSB-AD-U.zip
    └── TSB-AD-M.zip
```

See [`DATA.md`](DATA.md) for the exact archive and cohort SHA256 values. Every experimental runner verifies the relevant hashes and aborts on a mismatch; silently running a different benchmark snapshot is intentionally disallowed.

## 4. One-command manuscript reproduction

After the two verified archives are in place, run:

```bash
python scripts/reproduce_paper.py
```

The command performs, in order:

1. repository/provenance verification;
2. the U237 development-only delay sweep and frozen selection;
3. M70 label-free score generation;
4. M70 confirmatory evaluation using the already frozen operating point;
5. post-freeze AP, AUROC, VUS-ROC, and common-support checks;
6. comparison of all generated manuscript numbers with the frozen ledger.

A successful run ends with:

```text
BLAST_MANUSCRIPT_NUMBERS: PASS
BLAST_PAPER_REPRODUCTION: PASS
```

By default the command removes an existing local `results/` directory before starting so that stale outputs cannot be mistaken for a fresh reproduction. Pass `--keep-results` only when you intentionally want the script to refuse to overwrite an existing result directory.

## 5. Manual reproduction stages

The same pipeline can be run step by step.

### U237 development selection

```bash
python scripts/select_u237_delay.py
```

This stage computes the raw univariate causal Std256 stream, evaluates the frozen delay grid `D={0,32,64,96,127}`, applies the four manuscript eligibility criteria, and selects the smallest passing low-latency candidate from `{32,64}`. The code also checks macro superiority as a redundant consistency assertion implied by the minimum-gain criterion.

### M70 label-free scoring

```bash
python scripts/score_m70_label_free.py
```

This stage parses feature columns while keeping the final CSV label field opaque, fits normalization only on each filename-defined training prefix, computes the fixed endpoint score stream, and writes a SHA256 manifest for the generated pointwise score package. No anomaly metric is computed here.

### M70 confirmation

```bash
python scripts/evaluate_m70_confirmatory.py
```

Before reading labels, this stage verifies the label-free summary, dataset/cohort provenance, and every score-artifact hash. It then evaluates the frozen `d*=32` configuration without another delay search or score retuning.

### Post-freeze robustness

```bash
python scripts/evaluate_postfreeze_robustness.py
```

This reproduces AP, AUROC, and VUS-ROC on both cohorts and the common-support boundary check obtained by removing the final 32 timestamps from both attribution arms.

### Manuscript-number audit

```bash
python scripts/check_paper_results.py
```

This compares freshly generated outputs against the final numerical ledger documented in [`RESULTS.md`](RESULTS.md). The ledger is used only for verification; it is never used by score generation or metric computation.

## 6. Generated outputs

All experiment outputs are written beneath `results/`, which is ignored by Git. Important generated files include:

```text
results/
├── u237_delay_selection/summary.json
├── m70_label_free/
│   ├── label_free_summary.json
│   ├── pointwise_manifest.sha256
│   └── *.npz
├── m70_confirmatory/
│   ├── summary.json
│   └── per_series_70.csv
└── postfreeze_robustness/
    ├── summary.json
    ├── u237_full.csv
    ├── u237_common_support.csv
    ├── m70_full.csv
    └── m70_common_support.csv
```

Generated outputs are intentionally not committed to the repository. This prevents cached numbers from being confused with independently recomputed results.

## 7. Frozen reproduction invariants

For the submitted protocol, do not change:

- U237 or M70 cohort membership;
- the U237 evaluation start (zero-based index 767);
- M70 filename-defined training-prefix boundaries;
- the primary window `W=256`;
- the delay grid or low-latency candidate set;
- the four manuscript development-selection criteria (with the redundant macro-superiority consistency assertion retained in code);
- M70 prefix-normalization semantics;
- label-free scoring / confirmatory evaluation separation;
- VUS-PR semantics and per-entity temporal buffer definition;
- right-boundary handling;
- attribution-time versus evidence-availability semantics.

The reference implementation is CPU-compatible and does not require a GPU. Runtime depends on CPU, storage, and the VUS implementation.

## 8. Scientific record and public scope

The final values to reproduce are listed in [`RESULTS.md`](RESULTS.md). Browser-friendly documentation schematics are provided under [`../assets/paper/`](../assets/paper/) to illustrate the frozen method semantics and headline results. The original manuscript figure files are not part of this code release. None of the documentation figures are read by experimental scripts or affect numerical reproduction.

The submitted manuscript was additionally audited against a separately frozen private evidence bundle containing original experiment outputs, hashes, environment information, and preregistered/post-freeze checks. That private audit record is not required to rerun the public implementation and is not distributed here.
