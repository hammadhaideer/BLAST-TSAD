#!/usr/bin/env python3
"""Verify the stable public BLAST repository and submission metadata."""

from __future__ import annotations

import hashlib
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PAPER_TITLE = "BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies"
AUTHOR_ORDER = ["Hammad Ali Haider", "Marcin Pietroń", "Roberto Corizzo", "Panpan Zheng"]
VERSION = "1.0.0"

REQUIRED = [
    "README.md",
    "pyproject.toml",
    "CITATION.cff",
    "LICENSE",
    "environment.yml",
    "requirements.txt",
    ".github/workflows/ci.yml",
    "blast/__init__.py",
    "blast/core.py",
    "blast/data.py",
    "blast/metrics.py",
    "configs/rangerank_tsbad_confirmatory_237.txt",
    "configs/rangerank_tsbad_m_confirmatory_70.txt",
    "scripts/select_u237_delay.py",
    "scripts/score_m70_label_free.py",
    "scripts/evaluate_m70_confirmatory.py",
    "scripts/verify_repository.py",
    "examples/minimal_example.py",
    "tests/test_core.py",
    "tests/test_data.py",
    "docs/PROTOCOL.md",
    "docs/DATA.md",
    "docs/REPRODUCIBILITY.md",
    "docs/RELEASE_STATUS.md",
    "docs/BASELINES.md",
]

EXPECTED = {
    "configs/rangerank_tsbad_confirmatory_237.txt": "8572d575e9704920bfb5908478c3feb8672cf3c92f28550e1edb3a476448ffce",
    "configs/rangerank_tsbad_m_confirmatory_70.txt": "1869a60c4fabd35d19f1c7ce6a149a6d8fe7e6684455fbb3cceda7b3b4fff3f8",
}

DATA_HASHES = {
    "data/tsb_ad/TSB-AD-U.zip": "0c47020d3423723c70773736dbd800369f2b487328becbf339450d1ae5020961",
    "data/tsb_ad/TSB-AD-M.zip": "7de86ac27f30eeb48d833bb061055670e3f3de07defd995cf2bd5db10ccc9a0d",
}

METADATA_FILES = [
    "README.md",
    "CITATION.cff",
    "pyproject.toml",
    "docs/PROTOCOL.md",
    "docs/RELEASE_STATUS.md",
]

FORBIDDEN_PUBLIC_PATHS = {
    "results",
    "figures",
    "manuscript",
    "references",
    "audit",
    "reproducibility",
    "freeze_and_preregistration",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_in_order(text: str, items: list[str], source: str) -> None:
    positions = [text.find(item) for item in items]
    if any(pos < 0 for pos in positions):
        missing = [item for item, pos in zip(items, positions) if pos < 0]
        raise SystemExit(f"{source}: missing author(s): {missing}")
    if positions != sorted(positions):
        raise SystemExit(f"{source}: author order does not match submitted paper")


def verify_metadata() -> None:
    for rel in METADATA_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if PAPER_TITLE not in text:
            raise SystemExit(f"{rel}: exact submitted paper title is missing")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    init_py = (ROOT / "blast/__init__.py").read_text(encoding="utf-8")

    require_in_order(readme, AUTHOR_ORDER, "README.md")
    require_in_order(pyproject, AUTHOR_ORDER, "pyproject.toml")

    # CITATION.cff stores names as separate given/family fields, so enforce the
    # submitted surname order there rather than searching for display strings.
    require_in_order(citation, ['family-names: "Haider"', 'family-names: "Pietroń"', 'family-names: "Corizzo"', 'family-names: "Zheng"'], "CITATION.cff")

    if f'__version__ = "{VERSION}"' not in init_py:
        raise SystemExit("blast/__init__.py: package version mismatch")
    if f'version = "{VERSION}"' not in pyproject:
        raise SystemExit("pyproject.toml: package version mismatch")
    if f'version: "{VERSION}"' not in citation:
        raise SystemExit("CITATION.cff: release version mismatch")


def main() -> None:
    missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit("missing required files:\n  " + "\n  ".join(missing))

    for name in FORBIDDEN_PUBLIC_PATHS:
        if (ROOT / name).exists():
            raise SystemExit(f"forbidden public-release path is tracked/present: {name}")

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

    verify_metadata()

    for module in ("blast.core", "blast.data", "blast.metrics"):
        importlib.import_module(module)

    print("PUBLIC_STRUCTURE: PASS")
    print("PAPER_TITLE: PASS")
    print("AUTHOR_ORDER: PASS")
    print("RELEASE_VERSION: PASS")
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
