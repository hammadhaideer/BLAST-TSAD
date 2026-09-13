#!/usr/bin/env python3

from pathlib import Path
import csv
import hashlib
import json
import re
import zipfile

import numpy as np
import scipy
from scipy.stats import wilcoxon

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(ROOT / "scripts"),
)

import score_rangerank_tsbad_confirmatory as frozen


DATA_ZIP = ROOT / "data/tsb_ad/TSB-AD-M.zip"

COHORT = (
    ROOT
    / "config/rangerank_tsbad_m_confirmatory_70.txt"
)

SCORES = (
    ROOT
    / "results/latency_alignment_tsbadm_label_free"
)

OUT = (
    ROOT
    / "results/latency_alignment_tsbadm_confirmatory"
)

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
DSTAR = 32

MIN_GAIN = 0.015
MIN_WIN = 0.58
ALPHA = 0.05

EXPECTED_FAMILIES = {
    "CATSv2": 5,
    "Exathlon": 2,
    "GECCO": 1,
    "GHL": 25,
    "Genesis": 1,
    "MITDB": 6,
    "MSL": 3,
    "PSM": 1,
    "SMAP": 10,
    "SMD": 3,
    "SVDB": 12,
    "SWaT": 1,
}


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

        if (
            not p.is_file()
            or sha256(p) != digest
        ):
            raise RuntimeError(
                f"frozen artifact mismatch: {rel}"
            )

        seen.add(rel)

    if seen != required:
        raise RuntimeError(
            "freeze manifest content mismatch"
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

    return int(
        m.group(1)
    )


def family_from_name(name):
    matches = []

    for fam in EXPECTED_FAMILIES:
        if (
            f"_{fam}_" in name
            or name.startswith(
                f"{fam}_"
            )
        ):
            matches.append(fam)

    if len(matches) != 1:
        raise RuntimeError(
            f"cannot uniquely parse family: "
            f"{name}: {matches}"
        )

    return matches[0]


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
            "unexpected cohort size"
        )

    return names


def verify_pointwise_set(names):
    manifest = (
        SCORES
        / "pointwise_manifest.sha256"
    )

    summary = (
        SCORES
        / "label_free_summary.json"
    )

    if (
        not manifest.is_file()
        or not summary.is_file()
    ):
        raise RuntimeError(
            "label-free scoring is incomplete"
        )

    s = json.loads(
        summary.read_text()
    )

    if (
        s.get("status")
        != "LABEL_FREE_SCORING_COMPLETE"
        or s.get("series") != 70
        or s.get("frozen_delay") != 32
        or s.get("label_values_parsed") is not False
        or s.get("anomaly_metric_computed") is not False
    ):
        raise RuntimeError(
            "invalid label-free summary"
        )

    expected_paths = {
        str(
            (
                SCORES
                / f"{Path(name).stem}.npz"
            ).relative_to(ROOT)
        )
        for name in names
    }

    observed = set()

    for raw in manifest.read_text().splitlines():
        digest, rel = raw.split(
            maxsplit=1,
        )

        p = ROOT / rel

        if (
            not p.is_file()
            or sha256(p) != digest
        ):
            raise RuntimeError(
                f"pointwise hash mismatch: {rel}"
            )

        observed.add(rel)

    if observed != expected_paths:
        raise RuntimeError(
            "pointwise manifest is not exact 70/70"
        )


def read_labels(zf, filename):
    member = f"TSB-AD-M/{filename}"

    labels = []

    with zf.open(member, "r") as fh:
        header = fh.readline()

        if not header:
            raise RuntimeError(
                f"{filename}: missing header"
            )

        while True:
            raw = fh.readline()

            if not raw:
                break

            raw = raw.rstrip(
                b"\r\n"
            )

            if not raw:
                raise RuntimeError(
                    f"{filename}: empty row"
                )

            try:
                _feature_blob, label_blob = (
                    raw.rsplit(
                        b",",
                        1,
                    )
                )
            except ValueError as exc:
                raise RuntimeError(
                    f"{filename}: malformed row"
                ) from exc

            value = int(
                float(
                    label_blob
                    .strip()
                    .decode("utf-8")
                )
            )

            if value not in (0, 1):
                raise RuntimeError(
                    f"{filename}: label not binary"
                )

            labels.append(value)

    return np.asarray(
        labels,
        dtype=np.int64,
    )


def metric(y, score):
    L_e = int(
        frozen.entity_buffer_L(y)
    )

    return float(
        frozen.official_vus_pr(
            y,
            score,
            L_e,
        )
    )


def paired_summary(a, b):
    delta = (
        np.asarray(a, dtype=np.float64)
        - np.asarray(b, dtype=np.float64)
    )

    wins = int(
        np.sum(delta > 0)
    )

    losses = int(
        np.sum(delta < 0)
    )

    ties = int(
        np.sum(delta == 0)
    )

    if np.all(delta == 0):
        stat = 0.0
        p = 1.0
    else:
        stat, p = wilcoxon(
            delta,
            alternative="two-sided",
            zero_method="wilcox",
            correction=False,
            method="approx",
        )

        stat = float(stat)
        p = float(p)

    return {
        "mean_delta":
            float(np.mean(delta)),
        "median_delta":
            float(np.median(delta)),
        "wins":
            wins,
        "losses":
            losses,
        "ties":
            ties,
        "strict_win_fraction":
            float(wins / EXPECTED_N),
        "wilcoxon_stat":
            stat,
        "wilcoxon_p":
            p,
    }


