#!/usr/bin/env python3
"""Reproduce the post-freeze robustness and common-support checks."""

from __future__ import annotations

import argparse
import csv
import json
import zipfile
from pathlib import Path

import numpy as np

from blast.core import make_test_scores, scalar_endpoint_score
from blast.data import load_cohort, read_features_label_free, read_labels
from blast.metrics import evaluation_metrics, paired_summary
from blast.provenance import (
    M70_COHORT_SHA256,
    TSB_AD_M_SHA256,
    TSB_AD_U_SHA256,
    U237_COHORT_SHA256,
    require_sha256,
    sha256_file,
)

WINDOW = 256
DSTAR = 32
COMMON_START = 767
METRICS = ("vus_pr", "ap", "auroc", "vus_roc")


def verify_pointwise_manifest(score_dir: Path, names: list[str]) -> None:
    manifest = score_dir / "pointwise_manifest.sha256"
    expected_files = {f"{Path(name).stem}.npz" for name in names}
    listed: dict[str, str] = {}
    for line in manifest.read_text().splitlines():
        if not line.strip():
            continue
        digest, filename = line.split(maxsplit=1)
        listed[filename.strip()] = digest
    if set(listed) != expected_files:
        raise RuntimeError("M70 pointwise manifest does not match frozen cohort")
    for filename, expected in listed.items():
        if sha256_file(score_dir / filename) != expected:
            raise RuntimeError(f"M70 pointwise hash mismatch: {filename}")


def summarize(rows: list[dict], support: str) -> dict:
    result: dict[str, dict] = {"support": support}
    for metric in METRICS:
        d0 = np.asarray([r[f"{metric}_d0"] for r in rows], dtype=np.float64)
        d32 = np.asarray([r[f"{metric}_d32"] for r in rows], dtype=np.float64)
        paired = paired_summary(d32, d0)
        result[metric] = {"d0_macro": float(d0.mean()), "d32_macro": float(d32.mean()), "delta": float(d32.mean() - d0.mean()), "paired": paired}
    return result


def metric_row(name: str, y: np.ndarray, d0: np.ndarray, d32: np.ndarray) -> dict:
    m0 = evaluation_metrics(y, d0)
    m32 = evaluation_metrics(y, d32)
    row: dict[str, object] = {"filename": name}
    for metric in METRICS:
        row[f"{metric}_d0"] = m0[metric]
        row[f"{metric}_d32"] = m32[metric]
    return row


def run_u237(data: str, cohort_path: str) -> tuple[list[dict], list[dict]]:
    names = load_cohort(cohort_path)
    if len(names) != 237:
        raise RuntimeError("U237 cohort size mismatch")
    full: list[dict] = []
    common: list[dict] = []
    with zipfile.ZipFile(data) as zf:
        for name in names:
            x, _ = read_features_label_free(zf, "TSB-AD-U", name)
            if x.shape[1] != 1:
                raise RuntimeError(f"{name}: expected univariate series")
            labels = read_labels(zf, "TSB-AD-U", name)
            endpoint = scalar_endpoint_score(x[:, 0], WINDOW)
            y = labels[COMMON_START:]
            d0, _ = make_test_scores(endpoint, COMMON_START, 0)
            d32, _ = make_test_scores(endpoint, COMMON_START, DSTAR)
            full.append(metric_row(name, y, d0, d32))
            common.append(metric_row(name, y[:-DSTAR], d0[:-DSTAR], d32[:-DSTAR]))
    return full, common


def run_m70(data: str, cohort_path: str, score_dir: str) -> tuple[list[dict], list[dict]]:
    names = load_cohort(cohort_path)
    if len(names) != 70:
        raise RuntimeError("M70 cohort size mismatch")
    score_root = Path(score_dir)
    verify_pointwise_manifest(score_root, names)
    label_free = json.loads((score_root / "label_free_summary.json").read_text())
    if label_free.get("label_values_parsed") is not False:
        raise RuntimeError("M70 score package is not label-free")
    full: list[dict] = []
    common: list[dict] = []
    with zipfile.ZipFile(data) as zf:
        for name in names:
            with np.load(score_root / f"{Path(name).stem}.npz", allow_pickle=False) as z:
                if bool(z["label_values_parsed"].item()):
                    raise RuntimeError(f"{name}: score package parsed labels")
                train_index = int(z["train_index"].item())
                d0 = np.asarray(z["score_d0"], dtype=np.float64)
                d32 = np.asarray(z["score_d32"], dtype=np.float64)
            y = read_labels(zf, "TSB-AD-M", name)[train_index:]
            full.append(metric_row(name, y, d0, d32))
            common.append(metric_row(name, y[:-DSTAR], d0[:-DSTAR], d32[:-DSTAR]))
    return full, common


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--u-data", default="data/tsb_ad/TSB-AD-U.zip")
    ap.add_argument("--m-data", default="data/tsb_ad/TSB-AD-M.zip")
    ap.add_argument("--u-cohort", default="configs/rangerank_tsbad_confirmatory_237.txt")
    ap.add_argument("--m-cohort", default="configs/rangerank_tsbad_m_confirmatory_70.txt")
    ap.add_argument("--m-scores", default="results/m70_label_free")
    ap.add_argument("--out", default="results/postfreeze_robustness")
    args = ap.parse_args()

    provenance = {
        "u_data_sha256": require_sha256(args.u_data, TSB_AD_U_SHA256, "TSB-AD-U archive"),
        "m_data_sha256": require_sha256(args.m_data, TSB_AD_M_SHA256, "TSB-AD-M archive"),
        "u_cohort_sha256": require_sha256(args.u_cohort, U237_COHORT_SHA256, "U237 cohort"),
        "m_cohort_sha256": require_sha256(args.m_cohort, M70_COHORT_SHA256, "M70 cohort"),
    }
    u_full, u_common = run_u237(args.u_data, args.u_cohort)
    m_full, m_common = run_m70(args.m_data, args.m_cohort, args.m_scores)

    out = Path(args.out)
    write_rows(out / "u237_full.csv", u_full)
    write_rows(out / "u237_common_support.csv", u_common)
    write_rows(out / "m70_full.csv", m_full)
    write_rows(out / "m70_common_support.csv", m_common)
    summary = {
        "status": "POSTFREEZE_ROBUSTNESS_COMPLETE",
        "window": WINDOW,
        "frozen_delay": DSTAR,
        "provenance": provenance,
        "u237": {"series": len(u_full), "full": summarize(u_full, "primary full-length arrays"), "common_support": summarize(u_common, "last 32 timestamps removed from both arms")},
        "m70": {"series": len(m_full), "full": summarize(m_full, "primary full-length arrays"), "common_support": summarize(m_common, "last 32 timestamps removed from both arms")},
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
