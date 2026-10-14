#!/bin/bash
# usage: test-theme.sh <theme.zip> <theme id> <list|tile> [row1_y row2_y] [outdir]
# One-shot regression test: unzips the theme, installs it, plays the Latin track then the Japanese (CJK) track,
# presses PLAY (pause) and NEXT, and writes a contact sheet <outdir>/<id>_sheet.png plus the individual shots.
# Shots in order: 1 main menu, 2 after opening Files > Music, 3 Latin track playing, 4 paused, 5 CJK track (next).
# list = list-style main menu (rows at row1_y/row2_y, defaults 176/248); tile = tile menu (Files tile 127,135, list rows 110/186).
set -e; H="$(cd "$(dirname "$0")" && pwd)"; ZIP="$(realpath "$1")"; ID="$2"; STYLE="${3:-list}"; Y1="${4:-176}"; Y2="${5:-248}"; OUT="$(realpath -m "${6:-./sim-out}")"
mkdir -p "$OUT"; T="$(mktemp -d)"; unzip -q "$ZIP" -d "$T"
tap(){ printf 'down %s %s\nsleep 200\nup %s %s\nsleep 1500\n' "$1" "$2" "$1" "$2"; }
{ echo sleep 2500; echo key tab; echo sleep 500; echo key f5; echo sleep 1300
  if [ "$STYLE" = tile ]; then tap 127 135; tap 240 110; else tap 240 "$Y1"; tap 240 "$Y1"; fi
  echo key f5; echo sleep 1300; tap 240 $([ "$STYLE" = tile ] && echo 110 || echo "$Y1"); echo sleep 4000; echo key f5; echo sleep 1300
  echo key enter; echo sleep 1500; echo key f5; echo sleep 1300; echo key enter; echo sleep 1000; echo key right; echo sleep 3000; echo key f5; echo sleep 1300; echo quit
} > "$T/s.txt"
bash "$H/install-theme.sh" "$T" "$ID"; bash "$H/run-scenario.sh" "$T/s.txt" "$OUT/$ID"
python3 - "$OUT" "$ID" <<'P'
import sys, glob
from PIL import Image
out, i = sys.argv[1:3]; fs = sorted(glob.glob(f"{out}/{i}_?.png"))
W = Image.new("RGB", (240*len(fs), 400))
for k, f in enumerate(fs): W.paste(Image.open(f).resize((240, 400)), (k*240, 0))
W.save(f"{out}/{i}_sheet.png"); print("sheet:", f"{out}/{i}_sheet.png")
P
