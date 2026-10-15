#!/usr/bin/env python3
"""Rebuild the shipped Teal Vocaldroid tree.   usage: package.py <outdir>   (writes <outdir>/.rockbox)
Images and fonts are generated; the skin files (.wps .sbs), the cfg and the licence are authored text kept in static/.
Needs Pillow, numpy, fontTools and Noto Sans CJK Medium."""
import os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); COMMON = os.path.join(HERE, "..", "common")
OUT = os.path.abspath(sys.argv[1]); ID = "tealvocaldroid"
NOTO = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
IM = f"{OUT}/.rockbox/wps/{ID}"
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(IM); os.makedirs(f"{OUT}/.rockbox/fonts")
subprocess.check_call([sys.executable, f"{COMMON}/make_fonts.py", NOTO, f"{OUT}/.rockbox/fonts", ID, "28", "32", "40"])
subprocess.check_call([sys.executable, f"{HERE}/make_backdrops.py", IM])      # backdrops first: the meter images are cut from them
subprocess.check_call([sys.executable, f"{HERE}/make_icons.py", IM])
shutil.copytree(f"{HERE}/static/.rockbox", f"{OUT}/.rockbox", dirs_exist_ok=True)
print("built", OUT)
