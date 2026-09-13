# Data layout

The BLAST study uses TSB-AD benchmark archives. Dataset files are not redistributed by this repository.

## Expected local layout

Place locally obtained archives under:

```text
data/
└── tsb_ad/
    ├── TSB-AD-U.zip
    └── TSB-AD-M.zip
```

The public scripts resolve paths relative to the repository root.

## Cohorts

Two frozen cohort lists are included in `configs/`:

- `rangerank_tsbad_confirmatory_237.txt` — U237 development cohort;
- `rangerank_tsbad_m_confirmatory_70.txt` — M70 confirmation cohort.

The filenames encode the training-prefix boundary used by the frozen scoring pipeline. Do not alter cohort membership or training-boundary fields when reproducing the study.

## Dataset provenance

The frozen experimental archive records SHA256 checksums for the source dataset archives. Those checksums are retained in the private audit record and should be used to verify exact byte-level provenance before attempting a strict numerical reproduction.

## Licensing

TSB-AD and any underlying source datasets retain their original licenses and terms. This repository does not grant rights to redistribute them.
