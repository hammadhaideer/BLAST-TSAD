# Reproducibility

This repository is the stable public code companion for the BLAST paper submitted to ICASSP 2027.

## Reference environment

The submitted study used:

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
python -m pip install -e .
```

or:

```bash
python -m pip install -e .
```

## Repository verification

Install the test dependency and run:

```bash
python -m pip install pytest
pytest
python examples/minimal_example.py
```

The same checks run automatically in GitHub Actions.

## Data preparation

Obtain TSB-AD independently and place the two archives as documented in [`DATA.md`](DATA.md). For strict reproduction, verify the dataset and cohort SHA256 values listed there.

## Public experiment sequence

### U237 development

```bash
python scripts/select_u237_delay.py
```

This computes the primary causal score, evaluates the frozen delay grid, applies the documented paired gates, and selects the smallest passing low-latency candidate.

### M70 label-free scoring

```bash
python scripts/score_m70_label_free.py
```

This stage never converts or inspects label values. It writes local score artifacts under `results/m70_label_free/`.

### M70 confirmation

```bash
python scripts/evaluate_m70_confirmatory.py
```

This stage reads labels only after the score package exists and evaluates the development-frozen delay without a new search.

## Generated outputs

`results/` is ignored by Git. Numerical outputs are generated locally rather than committed to this public repository. This avoids conflating generated files with the implementation and keeps the repository free of manuscript-result disclosure.

## Frozen evidence record

Before submission, the study was frozen and audited in a separate evidence bundle containing:

- exact experiment artifacts;
- pointwise score arrays;
- frozen protocol documents and hashes;
- environment records;
- manuscript snapshot;
- post-freeze robustness and boundary-sensitivity artifacts.

That audit bundle is intentionally not published here. The public repository exposes the method/protocol implementation needed to inspect and rerun the BLAST pipeline without distributing the paper's frozen result package.

## Integrity rules

A reproduction should not alter:

- U237 or M70 cohort membership;
- training-prefix boundaries;
- `W=256` primary score window;
- the frozen delay grid or selection rule;
- the label-free/confirmatory separation;
- VUS-PR metric semantics;
- attribution-time versus release-time causality.

Hardware-dependent runtime may vary; the method itself is CPU-compatible and does not require a GPU.
