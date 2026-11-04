# Content review checklist

Use this while editing each chapter. It collects the problems actually found when converting DEM 7273 (2017 handouts), plus the general classes they belong to. Old teaching notes were usually written quickly the night before class, so expect several of these in every chapter. The audit script finds the mechanical ones; this list is for the ones that need reading and judgment.

## Contents

1. Statistical formulas
2. Statistical statements in prose
3. Code that runs but is wrong
4. Code that no longer runs
5. Text that doesn't match the output
6. Leftovers from other courses or examples
7. Prose and structure

---

## 1. Statistical formulas

Check every displayed equation symbol by symbol. These were all wrong in the original DEM 7273 notes:

| Formula | Common error | Correct form |
|---|---|---|
| Binomial pmf | $\binom{y}{n}$ | $\binom{n}{y}\pi^y(1-\pi)^{n-y}$ |
| Standard error of the mean | $\sigma/n$ | $\sigma/\sqrt{n}$; variance of $\bar{y}$ is $\sigma^2/n$ |
| Mean squared deviation of $\bar y$ | $E[(y-\mu)] = \sigma/n$ | $E[(\bar{y}-\mu)^2] = \sigma^2/n$ |
| Within-group SS (ANOVA) | deviations from the *grand* mean | $\sum_j\sum_i (y_{ij}-\bar{y}_{.j})^2$, deviations from the *group* mean |
| ANOVA model | "product of three terms" | a *sum*: $y_{ij} = \mu + \tau_j + \epsilon_{ij}$ |
| $R^2$ | $SSB/SST$ with inconsistent names | $SSB/TSS$; use one name for total SS throughout |
| Family-wise error | "more like .05/#tests" | $1-(1-\alpha)^m$ (Bonferroni *divides alpha* to control it) |
| Covariance | double sum, no denominator | $\sum_i (x_i-\bar x)(y_i-\bar y)/(n-1)$ |
| Pearson correlation | double sum over $\sigma_x\sigma_y$ | $s_{xy}/(s_x s_y)$ |
| Regression MSE | $\sum(y_i-\bar y)^2/(n-p)$ | $\sum(y_i-\hat y_i)^2/(n-p)$ |
| SE of slope | $\text{MSE}/S_{xx}$ | $\sqrt{\text{MSE}/S_{xx}}$ |
| Multiple regression | missing `+` before $\epsilon$; sum index reused | $y_i = \beta_0 + \sum_{k=1}^p \beta_k x_{ik} + \epsilon_i$ |
| Design matrix | subscripts scrambled | row $i$ is $(1, x_{1i}, x_{2i})$ |
| AIC | $RSS + 2k$ | $-2\log L + 2k$ ($= n\log(RSS/n)+2k$ + const for OLS) |
| Logit link | "inverse logit is $\log(p/(1-p))$" | logit is $\log(p/(1-p))$; inverse logit is $1/(1+e^{-x})$ |
| Predicted probability | $1/(1+\exp(\beta_0+\ldots))$ | $1/(1+\exp(-(\beta_0+\ldots)))$ |
| Probit | $E(y) = \Phi^{-1}(p) = \Phi(x\beta)$ | $\Phi^{-1}(p) = x\beta$, so $p = \Phi(x\beta)$ |

Also check that any `$...$` math with `\binom`, `\sum`, subscripts, etc. actually renders (Quarto uses MathJax).

## 2. Statistical statements in prose

- **Gauss–Markov theorem** is often cited as the *method* for solving OLS. It isn't: least squares minimization gives the estimator; Gauss–Markov says it's BLUE under the assumptions.
- **Median** is not always an observed value (even $n$). The mode is.
- **Confidence intervals**: make sure the "it IS..." definition is the repeated-sampling one.
- **Bootstrap** resamples *with* replacement, from the *observed data*, not "from the population".
- **Poisson / binomial** values are non-negative, not "positive".
- **Standardized coefficients**: $\beta$ is the change in *y* per SD change in *x* (a frequent "change in x" typo). Interpret all predictors per SD, not "1 unit".
- **Partial effects** hold other predictors constant, not "at their means".
- **"Independent variables"** are sometimes defined as predictors that are independent of *each other*. They aren't (that's what multicollinearity is about); say "ideally each reflects a unique component of the outcome".
- **K-S test** on residuals with estimated parameters is too lenient (Lilliefors). Use studentized residuals and say so.
- **Kendall's tau/phi on large samples**: significance is not strength; say so when $n$ is large.
- **Comparing logit coefficients across groups** is confounded by residual variance (Allison 1999). Add a caution wherever stratified logit coefficients are compared.
- **Welch vs. pooled t-test**: `t.test()` defaults to Welch; `lm()` is pooled. Explain the small difference.
- **Exponentiated mean of logs** is the geometric mean, not the arithmetic mean.
- **Log outcome coefficients**: percent change is $100(e^\beta-1)$.

## 3. Code that runs but is wrong

These produce output, so nobody noticed. Read each custom function and each by-hand calculation.

