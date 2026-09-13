# Data and cohort provenance

The ICASSP 2027 submission uses TSB-AD benchmark archives. Dataset files are not redistributed by this repository.

## Expected local layout

Place independently obtained archives under:

```text
data/
└── tsb_ad/
    ├── TSB-AD-U.zip
    └── TSB-AD-M.zip
```

The public runners resolve these paths relative to the repository root and also accept explicit `--data` arguments.

## Frozen source-archive checksums

The submitted study pinned the following archive SHA256 values:

```text
TSB-AD-U.zip  0c47020d3423723c70773736dbd800369f2b487328becbf339450d1ae5020961
TSB-AD-M.zip  7de86ac27f30eeb48d833bb061055670e3f3de07defd995cf2bd5db10ccc9a0d
```

A strict numerical reproduction should verify these before running the protocol.

## Frozen cohorts

Two cohort manifests are tracked in `configs/`:

```text
configs/rangerank_tsbad_confirmatory_237.txt
configs/rangerank_tsbad_m_confirmatory_70.txt
```

Their frozen SHA256 values are:

```text
U237 cohort  8572d575e9704920bfb5908478c3feb8672cf3c92f28550e1edb3a476448ffce
M70 cohort   1869a60c4fabd35d19f1c7ce6a149a6d8fe7e6684455fbb3cceda7b3b4fff3f8
```

The filenames encode training-prefix boundaries using `_tr_<index>_`. Do not alter cohort membership or those boundaries when reproducing the submitted protocol.

## Label handling

For M70, score generation is intentionally label-free. The public reader in `blast/data.py` splits each CSV row at the final comma, parses only the feature bytes, and leaves the label bytes opaque until the later confirmatory-evaluation stage.

## Licensing

TSB-AD and its underlying source datasets retain their original licenses and terms. This repository does not grant rights to redistribute benchmark data.
