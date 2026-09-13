#!/usr/bin/env python3

from pathlib import Path
import csv
import hashlib
import json
import math
import re
import zipfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]

DATA_ZIP = ROOT / "data/tsb_ad/TSB-AD-M.zip"
COHORT = ROOT / "config/rangerank_tsbad_m_confirmatory_70.txt"

OUT = ROOT / "results/latency_alignment_tsbadm_label_free"

FREEZE_MANIFEST = (
    ROOT
    / "docs/LATENCY_ALIGNMENT_TSBADM_CONFIRMATORY_ARTIFACTS_20260902.sha256"
)

EXPECTED_DATA_SHA = (
    "7de86ac27f30eeb48d833bb061055670e3f3de07defd995cf2bd5db10ccc9a0d"
)

EXPECTED_COHORT_SHA = (
    "1869a60c4fabd35d19f1c7ce6a149a6d8fe7e6684455fbb3cceda7b3b4fff3f8"
)

EXPECTED_N = 70

W = 256
D0 = 0
DSTAR = 32


def sha256(path):
    h = hashlib.sha256()

    with Path(path).open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def verify_freeze_manifest():
    if not FREEZE_MANIFEST.is_file():
        raise RuntimeError(
            "missing confirmatory artifact manifest"
        )

    required = {
        "docs/LATENCY_ALIGNMENT_TSBADM_CONFIRMATORY_FREEZE_20260902.md",
        "docs/LATENCY_ALIGNMENT_DEV237_OUTCOME_FREEZE_20260902.md",
        "scripts/score_latency_alignment_tsbadm_labelfree.py",
        "scripts/analyze_latency_alignment_tsbadm_confirmatory.py",
        "config/rangerank_tsbad_m_confirmatory_70.txt",
    }

    seen = set()

    for raw in FREEZE_MANIFEST.read_text().splitlines():
        raw = raw.strip()

        if not raw:
            continue

        digest, rel = raw.split(
            maxsplit=1,
        )

        p = ROOT / rel

        if not p.is_file():
            raise RuntimeError(
                f"missing frozen artifact: {rel}"
            )

        if sha256(p) != digest:
            raise RuntimeError(
                f"frozen artifact hash mismatch: {rel}"
            )

        seen.add(rel)

    if seen != required:
        raise RuntimeError(
            f"freeze manifest set mismatch: {seen ^ required}"
        )


def train_index_from_name(name):
    m = re.search(
        r"_tr_(\d+)_",
        name,
    )

    if not m:
        raise RuntimeError(
            f"missing train index: {name}"
        )

    return int(m.group(1))


def load_cohort():
    if sha256(COHORT) != EXPECTED_COHORT_SHA:
        raise RuntimeError(
            "cohort SHA mismatch"
        )

    names = [
        x.strip()
        for x in COHORT.read_text().splitlines()
        if x.strip()
    ]

    if len(names) != EXPECTED_N:
        raise RuntimeError(
            f"expected 70 series, got {len(names)}"
        )

    if len(set(names)) != EXPECTED_N:
        raise RuntimeError(
            "duplicate cohort member"
        )

    if not all(
        train_index_from_name(x) >= W
        for x in names
    ):
        raise RuntimeError(
            "insufficient training prefix"
        )

    return names


def header_only(zf, filename):
    member = f"TSB-AD-M/{filename}"

    if member not in zf.namelist():
        raise RuntimeError(
            f"missing archive member: {member}"
        )

    with zf.open(member, "r") as fh:
        raw = fh.readline()

    if not raw:
        raise RuntimeError(
            f"{filename}: empty CSV"
        )

    header = [
        x.strip()
        for x in next(
            csv.reader(
                [raw.decode("utf-8-sig").strip()]
            )
        )
    ]

    if len(header) < 3:
        raise RuntimeError(
            f"{filename}: expected >=2 features + Label"
        )

    if header[-1] != "Label":
        raise RuntimeError(
            f"{filename}: final field is not Label"
        )

    features = header[:-1]

    return features


