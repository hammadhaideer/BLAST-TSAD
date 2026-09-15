#!/usr/bin/env python3
"""Run the frozen BLAST U237 development delay-selection protocol."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

import numpy as np

from blast.core import make_test_scores, scalar_endpoint_score
from blast.data import load_cohort, read_features_label_free, read_labels
from blast.metrics import official_vus_pr, paired_summary
from blast.provenance import TSB_AD_U_SHA256, U237_COHORT_SHA256, require_sha256

WINDOW = 256
COMMON_START = 767
DELAYS = (0, 32, 64, 96, 127)
LOW_LATENCY = (32, 64)
MIN_GAIN = 0.015
MIN_WIN = 0.58
ALPHA = 0.01


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/tsb_ad/TSB-AD-U.zip")
    ap.add_argument("--cohort", default="configs/rangerank_tsbad_confirmatory_237.txt")
    ap.add_argument("--out", default="results/u237_delay_selection/summary.json")
    args = ap.parse_args()

    data_sha = require_sha256(args.data, TSB_AD_U_SHA256, "TSB-AD-U archive")
    cohort_sha = require_sha256(args.cohort, U237_COHORT_SHA256, "U237 cohort")
    cohort = load_cohort(args.cohort)
    if len(cohort) != 237:
        raise RuntimeError(f"expected 237 U237 members, found {len(cohort)}")

    per_delay: dict[int, list[float]] = {d: [] for d in DELAYS}
    with zipfile.ZipFile(args.data) as zf:
        for name in cohort:
            x, _ = read_features_label_free(zf, "TSB-AD-U", name)
            if x.shape[1] != 1:
                raise RuntimeError(f"{name}: U237 member is not univariate")
            labels = read_labels(zf, "TSB-AD-U", name)
            if len(labels) != len(x):
                raise RuntimeError(f"{name}: feature/label length mismatch")
            if len(x) <= COMMON_START + max(DELAYS):
                raise RuntimeError(f"{name}: series too short for frozen support")
            endpoint = scalar_endpoint_score(x[:, 0], WINDOW)
            y = labels[COMMON_START:]
            for d in DELAYS:
                scores, _ = make_test_scores(endpoint, COMMON_START, d)
                per_delay[d].append(official_vus_pr(y, scores))

    base = np.asarray(per_delay[0], dtype=np.float64)
    baseline_macro = float(base.mean())
    table: dict[str, dict] = {}
    for d in DELAYS:
        values = np.asarray(per_delay[d], dtype=np.float64)
        macro = float(values.mean())
        row: dict[str, object] = {"delay": d, "macro_vus_pr": macro}
        if d != 0:
            paired = paired_summary(values, base)
            gain = float(macro - baseline_macro)
            gates = {
                "macro_superiority": macro > baseline_macro,
                "absolute_gain_ge_0.015": gain >= MIN_GAIN,
                "median_gain_gt_0": paired["median_delta"] > 0.0,
                "win_fraction_ge_0.58": paired["strict_win_fraction"] >= MIN_WIN,
                "wilcoxon_p_lt_0.01": paired["wilcoxon_p"] < ALPHA,
            }
            row.update({"gain_vs_d0": gain, "paired": paired, "gates": gates, "passes": bool(all(gates.values()))})
        table[str(d)] = row

    eligible = [d for d in LOW_LATENCY if bool(table[str(d)]["passes"])]
    selected = min(eligible) if eligible else None
    summary = {
        "status": "COMPLETE",
        "series": len(cohort),
        "window": WINDOW,
        "common_start_zero_based": COMMON_START,
        "delays": list(DELAYS),
        "low_latency_candidates": list(LOW_LATENCY),
        "selection_rule": "smallest passing low-latency delay",
        "selected_delay": selected,
        "provenance": {"data_sha256": data_sha, "cohort_sha256": cohort_sha},
        "by_delay": table,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
