# Changelog

All notable public changes to BLAST-TSAD are documented here.

## v1.0.1 — 2026-09-16

Reproducibility-hardening release for the ICASSP 2027 submission.

### Correctness and provenance

- aligned the public M70 normalization with the frozen study, including the exact `64 * eps_float64 * max(1, |median|)` numerical floor before the sample-standard-deviation fallback;
- made the frozen VUS configuration explicit (`vus==0.0.6`, `version="opt"`, `thre=250`) while preserving the package defaults used by the audited study;
- added SHA256 verification for the two benchmark archives and both frozen cohort manifests;
- strengthened the label-free M70 handoff with a pointwise-score manifest that is verified before confirmatory labels are read;
- removed stale HSF transfer material from the public submission-facing documentation.

### Reproduction and verification

- added `scripts/reproduce_paper.py` for the end-to-end public reproduction path;
- added post-freeze AP, AUROC, VUS-ROC, and common-support robustness reproduction;
- added `scripts/check_paper_results.py` to compare freshly generated outputs with the frozen manuscript-number ledger;
- added metric/provenance tests and expanded repository invariant checks;
- added `docs/RESULTS.md` with the final manuscript tables and interpretation notes;
- added the final paper figures as public documentation assets.

No manuscript result or scientific claim is changed by this release; the update makes the public implementation match the frozen audited protocol more exactly.

## v1.0.0 — 2026-09-13

Initial stable public research-code release accompanying the ICASSP 2027 submission.

### Included

- BLAST bounded-latency attribution and release-time semantics;
- causal trailing sample-standard-deviation scoring;
- robust training-prefix normalization for multivariate confirmation;
- official VUS-PR evaluation wrapper;
- frozen U237 development and M70 confirmation cohort manifests;
- development delay-selection runner;
- label-free M70 score-generation runner;
- frozen-delay M70 confirmatory evaluation runner;
- invariant verification, unit tests, and GitHub Actions CI;
- protocol, dataset, baseline, reproducibility, and release-scope documentation.

### Public release scope

Raw datasets, generated pointwise outputs, manuscript files, checkpoints, and the private frozen audit bundle are intentionally excluded from the public repository.
