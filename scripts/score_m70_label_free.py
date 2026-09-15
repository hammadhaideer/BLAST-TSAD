#!/usr/bin/env python3
"""Generate the frozen M70 BLAST score artifacts without parsing labels."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

import numpy as np

from blast.core import make_test_scores, robust_prefix_normalize, scalar_endpoint_score
from blast.data import load_cohort, read_features_label_free, train_index_from_name
from blast.provenance import M70_COHORT_SHA256, TSB_AD_M_SHA256, require_sha256, sha256_file

WINDOW = 256
DSTAR = 32


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/tsb_ad/TSB-AD-M.zip")
    ap.add_argument("--cohort", default="configs/rangerank_tsbad_m_confirmatory_70.txt")
    ap.add_argument("--out", default="results/m70_label_free")
    args = ap.parse_args()

    data_sha = require_sha256(args.data, TSB_AD_M_SHA256, "TSB-AD-M archive")
    cohort_sha = require_sha256(args.cohort, M70_COHORT_SHA256, "M70 cohort")
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
            d0, valid0 = make_test_scores(endpoint, train_index, 0)
            d32, valid32 = make_test_scores(endpoint, train_index, DSTAR)

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
                valid_d0=valid0,
                valid_d32=valid32,
                label_values_parsed=np.asarray(False),
            )
            artifacts.append(path)

    manifest = out / "pointwise_manifest.sha256"
    manifest.write_text("".join(f"{sha256_file(p)}  {p.name}\n" for p in sorted(artifacts)))
    summary = {
        "status": "LABEL_FREE_SCORING_COMPLETE",
        "series": len(names),
        "window": WINDOW,
        "frozen_delay": DSTAR,
        "label_values_parsed": False,
        "anomaly_metric_computed": False,
        "normalization": "training-prefix median / (1.4826*MAD), with 64*eps*max(1,|median|) floor, sample-std fallback, then 1.0",
        "right_boundary": "zero-filled outside formal support; validity masks stored",
        "provenance": {
            "data_sha256": data_sha,
            "cohort_sha256": cohort_sha,
            "pointwise_manifest_sha256": sha256_file(manifest),
        },
    }
    (out / "label_free_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
