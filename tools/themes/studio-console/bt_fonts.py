"""Studio fonts -> Rockbox RB12 bitmap fonts: GNU Unifont (Latin, kana, JIS kanji) at 1x / 1.5x / 2x, DSEG7 digits."""
import struct, os, math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from fontTools.ttLib import TTFont
UNI = "/usr/share/fonts/opentype/unifont/unifont_jp.otf"
DSEG = os.environ.get("DSEG_DIR", os.path.expanduser("~/fonts/fonts-DSEG_v046"))   # folder containing DSEG7-Classic/
uni = ImageFont.truetype(UNI, 16); ucmap = TTFont(UNI).getBestCmap()
def jis0208():
    s = set()
    for hi in list(range(0x81, 0x85)) + list(range(0x88, 0xA0)) + list(range(0xE0, 0xEB)):
        for lo in range(0x40, 0xFD):
            if lo != 0x7F:
                try: s.add(ord(bytes([hi, lo]).decode("shift_jis")))
                except Exception: pass
    return s
codes = set(range(0x20, 0x7F)) | set(range(0xA0, 0x180)) | set(range(0x2010, 0x2030)) | set(range(0x2190, 0x2200)) \
      | set(range(0x25A0, 0x2600)) | set(range(0x3000, 0x3040)) | set(range(0xFF01, 0xFF5F)) | set(range(0xFF61, 0xFFA0)) | jis0208()
codes = sorted(c for c in codes if c in ucmap and c not in (0x302E, 0x302F))
def jis_l1():
    s = set()
    for hi in range(0x81, 0x99):
        for lo in range(0x40, 0xFD):
            if lo == 0x7F: continue
            v = (hi << 8) | lo
            if hi in (0x81, 0x82, 0x83, 0x84) or 0x889F <= v <= 0x9872:
                try: s.add(ord(bytes([hi, lo]).decode("shift_jis")))
                except Exception: pass
    return s
def encode_glyph(rows, w, H):
    a = np.asarray(rows, dtype=np.uint8).reshape(H, w); nb = (H + 7) // 8
    pad = np.zeros((nb * 8, w), np.uint8); pad[:H] = a
    return (pad.reshape(nb, 8, w) << np.arange(8, dtype=np.uint8)[None, :, None]).sum(1).astype(np.uint8).tobytes()
def write_fnt(path, H, asc, maxw, fc, dc, glyphs):
    last = max(glyphs); size = last - fc + 1; blob = bytearray(); off_of = {}
    for cp in sorted(glyphs):
        w, rows = glyphs[cp]; off_of[cp] = len(blob); blob += encode_glyph(rows, w, H)
    nbits = len(blob); ow = 4 if nbits >= 0xFFDB else 2; pad = (-nbits) % 4 if ow == 4 else nbits % 2
    offs, widths = [], []
    for cp in range(fc, last + 1):
        k = cp if cp in glyphs else dc; offs.append(off_of[k]); widths.append(glyphs[k][0])
    out = bytearray(b"RB12") + struct.pack("<HHHH", maxw, H, asc, 0) + struct.pack("<IIIIII", fc, dc, size, nbits, size, size) + blob + b"\0" * pad
    for o in offs: out += struct.pack("<I" if ow == 4 else "<H", o)
    out += bytes(widths); open(path, "wb").write(out)
    print(os.path.basename(path), len(glyphs), "glyphs", os.path.getsize(path) // 1024, "KB")
def uni_bits(ch):
    cw = int(uni.getlength(ch)); g = Image.new("L", (max(cw, 1), 16), 0)
    ImageDraw.Draw(g).text((0, 0), ch, font=uni, fill=255); return cw, np.asarray(g) > 100
def pixel_font(path, sc, bold=True, only=None):
    H = int(16 * sc); glyphs = {}; maxw = 1
    for c in (codes if only is None else [c for c in codes if c in only]):
        cw, a = uni_bits(chr(c))
        if c == 0x20: cw = 8
        W = max(1, int(cw * sc))
        if c == 0x20: glyphs[c] = (W, np.zeros((H, W), int)); maxw = max(maxw, W); continue
        im = Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.NEAREST); b = np.asarray(im) > 100
        if bold: b = b | np.pad(b[:, :-1], ((0, 0), (1, 0)))
        glyphs[c] = (W, b.astype(int)); maxw = max(maxw, W)
    write_fnt(path, H, int(14 * sc), maxw, 0x20, 0x3F, glyphs)

