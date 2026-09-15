#!/usr/bin/env python3
"""Evaluate already-generated M70 score artifacts with frozen d*=32."""

from __future__ import annotations

import argparse
import csv
import json
import zipfile
from pathlib import Path

import numpy as np

from blast.data import family_from_name, load_cohort, read_labels, train_index_from_name
from blast.metrics import official_vus_pr, paired_summary
from blast.provenance import M70_COHORT_SHA256, TSB_AD_M_SHA256, require_sha256, sha256_file

WINDOW = 256
DSTAR = 32

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


def verify_pointwise_manifest(score_dir: Path, names: list[str]) -> str:
    manifest = score_dir / "pointwise_manifest.sha256"
    if not manifest.is_file():
        raise RuntimeError("missing pointwise_manifest.sha256")
    expected_files = {f"{Path(name).stem}.npz" for name in names}
    listed: dict[str, str] = {}
    for line_no, line in enumerate(manifest.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise RuntimeError(f"invalid manifest line {line_no}: {line!r}")
        digest, filename = parts
        filename = filename.strip()
        if filename in listed:
            raise RuntimeError(f"duplicate manifest entry: {filename}")
        listed[filename] = digest
    if set(listed) != expected_files:
        missing = sorted(expected_files - set(listed))
        extra = sorted(set(listed) - expected_files)
        raise RuntimeError(f"pointwise manifest mismatch; missing={missing}, extra={extra}")
    for filename, expected in listed.items():
        if sha256_file(score_dir / filename) != expected:
            raise RuntimeError(f"pointwise score hash mismatch: {filename}")
    return sha256_file(manifest)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/tsb_ad/TSB-AD-M.zip")
    ap.add_argument("--cohort", default="configs/rangerank_tsbad_m_confirmatory_70.txt")
    ap.add_argument("--scores", default="results/m70_label_free")
    ap.add_argument("--out", default="results/m70_confirmatory")
    args = ap.parse_args()

    data_sha = require_sha256(args.data, TSB_AD_M_SHA256, "TSB-AD-M archive")
    cohort_sha = require_sha256(args.cohort, M70_COHORT_SHA256, "M70 cohort")
    names = load_cohort(args.cohort)
    if len(names) != 70:
        raise RuntimeError(f"expected 70 M70 members, found {len(names)}")

    score_dir = Path(args.scores)
    label_free_summary = json.loads((score_dir / "label_free_summary.json").read_text())
    if not (
        label_free_summary.get("status") == "LABEL_FREE_SCORING_COMPLETE"
        and label_free_summary.get("series") == 70
        and label_free_summary.get("frozen_delay") == DSTAR
        and label_free_summary.get("label_values_parsed") is False
        and label_free_summary.get("anomaly_metric_computed") is False
        and label_free_summary.get("provenance", {}).get("data_sha256") == data_sha
        and label_free_summary.get("provenance", {}).get("cohort_sha256") == cohort_sha
    ):
        raise RuntimeError("invalid or incomplete label-free score package")

    pointwise_manifest_sha = verify_pointwise_manifest(score_dir, names)
    rows: list[dict] = []
    family_counts: dict[str, int] = {}

    # Labels are opened only after the label-free package and its manifest pass.
    with zipfile.ZipFile(args.data) as zf:
        for name in names:
            path = score_dir / f"{Path(name).stem}.npz"
            with np.load(path, allow_pickle=False) as z:
                if bool(z["label_values_parsed"].item()):
                    raise RuntimeError(f"{name}: score artifact parsed labels")
                if str(z["filename"].item()) != name:
                    raise RuntimeError(f"{name}: filename mismatch")
                train_index = int(z["train_index"].item())
                if train_index != train_index_from_name(name):
                    raise RuntimeError(f"{name}: training-boundary mismatch")
                d0 = np.asarray(z["score_d0"], dtype=np.float64)
                d32 = np.asarray(z["score_d32"], dtype=np.float64)

            labels = read_labels(zf, "TSB-AD-M", name)
            y = labels[train_index:]
            if len(y) != len(d0) or len(y) != len(d32):
                raise RuntimeError(f"{name}: score/label length mismatch")
            v0 = official_vus_pr(y, d0)
            v32 = official_vus_pr(y, d32)
            family = family_from_name(name)
            family_counts[family] = family_counts.get(family, 0) + 1
            rows.append({"filename": name, "family": family, "vus_pr_d0": v0, "vus_pr_d32": v32, "delta": v32 - v0})

    if family_counts != EXPECTED_FAMILIES:
        raise RuntimeError(f"family composition mismatch: {family_counts}")

    v0 = np.asarray([r["vus_pr_d0"] for r in rows], dtype=np.float64)
    v32 = np.asarray([r["vus_pr_d32"] for r in rows], dtype=np.float64)
    paired = paired_summary(v32, v0)
    macro0 = float(v0.mean())
    macro32 = float(v32.mean())
    gain = macro32 - macro0

    family_results: dict[str, dict] = {}
    family0: list[float] = []
    family32: list[float] = []
    for family in EXPECTED_FAMILIES:
        group = [r for r in rows if r["family"] == family]
        m0 = float(np.mean([r["vus_pr_d0"] for r in group]))
        m32 = float(np.mean([r["vus_pr_d32"] for r in group]))
        family0.append(m0)
        family32.append(m32)
        family_results[family] = {"n": len(group), "macro_d0": m0, "macro_d32": m32, "gain": m32 - m0}

    fb0 = float(np.mean(family0))
    fb32 = float(np.mean(family32))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "per_series_70.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["filename", "family", "vus_pr_d0", "vus_pr_d32", "delta"])
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "status": "CONFIRMATORY_COMPLETE",
        "confirmation_protocol": "frozen d*=32 descriptive evaluation; no confirmation-driven selection or retuning",
        "series": len(rows),
        "window": WINDOW,
        "frozen_delay": DSTAR,
        "macro_vus_pr_d0": macro0,
        "macro_vus_pr_d32": macro32,
        "absolute_macro_gain": gain,
        "relative_macro_gain": float(gain / macro0),
        "paired_d32_vs_d0": paired,
        "family_balanced_macro_d0": fb0,
        "family_balanced_macro_d32": fb32,
        "family_results": family_results,
        "all_family_mean_gains_positive": bool(all(row["gain"] > 0.0 for row in family_results.values())),
        "provenance": {
            "data_sha256": data_sha,
            "cohort_sha256": cohort_sha,
            "pointwise_manifest_sha256": pointwise_manifest_sha,
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
