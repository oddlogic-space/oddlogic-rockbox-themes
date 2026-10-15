#!/usr/bin/env python3
"""Generate every bitmap the Teal Vocaldroid theme uses (needs Pillow).
Usage: make_icons.py [outdir]     default: .rockbox/wps/tealvocaldroid
Multi-state images are sprite sheets: sub-images stacked vertically, first = top.
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else ".rockbox/wps/tealvocaldroid"
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
os.makedirs(OUT, exist_ok=True)

BG    = (0x0F, 0x1A, 0x1C)   # page background
BAR   = (0x16, 0x28, 0x2B)   # status bar / button panels
TEAL  = (0x39, 0xC5, 0xBB)   # accent
DEEP  = (0x1F, 0x5F, 0x5A)
TXT   = (0xD8, 0xEE, 0xEC)
DIM   = (0x6A, 0x8F, 0x8C)   # inactive icon colour
LINE  = (0x8F, 0xB3, 0xB0)
MAG   = (0xE2, 0x50, 0x9A)   # magenta: active toggles, progress marker
S = 4                         # supersampling


def save(im, name, w, h):
    im.resize((w, h), Image.LANCZOS).save(os.path.join(OUT, name), format="BMP")


def tri(d, pts, col):
    d.polygon([(x * S, y * S) for x, y in pts], fill=col)


def rect(d, x0, y0, x1, y1, col):
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=col)


def line(d, pts, col, w=3):
    d.line([(x * S, y * S) for x, y in pts], fill=col, width=int(w * S), joint="curve")


# ---------------- playback controls (composited over bg_wps.bmp at their screen positions) ----------------
from PIL import ImageChops
try:
    BGW = Image.open(os.path.join(OUT, "bg_wps.bmp")).convert("RGB")
except FileNotFoundError:
    sys.exit("run make_backdrops.py first: the controls are composited over bg_wps.bmp")

def layer(w, h):
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)

def finish(layer_im, w, h, pos):
    """Downsample the shape layer and lay it over the real backdrop pixels at `pos`."""
    base = BGW.crop((pos[0], pos[1], pos[0] + w, pos[1] + h)).convert("RGBA")
    top = layer_im.resize((w, h), Image.LANCZOS)
    return Image.alpha_composite(base, top).convert("RGB")

def stack(frames, name):
    w, h = frames[0].size
    sheet = Image.new("RGB", (w, h * len(frames)))
    for i, fr in enumerate(frames):
        sheet.paste(fr, (0, i * h))
    sheet.save(os.path.join(OUT, name), format="BMP")

def round_btn(n, pos, fill, glyph, col, ring=None):
    im, d = layer(n, n)
    d.ellipse([S, S, (n - 1) * S, (n - 1) * S], fill=fill)
    if ring:
        d.ellipse([S, S, (n - 1) * S, (n - 1) * S], outline=ring, width=2 * S)
    glyph(d, n / 2, col)
    return finish(im, n, n, pos)

def g_prev(d, m, c):
    tri(d, [(m + 13, m - 15), (m + 13, m + 15), (m - 3, m)], c)
    tri(d, [(m - 2, m - 15), (m - 2, m + 15), (m - 18, m)], c)
    rect(d, m - 22, m - 15, m - 18, m + 15, c)
def g_next(d, m, c):
    tri(d, [(m - 13, m - 15), (m - 13, m + 15), (m + 3, m)], c)
    tri(d, [(m + 2, m - 15), (m + 2, m + 15), (m + 18, m)], c)
    rect(d, m + 18, m - 15, m + 22, m + 15, c)
def g_play(d, m, c):
    tri(d, [(m - 12, m - 20), (m - 12, m + 20), (m + 22, m)], c)
def g_pause(d, m, c):
    rect(d, m - 16, m - 20, m - 5, m + 20, c)
    rect(d, m + 5, m - 20, m + 16, m + 20, c)

# screen positions of each image (viewports in tealvocaldroid.wps offset these by +16/+16 etc.)
P_SHUF, P_PREV, P_PLAY, P_NEXT, P_REP, P_MENU = (16, 724), (110, 720), (200, 712), (306, 720), (408, 724), (420, 462)
MENU_W, MENU_H = 60, 62

save_rgb = lambda im, name: im.save(os.path.join(OUT, name), format="BMP")
save_rgb(round_btn(64, P_PREV, BAR, g_prev, TEAL), "prev.bmp")
save_rgb(round_btn(64, P_NEXT, BAR, g_next, TEAL), "next.bmp")
save_rgb(round_btn(80, P_PLAY, DEEP, g_play, TXT), "play.bmp")
save_rgb(round_btn(80, P_PLAY, DEEP, g_pause, TXT), "pause.bmp")

# ---- round toggle buttons, 56x56. Icons are centred on (28,28). ----
N = 56
cx, cy = N / 2, N / 2

def icon_repeat(d, col):
    x0, x1, yt, yb = cx - 15, cx + 15, cy - 8, cy + 8
    line(d, [(x0, cy + 3), (x0, yt), (x1 - 7, yt)], col, 2.6)
    tri(d, [(x1 - 8, yt - 5), (x1 - 8, yt + 5), (x1 + 2, yt)], col)
    line(d, [(x1, cy - 3), (x1, yb), (x0 + 7, yb)], col, 2.6)
    tri(d, [(x0 + 8, yb - 5), (x0 + 8, yb + 5), (x0 - 2, yb)], col)

def icon_shuffle(d, col):
    x0, x1, yt, yb = cx - 15, cx + 15, cy - 8, cy + 8
    line(d, [(x0, yb), (x0 + 8, yb), (x1 - 9, yt), (x1 - 8, yt)], col, 2.6)
    tri(d, [(x1 - 9, yt - 5), (x1 - 9, yt + 5), (x1 + 1, yt)], col)
    line(d, [(x0, yt), (x0 + 8, yt), (x1 - 9, yb), (x1 - 8, yb)], col, 2.6)
    tri(d, [(x1 - 9, yb - 5), (x1 - 9, yb + 5), (x1 + 1, yb)], col)

def label(d, text, col, size, dy=0):
    f = ImageFont.truetype(FONT, size * S, index=0)
    d.text((cx * S, (cy + dy) * S), text, font=f, fill=col, anchor="mm")

def toggle(pos, active, glyph, col, text=None, tsize=14, tdy=-1):
    im, d = layer(N, N)
    d.ellipse([S, S, (N - 1) * S, (N - 1) * S], fill=BAR)
    if active:
        d.ellipse([S, S, (N - 1) * S, (N - 1) * S], outline=MAG, width=2 * S)
    if glyph: glyph(d, col)
    if text: label(d, text, col, tsize, tdy)
    return finish(im, N, N, pos)

# repeat.bmp: off | all | one | repeat-shuffle | A-B
stack([toggle(P_REP, False, icon_repeat, DIM),
       toggle(P_REP, True,  icon_repeat, MAG),
       toggle(P_REP, True,  icon_repeat, MAG, "1", 14, -1),
       toggle(P_REP, True,  icon_repeat, MAG, "S", 14, -1),
       toggle(P_REP, True,  None, MAG, "A-B", 19, 0)], "repeat.bmp")
# shuffle.bmp: off | on
stack([toggle(P_SHUF, False, icon_shuffle, DIM),
       toggle(P_SHUF, True,  icon_shuffle, MAG)], "shuffle.bmp")

# ---------------- progress bar marker (12x14 pink pill) ----------------
w, h = 12, 14
im = Image.new("RGB", (w * S, h * S), (0x2A, 0x5A, 0x58)); d = ImageDraw.Draw(im)      # corners match the seek trough
d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=3 * S, fill=MAG)
save(im, "pb_knob.bmp", w, h)

# ---------------- status bar graphics (headset volume icon, ladder battery) ----------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_icons as SI
SI.headset().save(os.path.join(OUT, "speaker.bmp"), format="BMP")
SI.battery_fill().save(os.path.join(OUT, "battery_fill.bmp"), format="BMP")

# ---------------- live level-meter images + context button (need the real backdrop + teal_art) ----------------
import numpy as np
import teal_art as A
bgf = np.asarray(BGW, float)

def crop(canvas, box):
    x0, y0, x1, y1 = box
    return Image.fromarray(np.clip(canvas[y0:y1, x0:x1], 0, 255).astype(np.uint8), "RGB")

# meter_l/meter_r: the lit ladder, 20x400, laid over the pixels behind each column. The bar reveals it
# from the bottom, so teal sits low, mint in the middle and the magenta peak at the top.
for name, x in (("meter_l.bmp", 8), ("meter_r.bmp", 452)):
    cv = bgf.copy(); L = A.Layer()
    for y0, y1, f in A.ladder_rects(58, 400):
        L.rr((x, y0, x + A.MW, y1), 1.5, A.ladder_colour(f), 1.0)
    L.onto(cv)
    save_rgb(crop(cv, (x, 58, x + A.MW, 458)), name)

# menu.bmp: round "..." button with a small strip of washi tape across its top edge
cv = bgf.copy(); L = A.Layer()
L.rr((426, 474, 472, 520), 23, (0x0F, 0x1A, 0x1C), 0.95, outline=A.TEAL, ow=1.6)
for dx in (-10, 0, 10):
    L.rr((449 + dx - 3.2, 501 - 3.2, 449 + dx + 3.2, 501 + 3.2), 3.2, (0x8F, 0xB3, 0xB0))
A.washi(L, 449, 476, 44, 15, -12)
L.onto(cv)
save_rgb(crop(cv, (P_MENU[0], P_MENU[1], P_MENU[0] + MENU_W, P_MENU[1] + MENU_H)), "menu.bmp")

print("icons written to", OUT)
