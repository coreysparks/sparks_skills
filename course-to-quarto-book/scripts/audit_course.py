#!/usr/bin/env python3
"""Audit an old course repository of R Markdown files before converting it to
a Quarto book.

Usage:
    python3 -I audit_course.py <repo_dir> [--no-network] [--out report.md]

Stdlib only. Scans .Rmd/.rmd/.qmd/.R files (skipping .git, docs, _freeze,
renv, packrat) and reports, per file:

  * title / date from the YAML header, chunk count, word count
  * markdown headers with no space after the #'s (pandoc won't render them)
  * old-style inline chunk options ({r, echo=FALSE}) to convert to #| style
  * packages loaded (library/require/pkg::) -> feeds install_packages.R
  * deprecated or broken R idioms (see DEPRECATED below)
  * hard-coded local paths, setwd(), View(), install.packages(), file devices
  * remote URLs used in code, with their HTTP status and whether the file is
    actually a Git LFS pointer (a common silent failure for data on GitHub)
  * prose lines that contain numbers that look like model output, which are
    candidates for inline `r ` code

The report is Markdown, written to stdout or --out.
"""

import argparse
import os
import re
import sys
import urllib.request
import urllib.error

SKIP_DIRS = {".git", "docs", "_freeze", "_book", "renv", "packrat", ".quarto",
             "node_modules", ".Rproj.user"}
EXTS = (".rmd", ".qmd", ".r")

# (regex, message). Patterns are matched against code lines only.
DEPRECATED = [
    (r"\bqplot\(", "qplot() is deprecated in ggplot2 >= 3.4; use ggplot()"),
    (r"\.\.(density|count|prop|scaled)\.\.", "..stat.. notation is deprecated; use after_stat(stat)"),
    (r"\baes_string\(", "aes_string() is deprecated; use aes() with .data[[var]]"),
    (r"geom_(line|path|freqpoly|smooth|segment|abline|hline|vline)\([^)]*\b(size|lwd)\s*=",
     "size/lwd for lines is deprecated in ggplot2 >= 3.4; use linewidth"),
    (r"\.\$\w+", "`.$var` inside dplyr verbs (e.g. case_when) is unnecessary and fragile; use the bare column name"),
    (r"\b(spread|gather)\(", "spread()/gather() are superseded; use pivot_wider()/pivot_longer()"),
    (r"\bfuns\(", "funs() is defunct in dplyr; use a lambda or list of functions"),
    (r"\b(mutate|summarise|summarize|select|filter)_(each|all|at|if)\(", "scoped dplyr verbs are superseded; use across()"),
    (r"\bsjp\.\w+\(", "sjPlot sjp.* functions are defunct; use plot_model()"),
    (r"\bsjt\.\w+\(", "sjPlot sjt.* functions are defunct; use tab_model()"),
    (r"NetworkChange::multiplot|\bmultiplot\(", "multiplot() came from an unrelated package; use patchwork"),
    (r"\bas_data_frame\(", "as_data_frame() is deprecated; use as_tibble()"),
    (r"\bdata_frame\(", "data_frame() is deprecated; use tibble()"),
    (r"\bread_rds\(url\(", "reading an .rds over url(): check the URL still exists"),
    (r"\bnewdat\s*=", "partial argument match newdat= ; use newdata="),
    (r"lm\([^)]*scale\(|glm\([^)]*scale\(", "scale() inside a model formula gives wrong answers from predict() on new data; standardize in the data if the chapter predicts"),
    (r"\bxtabs\([^)]*\)\s*%>%|%>%\s*xtabs\(~", "check xtabs() piping (data = . placement)"),
    (r"\bsource\(\s*['\"]https?://", "source() of a remote script: inline it or vendor it so the book doesn't depend on it"),
]

RISKY = [
    (r"['\"]([A-Za-z]:[/\\]|/Users/|/home/|~/)[^'\"]*['\"]", "hard-coded local path"),
    (r"\bsetwd\(", "setwd() breaks project-relative paths"),
    (r"\bView\(", "View() fails or does nothing when rendering; use eval: false or print()"),
    (r"\binstall\.packages\(", "install.packages() in a chunk; set eval: false"),
    (r"\b(png|pdf|jpeg|tiff|svg)\(\s*(filename\s*=\s*)?['\"]", "graphics device writing to a file; remove or use ggsave() with eval: false"),
    (r"\bdev\.off\(", "dev.off(): paired with a file device above"),
    (r"\bset\.seed\(", None),  # tracked separately
]

