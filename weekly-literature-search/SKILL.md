---
name: weekly-literature-search
description: Weekly literature digest for demography & epidemiology.
version: 0.1.0
author: Corey Sparks (corey.sparks.utsa@gmail.com), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, literature-search, cron, email]
    related_skills: [arxiv, grounded-citations]
---

# Weekly Literature Search Skill

## Overview

Recurring weekly digest of the past seven calendar days of academic literature on three topics: spatial demography, Bayesian spatial epidemiology, and Bayesian demography. The user's cron job runs this search, verifies citations, and emails a formatted digest to **corey.sparks.utsa@gmail.com**.

Delivery is set explicitly on the cron job as `email:corey.sparks.utsa@gmail.com` — do NOT change it to the generic `"email"` shorthand, which routes to the gateway's connected IMAP account (coreysparksphd@gmail.com), not the user's preferred inbox.

## When to Use

- The user asks for yesterday's weekly literature search or says the weekly cron ran.
- Running, verifying, or refreshing a Weekly Literature Search cron job (schedule 0 7 * * 1).
- Delivering a literature-search digest as an email.

## Prerequisites

- Email platform enabled with EMAIL_HOME_ADDRESS set (email gateway). Covered by the email delivery setup.
- Source endpoints reachable (PubMed E-utilities, Crossref, arXiv) - no API keys required.

## How to Run

Run the sources in order with terminal (use only curl, grep, python3 -c, jq):

1. PubMed ESearch (no key) - fetch abstracts (EFetch) for the top IDs.
2. Crossref (no key) - bibliographic query + from-pub-date,until-pub-date.
3. arXiv API, sort by submittedDate descending.
4. Verify each DOI (https://doi.org/<doi> -> 200/301/302).
5. Dedupe against the prior run's continuity context.
6. Send the report to **corey.sparks.utsa@gmail.com** via the email gateway. The cron job `deliver` field must be `email:corey.sparks.utsa@gmail.com` (explicit), not `"email"` (routes to gateway account instead).

## Procedure

1. Pick the window. Coverage = [run date - 7, run date].
2. Run the sources (see references/literature-search-recipes.md for exact curl jobs).
   - PubMed ESearch (no key): bibliographic term + pub_date:[start TO end], then Efetch abstracts.
   - Crossref (no key): query.bibliographic + filter=from-pub-date,until-pub-date.
   - arXiv API: sort by submittedDate descending.
3. Verify citations. Resolve every DOI via https://doi.org/{doi}; confirm HTTP 200, 301, or 302. Do not report a paper whose DOI does not resolve.
4. Dedupe. Drop any paper already reported in a previous run (use continuity context).
5. Assemble the report for the remaining papers.
6. Deliver by email to corey.sparks.utsa@gmail.com via the email gateway.

## Output template

For each paper, report: Title; Authors; Publication; Publication date; DOI/URL; Research question (1-2 sentences from the abstract); Data used; Statistical/Bayesian methods; Main findings; Why useful. Cap at 10 papers. End with a **Top 3 papers to read.** section.

## Output format

The report must be produced in clean Markdown. Before delivering:
1. Save the report as `C:/Users/corey/litsearch/weekly_digest_YYYY-MM-DD.md` (substitute run date).
2. Create `C:/Users/corey/litsearch/` if it does not exist.
3. Use the same Markdown content as the email body.

File naming: `weekly_digest_2026-11-03.md` (ISO date of run day).

## Pitfalls

- **`deliver: "email"` routes to the gateway's connected IMAP account, not the user's inbox.** Always set the cron job deliver field to `email:corey.sparks.utsa@gmail.com` explicitly. To diagnose a misdirected send, run `hermes logs gateway | grep -i "Sent reply to"` — the log line shows the actual recipient.
- PubMed pub_date range filters are sometimes not honored by this endpoint (return 0 for range queries). If a range query returns 0, fetch abstracts by rank and read dates from each abstract; state the coverage window explicitly in the output.
- Crossref to-pub-date filter is invalid; use from-pub-date,until-pub-date.
- A cron run blocked by a configuration preflight (or a blocked command) produces no output - execute the search once directly and deliver, then fix the preflight.
- Bare Windows paths mangle under MSYS/bash (double backslashes). When sending a file (--file), pass a path relative to the hermes-home directory.

## Verification

- Every reported paper has a DOI that resolves (200/301/302).
- No paper overlaps the prior run's continuity context.
- The email tool returns success (sent) and the digest arrives at the configured address.

See references/literature-search-recipes.md for the canonical source queries.
