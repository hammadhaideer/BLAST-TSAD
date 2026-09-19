# Changelog

All notable public changes to BLAST-TSAD are documented here.

Paper: **BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies**.

## Submission metadata synchronization — 2026-09-19

Submission-facing metadata and documentation were synchronized with the final manuscript:

- updated the public author list to Hammad Ali Haider and Panpan Zheng in the README, package metadata, citation metadata, and repository verification checks;
- aligned the U237 selection documentation with the four eligibility criteria stated in the manuscript;
- retained the implementation's macro-superiority assertion as a redundant consistency check implied by the minimum-gain criterion.

No experiment, cohort, metric, reported number, or frozen scientific protocol was changed by this metadata update.

## v1.0.2 — 2026-09-16

Submission-facing cleanup and confirmatory-protocol clarification.

### Correctness and presentation

- removed post-hoc pass/fail-style gates from the M70 confirmatory evaluator; M70 is now represented exactly as a frozen descriptive confirmation stage, with no confirmation-driven selection or retuning;
- clarified the same distinction in the README and protocol documentation;
- added direct official TSB-AD archive links while retaining strict frozen SHA256 verification;
- changed the README badge from “release” to “version” because the repository does not currently publish a GitHub Release object;
- removed literal Markdown code markers from the M70 figure caption and kept the public figures/table presentation compact and readable;
- refreshed package and citation metadata to v1.0.2.

No frozen manuscript number, cohort, metric definition, delay-selection rule, or scientific claim changes in v1.0.2.

## v1.0.1 — 2026-09-16

Reproducibility-hardening release for the ICASSP 2027 submission.

### Correctness and provenance

- aligned the public M70 normalization with the frozen study, including the exact `64 * eps_float64 * max(1, |median|)` numerical floor before the sample-standard-deviation fallback;
- made the frozen VUS configuration explicit (`vus==0.0.6`, `version="opt"`, `thre=250`) while preserving the audited study semantics;
- added SHA256 verification for the two benchmark archives and both frozen cohort manifests;
- strengthened the label-free M70 handoff with a pointwise-score manifest that is verified before confirmatory labels are read;
- removed stale HSF transfer material from the public submission-facing documentation.

### Reproduction and verification

- added `scripts/reproduce_paper.py` for the end-to-end public reproduction path;
- added post-freeze AP, AUROC, VUS-ROC, and common-support robustness reproduction;
- added `scripts/check_paper_results.py` to compare freshly generated outputs with the frozen manuscript-number ledger;
- added metric/provenance tests and expanded repository invariant checks;
- added `docs/RESULTS.md` with the final manuscript numerical tables and interpretation notes;
- added browser-friendly SVG documentation figures for the method, workflow, and confirmation summary.

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
