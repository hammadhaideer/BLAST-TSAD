# Documentation figures

This directory contains lightweight vector figures used by the public BLAST repository documentation. They reproduce the scientific semantics and headline results of the submitted manuscript while keeping the code release compact and browser-friendly.

- `figure1_attribution.svg` — endpoint assignment versus bounded-latency attribution.
- `figure2_workflow.svg` — fixed causal scoring, BLAST attribution, and the frozen U237→M70 protocol.
- `figure3_confirmation_summary.svg` — headline frozen M70 confirmation results and interpretation.

These SVGs are **documentation assets only**. No experiment script reads them, and they do not affect numerical reproduction. The submitted-paper source figures remain part of the manuscript source package rather than this code repository.

Integrity hashes for the documentation SVGs are recorded in `SHA256SUMS.txt` and checked by `scripts/verify_repository.py`.
