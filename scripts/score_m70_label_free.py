#!/usr/bin/env python3
"""Generate M70 BLAST score artifacts without parsing label values."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np

from blast.core import make_test_scores, robust_prefix_normalize, scalar_endpoint_score
from blast.data import load_cohort, read_features_label_free, train_index_from_name

WINDOW = 256
DSTAR = 32


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/tsb_ad/TSB-AD-M.zip")
    ap.add_argument("--cohort", default="configs/rangerank_tsbad_m_confirmatory_70.txt")
    ap.add_argument("--out", default="results/m70_label_free")
    args = ap.parse_args()

    names = load_cohort(args.cohort)
    if len(names) != 70:
        raise RuntimeError(f"expected 70 M70 members, found {len(names)}")

    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise RuntimeError(f"refusing to overwrite non-empty directory: {out}")
    out.mkdir(parents=True, exist_ok=True)

    artifacts: list[Path] = []
    with zipfile.ZipFile(args.data) as zf:
        for name in names:
            x, feature_names = read_features_label_free(zf, "TSB-AD-M", name)
            train_index = train_index_from_name(name)
            if train_index < WINDOW:
                raise RuntimeError(f"{name}: training prefix shorter than window")

            z, stats = robust_prefix_normalize(x, train_index)
            endpoint = scalar_endpoint_score(z, WINDOW)
            d0, _ = make_test_scores(endpoint, train_index, 0)
            d32, _ = make_test_scores(endpoint, train_index, DSTAR)

            path = out / f"{Path(name).stem}.npz"
            np.savez_compressed(
                path,
                filename=np.asarray(name),
                T=np.asarray(len(x), dtype=np.int64),
                train_index=np.asarray(train_index, dtype=np.int64),
                channel_count=np.asarray(x.shape[1], dtype=np.int64),
                feature_names=np.asarray(feature_names),
                prefix_median=stats.median,
                prefix_scale=stats.scale,
                score_d0=d0,
                score_d32=d32,
                label_values_parsed=np.asarray(False),
            )
            artifacts.append(path)

    manifest = out / "pointwise_manifest.sha256"
    manifest.write_text("".join(f"{sha256(p)}  {p.as_posix()}\n" for p in artifacts))

    summary = {
        "status": "LABEL_FREE_SCORING_COMPLETE",
        "series": len(names),
        "window": WINDOW,
        "frozen_delay": DSTAR,
        "label_values_parsed": False,
        "anomaly_metric_computed": False,
        "normalization": "training-prefix median/MAD with sample-std fallback",
    }
    (out / "label_free_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
