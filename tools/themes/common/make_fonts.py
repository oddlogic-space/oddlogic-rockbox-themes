#!/usr/bin/env python3
"""Build Rockbox .fnt bitmap fonts (1-bit) straight from Noto Sans CJK - no convbdf needed.
Covers Latin, kana, all JIS X 0208 kanji, fullwidth forms.  The .fnt writer was verified by
round-tripping two real Rockbox fonts byte-for-byte.
Usage: make_fonts.py <font.ttc> <outdir> <name> [size ...]    (needs Pillow + fontTools)
Writes <outdir>/<size>-<name>.fnt for each size (default 28 32 40).
"""
import struct, sys, os
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTCollection

SRC, OUT, NAME = sys.argv[1:4]
WANT = [int(a) for a in sys.argv[4:]] or [28, 32, 40]
FACE = 0                          # 0 = Noto Sans CJK JP (JP glyph forms)
SIZES = {28: 36, 32: 42, 40: 52}  # glyph pixel size -> line height (adds leading)
THRESH = 110                      # lower = bolder
DEFAULT_CH = 0x3F                 # '?' shown for missing glyphs

cmap = TTCollection(SRC).fonts[FACE].getBestCmap()

def jis0208():
    s = set()
    for hi in list(range(0x81, 0x85)) + list(range(0x88, 0xA0)) + list(range(0xE0, 0xEB)):
        for lo in range(0x40, 0xFD):
            if lo != 0x7F:
                try: s.add(ord(bytes([hi, lo]).decode("shift_jis")))
                except Exception: pass
    return s

codes = set(range(0x20, 0x7F)) | set(range(0xA0, 0x180)) | set(range(0x2010, 0x2030)) \
      | set(range(0x3000, 0x3040)) | set(range(0xFF01, 0xFF5F)) | set(range(0xFF61, 0xFFA0)) | jis0208()
codes = sorted(c for c in codes if (c in cmap or c == 0x20) and c not in (0x302E, 0x302F))

def encode_glyph(rows, w, H):
    nb = (H + 7) // 8; out = bytearray(w * nb)
    for y in range(H):
        for x in range(w):
            if rows[y][x]: out[(y // 8) * w + x] |= 1 << (y % 8)
    return bytes(out)

def write_fnt(path, H, asc, maxw, fc, dc, glyphs):
    last = max(glyphs); size = last - fc + 1
    blob = bytearray(); off_of = {}
    for cp in sorted(glyphs):
        w, rows = glyphs[cp]; off_of[cp] = len(blob); blob += encode_glyph(rows, w, H)
    nbits = len(blob); ow = 4 if nbits >= 0xFFDB else 2
    pad = (-nbits) % 4 if ow == 4 else 0
    offs, widths = [], []
    for cp in range(fc, last + 1):
        k = cp if cp in glyphs else dc
        offs.append(off_of[k]); widths.append(glyphs[k][0])
    out = bytearray(b"RB12") + struct.pack("<HHHH", maxw, H, asc, 0)
    out += struct.pack("<IIIIII", fc, dc, size, nbits, size, size) + blob + b"\0" * pad
    for o in offs: out += struct.pack("<I" if ow == 4 else "<H", o)
    out += bytes(widths)
    open(path, "wb").write(out)

def build(size, H):
    font = ImageFont.truetype(SRC, size, index=FACE)
    asc = round(size * 0.88) + (H - size) // 2
    M = 6; glyphs = {}; maxw = 1
    for c in codes:
        adv = min(255, max(1, round(font.getlength(chr(c)))))
        im = Image.new("L", (adv + 2 * M, H), 0)
        if c != 0x20:
            ImageDraw.Draw(im).text((M, asc), chr(c), font=font, fill=255, anchor="ls")
        im = im.crop((M, 0, M + adv, H)); px = im.load()
        glyphs[c] = (adv, [[1 if px[x, y] >= THRESH else 0 for x in range(adv)] for y in range(H)])
        maxw = max(maxw, adv)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{size}-{NAME}.fnt")
    write_fnt(path, H, asc, maxw, 0x20, DEFAULT_CH, glyphs)
    print(path, len(glyphs), "glyphs,", os.path.getsize(path) // 1024, "KB")

for s, h in SIZES.items():
    if s in WANT: build(s, h)