def read_features_without_labels(zf, filename):
    """
    Read feature values only.

    The final Label field is separated at the byte level and
    deliberately never decoded, parsed, converted, inspected,
    stored, compared, or counted by value.
    """

    member = f"TSB-AD-M/{filename}"
    features = header_only(
        zf,
        filename,
    )

    C = len(features)

    rows = []

    with zf.open(member, "r") as fh:
        header = fh.readline()

        if not header:
            raise RuntimeError(
                f"{filename}: missing header"
            )

        row_idx = 0

        while True:
            raw = fh.readline()

            if not raw:
                break

            raw = raw.rstrip(
                b"\r\n"
            )

            if not raw:
                raise RuntimeError(
                    f"{filename}: empty row {row_idx}"
                )

            try:
                feature_blob, _ignored_label_blob = (
                    raw.rsplit(
                        b",",
                        1,
                    )
                )
            except ValueError as exc:
                raise RuntimeError(
                    f"{filename}: malformed row {row_idx}"
                ) from exc

            fields = feature_blob.split(
                b","
            )

            if len(fields) != C:
                raise RuntimeError(
                    f"{filename}: feature count mismatch"
                )

            row = np.empty(
                C,
                dtype=np.float64,
            )

            for c, field in enumerate(fields):
                field = field.strip()

                if not field:
                    raise RuntimeError(
                        f"{filename}: missing feature "
                        f"row={row_idx} channel={c}"
                    )

                try:
                    value = float(
                        field.decode("utf-8")
                    )
                except Exception as exc:
                    raise RuntimeError(
                        f"{filename}: invalid feature "
                        f"row={row_idx} channel={c}"
                    ) from exc

                if not math.isfinite(value):
                    raise RuntimeError(
                        f"{filename}: nonfinite feature "
                        f"row={row_idx} channel={c}"
                    )

                row[c] = value

            rows.append(row)
            row_idx += 1

    if not rows:
        raise RuntimeError(
            f"{filename}: no rows"
        )

    x = np.stack(
        rows,
        axis=0,
    )

    if (
        x.ndim != 2
        or x.shape[1] != C
        or not np.isfinite(x).all()
    ):
        raise RuntimeError(
            f"{filename}: invalid feature matrix"
        )

    return x, features


def robust_prefix_standardize(x, train_index):
    prefix = np.asarray(
        x[:train_index],
        dtype=np.float64,
    )

    med = np.median(
        prefix,
        axis=0,
    )

    mad = np.median(
        np.abs(
            prefix - med[None, :]
        ),
        axis=0,
    )

    scale = (
        1.4826
        * mad
    )

    for c in range(x.shape[1]):
        floor = (
            64.0
            * np.finfo(np.float64).eps
            * max(
                1.0,
                abs(float(med[c])),
            )
        )

        if (
            not np.isfinite(scale[c])
            or scale[c] <= floor
        ):
            alt = float(
                np.std(
                    prefix[:, c],
                    ddof=1,
                )
            )

            if (
                np.isfinite(alt)
                and alt > floor
            ):
                scale[c] = alt
            else:
                scale[c] = 1.0

    z = (
        x - med[None, :]
    ) / scale[None, :]

    if not np.isfinite(z).all():
        raise RuntimeError(
            "nonfinite standardized features"
        )

    return z, med, scale


def rolling_sample_std(v, w):
    v = np.asarray(
        v,
        dtype=np.float64,
    )

    if len(v) < w:
        raise RuntimeError(
            "series shorter than window"
        )

    cs = np.concatenate(
        (
            np.array([0.0]),
            np.cumsum(v),
        )
    )

    cs2 = np.concatenate(
        (
            np.array([0.0]),
            np.cumsum(v * v),
        )
    )

    sums = (
        cs[w:]
        - cs[:-w]
    )

    sums2 = (
        cs2[w:]
        - cs2[:-w]
    )

    ss = (
        sums2
        - (sums * sums) / float(w)
    )

    ss = np.maximum(
        ss,
        0.0,
    )

    return np.sqrt(
        ss / float(w - 1)
    )


def scalar_endpoint_score(z):
    T, C = z.shape

    per_channel = []

    for c in range(C):
        per_channel.append(
            rolling_sample_std(
                z[:, c],
                W,
            )
        )

    M = np.column_stack(
        per_channel
    )

    score = np.mean(
        M,
        axis=1,
    )

    endpoint = np.full(
        T,
        np.nan,
        dtype=np.float64,
    )

    endpoint[
        W - 1:
    ] = score

    return endpoint


