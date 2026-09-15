# Data Preparation

BLAST uses the public **TSB-AD** benchmark maintained by The Datum Org:

https://github.com/TheDatumOrg/TSB-AD

Dataset archives are not redistributed by this repository. Obtain them from the benchmark source under its original licensing terms.

## Expected layout

Place the independently obtained archives at:

```text
data/
└── tsb_ad/
    ├── TSB-AD-U.zip
    └── TSB-AD-M.zip
```

All runners resolve these paths relative to the repository root by default and also accept explicit path arguments.

## Frozen archive checksums

The submitted study used exactly these archive SHA256 values:

```text
TSB-AD-U.zip  0c47020d3423723c70773736dbd800369f2b487328becbf339450d1ae5020961
TSB-AD-M.zip  7de86ac27f30eeb48d833bb061055670e3f3de07defd995cf2bd5db10ccc9a0d
```

The experiment runners fail closed when these hashes do not match. This prevents an unnoticed benchmark revision from being mistaken for a reproduction of the submitted study.

## Frozen cohorts

The exact cohort manifests are tracked in:

```text
configs/rangerank_tsbad_confirmatory_237.txt
configs/rangerank_tsbad_m_confirmatory_70.txt
```

Their SHA256 values are:

```text
U237 cohort  8572d575e9704920bfb5908478c3feb8672cf3c92f28550e1edb3a476448ffce
M70 cohort   1869a60c4fabd35d19f1c7ce6a149a6d8fe7e6684455fbb3cceda7b3b4fff3f8
```

U237 contains 237 univariate TSB-AD-U series. M70 contains 70 TSB-AD-M series from 12 dataset families.

## Evaluation boundaries

- **U237:** evaluation begins at zero-based raw index `767`.
- **M70:** filenames encode the training-prefix boundary using `_tr_<index>_`; that index is the first evaluation timestamp.

Cohort membership and evaluation boundaries are frozen and must not be changed when reproducing the submitted protocol.

## M70 label handling

M70 score generation is intentionally separated from label-based evaluation.

During label-free scoring, [`blast/data.py`](../blast/data.py) splits each CSV row at the final comma, parses only the feature bytes, and leaves the final label field opaque. Labels are opened only by the later confirmatory-evaluation stage after all score artifacts and their SHA256 manifest already exist.

## Licensing

TSB-AD and its underlying source datasets retain their original licenses and terms. This repository grants no additional redistribution rights for benchmark data.
