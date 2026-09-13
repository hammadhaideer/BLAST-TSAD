# Reproducibility

This repository is the public implementation accompanying **BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies**, submitted to ICASSP 2027.

## 1. Reference environment

The submitted study used:

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

## 2. Verify the repository

Install the test dependency and run:

```bash
python -m pip install pytest
python scripts/verify_repository.py
pytest
python examples/minimal_example.py
```

GitHub Actions executes the same verification path on every push and pull request to `main`.

## 3. Prepare the data

Obtain the TSB-AD archives independently and place them as described in [`DATA.md`](DATA.md). For strict reproduction, verify the archive and cohort SHA256 values listed there.

## 4. Run the submitted protocol

### U237 development selection

```bash
python scripts/select_u237_delay.py
```

This stage computes the primary causal score stream, evaluates the frozen delay grid, applies the documented development gates, and selects the smallest eligible low-latency delay.

### M70 label-free scoring

```bash
python scripts/score_m70_label_free.py
```

This stage does not parse anomaly labels. It fits normalization only on each training prefix and writes local score artifacts to `results/m70_label_free/`.

### M70 confirmation

```bash
python scripts/evaluate_m70_confirmatory.py
```

This stage reads labels only after the score package exists and evaluates the already frozen delay without a new delay search or score retuning.

## 5. Generated outputs

All generated experiment outputs are written beneath `results/`, which is ignored by Git. The public repository contains the implementation, cohort manifests, environment pins, and rerun protocol rather than committed paper-result files.

## 6. Reproduction invariants

For the submitted protocol, do not change:

- U237 or M70 cohort membership;
- M70 training-prefix boundaries;
- primary score window `W = 256`;
- delay grid or low-latency candidate set;
- development selection thresholds;
- label-free scoring / confirmatory evaluation separation;
- VUS-PR semantics and per-entity buffer definition;
- attribution-time versus evidence-availability semantics.

Hardware-dependent runtime may vary. The BLAST reference implementation is CPU-compatible and does not require a GPU.

## 7. Scientific record

The submitted manuscript was audited against a separately frozen internal evidence record containing exact experiment outputs, hashes, environment information, and post-freeze checks. That record is not required to inspect or rerun the public implementation and is not distributed in this repository.
