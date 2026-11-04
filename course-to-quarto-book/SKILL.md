---
name: course-to-quarto-book
description: Convert an old course repository of R Markdown lecture notes and handouts into a cleaned-up, edited Quarto book published to GitHub Pages with GitHub Actions, plus a student package-installer script and setup guide. Use this whenever the user wants to modernize, clean up, revise, or share old course materials, notes, examples, or handouts (.Rmd or .qmd files) from a class they taught, turn a folder of lectures into a book or website, convert R Markdown to Quarto for a course, or publish course notes on GitHub Pages, even if they don't say "book" or "Quarto".
version: 1.0.0
author: Corey Sparks (coreysparks)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [teaching, quarto, R, rmarkdown, github-pages, github-actions, course-materials]
    related_skills: [my-writing-style, my-colors, quarto]
---

# Course notes to Quarto book

Turns a repository of old weekly R Markdown handouts into a book people can actually use: one Quarto book with a preface and a setup page, chapters that run on current R, prose that's been edited and checked against the output, further reading for each chapter, a one-line package installer for students, and automatic publishing to GitHub Pages.

This workflow was built converting DEM 7273 (a 2017 graduate statistics course, 12 handouts). Expect the same kinds of problems in any old course repo. The notes were written quickly, the data links rot, packages change, and nobody re-checked the numbers in the prose. So treat it as an editing and verification job, not a file-format conversion.

## What you need from the user

Most of this can be inferred from the repo (README, YAML headers, git remote). Ask only for what you can't find:

- Course code and title, the year it was taught, and the author name to show.
- Whether to publish now (pushing to the default branch deploys the site).

Make reasonable choices yourself about chapter order, titles, file names, and parts, and report them at the end. Ask before you do something the user would want a say in: replacing a data set with a different one, cutting substantive content, or pushing.

If the user has `my-writing-style`, `my-colors`, or `quarto` skills, load them before editing. The prose should stay in the instructor's teaching voice, and plots and theme should use their palette. The bundled `_common.R` and `utsa.scss` use the UTSA palette via the `sparkscolors` package; swap them for another institution's colors if that applies.

## Workflow

### 1. Audit before touching anything

Run the audit script on the repo:

```bash
python3 -I <skill-dir>/scripts/audit_course.py <repo> --out <scratch>/audit.md
```

It reports, for every `.Rmd/.qmd/.R` file: title and date, broken headers, old-style chunk options, packages used, deprecated idioms, local paths, `View()`/`setwd()`, missing `set.seed()`, and prose lines with numbers that look like hard-coded results. It also checks every remote URL in the code. This matters most: data files on GitHub often turn into **Git LFS pointer files** or 404s, and the code then fails with confusing errors like `object 'TFR' not found`.

Then **read every source file in full**. The script finds mechanical problems; you need to read the files to find formulas that are wrong, chunks pasted from a different example, and prose about a different outcome than the one modeled. Also check which R packages are installed (`requireNamespace`) and which data URLs work, and download any large data file once to a scratch folder to inspect variable codes.

Fix data problems before writing chapters:
- A data file that exists in the repo itself: read it from the repo's own raw URL (`https://raw.githubusercontent.com/<user>/<repo>/<branch>/data/<file>`). This works for students who haven't cloned the repo, and for CI.
- An LFS pointer: `https://media.githubusercontent.com/media/<user>/<repo>/<branch>/<file>` sometimes works, but it's subject to bandwidth quotas. Prefer copying the file into the course repo's `data/` if the license allows.
- Gone entirely: substitute the closest available data (ask the user first), and say so in the preface.

### 2. Scaffold the book

```
<repo>/
├── _quarto.yml            # from assets/_quarto.yml
├── index.qmd              # preface (write it; see below)
├── setup.qmd              # from assets/setup.qmd ("Before the First Class")
├── chapters/NN-slug.qmd   # one per handout, in teaching order
├── _common.R              # from assets/_common.R (seed, plot colors, fmt_p())
├── utsa.scss              # from assets/utsa.scss
├── install_packages.R     # from assets/install_packages.R
├── .github/workflows/publish.yml   # from assets/publish.yml
├── .gitignore             # from assets/gitignore
└── data/
```

- Move files with `git mv old.Rmd chapters/NN-slug.qmd` so history follows them. Delete stale rendered `.html` files from the old setup (`git rm`). They're build artifacts.
- Fill every `{{PLACEHOLDER}}` in the templates. `grep -rn '{{' .` afterwards to make sure none are left.
- `execute-dir: project` in `_quarto.yml` means code runs from the repo root, so `data/file.csv` and `source("_common.R")` work from any chapter.
- Group chapters into `part:`s by topic.

The **preface** (`index.qmd`, unnumbered) should say what the course was (number, title, institution, year), the idea that organizes it, how the book is laid out (one line per part), where the software setup lives (link to `setup.qmd` and show the one-line installer), the data sets used with links and citation requirements (IPUMS, DHS, and so on), what changed from the original handouts (especially substituted data), and how to render it.

### 3. Convert each chapter

For each file:

- Replace the YAML header with a level-1 chapter title and an id: `# Comparing Two Groups {#sec-two-groups}`.
- First chunk:
  ````
  ```{r}
  #| label: setup
  #| include: false
  source("_common.R")
  ```
  ````
