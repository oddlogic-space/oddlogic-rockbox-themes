"""Rockbox RB12 bitmap fonts, shared by every theme: character sets, rasterisers, writer and reader.

Rasterisers
  noto_font(...)      Noto at the target size, thresholded (Waveform Bot HUD, Teal Vocaldroid, In Love, Pretty Sad)
  noto_ss_font(...)   Noto at 4x, box-filtered down, then thresholded: cleaner strokes (Studio Console)
  pixel_font(...)     GNU Unifont at an integer scale with a one-pixel double strike (Studio Console)
  seg7_font(...)      DSEG7 Classic Bold digits (Studio Console)
"""
import math
import os
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont, TTCollection

NOTO_DIR = "/usr/share/fonts/opentype/noto"
UNIFONT_JP = "/usr/share/fonts/opentype/unifont/unifont_jp.otf"


# ---------------------------------------------------------------- character sets
def jis0208():
    """Every JIS X 0208 character: non-kanji rows, level 1 and level 2 kanji."""
    s = set()
    for hi in list(range(0x81, 0x85)) + list(range(0x88, 0xA0)) + list(range(0xE0, 0xEB)):
        for lo in range(0x40, 0xFD):
            if lo != 0x7F:
                try:
                    s.add(ord(bytes([hi, lo]).decode("shift_jis")))
                except UnicodeDecodeError:
                    pass
    return s


def jis_level1():
    """JIS X 0208 non-kanji rows plus level 1 kanji (enough for large display sizes)."""
    s = set()
    for hi in range(0x81, 0x99):
        for lo in range(0x40, 0xFD):
            if lo == 0x7F:
                continue
            v = (hi << 8) | lo
            if hi in (0x81, 0x82, 0x83, 0x84) or 0x889F <= v <= 0x9872:
                try:
                    s.add(ord(bytes([hi, lo]).decode("shift_jis")))
                except UnicodeDecodeError:
                    pass
    return s


# Hangul tone marks U+302E/F sit inside the CJK punctuation block but are never wanted
_NEVER = {0x302E, 0x302F}


def codes_text():
    """Latin-1 and Extended-A, punctuation, CJK symbols, full- and half-width forms, all of JIS X 0208."""
    c = (set(range(0x20, 0x7F)) | set(range(0xA0, 0x180)) | set(range(0x2010, 0x2030))
         | set(range(0x3000, 0x3040)) | set(range(0xFF01, 0xFF5F)) | set(range(0xFF61, 0xFFA0)) | jis0208())
    return c - _NEVER


def codes_wide():
    """codes_text() plus arrows and geometric shapes."""
    return codes_text() | set(range(0x2190, 0x2200)) | set(range(0x25A0, 0x2600))


def codes_large():
    """For big sizes: Latin-1, punctuation, CJK symbols, full-width forms, JIS level 1."""
    c = (set(range(0x20, 0x7F)) | set(range(0xA0, 0x100)) | set(range(0x2010, 0x2030))
         | set(range(0x3000, 0x3040)) | set(range(0xFF01, 0xFF5F)) | jis_level1())
    return c - _NEVER


# ---------------------------------------------------------------- writer / reader
def encode_glyph(rows, w, h):
    """Rockbox glyph layout: 8-row strips, one byte per column, least significant bit on top."""
    a = np.asarray(rows, dtype=np.uint8).reshape(h, w)
    nb = (h + 7) // 8
    pad = np.zeros((nb * 8, w), np.uint8)
    pad[:h] = a
    return (pad.reshape(nb, 8, w) << np.arange(8, dtype=np.uint8)[None, :, None]).sum(1).astype(np.uint8).tobytes()


