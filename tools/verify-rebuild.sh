#!/usr/bin/env bash
# Rebuild every theme from the scripts in tools/themes/ and compare, file by file, with the zip in themes/<slug>/download/.
# usage: tools/verify-rebuild.sh [slug ...]      (default: all)    env: DSEG_DIR (needed for studio-console), WORK (scratch dir)
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"; T="$REPO/tools/themes"; WORK="${WORK:-$(mktemp -d)}"; fail=0
want() { [ $# -eq 0 ] && return 0; for s in "${ARGS[@]}"; do [ "$s" = "$1" ] && return 0; done; [ ${#ARGS[@]} -eq 0 ]; }
ARGS=("$@")
check() {  # slug builtdir
  local slug="$1" built="$2" zip ship="$WORK/ship/$1"
  zip=$(ls "$REPO"/themes/$slug/download/*.zip | head -1); rm -rf "$ship"; mkdir -p "$ship"; unzip -q "$zip" -d "$ship"
  if diff -rq "$built/.rockbox" "$ship/.rockbox" >"$WORK/$slug.diff" 2>&1; then echo "PASS  $slug  (identical to $(basename "$zip"))"
  else echo "FAIL  $slug"; sed 's/^/        /' "$WORK/$slug.diff"; fail=1; fi
}
run() { local slug="$1"; shift; want "$slug" || return 0; echo "... building $slug"; "$@" >"$WORK/$slug.log" 2>&1 || { echo "FAIL  $slug (build error, see $WORK/$slug.log)"; fail=1; return 1; }; }
run waveform-bot-hud python3 "$T/waveform-bot-hud/package.py" "$WORK/out/waveform-bot-hud" && want waveform-bot-hud && check waveform-bot-hud "$WORK/out/waveform-bot-hud"
run teal-vocaldroid python3 "$T/teal-vocaldroid/package.py" "$WORK/out/teal-vocaldroid" && want teal-vocaldroid && check teal-vocaldroid "$WORK/out/teal-vocaldroid"
if want in-love || want pretty-sad; then
  run in-love python3 "$T/in-love-pretty-sad/package.py" "$WORK/out" && { want in-love && check in-love "$WORK/out/inlove"; want pretty-sad && check pretty-sad "$WORK/out/prettysad"; }
fi
if want studio-console; then
  run studio-console python3 "$T/studio-console/build.py" "$WORK/out/studio-console" studioconsole "Studio Console" && check studio-console "$WORK/out/studio-console"
fi
want drift-mountain && echo "SKIP  drift-mountain (build scripts not in the repo yet; see tools/themes/README.md)"
echo "work dir: $WORK"; exit $fail
