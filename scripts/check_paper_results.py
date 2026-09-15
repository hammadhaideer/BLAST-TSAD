#!/usr/bin/env python3
"""Check generated BLAST outputs against the numerical manuscript ledger."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ABS_TOL = 5e-10
EXPECTED_U_SWEEP = {"0": 0.3042832564449439, "32": 0.33001814197604906, "64": 0.3503386608723718, "96": 0.36761371714851354, "127": 0.36956436228563205}
EXPECTED_M70 = {"d0": 0.17049159333681876, "d32": 0.20893746299321103, "gain": 0.03844586965639227, "wins": 54, "losses": 16, "median_delta": 0.0010183441024261266, "p": 2.6469292099729694e-07, "family_d0": 0.24272532701248975, "family_d32": 0.27836120757182914}
EXPECTED_ROBUST = {
    "u237": {
        "ap": (0.2586017077565239, 0.2864346639804091, 6.091233764437019e-11),
        "auroc": (0.6690525371885707, 0.6902959919065496, 0.0012102545069873358),
        "vus_roc": (0.7215649347988493, 0.7356820754553808, 8.299821878179808e-06),
    },
    "m70": {
        "ap": (0.13977235866131896, 0.182969952074689, 0.0004710881178029557),
        "auroc": (0.5259159281384553, 0.5428139503600816, 0.06569318707369064),
        "vus_roc": (0.6087072548069323, 0.6209005304098136, 0.00019538163395649573),
    },
}
EXPECTED_COMMON_ROUNDED = {"u237": (0.3036, 0.3304), "m70": (0.1705, 0.2089)}


def close(got: float, expected: float, label: str, tol: float = ABS_TOL) -> None:
    if not math.isclose(float(got), float(expected), rel_tol=0.0, abs_tol=tol):
        raise SystemExit(f"{label}: expected {expected!r}, got {got!r}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--u237", default="results/u237_delay_selection/summary.json")
    ap.add_argument("--m70", default="results/m70_confirmatory/summary.json")
    ap.add_argument("--robustness", default="results/postfreeze_robustness/summary.json")
    args = ap.parse_args()
    u = json.loads(Path(args.u237).read_text())
    m = json.loads(Path(args.m70).read_text())
    r = json.loads(Path(args.robustness).read_text())

    if u.get("selected_delay") != 32:
        raise SystemExit(f"U237 selected delay mismatch: {u.get('selected_delay')}")
    for d, expected in EXPECTED_U_SWEEP.items():
        close(u["by_delay"][d]["macro_vus_pr"], expected, f"U237 d={d}")
    d32 = u["by_delay"]["32"]
    if d32["paired"]["wins"] != 183 or d32["paired"]["losses"] != 54:
        raise SystemExit("U237 d=32 win/loss count mismatch")
    close(d32["paired"]["median_delta"], 0.003978805351937106, "U237 median delta")
    close(d32["paired"]["wilcoxon_p"], 3.848184724961484e-22, "U237 Wilcoxon p", 1e-30)

    close(m["macro_vus_pr_d0"], EXPECTED_M70["d0"], "M70 d=0")
    close(m["macro_vus_pr_d32"], EXPECTED_M70["d32"], "M70 d=32")
    close(m["absolute_macro_gain"], EXPECTED_M70["gain"], "M70 gain")
    if m["paired_d32_vs_d0"]["wins"] != EXPECTED_M70["wins"] or m["paired_d32_vs_d0"]["losses"] != EXPECTED_M70["losses"]:
        raise SystemExit("M70 win/loss count mismatch")
    close(m["paired_d32_vs_d0"]["median_delta"], EXPECTED_M70["median_delta"], "M70 median delta")
    close(m["paired_d32_vs_d0"]["wilcoxon_p"], EXPECTED_M70["p"], "M70 Wilcoxon p", 1e-12)
    close(m["family_balanced_macro_d0"], EXPECTED_M70["family_d0"], "M70 family-balanced d=0")
    close(m["family_balanced_macro_d32"], EXPECTED_M70["family_d32"], "M70 family-balanced d=32")
    if m.get("all_family_mean_gains_positive") is not True:
        raise SystemExit("not all 12 M70 family mean gains are positive")

    for cohort, metrics in EXPECTED_ROBUST.items():
        for metric, (d0, d32v, p) in metrics.items():
            got = r[cohort]["full"][metric]
            close(got["d0_macro"], d0, f"{cohort} {metric} d=0")
            close(got["d32_macro"], d32v, f"{cohort} {metric} d=32")
            close(got["paired"]["wilcoxon_p"], p, f"{cohort} {metric} p", 1e-10)

    for cohort, (d0, d32v) in EXPECTED_COMMON_ROUNDED.items():
        got = r[cohort]["common_support"]["vus_pr"]
        if round(got["d0_macro"], 4) != d0 or round(got["d32_macro"], 4) != d32v:
            raise SystemExit(f"{cohort} common-support VUS-PR mismatch: {got['d0_macro']} -> {got['d32_macro']}")

    if r["m70"]["full"]["auroc"]["paired"]["wilcoxon_p"] < 0.05:
        raise SystemExit("M70 AUROC unexpectedly became significant")
    print("BLAST_MANUSCRIPT_NUMBERS: PASS")


if __name__ == "__main__":
    main()
