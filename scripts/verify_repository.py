#!/usr/bin/env python3
"""Verify the stable public BLAST repository structure and frozen manifests."""

from __future__ import annotations

import hashlib
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REQUIRED = [
    "blast/__init__.py",
    "blast/core.py",
    "blast/data.py",
    "blast/metrics.py",
    "configs/rangerank_tsbad_confirmatory_237.txt",
    "configs/rangerank_tsbad_m_confirmatory_70.txt",
    "scripts/select_u237_delay.py",
    "scripts/score_m70_label_free.py",
    "scripts/evaluate_m70_confirmatory.py",
    "docs/PROTOCOL.md",
    "docs/DATA.md",
    "docs/REPRODUCIBILITY.md",
    "CITATION.cff",
    "LICENSE",
    "environment.yml",
    "requirements.txt",
]

EXPECTED = {
    "configs/rangerank_tsbad_confirmatory_237.txt": "8572d575e9704920bfb5908478c3feb8672cf3c92f28550e1edb3a476448ffce",
    "configs/rangerank_tsbad_m_confirmatory_70.txt": "1869a60c4fabd35d19f1c7ce6a149a6d8fe7e6684455fbb3cceda7b3b4fff3f8",
}

DATA_HASHES = {
    "data/tsb_ad/TSB-AD-U.zip": "0c47020d3423723c70773736dbd800369f2b487328becbf339450d1ae5020961",
    "data/tsb_ad/TSB-AD-M.zip": "7de86ac27f30eeb48d833bb061055670e3f3de07defd995cf2bd5db10ccc9a0d",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit("missing required files:\n  " + "\n  ".join(missing))

    for rel, expected in EXPECTED.items():
        got = sha256(ROOT / rel)
        if got != expected:
            raise SystemExit(f"cohort hash mismatch: {rel}\nexpected {expected}\nfound    {got}")

    u = [x for x in (ROOT / "configs/rangerank_tsbad_confirmatory_237.txt").read_text().splitlines() if x.strip()]
    m = [x for x in (ROOT / "configs/rangerank_tsbad_m_confirmatory_70.txt").read_text().splitlines() if x.strip()]
    if len(u) != 237 or len(set(u)) != 237:
        raise SystemExit("U237 cohort is not exactly 237 unique members")
    if len(m) != 70 or len(set(m)) != 70:
        raise SystemExit("M70 cohort is not exactly 70 unique members")

    for module in ("blast.core", "blast.data", "blast.metrics"):
        importlib.import_module(module)

    print("PUBLIC_STRUCTURE: PASS")
    print("U237_COHORT: PASS")
    print("M70_COHORT: PASS")
    print("BLAST_IMPORTS: PASS")

    present = 0
    for rel, expected in DATA_HASHES.items():
        path = ROOT / rel
        if path.is_file():
            present += 1
            got = sha256(path)
            if got != expected:
                raise SystemExit(f"dataset hash mismatch: {rel}\nexpected {expected}\nfound    {got}")
            print(f"DATASET_HASH: PASS {rel}")
    if present == 0:
        print("DATASET_HASH: SKIPPED (datasets are not distributed)")

    print("BLAST_PUBLIC_REPOSITORY_VERIFICATION: PASS")


if __name__ == "__main__":
    main()
