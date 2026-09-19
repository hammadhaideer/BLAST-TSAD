#!/usr/bin/env python3
"""Verify the public BLAST repository and submission-facing invariants."""

from __future__ import annotations

import hashlib
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PAPER_TITLE = "BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies"
AUTHOR_ORDER = ["Hammad Ali Haider", "Panpan Zheng"]
VERSION = "1.0.2"

REQUIRED = [
    "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "pyproject.toml",
    "CITATION.cff", "LICENSE", "environment.yml", "requirements.txt",
    ".github/workflows/ci.yml",
    "blast/__init__.py", "blast/core.py", "blast/data.py", "blast/metrics.py",
    "blast/provenance.py",
    "configs/rangerank_tsbad_confirmatory_237.txt",
    "configs/rangerank_tsbad_m_confirmatory_70.txt",
    "scripts/select_u237_delay.py", "scripts/score_m70_label_free.py",
    "scripts/evaluate_m70_confirmatory.py", "scripts/evaluate_postfreeze_robustness.py",
    "scripts/check_paper_results.py", "scripts/reproduce_paper.py",
    "scripts/verify_repository.py", "examples/minimal_example.py",
    "tests/test_core.py", "tests/test_data.py", "tests/test_metrics.py",
    "docs/PROTOCOL.md", "docs/DATA.md", "docs/RESULTS.md",
    "docs/REPRODUCIBILITY.md", "docs/RELEASE_STATUS.md", "docs/BASELINES.md",
    "assets/paper/README.md", "assets/paper/SHA256SUMS.txt",
    "assets/paper/figure1_attribution.svg",
    "assets/paper/figure2_workflow.svg",
    "assets/paper/figure3_confirmation_summary.svg",
]

COHORT_HASHES = {
    "configs/rangerank_tsbad_confirmatory_237.txt": "8572d575e9704920bfb5908478c3feb8672cf3c92f28550e1edb3a476448ffce",
    "configs/rangerank_tsbad_m_confirmatory_70.txt": "1869a60c4fabd35d19f1c7ce6a149a6d8fe7e6684455fbb3cceda7b3b4fff3f8",
}

ASSET_HASHES = {
    "assets/paper/figure1_attribution.svg": "cd8dc07b5d1e35e3217c2c5db61a9661ba28a0e9a0f296d48a3c126f844268bf",
    "assets/paper/figure2_workflow.svg": "183064482e8a3e381446fde8b74580441de28e211ff0a3d3d5915a040b7d4ce3",
    "assets/paper/figure3_confirmation_summary.svg": "7a706cf9fb3cfc7807a8ad58300eaca32846eb5ff5e2aa3303a9c6c509403ea0",
}

DATA_HASHES = {
    "data/tsb_ad/TSB-AD-U.zip": "0c47020d3423723c70773736dbd800369f2b487328becbf339450d1ae5020961",
    "data/tsb_ad/TSB-AD-M.zip": "7de86ac27f30eeb48d833bb061055670e3f3de07defd995cf2bd5db10ccc9a0d",
}

METADATA_FILES = [
    "README.md", "CHANGELOG.md", "CITATION.cff", "pyproject.toml",
    "docs/PROTOCOL.md", "docs/RESULTS.md", "docs/REPRODUCIBILITY.md",
    "docs/RELEASE_STATUS.md",
]

SUBMISSION_NARRATIVE_FILES = [
    "README.md", "docs/BASELINES.md", "docs/PROTOCOL.md", "docs/RESULTS.md",
    "docs/REPRODUCIBILITY.md", "docs/RELEASE_STATUS.md",
]

