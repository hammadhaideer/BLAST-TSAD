# Public release status

## Visibility

This repository is public and may be linked from the BLAST manuscript.

## What is public now

- core M70 BLAST scoring code;
- confirmatory-analysis code;
- frozen cohort configuration files;
- environment/dependency specifications;
- protocol, data-layout, and reproducibility documentation;
- citation metadata.

## What is intentionally not public

- manuscript source or submitted PDF;
- figures or paper tables;
- generated numerical results;
- pointwise score arrays;
- raw benchmark datasets;
- model checkpoints and caches;
- the internal audit bundle and development logs.

## Dependency-closure status

The current code companion still depends on helper/freeze artifacts from the frozen experimental repository that are not yet present in this public snapshot. The public repository should not be described as a complete clean-room numerical reproduction until those exact frozen dependencies are copied from the audit bundle and verified.

This file will be updated when dependency closure has been completed.
