# Expected Manuscript Results

This page records the **final BLAST numbers reported in the ICASSP 2027 submission** and the higher-precision values retained for public reproduction checks. These values are a verification ledger; they are never read by the score-generation or metric-computation code.

The executable checker [`scripts/check_paper_results.py`](../scripts/check_paper_results.py) compares freshly generated outputs with this ledger.

## Primary operating point

- causal score: trailing sample standard deviation;
- window: `W = 256`;
- frozen BLAST delay: `d* = 32` samples;
- primary metric: VUS-PR;
- controlled baseline: the **same endpoint-score stream** under `d = 0`.

## Primary VUS-PR results

| Cohort | `d=0` | `d=32` | Gain | Wins | Median paired gain | Wilcoxon `p` |
|---|---:|---:|---:|---:|---:|---:|
| U237 development | 0.3042832564 | 0.3300181420 | +0.0257348855 | 183 / 237 | +0.0039788054 | 3.848e-22 |
| M70 confirmation | 0.1704915933 | 0.2089374630 | +0.0384458697 | 54 / 70 | +0.0010183441 | 2.647e-7 |

The M70 relative macro VUS-PR increase is approximately **22.6%**. M70 family-balanced VUS-PR changes from **0.2427253270** to **0.2783612076**, a gain of **0.0356358806**, and all 12 family mean VUS-PR gains are positive.

<p align="center">
  <img src="../assets/paper/Figure3_M70_family_gain_FINAL.png" width="520" alt="Family-wise M70 mean VUS-PR gain at d*=32">
</p>

<p align="center"><em>Family-wise M70 confirmation at the frozen `d*=32`; all 12 family means are positive.</em></p>

## U237 development-only latency sweep

| Delay | `d/W` | Macro VUS-PR | Gain vs. `d=0` | Selection role |
|---:|---:|---:|---:|---|
| 0 | 0.000 | 0.3042832564 | 0.0000000000 | endpoint reference |
| **32** | **0.125** | **0.3300181420** | **+0.0257348855** | **smallest passing low-latency candidate** |
| 64 | 0.250 | 0.3503386609 | +0.0460554044 | passing low-latency candidate |
| 96 | 0.375 | 0.3676137171 | +0.0633304607 | development sweep only |
| 127 | 0.496 | 0.3695643623 | +0.0652811058 | development sweep only |

All four nonzero delays satisfy the generic positive-development gates, but the frozen rule selects the **smallest passing delay within the predeclared low-latency set `{32,64}`**. Therefore `d*=32` is frozen before M70 confirmation; it is not the development optimum.

## Post-freeze metric robustness

| Cohort | Metric | `d=0` | `d=32` | Gain | Wilcoxon `p` |
|---|---|---:|---:|---:|---:|
| U237 | AP | 0.2586017078 | 0.2864346640 | +0.0278329562 | 6.091e-11 |
| U237 | AUROC | 0.6690525372 | 0.6902959919 | +0.0212434547 | 1.210e-3 |
| U237 | VUS-ROC | 0.7215649348 | 0.7356820755 | +0.0141171407 | 8.300e-6 |
| M70 | AP | 0.1397723587 | 0.1829699521 | +0.0431975934 | 4.711e-4 |
| M70 | AUROC | 0.5259159281 | 0.5428139504 | +0.0168980222 | **0.0657** |
| M70 | VUS-ROC | 0.6087072548 | 0.6209005304 | +0.0121932756 | 1.954e-4 |

The M70 AUROC increase is numerical but **not statistically significant at `p<0.05`**. The repository preserves this negative robustness detail explicitly.

## Common-support boundary sensitivity

The primary implementation preserves output length by zero-filling the final `d` positions that have no future endpoint score. As a post-freeze boundary check, both arms are also evaluated on identical temporal support by removing the final 32 samples from each.

| Cohort | Common-support `d=0` | Common-support `d=32` | Gain | Wilcoxon `p` |
|---|---:|---:|---:|---:|
| U237 | 0.303624181 | 0.330447853 | +0.026823672 | 2.48571e-23 |
| M70 | 0.170531317 | 0.208923014 | +0.038391697 | 1.16342e-7 |

The manuscript rounds these values to `0.3036→0.3304` and `0.1705→0.2089`. The improvement therefore persists when right-edge zero filling is removed from both arms.

## Contextual TimeRCD value

The manuscript reports a reproduced **TimeRCD VUS-PR of 0.2101** on the same M70 evaluation region for context only. TimeRCD uses a different full-series zero-shot information-access protocol, so it is **not** a controlled causal competitor to BLAST. This repository reproduces the controlled BLAST experiment and does not vendor or modify the TimeRCD implementation.

## Paper figures

The final paper figures are included under [`../assets/paper/`](../assets/paper/) as documentation assets:

- `Figure1.png` — endpoint assignment versus BLAST attribution;
- `Figure2_BLAST_final.png` — causal workflow and development-to-confirmation freeze;
- `Figure3_M70_family_gain_FINAL.pdf` — original vector family-gain figure;
- `Figure3_M70_family_gain_FINAL.png` — web-rendered copy used in this documentation.

Their SHA256 values are tracked in `assets/paper/SHA256SUMS.txt` and checked by `scripts/verify_repository.py`.

## Interpretation

BLAST improves **temporal localization** of a fixed causal score stream under an explicitly declared evidence delay. These results do not imply earlier computation, earlier alarm delivery, or earlier intervention, and they do not establish `d*=32` as universally optimal for other score streams.
