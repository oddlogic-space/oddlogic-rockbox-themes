#!/usr/bin/env bash
# Runs check_theme.py on every shipped zip in themes/*/download/.
# usage: tools/kit/check-all.sh      (builds checkwps on first use; set CHECKWPS to use an existing binary)
set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
CHECKWPS="${CHECKWPS:-$("$REPO/tools/kit/build-checkwps.sh")}" || exit 1
fail=0
for z in "$REPO"/themes/*/download/*.zip; do
  out=$(python3 "$REPO/tools/kit/check_theme.py" "$z" --checkwps "$CHECKWPS")
  echo "$out" | grep -E '^(PROBLEM|zip:)' | sed 's/^/  /'
  echo "$out" | tail -1
  echo "$out" | tail -1 | grep -q '^0 problem' || fail=1
done
exit $fail
