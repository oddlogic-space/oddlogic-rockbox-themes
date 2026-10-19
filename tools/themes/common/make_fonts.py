#!/usr/bin/env python3
"""Build Rockbox .fnt bitmap fonts (1-bit) straight from Noto Sans/Serif CJK - no convbdf needed.
Covers Latin, kana, all JIS X 0208 kanji, fullwidth forms.  The rasteriser and writer live in rbfont.py.
Usage: make_fonts.py <font.ttc> <outdir> <name> [size ...]    (needs Pillow, numpy + fontTools)
Writes <outdir>/<size>-<name>.fnt for each size (default 28 32 40).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rbfont  # noqa: E402

SIZES = {28: 36, 32: 42, 40: 52}  # glyph pixel size -> line height (adds leading)

if __name__ == "__main__":
    src, out, name = sys.argv[1:4]
    want = [int(a) for a in sys.argv[4:]] or [28, 32, 40]
    os.makedirs(out, exist_ok=True)
    for size, height in SIZES.items():
        if size in want:
            rbfont.noto_font(src, os.path.join(out, f"{size}-{name}.fnt"), size, height)
