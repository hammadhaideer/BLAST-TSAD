# Contributing to BLAST-TSAD

Thank you for your interest in BLAST-TSAD. This repository is maintained primarily as a research artifact accompanying the ICASSP 2027 submission, so changes should preserve the scientific semantics and reproducibility guarantees documented in `docs/PROTOCOL.md` and `docs/REPRODUCIBILITY.md`.

## Reporting a reproducibility issue

When opening an issue, please include:

- operating system;
- Python version;
- package versions or the environment file used;
- the exact command that failed;
- the complete traceback or error message;
- whether the official TSB-AD archive checksums match `docs/DATA.md`;
- whether `python scripts/verify_repository.py` passes.

A minimal reproducible example is strongly preferred.

## Proposed code changes

Before proposing a change, please make sure that it:

1. does not alter the causal information-access semantics of BLAST without explicit discussion;
2. does not silently change the frozen U237 or M70 cohort manifests;
3. does not substitute a different metric implementation when official VUS-PR is unavailable;
4. does not introduce label access into the M70 label-free scoring stage;
5. preserves the distinction between event attribution time and evidence-availability time;
6. includes or updates tests when behavior changes.

Run the local validation suite before submitting a change:

```bash
python scripts/verify_repository.py
pytest
python examples/minimal_example.py
```

## Data and generated artifacts

Raw TSB-AD archives, generated result files, pointwise score archives, checkpoints, and the private audit bundle are intentionally excluded from version control. Please do not commit benchmark data or third-party artifacts whose licenses do not permit redistribution.

## Scientific scope

The public repository is intended to remain a stable reference implementation for the submission. Refactoring, documentation improvements, bug fixes, and reproducibility improvements are welcome when they do not silently change the reported protocol. Changes that affect experimental semantics should be clearly identified and justified.