def make_test_scores(endpoint, train_index):
    T = len(endpoint)
    N = T - train_index

    if N <= DSTAR:
        raise RuntimeError(
            "evaluation span too short"
        )

    d0 = np.asarray(
        endpoint[
            train_index:T
        ],
        dtype=np.float64,
    )

    if not np.isfinite(d0).all():
        raise RuntimeError(
            "nonfinite d0"
        )

    d32 = np.zeros(
        N,
        dtype=np.float64,
    )

    usable = (
        N - DSTAR
    )

    vals = endpoint[
        train_index + DSTAR:
        T
    ]

    if len(vals) != usable:
        raise RuntimeError(
            "d32 alignment mismatch"
        )

    if not np.isfinite(vals).all():
        raise RuntimeError(
            "nonfinite d32"
        )

    d32[:usable] = vals

    return d0, d32


def main():
    OUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    if sha256(DATA_ZIP) != EXPECTED_DATA_SHA:
        raise RuntimeError(
            "TSB-AD-M archive SHA mismatch"
        )

    verify_freeze_manifest()

    names = load_cohort()

    print(
        "============================================================"
    )
    print(
        "LATENCY ALIGNMENT TSB-AD-M LABEL-FREE SCORING"
    )
    print(
        "============================================================"
    )
    print(
        "SERIES =", len(names)
    )
    print(
        "W =", W
    )
    print(
        "FROZEN_DELAY =", DSTAR
    )
    print(
        "LABEL_VALUES_PARSED = False"
    )
    print(
        "NO ANOMALY METRIC WILL BE COMPUTED"
    )
    print(
        "============================================================",
        flush=True,
    )

    with zipfile.ZipFile(
        DATA_ZIP
    ) as zf:

        for idx, name in enumerate(
            names,
            1,
        ):
            out = (
                OUT
                / f"{Path(name).stem}.npz"
            )

            if out.exists():
                print(
                    f"[LABEL_FREE] {idx}/70 "
                    f"{name} EXISTS",
                    flush=True,
                )
                continue

            x, features = (
                read_features_without_labels(
                    zf,
                    name,
                )
            )

            train_index = (
                train_index_from_name(
                    name
                )
            )

            if train_index > len(x):
                raise RuntimeError(
                    f"{name}: invalid train index"
                )

            z, med, scale = (
                robust_prefix_standardize(
                    x,
                    train_index,
                )
            )

            endpoint = (
                scalar_endpoint_score(z)
            )

            d0, d32 = (
                make_test_scores(
                    endpoint,
                    train_index,
                )
            )

            tmp = out.with_suffix(
                ".npz.tmp"
            )

            with tmp.open("wb") as f:
                np.savez_compressed(
                    f,
                    filename=np.array(name),
                    T=np.array(
                        len(x),
                        dtype=np.int64,
                    ),
                    train_index=np.array(
                        train_index,
                        dtype=np.int64,
                    ),
                    channel_count=np.array(
                        x.shape[1],
                        dtype=np.int64,
                    ),
                    feature_names=np.asarray(
                        features,
                        dtype=str,
                    ),
                    prefix_median=med,
                    prefix_scale=scale,
                    score_d0=d0,
                    score_d32=d32,
                    label_values_parsed=np.array(
                        False
                    ),
                )

            tmp.replace(out)

            print(
                f"[LABEL_FREE] {idx}/70 "
                f"{name} "
                f"T={len(x)} "
                f"C={x.shape[1]} "
                f"test={len(d0)}",
                flush=True,
            )

    files = sorted(
        OUT.glob("*.npz")
    )

    if len(files) != EXPECTED_N:
        raise RuntimeError(
            f"incomplete pointwise set: {len(files)}/70"
        )

    lines = []

    for p in files:
        lines.append(
            f"{sha256(p)}  "
            f"{p.relative_to(ROOT)}"
        )

    manifest = (
        OUT
        / "pointwise_manifest.sha256"
    )

    manifest.write_text(
        "\n".join(lines)
        + "\n"
    )

    summary = {
        "status":
            "LABEL_FREE_SCORING_COMPLETE",
        "series":
            EXPECTED_N,
        "window":
            W,
        "frozen_delay":
            DSTAR,
        "aggregation":
            "mean_channel_prefix_standardized_std256",
        "label_values_parsed":
            False,
        "anomaly_metric_computed":
            False,
        "pointwise_manifest_sha256":
            sha256(manifest),
    }

    (
        OUT
        / "label_free_summary.json"
    ).write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print()
    print(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
    )
    print()
    print(
        "LABEL_VALUES_PARSED = False"
    )
    print(
        "UNTOUCHED_LABELS_OPENED = False"
    )


if __name__ == "__main__":
    main()