- Convert every chunk to `#|` options and give each a unique kebab-case label. `results='asis'` becomes `#| output: asis`. `eval=F` becomes `#| eval: false`.
- Fix headers (`##Title` becomes `## Title`). Only the chapter title is `#`. Pseudo-code or comments in prose that start with `#` must go in a code block, or they become headers.
- Replace "see last week's handout" and RPubs links with cross-references (`@sec-...`).
- Say the repeated boilerplate (the same data-description paragraph in every handout) once, then point back to it.
- Fix code from the audit, using the replacement table in `references/content-review-checklist.md`.
- End with `## Additional resources {.unnumbered}`: 3–6 annotated items (free online books, package docs, the classic paper on the topic). Check every URL with `curl -sIL -o /dev/null -w '%{http_code}'`. Some sites return 403 or 406 to curl but work in a browser; prefer an alternative or a DOI.

### 4. Edit and correct the content

Work through `references/content-review-checklist.md` for every chapter. It lists the formula errors, wrong-but-running code, and statistical misstatements that turned up in practice, which you'd otherwise miss.

Principles:
- **Correctness first.** Fix wrong formulas and wrong code even if the output "looked fine".
- **Keep the voice.** The instructor's humor, asides, and first-person stance are part of the material. Edit for clarity, consistency, and accuracy; don't rewrite it into textbook prose.
- **No hard-coded results.** Every number in the prose that comes from output becomes inline R. Every conclusion that depends on a result (significant or not, which is larger) is generated with an inline `if`, so a re-render can never contradict the text. Use `fmt_p()` from `_common.R` for p-values.
- **Modernize gently.** Update to current idioms where the old code is deprecated or broken. Don't rewrite working base R into tidyverse just for style. Students may be learning both.

### 5. Render and verify

```bash
quarto render 2>&1 | grep -iE "error|warn|quitting|unable"
```

Render early (after the first two or three chapters) to catch setup problems, then render the whole book. Fix every error and every unresolved cross-reference warning.

Then **verify the prose against the output**. This is the step that makes the book trustworthy:

```bash
bash <skill-dir>/scripts/rendered_text.sh docs <scratch>/text
```

Read each chapter's text and check every interpretive sentence against the printed output above it: direction, rough size, "wider/narrower", "significant", "similar", which test rejects. Fix claims the output doesn't support. Also `grep '\^{-'` for badly formatted inline numbers.

Look at a few figures (open the PNGs in `docs/chapters/*_files/figure-html/`). Check that the palette applied, categories are distinguishable, and nothing is hidden. For example, dark box fills can hide a dark median line; give that plot a gray outline.

Ignore IDE "no symbol named X in scope" warnings on `.qmd` files. The linter doesn't see `library()` calls in earlier chunks.

### 6. Student installer and setup page

`install_packages.R` (base R only, so it runs on a fresh install) checks the R version, installs only missing packages, verifies each loads, and test-downloads the course data. Students run one line:

```r
source("https://raw.githubusercontent.com/<user>/<repo>/<branch>/install_packages.R")
```

Fill its package list from the audit's "Packages used", minus any you removed. Fill the setup page's package table to match. Test both paths:

```bash
Rscript install_packages.R          # "already installed" path
# "install" path, into a throwaway library so the user's library is untouched:
sed 's/"tidyverse",/"fortunes", "tidyverse",/' install_packages.R > /tmp/t.R
Rscript -e ".libPaths(c('/tmp/lib', .libPaths())); source('/tmp/t.R')"
```

### 7. Publishing with GitHub Actions

- `publish.yml` renders on every push to the default branch and deploys `docs/` with `actions/deploy-pages`. Its package list must include everything the chapters load (plus `github::coreysparks/sparkscolors` for the palette).
- Commit `_freeze/` (with `freeze: auto`, CI reuses cached results for unchanged chapters, which keeps builds fast and reproducible). Don't commit `docs/`; the workflow builds it.
- In the repo settings, **Pages > Source must be "GitHub Actions"**. Ask the user to set this, or check with `gh api repos/<user>/<repo>/pages`.
- Write the README: link to the published book (`https://<user>.github.io/<repo>/`), a contents table, student setup steps, data sources, repo layout, how to build locally, how publishing works, and a short "changes from the original" list.
- Pushing deploys the site, so confirm with the user before pushing. If `git push` hangs with no output, it's usually waiting on a macOS keychain prompt. Kill it and push with `git -c credential.helper= -c "credential.helper=!gh auth git-credential" push origin <branch>`.
- Watch the run: `gh run list -R <user>/<repo> -L 3` and `gh run view <id> --log-failed` if it fails. The most common CI failure is a package missing from `publish.yml`.

## Report back

Tell the user, briefly:
- where the book lives (URL) and whether the deploy succeeded,
- what was wrong and fixed (data problems, formula errors, broken or misleading code, leftover content), by category with one or two examples each,
- anything that changed substantively (substituted data, cut sections, rewritten interpretations),
- anything left undone or that needs their judgment.

## Bundled files

- `scripts/audit_course.py`: pre-conversion audit (stdlib Python; `--no-network` to skip URL checks).
- `scripts/rendered_text.sh`: rendered book to plain text for claim checking.
- `references/content-review-checklist.md`: the formula/code/prose error catalog. Read it before editing chapters.
- `assets/_quarto.yml`, `assets/publish.yml`, `assets/gitignore`: book config, CI workflow, ignore rules.
- `assets/_common.R`: seed, ggplot2 theme and UTSA palette defaults, base-R palette, `fmt_p()`.
- `assets/utsa.scss`: book theme in UTSA colors.
- `assets/install_packages.R`, `assets/setup.qmd`: student installer and the "Before the First Class" page.