FORBIDDEN_PUBLIC_PATHS = {
    "results", "figures", "manuscript", "references", "audit",
    "reproducibility", "freeze_and_preregistration",
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
        raise SystemExit(f"{source}: author order does not match the manuscript")


def verify_metadata() -> None:
    for rel in METADATA_FILES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if PAPER_TITLE not in text:
            raise SystemExit(f"{rel}: exact paper title is missing")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    init_py = (ROOT / "blast/__init__.py").read_text(encoding="utf-8")
    release_status = (ROOT / "docs/RELEASE_STATUS.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    confirmatory = (ROOT / "scripts/evaluate_m70_confirmatory.py").read_text(encoding="utf-8")

    require_in_order(readme, AUTHOR_ORDER, "README.md")
    require_in_order(pyproject, AUTHOR_ORDER, "pyproject.toml")
    require_in_order(
        citation,
        ['family-names: "Haider"', 'family-names: "Zheng"'],
        "CITATION.cff",
    )
    if readme.count("Hammad Ali Haider") < 2 or readme.count("Panpan Zheng") < 2:
        raise SystemExit("README.md: submission authorship is incomplete")
    if pyproject.count('{name = "') != len(AUTHOR_ORDER):
        raise SystemExit("pyproject.toml: project author count does not match the manuscript")
    if citation.count("family-names:") != 2 * len(AUTHOR_ORDER):
        raise SystemExit("CITATION.cff: software and preferred-citation author counts do not match the manuscript")

    if f'__version__ = "{VERSION}"' not in init_py:
        raise SystemExit("blast/__init__.py: package version mismatch")
    if f'version = "{VERSION}"' not in pyproject:
        raise SystemExit("pyproject.toml: package version mismatch")
    if f'version: "{VERSION}"' not in citation:
        raise SystemExit("CITATION.cff: release version mismatch")
    if any(f"v{VERSION}" not in text for text in (readme, release_status, changelog)):
        raise SystemExit("public documentation does not consistently expose the release version")

    if "CONFIRM_GO" in confirmatory or "MIN_GAIN" in confirmatory or "MIN_WIN" in confirmatory:
        raise SystemExit("M70 confirmatory evaluator contains selection-style gates")
    if "no confirmation-driven selection or retuning" not in confirmatory:
        raise SystemExit("M70 confirmatory evaluator does not declare frozen descriptive confirmation")

    results = (ROOT / "docs/RESULTS.md").read_text(encoding="utf-8")
    for value in ("0.3042832564", "0.3300181420", "0.1704915933", "0.2089374630", "0.0657"):
        if value not in results:
            raise SystemExit(f"docs/RESULTS.md: frozen manuscript value missing: {value}")

    for rel in SUBMISSION_NARRATIVE_FILES:
        if "HSF" in (ROOT / rel).read_text(encoding="utf-8"):
            raise SystemExit(f"{rel}: stale HSF transfer text must not appear in the public submission narrative")


def main() -> None:
    missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit("missing required files:\n  " + "\n  ".join(missing))

    for name in FORBIDDEN_PUBLIC_PATHS:
        if (ROOT / name).exists():
            raise SystemExit(f"forbidden public-release path is tracked/present: {name}")

    for rel, expected in COHORT_HASHES.items():
        got = sha256(ROOT / rel)
        if got != expected:
            raise SystemExit(f"cohort hash mismatch: {rel}\nexpected {expected}\nfound    {got}")

    for rel, expected in ASSET_HASHES.items():
        got = sha256(ROOT / rel)
        if got != expected:
            raise SystemExit(f"documentation-asset hash mismatch: {rel}\nexpected {expected}\nfound    {got}")

    manifest = (ROOT / "assets/paper/SHA256SUMS.txt").read_text(encoding="utf-8")
    for rel, digest in ASSET_HASHES.items():
        name = Path(rel).name
        if f"{digest}  {name}" not in manifest:
            raise SystemExit(f"assets/paper/SHA256SUMS.txt: missing checksum for {name}")

    u = [x for x in (ROOT / "configs/rangerank_tsbad_confirmatory_237.txt").read_text().splitlines() if x.strip()]
    m = [x for x in (ROOT / "configs/rangerank_tsbad_m_confirmatory_70.txt").read_text().splitlines() if x.strip()]
    if len(u) != 237 or len(set(u)) != 237:
        raise SystemExit("U237 cohort is not exactly 237 unique members")
    if len(m) != 70 or len(set(m)) != 70:
        raise SystemExit("M70 cohort is not exactly 70 unique members")

    verify_metadata()

    for module in ("blast.core", "blast.data", "blast.metrics", "blast.provenance"):
        importlib.import_module(module)

    print("PUBLIC_STRUCTURE: PASS")
    print("PAPER_TITLE: PASS")
    print("AUTHOR_ORDER: PASS")
    print("RELEASE_VERSION: PASS")
    print("M70_CONFIRMATORY_SEMANTICS: PASS")
    print("U237_COHORT: PASS")
    print("M70_COHORT: PASS")
    print("DOCUMENTATION_ASSETS: PASS")
    print("RESULT_LEDGER: PASS")
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
