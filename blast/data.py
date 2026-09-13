"""Small TSB-AD helpers used by the public BLAST runners.

The label-free reader deliberately discards the final CSV field as bytes and
never decodes or converts it.  This mirrors the separation used for M70 score
generation in the submitted study.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import numpy as np


def train_index_from_name(name: str) -> int:
    match = re.search(r"_tr_(\d+)_", name)
    if not match:
        raise ValueError(f"cannot parse training boundary from {name}")
    return int(match.group(1))


def family_from_name(name: str) -> str:
    match = re.match(r"^\d+_([^_]+)_id_", Path(name).name)
    if not match:
        raise ValueError(f"cannot parse family from {name}")
    return match.group(1)


def load_cohort(path: str | Path) -> list[str]:
    names = [line.strip() for line in Path(path).read_text().splitlines() if line.strip()]
    if len(names) != len(set(names)):
        raise ValueError("cohort contains duplicate filenames")
    return names


def _member(prefix: str, filename: str) -> str:
    return f"{prefix.rstrip('/')}/{filename}"


def read_features_label_free(
    zf: zipfile.ZipFile,
    prefix: str,
    filename: str,
) -> tuple[np.ndarray, list[str]]:
    """Read feature columns while keeping the label field opaque."""

    member = _member(prefix, filename)
    if member not in zf.namelist():
        raise FileNotFoundError(member)

    rows: list[list[float]] = []
    with zf.open(member, "r") as fh:
        raw_header = fh.readline()
        if not raw_header:
            raise ValueError(f"{filename}: missing header")
        header = raw_header.decode("utf-8").strip().split(",")
        if len(header) < 2:
            raise ValueError(f"{filename}: expected features plus label")
        feature_names = header[:-1]

        for raw in fh:
            raw = raw.rstrip(b"\r\n")
            if not raw:
                raise ValueError(f"{filename}: empty row")
            try:
                feature_blob, _opaque_label_blob = raw.rsplit(b",", 1)
            except ValueError as exc:
                raise ValueError(f"{filename}: malformed row") from exc
            values = [float(x) for x in feature_blob.decode("utf-8").split(",")]
            if len(values) != len(feature_names):
                raise ValueError(f"{filename}: inconsistent feature count")
            rows.append(values)

    x = np.asarray(rows, dtype=np.float64)
    if x.ndim != 2 or not np.all(np.isfinite(x)):
        raise ValueError(f"{filename}: invalid feature matrix")
    return x, feature_names


def read_labels(
    zf: zipfile.ZipFile,
    prefix: str,
    filename: str,
) -> np.ndarray:
    """Read only the final binary label column."""

    member = _member(prefix, filename)
    labels: list[int] = []
    with zf.open(member, "r") as fh:
        if not fh.readline():
            raise ValueError(f"{filename}: missing header")
        for raw in fh:
            raw = raw.rstrip(b"\r\n")
            if not raw:
                raise ValueError(f"{filename}: empty row")
            try:
                _feature_blob, label_blob = raw.rsplit(b",", 1)
            except ValueError as exc:
                raise ValueError(f"{filename}: malformed row") from exc
            value = int(float(label_blob.strip().decode("utf-8")))
            if value not in (0, 1):
                raise ValueError(f"{filename}: label is not binary")
            labels.append(value)
    return np.asarray(labels, dtype=np.int64)
