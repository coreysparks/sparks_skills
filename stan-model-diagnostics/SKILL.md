---
name: stan-model-diagnostics
description: Run Bayesian diagnostics on a fitted Stan/brms model.
version: 0.1.0
author: Corey Sparks (coreysparks), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Stan, Bayesian, MCMC, diagnostics, R, brms, rstan]
    related_skills: []
---

# Stan Model Diagnostics Skill

Runs the standard suite of Bayesian MCMC diagnostics on a fitted `rstan` or `brms` model object and produces a markdown report with numeric summaries and saved plots. Covers convergence (Rhat, ESS), sampler health (divergences, treedepth, BFMI), posterior predictive checks, and leave-one-out cross-validation (LOO-CV).

Does NOT refit models — the fitted object must already exist on disk as an `.rds` file.

## When to Use

- After fitting a Stan or brms model, before writing up results
- Comparing two model fits via LOO
- Investigating convergence warnings from `rstan` or `cmdstanr`
- Producing a diagnostics appendix for a manuscript

Don't use for: model specification, prior predictive checks, or non-Stan models.

## Prerequisites

- R with packages: `rstan` or `brms`, `bayesplot`, `loo`, `posterior`, `tidyverse`, `knitr`
- Fitted model saved as `.rds`: `saveRDS(fit, "models/my_model.rds")`

## How to Run

```
terminal(command="Rscript C:/Users/corey/scripts/stan_diagnostics.R --model models/my_model.rds --out reports/diagnostics_my_model.md", timeout=180)
```

Or run the steps below interactively via `terminal` R calls.

## Procedure

1. **Load the model** — `fit <- readRDS("models/my_model.rds")`; confirm class is `stanfit` or `brmsfit`.
2. **Rhat and ESS** — `posterior::summarise_draws(fit)` or `brms::summary(fit)`. Flag any parameter with `Rhat > 1.01` or `ess_bulk < 400`.
3. **Divergences and treedepth** — for `stanfit`: `rstan::get_num_divergences(fit)`; `rstan::check_treedepth(fit)`. For `brmsfit`: `brms::nuts_params(fit)`. Any divergences require investigation before trusting results.
4. **BFMI** — `rstan::get_bfmi(fit)`; values < 0.2 indicate poor energy exploration.
5. **Trace plots** — `bayesplot::mcmc_trace(as.array(fit), pars=c(...))` for key parameters; save with `ggsave()`.
6. **Posterior predictive check** — `brms::pp_check(fit)` or `bayesplot::ppc_dens_overlay(y, yrep[1:50,])`; save plot.
7. **LOO-CV** — `loo_result <- loo(fit)`; `print(loo_result)`; flag any Pareto-k > 0.7 as problematic observations.
8. **Model comparison (if applicable)** — `loo_compare(loo1, loo2)`; difference > 4 SE is practically meaningful.
9. **Assemble report** — write findings to a markdown file: numeric table of Rhat/ESS, divergence count, BFMI, LOO ELPD, and embedded plot paths.

## Output Template

```markdown
# Stan Diagnostics — <model name> — <date>

## Convergence
| Parameter | Rhat | ESS_bulk | ESS_tail |
|-----------|------|----------|----------|
| ...       | ...  | ...      | ...      |

**Flagged:** <list params with Rhat > 1.01 or ESS < 400, or "none">

## Sampler Health
- Divergences: N
- Max treedepth exceeded: N
- BFMI: [chain values]

## LOO-CV
- ELPD: X.X (SE Y.Y)
- Pareto-k > 0.7: N observations

## Posterior Predictive Check
![PPC plot](reports/ppc_<model>.png)

## Verdict
<Pass / Needs attention / Do not trust — 1-2 sentences>
```

## Pitfalls

- `brmsfit` objects wrap a `stanfit`; extract with `fit$fit` for raw Stan accessors.
- LOO can be slow for large datasets — use `loo(fit, cores=4)` to parallelize.
- Pareto-k warnings do not automatically invalidate the model; use `loo::reloo()` for exact LOO on flagged observations.
- Rhat of exactly 1.000 for every parameter is a red flag (chains may not have mixed — check trace plots).
- `mcmc_trace` on a `brmsfit` requires extracting with `as.array(fit$fit)` or `brms::as_draws_array(fit)`.

## Verification

- All reported Rhat values come from `posterior::summarise_draws()`, not from manual inspection.
- Divergence count matches `rstan::get_num_divergences()` output exactly.
- LOO result printed with `print(loo_result)` and `loo_result$estimates` values match the report.
- Markdown report file exists on disk and plots are non-empty PNGs.
