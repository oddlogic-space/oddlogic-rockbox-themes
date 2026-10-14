#!/bin/bash
# usage: run-scenario.sh <scenario.txt> <output prefix>
# Runs the simulator headless, executes the scenario, and writes <prefix>_1.png, <prefix>_2.png ... (480x800) for every 'key f5'.
set -e; WORK="${WORK:-$HOME/rockbox-sim}"; BLD="$WORK/bld"; cd "$BLD"; rm -f simdisk/dump*.bmp
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy RB_SIMCMD="$(realpath "$1")" timeout 180 ./rockboxui > run.log 2>&1 || true
python3 - "$2" <<'P'
import sys, glob
from PIL import Image
fs = sorted(glob.glob("simdisk/dump*.bmp"))
for i, f in enumerate(fs, 1): Image.open(f).convert("RGB").save(f"{sys.argv[1]}_{i}.png")
print("screenshots:", len(fs))
P