- Standard error helpers dividing by $n$ (or by `table(is.na(x))[1]`) instead of $\sqrt{n}$.
- `length(x)` used as $n$ when `x` has `NA`s. Use `sum(!is.na(x))`.
- t-test p-value computed with `df = n2 - n1` (nonsense). Use Welch df or `n1 + n2 - 2`.
- Error bars with `ymin = est + 1.96*se, ymax = est - 1.96*se` (flipped).
- SE of a proportion as `sd(x)/length(x)`; should be $\sqrt{p(1-p)/n}$.
- `predict(newdata = ...)` on a model with `scale()` in the formula: re-standardizes the new data with its own mean/SD. Precompute z-scores in the data.
- `glm(y ~ ..., family = binomial)` where `y` is `as.factor()` of a multi-category code: works by accident (first level = 0). Make the binary outcome explicit.
- Hard-coded sample sizes like `sample(1:141000, ...)`: breaks when filters change. Use `slice_sample()`.
- Variables coded with sentinel values (e.g. IPUMS 999999/999998 = N/A/missing) used without recoding in some chunks.
- Inline code referencing a wrong object path (e.g. `sums$sums$r.squared`) renders as blank or errors.
- Comparing nested models fit to different observations (missing data differ). Build a complete-case data set first.
- Labels hard-coded to coefficient positions in base-R plots (`labels = c(...)` in a fixed order). Use the coefficient names.
- Axis labels swapped (`xlab("Income")` on the age axis).
- `chisq.test()` on a different table than the one discussed (e.g. raw `labforce` with a 0 code instead of the recoded variable).

## 4. Code that no longer runs

The audit script flags most of these. Typical replacements:

| Old | Replacement |
|---|---|
| `qplot()` | `ggplot()` + geom, or drop the section |
| `..density..` | `after_stat(density)` |
| `size =`/`lwd =` for lines | `linewidth =` |
| `spread()` / `gather()` | `pivot_wider()` / `pivot_longer()` |
| `.$var` in `case_when()` | `var` |
| `sjPlot::sjp.lm()` | `sjPlot::plot_model()` |
| `multiplot()` from random packages | `patchwork` (`p1 + p2 + plot_layout(ncol = 2)`) |
| `source("https://.../helper.R")` | inline the helper function in the chapter |
| `read_csv(..., col_types = read_rds(url(...)))` | drop `col_types` or define it inline |
| `png("C:/Users/...")` ... `dev.off()` | remove; mention `ggsave()` in a callout |
| `View(df)` | `#| eval: false` or `print(df)` |
| `setwd()` / absolute paths | project-relative paths with `execute-dir: project` |
| `results='asis'` | `#| output: asis` |
| `stargazer(..., type = "html")` | still works with `#| output: asis`; mention `modelsummary` as the modern option |

Packages that were on CRAN in 20XX may be archived now. Test each with `requireNamespace()` and `install.packages()` before relying on it.

## 5. Text that doesn't match the output

The most common problem in old notes: the prose describes numbers from an earlier run, an earlier data version, or a different example.

- Replace every number in the prose that comes from output with inline R: `` `r round(coef(fit)[2], 3)` ``. Compute intermediate values in a hidden chunk (`#| include: false`) to keep inline code short.
- Where the *conclusion* depends on the result (test significant or not, which test rejects), use an inline `if`: `` `r if (p < 0.05) "..." else "..."` ``.
- Format p-values with a helper (`fmt_p()` in `_common.R`), since knitr renders small numbers as `5^{-5}` inline.
- Format tiny coefficients with `format(x, scientific = FALSE)`.
- After rendering, read the rendered text next to the output and verify every interpretive claim (direction, size, "wider", "similar", "significant"). Rewrite claims that the output doesn't support. Do not leave a claim in place because it was in the original.
- `set.seed()` once per chapter (in `_common.R`) so simulated examples are stable.

## 6. Leftovers from other courses or examples

Old notes are often adapted from another course or a previous year. Look for:

- Chunks that reference objects never created (e.g. `svyglm(..., design = des)` with no `des`), usually pasted from a different example. Remove them or move them to the chapter where they belong.
- Interpretation text about a different outcome than the one modeled (e.g. "poor/fair health" in a migration model).
- Titles and numbering that don't match ("Example 3" on the fourth handout, two "Part 2"s, "Last time we saw..." referring to a lecture that isn't in the repo).
- Links to the previous handout on RPubs or a course site. Replace with cross-references (`@sec-...`).
- Install scripts that install dozens of packages from other courses.

## 7. Prose and structure

- Headers without a space after `#` (pandoc treats them as text). Plain `#` comments or pseudo-code in prose become headers too; put them in a code block.
- Inconsistent heading levels. Chapter title is the only `#`; sections start at `##`.
- Repeated boilerplate (the same "Really real data example" paragraph in every handout). Say it once in the preface or first use, then cross-reference.
- Definitions lists written as run-on lines (no blank lines). Convert to proper lists.
- "Sneaky" typos to search for: who's/whose, it's/its, affect/effect, verses/versus, principle/principal, compliment/complement, "the the".
- Keep the instructor's voice: humor, first person, direct "you". Edit for clarity and correctness, don't flatten it.
- Pejoratives about other software ("SPSS (barf!)") are fine in a classroom but may not be in a public book. Ask, or soften.
- Each chapter ends with an "Additional resources" section of 3–6 annotated items. Check every URL. Prefer free, stable sources; give full citations for print books.
