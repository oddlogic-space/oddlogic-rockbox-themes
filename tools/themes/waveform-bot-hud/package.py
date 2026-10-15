#!/usr/bin/env python3
"""Rebuild the shipped Waveform Bot HUD tree.   usage: package.py <outdir>   (writes <outdir>/.rockbox)
Needs Pillow, numpy, fontTools and Noto Sans CJK Medium (/usr/share/fonts/opentype/noto/)."""
import os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); COMMON = os.path.join(HERE, "..", "common")
OUT = os.path.abspath(sys.argv[1]); ID = "waveformbot"
NOTO = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(f"{OUT}/.rockbox/fonts")
subprocess.check_call([sys.executable, f"{COMMON}/make_fonts.py", NOTO, f"{OUT}/.rockbox/fonts", ID, "28", "32", "40"])
subprocess.check_call([sys.executable, f"{HERE}/build.py", OUT])
shutil.copy(f"{HERE}/licence/COPYING-{ID}.txt", f"{OUT}/.rockbox/fonts/")
print("built", OUT)
