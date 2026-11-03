---
name: manuscript-tracker
description: Track manuscript submissions, reviews, and deadlines.
version: 0.1.0
author: Corey Sparks (coreysparks), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [manuscripts, publishing, academia, deadlines, writing]
    related_skills: []
---

# Manuscript Tracker Skill

Tracks the status of academic manuscripts across the submission lifecycle: in-prep, submitted, under review, revision requested, accepted, rejected, and published. Stores records in a local JSON file and surfaces deadlines, overdue revisions, and status summaries on request.

Does NOT send emails or auto-submit — it is a local record and reporting tool.

## When to Use

- Logging a new submission or status change
- Checking which manuscripts have upcoming or overdue revision deadlines
- Getting a summary of all active manuscripts
- Recording a desk rejection, acceptance, or publication

Don't use for: grant tracking (different lifecycle), co-author task assignment.

## Prerequisites

- Python 3 (stdlib only — `json`, `datetime`, `pathlib`)
- Data file: `C:/Users/corey/manuscripts/tracker.json` (created on first add)

## Data File Location

`C:/Users/corey/manuscripts/tracker.json`

Create the directory if absent:
```
terminal(command="mkdir -p C:/Users/corey/manuscripts")
```

## Record Schema

```json
{
  "id": "short-slug",
  "title": "Full manuscript title",
  "authors": ["Sparks", "Bitew"],
  "journal": "Demographic Research",
  "status": "under_review",
  "submitted_date": "2026-10-01",
  "decision_date": null,
  "revision_due": null,
  "notes": "R&R expected by Dec 2026"
}
```

**Valid statuses:** `in_prep`, `submitted`, `under_review`, `revision_requested`, `revision_submitted`, `accepted`, `rejected`, `published`

## Procedure

### Add or update a manuscript
1. `read_file` the tracker JSON (or start with `[]` if new).
2. Find existing record by `id` or append a new one.
3. Set fields; write back with `write_file`.

### List all manuscripts
1. `read_file` the tracker JSON.
2. Print a summary table: id, title (truncated), journal, status, days since submission, revision due.

### Check deadlines
1. `read_file` the tracker JSON.
2. For each record with `revision_due` set, compute days until due; flag overdue (< 0) and urgent (< 14 days).
3. Report in order of urgency.

### Mark a decision
1. `read_file` the tracker JSON.
2. Update `status`, set `decision_date` to today, set `revision_due` if R&R.
3. `write_file` back.

## Quick Reference — Python snippets

```python
import json, pathlib
from datetime import date, datetime

TRACKER = pathlib.Path("C:/Users/corey/manuscripts/tracker.json")
manuscripts = json.loads(TRACKER.read_text()) if TRACKER.exists() else []

# Summary
for m in manuscripts:
    sub = m.get('submitted_date', '—')
    rev = m.get('revision_due')
    due_str = ''
    if rev:
        days = (date.fromisoformat(rev) - date.today()).days
        due_str = f'  rev due in {days}d'
    print(f"{m['id']:20} {m['status']:20} {m['journal']:30}{due_str}")

# Add / update
def upsert(manuscripts, record):
    for i, m in enumerate(manuscripts):
        if m['id'] == record['id']:
            manuscripts[i] = record
            return manuscripts
    manuscripts.append(record)
    return manuscripts

manuscripts = upsert(manuscripts, {
    "id": "ethiopia-stunting-2026",
    "title": "Bayesian spatial analysis of child stunting in Ethiopia",
    "authors": ["Sparks", "Bitew"],
    "journal": "BMC Public Health",
    "status": "under_review",
    "submitted_date": str(date.today()),
    "decision_date": None,
    "revision_due": None,
    "notes": ""
})
TRACKER.write_text(json.dumps(manuscripts, indent=2))
```

## Pitfalls

- Always `read_file` before `write_file` — never overwrite without reading current state first.
- `revision_due` should be set when status changes to `revision_requested`; journals typically allow 30–90 days.
- Use ISO date strings (`YYYY-MM-DD`) for all date fields — no other formats.
- If multiple co-authors update the file from different machines, merge conflicts can silently drop records; keep one canonical copy.

## Verification

- After every write, `read_file` and confirm record count is correct and the updated record reflects changes.
- Deadline report lists every record with a non-null `revision_due` and correctly computes days remaining.