def main():
    OUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = (
        OUT
        / "summary.json"
    )

    if summary_path.exists():
        raise RuntimeError(
            "confirmatory summary already exists; "
            "refusing silent rerun"
        )

    if sha256(DATA_ZIP) != EXPECTED_DATA_SHA:
        raise RuntimeError(
            "data archive SHA mismatch"
        )

    verify_freeze_manifest()

    names = load_cohort()

    verify_pointwise_set(
        names
    )

    family_counts = {}

    rows = []

    # No aggregate fresh result is printed until all 70 labels
    # have been evaluated.
    with zipfile.ZipFile(
        DATA_ZIP
    ) as zf:

        for name in names:
            p = (
                SCORES
                / f"{Path(name).stem}.npz"
            )

            with np.load(
                p,
                allow_pickle=False,
            ) as z:
                if bool(
                    z["label_values_parsed"].item()
                ):
                    raise RuntimeError(
                        f"{name}: invalid label-free artifact"
                    )

                stored_name = str(
                    z["filename"].item()
                )

                if stored_name != name:
                    raise RuntimeError(
                        f"{name}: filename mismatch"
                    )

                T = int(
                    z["T"].item()
                )

                train_index = int(
                    z["train_index"].item()
                )

                if (
                    train_index
                    != train_index_from_name(name)
                ):
                    raise RuntimeError(
                        f"{name}: train index mismatch"
                    )

                d0 = np.asarray(
                    z["score_d0"],
                    dtype=np.float64,
                )

                d32 = np.asarray(
                    z["score_d32"],
                    dtype=np.float64,
                )

            labels = read_labels(
                zf,
                name,
            )

            if len(labels) != T:
                raise RuntimeError(
                    f"{name}: label length mismatch"
                )

            y = labels[
                train_index:
            ]

            if (
                len(d0) != len(y)
                or len(d32) != len(y)
            ):
                raise RuntimeError(
                    f"{name}: score/label mismatch"
                )

            v0 = metric(
                y,
                d0,
            )

            v32 = metric(
                y,
                d32,
            )

            fam = family_from_name(
                name
            )

            family_counts[fam] = (
                family_counts.get(
                    fam,
                    0,
                )
                + 1
            )

            rows.append(
                {
                    "filename": name,
                    "family": fam,
                    "vus_pr_d0": v0,
                    "vus_pr_d32": v32,
                    "delta": v32 - v0,
                }
            )

    if family_counts != EXPECTED_FAMILIES:
        raise RuntimeError(
            f"family composition mismatch: "
            f"{family_counts}"
        )

    d0 = np.asarray(
        [
            r["vus_pr_d0"]
            for r in rows
        ],
        dtype=np.float64,
    )

    d32 = np.asarray(
        [
            r["vus_pr_d32"]
            for r in rows
        ],
        dtype=np.float64,
    )

    macro0 = float(
        np.mean(d0)
    )

    macro32 = float(
        np.mean(d32)
    )

    paired = paired_summary(
        d32,
        d0,
    )

    family_results = {}

    family_d0 = []
    family_d32 = []

    for fam in EXPECTED_FAMILIES:
        group = [
            r
            for r in rows
            if r["family"] == fam
        ]

        m0 = float(
            np.mean(
                [
                    r["vus_pr_d0"]
                    for r in group
                ]
            )
        )

        m32 = float(
            np.mean(
                [
                    r["vus_pr_d32"]
                    for r in group
                ]
            )
        )

        family_d0.append(m0)
        family_d32.append(m32)

        family_results[fam] = {
            "n":
                len(group),
            "macro_d0":
                m0,
            "macro_d32":
                m32,
            "gain":
                m32 - m0,
        }

    fb0 = float(
        np.mean(family_d0)
    )

    fb32 = float(
        np.mean(family_d32)
    )

    gain = (
        macro32
        - macro0
    )

    gates = {
        "macro_superiority":
            macro32 > macro0,

        "absolute_gain_ge_0.015":
            gain >= MIN_GAIN,

        "median_delta_gt_0":
            paired[
                "median_delta"
            ] > 0,

        "win_fraction_ge_0.58":
            paired[
                "strict_win_fraction"
            ] >= MIN_WIN,

        "wilcoxon_p_lt_0.05":
            paired[
                "wilcoxon_p"
            ] < ALPHA,

        "family_balanced_superiority":
            fb32 > fb0,
    }

    confirm_go = bool(
        all(gates.values())
    )

    per_csv = (
        OUT
        / "per_series_70.csv"
    )

    with per_csv.open(
        "w",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "filename",
                "family",
                "vus_pr_d0",
                "vus_pr_d32",
                "delta",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "status":
            "FRESH_CONFIRMATORY_COMPLETE",

        "scipy_version":
            scipy.__version__,

        "series":
            EXPECTED_N,

        "window":
            W,

        "frozen_delay":
            DSTAR,

        "macro_vus_pr_d0":
            macro0,

        "macro_vus_pr_d32":
            macro32,

        "absolute_macro_gain":
            gain,

        "paired_d32_vs_d0":
            paired,

        "family_balanced_macro_d0":
            fb0,

        "family_balanced_macro_d32":
            fb32,

        "family_results":
            family_results,

        "gates":
            gates,

        "CONFIRM_GO":
            confirm_go,
    }

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print(
        "============================================================"
    )
    print(
        "FRESH CONFIRMATORY RESULT"
    )
    print(
        "============================================================"
    )
    print(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
    )
    print()
    print(
        "CONFIRM_GO =",
        confirm_go,
    )


if __name__ == "__main__":
    main()
