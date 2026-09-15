# Expected Manuscript Results

This page records the **final BLAST numbers reported in the ICASSP 2027 submission** for **BLAST: Bounded-Latency Attribution of Streaming Time-Series Anomalies**, together with higher-precision values used by the public reproduction checker. These values are a verification ledger; score generation and metric computation never read them.

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

The M70 relative macro VUS-PR increase is approximately **22.6%**. Family-balanced VUS-PR changes from **0.2427253270** to **0.2783612076**, a gain of **0.0356358806**.

<p align="center">
  <img src="../assets/paper/figure3_confirmation_summary.svg" width="700" alt="Frozen M70 confirmation summary">
</p>

## M70 family-wise confirmation

All 12 family means are positive under the frozen `d*=32` setting.

| Family | n | `d=0` | `d=32` | Gain |
|---|---:|---:|---:|---:|
| CATSv2 | 5 | 0.162618 | 0.167985 | +0.005367 |
| Exathlon | 2 | 0.963814 | 0.978489 | +0.014675 |
| GECCO | 1 | 0.124383 | 0.157620 | +0.033237 |
| GHL | 25 | 0.015356 | 0.015492 | +0.000136 |
| Genesis | 1 | 0.003901 | 0.003979 | +0.000078 |
| MITDB | 6 | 0.208069 | 0.235224 | +0.027155 |
| MSL | 3 | 0.392138 | 0.506789 | +0.114651 |
| PSM | 1 | 0.142895 | 0.147558 | +0.004663 |
| SMAP | 10 | 0.120347 | 0.241150 | +0.120803 |
| SMD | 3 | 0.358585 | 0.400422 | +0.041837 |
| SVDB | 12 | 0.310361 | 0.372924 | +0.062563 |
| SWaT | 1 | 0.110238 | 0.112704 | +0.002466 |

## U237 development-only latency sweep

| Delay | `d/W` | Macro VUS-PR | Gain vs. `d=0` | Selection role |
|---:|---:|---:|---:|---|
| 0 | 0.000 | 0.3042832564 | 0.0000000000 | endpoint reference |
| **32** | **0.125** | **0.3300181420** | **+0.0257348855** | **smallest passing low-latency candidate** |
| 64 | 0.250 | 0.3503386609 | +0.0460554044 | passing low-latency candidate |
| 96 | 0.375 | 0.3676137171 | +0.0633304607 | development sweep only |
| 127 | 0.496 | 0.3695643623 | +0.0652811058 | development sweep only |

All four nonzero delays satisfy the generic development gates, but the frozen rule selects the **smallest passing delay within the predeclared low-latency set `{32,64}`**. Therefore `d*=32` is frozen before M70 confirmation; it is not the development optimum.

## Post-freeze metric robustness

| Cohort | Metric | `d=0` | `d=32` | Gain | Wilcoxon `p` |
|---|---|---:|---:|---:|---:|
| U237 | AP | 0.2586017078 | 0.2864346640 | +0.0278329562 | 6.091e-11 |
| U237 | AUROC | 0.6690525372 | 0.6902959919 | +0.0212434547 | 1.210e-3 |
| U237 | VUS-ROC | 0.7215649348 | 0.7356820755 | +0.0141171407 | 8.300e-6 |
| M70 | AP | 0.1397723587 | 0.1829699521 | +0.0431975934 | 4.711e-4 |
| M70 | AUROC | 0.5259159281 | 0.5428139504 | +0.0168980222 | **0.0657** |
| M70 | VUS-ROC | 0.6087072548 | 0.6209005304 | +0.0121932756 | 1.954e-4 |

The M70 AUROC increase is numerical but **not statistically significant at `p<0.05`**. This negative robustness detail is preserved explicitly.

## Common-support boundary sensitivity

The primary implementation preserves output length by zero-filling the final `d` positions that have no future endpoint score. As a post-freeze boundary check, both arms are also evaluated on identical temporal support by removing the final 32 samples from each.

| Cohort | Common-support `d=0` | Common-support `d=32` | Gain | Wins | Wilcoxon `p` |
|---|---:|---:|---:|---:|---:|
| U237 | 0.303624181 | 0.330447853 | +0.026823672 | 185 / 237 | 2.48571e-23 |
| M70 | 0.170531317 | 0.208923014 | +0.038391697 | 57 / 70 | 1.16342e-7 |

The improvement therefore persists when right-edge zero filling is removed from both arms.

## Contextual TimeRCD value

The manuscript reports a reproduced **TimeRCD VUS-PR of 0.2101** on the same M70 evaluation region for context only. TimeRCD uses a different full-series zero-shot information-access protocol, so it is **not** a controlled causal competitor to BLAST. This repository reproduces the controlled BLAST experiment and does not vendor or modify the TimeRCD implementation.

## Documentation figures

Browser-friendly vector figures are included under [`../assets/paper/`](../assets/paper/):

- `figure1_attribution.svg` — endpoint assignment versus BLAST attribution;
- `figure2_workflow.svg` — fixed causal scoring and frozen development-to-confirmation workflow;
- `figure3_confirmation_summary.svg` — headline M70 confirmation summary.

They are explanatory documentation assets only and are not read by experimental code. Their SHA256 values are tracked in `assets/paper/SHA256SUMS.txt` and checked by `scripts/verify_repository.py`.

## Interpretation

BLAST improves **temporal localization** of a fixed causal score stream under an explicitly declared evidence delay. These results do not imply earlier computation, earlier alarm delivery, or earlier intervention, and they do not establish `d*=32` as universally optimal for other score streams.