URL_RE = re.compile(r"https?://[^\s'\")]+")
LIB_RE = re.compile(r"\b(?:library|require|requireNamespace)\(\s*['\"]?([A-Za-z][A-Za-z0-9.]*)")
NS_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9.]*)::")
BAD_HEADER_RE = re.compile(r"^(#{1,6})([^#\s].*)$")
INLINE_OPTS_RE = re.compile(r"^```\{r[ ,]+[^}]*=")
CHUNK_START_RE = re.compile(r"^\s*```+\s*\{")
CHUNK_END_RE = re.compile(r"^\s*```+\s*$")
NUM_IN_PROSE_RE = re.compile(r"(?<![\w$`.])-?\d+\.\d{2,}(?![\w.])|\b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?%")
BASE_PKGS = {"base", "stats", "utils", "graphics", "grDevices", "methods", "datasets", "tools", "grid", "parallel", "splines", "stats4", "tcltk", "compiler"}


def find_files(root):
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.endswith("_files")]
        for f in files:
            if f.lower().endswith(EXTS):
                out.append(os.path.join(d, f))
    return sorted(out)


def split_lines(path):
    """Yield (lineno, text, kind) with kind in {'yaml','code','prose'}."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    is_r_script = path.lower().endswith(".r")
    in_yaml = False
    in_code = is_r_script
    for i, line in enumerate(lines, 1):
        if is_r_script:
            yield i, line, "code"
            continue
        if i == 1 and line.strip() == "---":
            in_yaml = True
            yield i, line, "yaml"
            continue
        if in_yaml:
            yield i, line, "yaml"
            if line.strip() in ("---", "..."):
                in_yaml = False
            continue
        if not in_code and CHUNK_START_RE.match(line):
            in_code = True
            yield i, line, "chunk-header"
            continue
        if in_code and CHUNK_END_RE.match(line):
            in_code = False
            yield i, line, "chunk-end"
            continue
        yield i, line, "code" if in_code else "prose"


def check_url(url, timeout=20):
    """Return (status, note). Detects Git LFS pointer files."""
    req = urllib.request.Request(url, headers={"User-Agent": "course-audit/1.0", "Range": "bytes=0-299"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            head = r.read(300)
            status = r.status
    except urllib.error.HTTPError as e:
        return e.code, "HTTP error"
    except Exception as e:  # noqa: BLE001
        return None, f"failed: {type(e).__name__}"
    text = head.decode("utf-8", errors="replace")
    if text.startswith("version https://git-lfs.github.com/spec"):
        return status, "GIT LFS POINTER, not the data (try media.githubusercontent.com or move the file into the repo)"
    if "<html" in text.lower()[:300] and not url.endswith((".html", ".htm", "/")):
        return status, "returned an HTML page, not a data file (check ?raw=true / raw.githubusercontent.com)"
    return status, "ok"


def audit_file(path, root):
    rel = os.path.relpath(path, root)
    info = {"file": rel, "title": "", "date": "", "chunks": 0, "words": 0,
            "bad_headers": [], "inline_opts": 0, "packages": set(), "issues": [],
            "urls": [], "numbers": [], "seed": False}
    for n, line, kind in split_lines(path):
        if kind == "yaml":
            m = re.match(r"\s*(title|date):\s*(.*)", line)
            if m:
                info[m.group(1)] = m.group(2).strip().strip('"')
            continue
        if kind == "chunk-header":
            info["chunks"] += 1
            if INLINE_OPTS_RE.match(line.strip()):
                info["inline_opts"] += 1
            continue
        if kind == "chunk-end":
            continue
        if kind == "prose":
            info["words"] += len(line.split())
            if BAD_HEADER_RE.match(line):
                info["bad_headers"].append((n, line.strip()[:70]))
            stripped = re.sub(r"`r [^`]*`", "", line)  # ignore existing inline code
            stripped = re.sub(r"\$[^$]*\$", "", stripped)  # ignore math
            if NUM_IN_PROSE_RE.search(stripped):
                info["numbers"].append((n, line.strip()[:110]))
            for u in URL_RE.findall(line):
                pass  # prose links are checked only if --check-prose-links
            continue
        # code
        code = line.split("#", 1)[0] if not line.lstrip().startswith("#|") else ""
        for pkg in LIB_RE.findall(code) + NS_RE.findall(code):
            if pkg not in BASE_PKGS:
                info["packages"].add(pkg)
        for pat, msg in DEPRECATED:
            if re.search(pat, code):
                info["issues"].append((n, msg, line.strip()[:90]))
        for pat, msg in RISKY:
            if re.search(pat, line):  # include commented-out paths too
                if msg is None:
                    info["seed"] = True
                else:
                    info["issues"].append((n, msg, line.strip()[:90]))
        for u in URL_RE.findall(code):
            info["urls"].append((n, u.rstrip(",;")))
        if re.search(r"\b(rnorm|runif|rpois|rbinom|sample|slice_sample|sample_n)\(", code):
            info.setdefault("random", True)
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--no-network", action="store_true", help="skip URL checks")
    ap.add_argument("--out", help="write the report to this file")
    args = ap.parse_args()

    root = os.path.abspath(args.repo)
    files = find_files(root)
    if not files:
        sys.exit(f"No .Rmd/.qmd/.R files found under {root}")
    audits = [audit_file(f, root) for f in files]

    url_status = {}
    if not args.no_network:
        for u in sorted({u for a in audits for _, u in a["urls"]}):
            url_status[u] = check_url(u)

    out = []
    w = out.append
    w(f"# Course audit: `{os.path.basename(root)}`\n")
    w(f"{len(files)} source files scanned.\n")

    w("## Files\n")
    w("| File | Title | Date | Chunks | Words | Old chunk opts | Bad headers | Issues |")
    w("|---|---|---|---|---|---|---|---|")
    for a in audits:
        w(f"| `{a['file']}` | {a['title'][:50]} | {a['date']} | {a['chunks']} | {a['words']} | "
          f"{a['inline_opts']} | {len(a['bad_headers'])} | {len(a['issues'])} |")
    w("")

    pkgs = sorted(set().union(*(a["packages"] for a in audits)), key=str.lower)
    w("## Packages used\n")
    w(", ".join(f"`{p}`" for p in pkgs) if pkgs else "(none found)")
    w("\nUse this list for `install_packages.R`, the GitHub Actions workflow, and the setup page. "
      "Check each one still installs from CRAN; replace any that don't.\n")

    if url_status:
        w("## Remote URLs used in code\n")
        w("| Status | Note | URL | Used in |")
        w("|---|---|---|---|")
        for u, (st, note) in url_status.items():
            where = ", ".join(sorted({a["file"] for a in audits for _, x in a["urls"] if x == u}))
            flag = "" if (st and st < 400 and note == "ok") else "**"
            w(f"| {flag}{st}{flag} | {flag}{note}{flag} | {u} | {where} |")
        w("")

    w("## Per-file findings\n")
    for a in audits:
        if not (a["bad_headers"] or a["issues"] or a["numbers"] or (a.get("random") and not a["seed"])):
            continue
        w(f"### `{a['file']}`\n")
        if a.get("random") and not a["seed"]:
            w("- Uses random number generation with no `set.seed()`: output changes every render.")
        for n, h in a["bad_headers"]:
            w(f"- L{n}: header missing a space after `#`: `{h}`")
        grouped = {}
        for n, msg, src in a["issues"]:
            grouped.setdefault(msg, []).append((n, src))
        for msg, hits in grouped.items():
            lines = ", ".join(f"L{n}" for n, _ in hits[:12]) + (" ..." if len(hits) > 12 else "")
            w(f"- {msg} ({lines}), e.g. `{hits[0][1]}`")
        if a["numbers"]:
            w(f"- {len(a['numbers'])} prose line(s) with numbers that may be hard-coded results "
              "(replace with inline `r ` code if they come from output):")
            for n, line in a["numbers"][:15]:
                w(f"  - L{n}: {line}")
        w("")

    report = "\n".join(out) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"Wrote {args.out}")
    else:
        sys.stdout.write(report)


if __name__ == "__main__":
    main()
