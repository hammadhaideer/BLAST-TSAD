#!/usr/bin/env python3
"""Run the public BLAST manuscript-reproduction pipeline end to end."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    cmd = [sys.executable, *args]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-results", action="store_true", help="refuse to remove an existing results/ directory before reproduction")
    args = ap.parse_args()
    results = ROOT / "results"
    if results.exists():
        if args.keep_results:
            raise SystemExit("results/ already exists; remove it or rerun without --keep-results")
        shutil.rmtree(results)

    run("scripts/verify_repository.py")
    run("scripts/select_u237_delay.py")
    run("scripts/score_m70_label_free.py")
    run("scripts/evaluate_m70_confirmatory.py")
    run("scripts/evaluate_postfreeze_robustness.py")
    run("scripts/check_paper_results.py")
    print("BLAST_PAPER_REPRODUCTION: PASS")
    print(f"Generated outputs: {results}")


if __name__ == "__main__":
    main()
