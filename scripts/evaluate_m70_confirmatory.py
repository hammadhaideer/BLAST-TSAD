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

WINDOW = 256
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/tsb_ad/TSB-AD-M.zip")
    ap.add_argument("--cohort", default="configs/rangerank_tsbad_m_confirmatory_70.txt")
    ap.add_argument("--scores", default="results/m70_label_free")
    ap.add_argument("--out", default="results/m70_confirmatory")
    args = ap.parse_args()

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
    ):
        raise RuntimeError("invalid or incomplete label-free score package")

    rows: list[dict] = []
    family_counts: dict[str, int] = {}

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
            rows.append({
                "filename": name,
                "family": family,
                "vus_pr_d0": v0,
                "vus_pr_d32": v32,
                "delta": v32 - v0,
            })

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
    gates = {
        "macro_superiority": macro32 > macro0,
        "absolute_gain_ge_0.015": gain >= MIN_GAIN,
        "median_delta_gt_0": paired["median_delta"] > 0.0,
        "win_fraction_ge_0.58": paired["strict_win_fraction"] >= MIN_WIN,
        "wilcoxon_p_lt_0.05": paired["wilcoxon_p"] < ALPHA,
        "family_balanced_superiority": fb32 > fb0,
    }

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "per_series_70.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["filename", "family", "vus_pr_d0", "vus_pr_d32", "delta"])
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "status": "CONFIRMATORY_COMPLETE",
        "series": len(rows),
        "window": WINDOW,
        "frozen_delay": DSTAR,
        "macro_vus_pr_d0": macro0,
        "macro_vus_pr_d32": macro32,
        "absolute_macro_gain": gain,
        "paired_d32_vs_d0": paired,
        "family_balanced_macro_d0": fb0,
        "family_balanced_macro_d32": fb32,
        "family_results": family_results,
        "gates": gates,
        "CONFIRM_GO": bool(all(gates.values())),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
