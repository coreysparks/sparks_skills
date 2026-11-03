# sparks_skills

Personal [Hermes Agent](https://hermes-agent.nousresearch.com) skills by [Corey Sparks](https://github.com/coreysparks) — demographer, data scientist, and population health researcher at UTSA.

## Skills

### 📚 weekly-literature-search
Weekly digest of academic literature in spatial demography, Bayesian spatial epidemiology, and Bayesian demography. Searches PubMed, Crossref, and arXiv; verifies DOIs; deduplicates across runs; delivers a formatted Markdown report by email every Monday at 7 AM.

**Delivery:** Email to `corey.sparks.utsa@gmail.com`
**Schedule:** Every Monday 7:00 AM CST
**Output:** `C:/Users/corey/litsearch/weekly_digest_YYYY-MM-DD.md`

---

### 🌍 dhs-data-pipeline
Automates downloading, cleaning, and preparing Demographic and Health Surveys (DHS) data for analysis in R. Covers dataset discovery via the `rdhs` package, variable selection, household/child/woman recode merging, survey design setup, and export to `.rds`/`.csv`. Focused on child nutrition outcomes (stunting, wasting, underweight) for Ethiopia DHS rounds.

**Key packages:** `rdhs`, `haven`, `tidyverse`, `survey`
**Output:** Analysis-ready `.rds` / `.csv` files

---

### 📊 stan-model-diagnostics
Runs the standard Bayesian MCMC diagnostic suite on a fitted `rstan` or `brms` model and produces a Markdown report. Covers Rhat, ESS, divergences, treedepth, BFMI, posterior predictive checks, and LOO-CV with model comparison.

**Key packages:** `rstan`, `brms`, `bayesplot`, `loo`, `posterior`
**Output:** Markdown diagnostics report + PNG plots

---

### 📝 manuscript-tracker
Tracks academic manuscripts across the full submission lifecycle (in-prep → submitted → under review → R&R → accepted/rejected/published). Stores records in a local JSON file and surfaces upcoming and overdue revision deadlines.

**Data file:** `C:/Users/corey/manuscripts/tracker.json`
**Key fields:** title, journal, status, submitted_date, revision_due

---

## Installation

To use these skills in your own Hermes Agent session, copy any `SKILL.md` into your skills directory:

```bash
# Example: install dhs-data-pipeline
mkdir -p ~/.hermes/skills/research/dhs-data-pipeline
cp dhs-data-pipeline/SKILL.md ~/.hermes/skills/research/dhs-data-pipeline/SKILL.md
```

Then reload skills in a new Hermes session.

## About

Built with [Hermes Agent](https://hermes-agent.nousresearch.com) by Nous Research.