NOTO = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"
def noto_font(path, size, weight="Bold", only=None, thr=118, ss=4):
    """clean outline-derived bitmap font: Noto Sans CJK JP rendered at ss x, box-filtered down, thresholded (RB12 is 1-bit)"""
    f = ImageFont.truetype(NOTO % weight, size * ss, index=0); cm = TTFont(NOTO % weight, fontNumber=0).getBestCmap()
    H = math.ceil(size * 1.09); asc = round(size * 0.88); glyphs = {}; maxw = 1
    for c in codes:
        if only is not None and c not in only: continue
        if c not in cm and c != 0x20: continue
        ch = chr(c); adv = max(2, int(round(f.getlength(ch) / ss)))
        if c == 0x20: glyphs[c] = (adv, np.zeros((H, adv), int)); maxw = max(maxw, adv); continue
        W = adv + 4; im = Image.new("L", (W * ss, H * ss), 0)
        ImageDraw.Draw(im).text((2 * ss, asc * ss), ch, font=f, fill=255, anchor="ls")
        a = np.asarray(im.resize((W, H), Image.BOX)) > thr
        a = a[:, 2:2 + adv]
        if not a.any(): glyphs[c] = (adv, np.zeros((H, adv), int)); continue
        glyphs[c] = (adv, a.astype(int)); maxw = max(maxw, adv)
    write_fnt(path, H, asc, maxw, 0x20, 0x3F, glyphs)
def seg7_glyphs(size, chars="0123456789:-/ "):
    f = ImageFont.truetype(f"{DSEG}/DSEG7-Classic/DSEG7Classic-Bold.ttf", size)
    H = size + 4; asc = size + 2; glyphs = {}; M = 8     # DSEG digits are ~1.07 x size tall: leave room above the baseline so the top row is never clipped
    for ch in chars:
        adv = int(round(f.getlength(ch))) + (10 if ch == " " else 0)
        if ch == " ": glyphs[32] = (adv, np.zeros((H, adv), int)); continue
        im = Image.new("L", (adv + 2 * M, H), 0); d = ImageDraw.Draw(im); d.fontmode = "1"; d.text((M, asc), ch, font=f, fill=255, anchor="ls")
        glyphs[ord(ch)] = (adv, (np.asarray(im.crop((M, 0, M + adv, H))) > 100).astype(int))
    if "1" in chars and "0" in chars:      # the font's '1' renders two rows short at small sizes: rebuild it from the right-hand segments of '0'
        w0, a0 = glyphs[ord("0")]; cols = np.nonzero(a0.any(0))[0]; t = 2 if size < 18 else 3
        a1 = np.zeros_like(a0); a1[:, cols.max() - t + 1:cols.max() + 1] = a0[:, cols.max() - t + 1:cols.max() + 1]; glyphs[ord("1")] = (w0, a1)
    return H, asc, glyphs
def seg7_font(path, size):
    H, asc, g = seg7_glyphs(size); write_fnt(path, H, asc, max(w for w, _ in g.values()), 0x20, 0x20, g)
def build(outdir, ID):
    os.makedirs(outdir, exist_ok=True)
    pixel_font(f"{outdir}/{ID}-16.fnt", 1); noto_font(f"{outdir}/{ID}-24.fnt", 21); noto_font(f"{outdir}/{ID}-32.fnt", 28, only=set(range(0x20, 0x7F)) | set(range(0xA0, 0x100)) | set(range(0x2010, 0x2030)) | set(range(0x3000, 0x3040)) | set(range(0xFF01, 0xFF5F)) | jis_l1())
    for s in (20, 14, 13): seg7_font(f"{outdir}/{ID}-s{s}.fnt", s)
if __name__ == "__main__": build("/tmp/fonttest", "t")
