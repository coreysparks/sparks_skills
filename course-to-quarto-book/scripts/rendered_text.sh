#!/usr/bin/env bash
# Convert every rendered HTML page of a Quarto book to plain text, so the
# prose and the printed output can be read side by side when checking that
# each interpretive claim matches the results.
#
# Usage: rendered_text.sh <book_output_dir> <text_out_dir>
#   e.g. rendered_text.sh docs /tmp/book-text
#
# Then, for example:
#   grep -n "p-value\|significant\|larger\|smaller\|wider" /tmp/book-text/*.txt
#   grep -n '\^{-' /tmp/book-text/*.txt      # badly formatted inline numbers
set -euo pipefail
src="${1:?book output dir, e.g. docs}"
out="${2:?output dir for text files}"
mkdir -p "$out"
find "$src" -name '*.html' -not -path '*/site_libs/*' | while read -r f; do
  name="$(basename "${f%.html}")"
  quarto pandoc "$f" -t plain --wrap=none -o "$out/$name.txt"
done
ls "$out"
