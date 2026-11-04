# =============================================================================
# {{COURSE_CODE}}: {{COURSE_TITLE}}
# Package installation script
#
# Run this once at the beginning of the semester. In RStudio, either open this
# file and click "Source", or paste this line into the Console:
#
#   source("https://raw.githubusercontent.com/{{GITHUB_USER}}/{{REPO}}/{{DEFAULT_BRANCH}}/install_packages.R")
#
# The script will:
#   1. check that your version of R is recent enough,
#   2. install any course packages you don't already have,
#   3. make sure every package loads, and
#   4. check that you can download the course data.
#
# It's safe to run more than once. Packages you already have are skipped.
# =============================================================================

local({

  # ---- Settings --------------------------------------------------------------
  min_r_version <- "4.1.0"

  # Fill in from the packages the chapters actually load (see the audit
  # script output). Keep knitr and rmarkdown so students can render .qmd files.
  course_packages <- c(
    "tidyverse",  # readr, dplyr, tidyr, ggplot2, and friends
    {{PACKAGES}}  # one "pkg",  # short purpose comment  per line
    "knitr",      # needed to render Quarto and R Markdown documents
    "rmarkdown"   # needed to render Quarto and R Markdown documents
  )

  # ---- Helpers ----------------------------------------------------------------
  line <- function() cat(strrep("-", 70), "\n")
  say <- function(...) cat(..., "\n", sep = "")
  is_installed <- function(pkg) requireNamespace(pkg, quietly = TRUE)

  line()
  say("{{COURSE_CODE}} setup: installing the packages for this course")
  line()

  # ---- 1. Check R version -----------------------------------------------------
  say("\nStep 1 of 4: checking your version of R...")
  say("  You have ", R.version.string)
  if (getRversion() < min_r_version) {
    say("  WARNING: This course needs R ", min_r_version, " or newer.")
    say("  Please install the latest version from https://cran.r-project.org")
    say("  and then run this script again.")
    return(invisible(FALSE))
  }
  say("  OK")

  # Use a reliable CRAN mirror if one isn't already set
  repos <- getOption("repos")
  if (is.null(repos) || isTRUE(repos[["CRAN"]] == "@CRAN@")) {
    options(repos = c(CRAN = "https://cloud.r-project.org"))
  }

  # On Windows and macOS, prefer pre-built binary packages (much faster,
  # no compilers needed)
  if (.Platform$OS.type == "windows" || Sys.info()[["sysname"]] == "Darwin") {
    options(install.packages.check.source = "no",
            install.packages.compile.from.source = "never")
  }

  # ---- 2. Install missing packages -------------------------------------------
  say("\nStep 2 of 4: installing packages you don't have yet...")
  missing <- course_packages[!vapply(course_packages, is_installed, logical(1))]

  if (length(missing) == 0) {
    say("  You already have all ", length(course_packages), " packages. Nice!")
  } else {
    say("  Installing ", length(missing), " package(s): ", paste(missing, collapse = ", "))
    say("  This can take several minutes, especially for the tidyverse. Hang in there.\n")
    for (pkg in missing) {
      say("  -> ", pkg)
      tryCatch(
        install.packages(pkg, dependencies = TRUE, quiet = TRUE),
        error = function(e) say("     Problem installing ", pkg, ": ", conditionMessage(e))
      )
    }
  }

  # ---- 3. Check that everything loads ------------------------------------------
  say("\nStep 3 of 4: checking that each package loads...")
  status <- vapply(course_packages, function(pkg) {
    ok <- suppressWarnings(suppressMessages(
      requireNamespace(pkg, quietly = TRUE)
    ))
    say(sprintf("  %-10s %s", pkg, if (ok) "OK" else "NOT INSTALLED"))
    ok
  }, logical(1))

  # ---- 4. Check the course data ------------------------------------------------
  say("\nStep 4 of 4: checking that you can download the course data...")
  data_url <- "{{DATA_CHECK_URL}}"
  data_ok <- tryCatch({
    dat <- utils::read.csv(data_url)
    say("  Downloaded the course data (", nrow(dat), " rows). OK")
    TRUE
  }, error = function(e) {
    say("  Could not download the course data. Check your internet connection.")
    FALSE
  })

  # ---- Summary ------------------------------------------------------------------
  line()
  if (all(status) && data_ok) {
    say("All done! You're ready for {{COURSE_CODE}}.")
  } else {
    failed <- names(status)[!status]
    if (length(failed) > 0) {
      say("These packages did not install: ", paste(failed, collapse = ", "))
      say("Try running this script again. If it still fails, try installing one at")
      say("a time, for example: install.packages(\"", failed[1], "\")")
      say("and bring the error message to class or office hours.")
    }
    if (!data_ok) say("The data download failed; check your internet connection.")
  }
  line()

  invisible(all(status) && data_ok)
})
