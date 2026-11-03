---
name: dhs-data-pipeline
description: Download, clean, and prep DHS survey data in R.
version: 0.1.0
author: Corey Sparks (coreysparks), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [DHS, demography, data, R, survey, Ethiopia]
    related_skills: []
---

# DHS Data Pipeline Skill

Automates downloading, cleaning, and preparing Demographic and Health Surveys (DHS) data for analysis in R. Covers dataset discovery, download via the `rdhs` package, variable selection, and export to analysis-ready formats. Focused on child health and nutrition outcomes (e.g., stunting, wasting, underweight) but applicable to any DHS topic.

Does NOT run models — output is a clean `.rds` or `.csv` ready for Stan/brms/INLA.

## When to Use

- Pulling a new DHS country/round dataset (e.g., Ethiopia 2016, 2019)
- Re-extracting variables after adding new predictors
- Preparing child-level nutrition outcome datasets
- Merging household, woman, and child recode files

Don't use for: model fitting, post-estimation, or non-DHS survey sources.

## Prerequisites

- R installed with packages: `rdhs`, `haven`, `tidyverse`, `survey`, `here`
- DHS program account credentials stored as env vars:
  - `DHS_EMAIL` — registered email
  - `DHS_PASSWORD` — DHS portal password
  - `DHS_PROJECT` — project name as registered on the DHS website
- Run `Rscript -e "rdhs::set_rdhs_config()"` once interactively to cache credentials

## How to Run

```
terminal(command="Rscript C:/Users/corey/litsearch/dhs_pipeline.R --country ET --round 7 --outcome stunting", timeout=300)
```

Or invoke step-by-step via `terminal` calls (see Procedure).

## Quick Reference

```r
library(rdhs)
# Search datasets
dhs_datasets(countryIds="ET", surveyYearStart=2016)
# Download
datasets <- get_datasets(dataset_filenames)
# Load
dat <- readRDS(datasets[["ETKI71FL"]])
```

## Procedure

1. **Set credentials** — confirm `DHS_EMAIL`, `DHS_PASSWORD`, `DHS_PROJECT` are set; run `rdhs::set_rdhs_config(email=..., project=..., password=...)` once.
2. **Identify dataset** — use `dhs_datasets(countryIds="ET", surveyYearStart=YYYY)` to find the correct filename (KR = kids recode, HR = household, IR = individual/woman).
3. **Download** — `get_datasets(dataset_filenames)` fetches and caches `.dta` files locally under `~/.rdhs/`.
4. **Load and recode** — read with `haven::read_dta()`; apply DHS variable labels; create binary outcome columns (e.g., `stunted = hw70 < -200`).
5. **Merge recodes** — join KR + HR on `hv001`/`hv002` cluster/household keys; join IR on `caseid` if maternal variables needed.
6. **Apply survey design** — `svydesign(ids=~v021, strata=~v022, weights=~v005/1e6, data=dat, nest=TRUE)`.
7. **Export** — `saveRDS(dat, "data/ET_KR_clean.rds")` and optionally `write_csv(dat, "data/ET_KR_clean.csv")`.

## Pitfalls

- DHS weights (`v005`) must be divided by 1,000,000 before use in `svydesign`.
- `hw70`/`hw71`/`hw72` (HAZ/WAZ/WHZ) use -9999 as missing — recode to `NA` before computing outcomes.
- Cluster IDs (`v021`) are not globally unique across rounds; always filter to a single survey before merging.
- `rdhs` caches datasets; if a file is corrupt, delete `~/.rdhs/datasets/` and re-download.
- DHS `.dta` files are Stata 14+ format — use `haven::read_dta()`, not `foreign::read.dta()`.
- The DHS API rate-limits; add `Sys.sleep(1)` between repeated dataset calls.

## Verification

- Row count matches DHS report's published sample size (±1% for filter differences).
- Outcome variable prevalence (e.g., stunting %) matches DHS key indicators table.
- `svydesign` object has correct number of strata and PSUs before proceeding to modeling.