def write_fnt(path, h, asc, maxw, first, default, glyphs, quiet=False):
    """glyphs: {codepoint: (width, rows)}. Code points without a glyph use `default`."""
    last = max(glyphs)
    size = last - first + 1
    blob = bytearray()
    off_of = {}
    for cp in sorted(glyphs):
        w, rows = glyphs[cp]
        off_of[cp] = len(blob)
        blob += encode_glyph(rows, w, h)
    nbits = len(blob)
    ow = 4 if nbits >= 0xFFDB else 2
    # the offset table must be aligned to its entry size, or Rockbox refuses the font and the whole skin falls back
    pad = (-nbits) % 4 if ow == 4 else nbits % 2
    offs, widths = [], []
    for cp in range(first, last + 1):
        k = cp if cp in glyphs else default
        offs.append(off_of[k])
        widths.append(glyphs[k][0])
    out = bytearray(b"RB12") + struct.pack("<HHHH", maxw, h, asc, 0)
    out += struct.pack("<IIIIII", first, default, size, nbits, size, size) + blob + b"\0" * pad
    out += struct.pack("<%d%s" % (size, "I" if ow == 4 else "H"), *offs)
    out += bytes(widths)
    with open(path, "wb") as f:
        f.write(out)
    if not quiet:
        print(os.path.basename(path), len(glyphs), "glyphs", os.path.getsize(path) // 1024, "KB")


class Fnt:
    """Read an RB12 font and draw text with it (for previews and mock-ups)."""

    def __init__(s, path):
        d = open(path, "rb").read()
        s.maxw, s.h, s.asc, _ = struct.unpack("<HHHH", d[4:12])
        s.fc, s.dc, s.size, nbits, noff, nwid = struct.unpack("<IIIIII", d[12:36])
        ow = 4 if nbits >= 0xFFDB else 2
        pad = (-nbits) % 4 if ow == 4 else nbits % 2
        o = 36
        s.bits = d[o:o + nbits]
        o += nbits + pad
        s.offs = list(struct.unpack("<%d%s" % (noff, "I" if ow == 4 else "H"), d[o:o + noff * ow]))
        o += noff * ow
        s.w = list(d[o:o + nwid])

    def width(s, t):
        return sum(s.w[ord(c) - s.fc] for c in t)

    def draw(s, im, x, y, t, col, align="l", box=None):
        if align != "l":
            tw = s.width(t)
            x = x + (box - tw) // 2 if align == "c" else x + box - tw
        px = im.load()
        for ch in t:
            i = ord(ch) - s.fc
            w = s.w[i]
            a = s.offs[i]
            for xx in range(w):
                for yy in range(s.h):
                    if (s.bits[a + (yy // 8) * w + xx] >> (yy % 8)) & 1:
                        X, Y = x + xx, y + yy
                        if 0 <= X < im.width and 0 <= Y < im.height:
                            px[X, Y] = col
            x += w


# ---------------------------------------------------------------- rasterisers
def noto_font(src, path, size, height, face=0, thresh=110, codes=None):
    """Noto (a .ttc) rendered at `size` and thresholded; height adds leading, ascent is centred in it."""
    cmap = TTCollection(src).fonts[face].getBestCmap()
    codes = sorted(c for c in (codes_text() if codes is None else codes) if c in cmap or c == 0x20)
    font = ImageFont.truetype(src, size, index=face)
    asc = round(size * 0.88) + (height - size) // 2
    m = 6
    glyphs = {}
    maxw = 1
    for c in codes:
        adv = min(255, max(1, round(font.getlength(chr(c)))))
        im = Image.new("L", (adv + 2 * m, height), 0)
        if c != 0x20:
            ImageDraw.Draw(im).text((m, asc), chr(c), font=font, fill=255, anchor="ls")
        px = im.crop((m, 0, m + adv, height)).load()
        glyphs[c] = (adv, [[1 if px[x, y] >= thresh else 0 for x in range(adv)] for y in range(height)])
        maxw = max(maxw, adv)
    write_fnt(path, height, asc, maxw, 0x20, 0x3F, glyphs, quiet=True)
    print(path, len(glyphs), "glyphs,", os.path.getsize(path) // 1024, "KB")


def noto_ss_font(path, size, weight="Bold", only=None, thr=118, ss=4):
    """Noto Sans CJK JP rendered at ss x, box-filtered down and thresholded: clean 1-bit strokes."""
    src = f"{NOTO_DIR}/NotoSansCJK-{weight}.ttc"
    f = ImageFont.truetype(src, size * ss, index=0)
    cm = TTFont(src, fontNumber=0).getBestCmap()
    h = math.ceil(size * 1.09)
    asc = round(size * 0.88)
    glyphs = {}
    maxw = 1
    for c in sorted(c for c in codes_wide() if c in _unifont_cmap()):
        if only is not None and c not in only:
            continue
        if c not in cm and c != 0x20:
            continue
        ch = chr(c)
        adv = max(2, int(round(f.getlength(ch) / ss)))
        if c == 0x20:
            glyphs[c] = (adv, np.zeros((h, adv), int))
            maxw = max(maxw, adv)
            continue
        w = adv + 4
        im = Image.new("L", (w * ss, h * ss), 0)
        ImageDraw.Draw(im).text((2 * ss, asc * ss), ch, font=f, fill=255, anchor="ls")
        a = (np.asarray(im.resize((w, h), Image.BOX)) > thr)[:, 2:2 + adv]
        if not a.any():
            glyphs[c] = (adv, np.zeros((h, adv), int))
            continue
        glyphs[c] = (adv, a.astype(int))
        maxw = max(maxw, adv)
    write_fnt(path, h, asc, maxw, 0x20, 0x3F, glyphs)


_ucmap = None


def _unifont_cmap():
    # the Studio Console code list was defined over what Unifont JP covers; keep that so output stays identical
    global _ucmap
    if _ucmap is None:
        _ucmap = TTFont(UNIFONT_JP).getBestCmap()
    return _ucmap


def pixel_font(path, sc, bold=True, only=None):
    """GNU Unifont JP scaled by `sc` with nearest-neighbour; bold = one-pixel double strike."""
    uni = ImageFont.truetype(UNIFONT_JP, 16)
    h = int(16 * sc)
    glyphs = {}
    maxw = 1
    codes = sorted(c for c in codes_wide() if c in _unifont_cmap())
    for c in (codes if only is None else [c for c in codes if c in only]):
        ch = chr(c)
        cw = int(uni.getlength(ch))
        g = Image.new("L", (max(cw, 1), 16), 0)
        ImageDraw.Draw(g).text((0, 0), ch, font=uni, fill=255)
        a = np.asarray(g) > 100
        if c == 0x20:
            cw = 8
        w = max(1, int(cw * sc))
        if c == 0x20:
            glyphs[c] = (w, np.zeros((h, w), int))
            maxw = max(maxw, w)
            continue
        b = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.NEAREST)) > 100
        if bold:
            b = b | np.pad(b[:, :-1], ((0, 0), (1, 0)))
        glyphs[c] = (w, b.astype(int))
        maxw = max(maxw, w)
    write_fnt(path, h, int(14 * sc), maxw, 0x20, 0x3F, glyphs)


def seg7_glyphs(size, dseg_dir, chars="0123456789:-/ "):
    f = ImageFont.truetype(f"{dseg_dir}/DSEG7-Classic/DSEG7Classic-Bold.ttf", size)
    # DSEG digits are ~1.07 x size tall: leave room above the baseline so the top row is never clipped
    h = size + 4
    asc = size + 2
    glyphs = {}
    m = 8
    for ch in chars:
        adv = int(round(f.getlength(ch))) + (10 if ch == " " else 0)
        if ch == " ":
            glyphs[32] = (adv, np.zeros((h, adv), int))
            continue
        im = Image.new("L", (adv + 2 * m, h), 0)
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        d.text((m, asc), ch, font=f, fill=255, anchor="ls")
        glyphs[ord(ch)] = (adv, (np.asarray(im.crop((m, 0, m + adv, h))) > 100).astype(int))
    if "1" in chars and "0" in chars:
        # the font's '1' renders two rows short at small sizes: rebuild it from the right-hand segments of '0'
        w0, a0 = glyphs[ord("0")]
        cols = np.nonzero(a0.any(0))[0]
        t = 2 if size < 18 else 3
        a1 = np.zeros_like(a0)
        a1[:, cols.max() - t + 1:cols.max() + 1] = a0[:, cols.max() - t + 1:cols.max() + 1]
        glyphs[ord("1")] = (w0, a1)
    return h, asc, glyphs


def seg7_font(path, size, dseg_dir):
    h, asc, g = seg7_glyphs(size, dseg_dir)
    write_fnt(path, h, asc, max(w for w, _ in g.values()), 0x20, 0x20, g)
