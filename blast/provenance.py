"""Frozen data/cohort provenance for the BLAST ICASSP 2027 study."""

from __future__ import annotations

import hashlib
from pathlib import Path


TSB_AD_U_SHA256 = "0c47020d3423723c70773736dbd800369f2b487328becbf339450d1ae5020961"
TSB_AD_M_SHA256 = "7de86ac27f30eeb48d833bb061055670e3f3de07defd995cf2bd5db10ccc9a0d"
U237_COHORT_SHA256 = "8572d575e9704920bfb5908478c3feb8672cf3c92f28550e1edb3a476448ffce"
M70_COHORT_SHA256 = "1869a60c4fabd35d19f1c7ce6a149a6d8fe7e6684455fbb3cceda7b3b4fff3f8"


def sha256_file(path: str | Path) -> str:
    """Return SHA256 for a local file."""

    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_sha256(path: str | Path, expected: str, label: str) -> str:
    """Fail closed when a frozen input does not match its audited checksum."""

    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    got = sha256_file(path)
    if got != expected:
        raise RuntimeError(
            f"{label} SHA256 mismatch\nexpected {expected}\nfound    {got}\npath     {path}"
        )
    return got
