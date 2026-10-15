#!/usr/bin/env python3
"""Generate the two 480x800 backdrops (menu + playback) with soft hair-like wisps.

The status bar, heading band and volume trough are baked in, so the skins only need %X().
Wisps are deliberately low contrast (a few % lighter than the background) so text stays
easy on the eyes; a few thin magenta streaks give the livery-style accent.

Usage: make_backdrops.py [outdir]   (needs Pillow + numpy)
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import teal_art as A
import status_icons as SI

OUT = sys.argv[1] if len(sys.argv) > 1 else ".rockbox/wps/tealvocaldroid"
os.makedirs(OUT, exist_ok=True)

W, H, SS = 480, 800, 2
BG    = np.array([0x0F, 0x1A, 0x1C], float)
BG_RGB = (0x0F, 0x1A, 0x1C)
BAR   = (0x16, 0x28, 0x2B)
BAND  = (0x1A, 0x30, 0x34)
RULE  = (0x2A, 0x8B, 0x84)
TEAL  = np.array([0x39, 0xC5, 0xBB], float)
MINT  = np.array([0xB8, 0xF0, 0xEA], float)
MAG   = np.array([0xE2, 0x50, 0x9A], float)


def bezier(p0, p1, p2, p3, n=160):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = (np.array(p, float) for p in (p0, p1, p2, p3))
    pts = ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3
    return pts


def ribbon_mask(pts, wmax, head=0.12, power=1.15):
    """Tapered strand: swells quickly near the root, long taper to a point."""
    n = len(pts)
    t = np.linspace(0, 1, n)
    prof = np.minimum(1.0, t / head) ** 0.8 * (1 - t) ** power
    prof = prof / prof.max() * wmax
    d = np.gradient(pts, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None] + 1e-9
    nrm = np.stack([-d[:, 1], d[:, 0]], axis=1)
    left = pts + nrm * prof[:, None] / 2
    right = pts - nrm * prof[:, None] / 2
    poly = np.concatenate([left, right[::-1]]) * SS
    m = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in poly], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(0.8 * SS))
    return np.asarray(m.resize((W, H), Image.LANCZOS), float) / 255.0


def over(canvas, mask, color, alpha, fade=None):
    a = mask * alpha
    if fade is not None:                       # per-row multiplier, e.g. wisps that die out downwards
        a = a * fade[:, None]
    a = a[..., None]
    canvas[:] = canvas * (1 - a) + np.array(color, float) * a


def strands(canvas, root, c1, c2, tip, count, spread, wmax, color, alpha, jitter=0.0, seed=1, fade=None):
    rng = np.random.default_rng(seed)
    for i in range(count):
        k = (i - (count - 1) / 2)
        off = np.array(spread, float) * k
        j = lambda s: rng.normal(0, jitter, 2) * s
        pts = bezier(np.array(root) + off * 0.3, np.array(c1) + off + j(1), np.array(c2) + off * 1.4 + j(2),
                     np.array(tip) + off * 0.6 + j(3))
        w = wmax * (0.55 + 0.45 * rng.random())
        over(canvas, ribbon_mask(pts, w), color, alpha * (0.7 + 0.3 * rng.random()), fade)


def base():
    y = np.linspace(0, 1, H)[:, None, None]
    return np.ones((H, W, 3)) * (BG * (1 - 0.35 * y) + np.array([0x0C, 0x16, 0x19]) * 0.35 * y)


def rect(canvas, x0, y0, x1, y1, color):
    canvas[y0:y1, x0:x1] = np.array(color, float)


def chrome(canvas, band):
    rect(canvas, 0, 0, W, 50, BAR)
    rect(canvas, 0, 50, W, 52, RULE)
    if band:
        A.hgrad(canvas, (0, 52, W, 110), A.BAND_A, A.BAND_B)
    rect(canvas, 46, 19, 166, 31, BG)          # volume trough
    # battery frame is part of the backdrop (NOT a %xd image: skin images are repainted on every level-meter
    # tick and would wipe the live fill drawn on top of them, which showed up as flashing)
    canvas[5:5 + SI.BATT_H, 444:444 + SI.BATT_W] = np.asarray(SI.battery_frame(), float)


def save(canvas, name):
    Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8), "RGB").save(os.path.join(OUT, name), format="BMP")
    print("wrote", name)


# ---------------- menu backdrop: twin tails sweeping from the top right ----------------
c = base()
strands(c, (560, -60), (470, 230), (230, 300), (-40, 560), 5, (16, 10), 70, TEAL, 0.075, 18, seed=3)
strands(c, (580, 120), (430, 420), (250, 520), (-30, 790), 4, (14, 12), 56, TEAL, 0.06, 18, seed=5)
strands(c, (560, 20), (440, 300), (240, 380), (-40, 640), 3, (20, 12), 22, MINT, 0.035, 14, seed=7)
# thin magenta wisps hugging the bundles
strands(c, (565, 30), (455, 270), (235, 340), (-40, 600), 2, (30, 18), 9, MAG, 0.22, 10, seed=11)
strands(c, (585, 330), (440, 560), (280, 640), (60, 800), 2, (26, 16), 8, MAG, 0.20, 10, seed=13)
# livery speed streaks, bottom right
for i, (x0, y0, ln, w, a) in enumerate([(300, 735, 190, 4, 0.45), (350, 752, 150, 3, 0.32), (250, 768, 230, 2, 0.22)]):
    pts = bezier((x0, y0), (x0 + ln * 0.4, y0 - 3), (x0 + ln * 0.7, y0 - 10), (x0 + ln, y0 - 22))
    over(c, ribbon_mask(pts, w, head=0.02, power=0.8), MAG if i != 2 else TEAL, a)
chrome(c, band=True)
# heading band: piano roll, glass title plate, stencil-01 washi tape (clipped to the band)
L = A.Layer()
A.pianoroll(L, 0, 52, 480, 110, lane=7, beat=30, notes=False)
A.pianoroll(L, 352, 52, 480, 110, lane=7, beat=24, notes=True)
L.rr((348, 52, 350, 110), 0, A.MAG); L.poly([(342, 52), (356, 52), (349, 62)], A.MAG)       # playhead
A.plate(L, (14, 60, 330, 106))
A.washi(L, 330, 76, 80, 28, 28, glyph01=True)
L.rr((0, 52, 8, 110), 0, A.MAG)
L.onto(c, clip=(52, 110))
save(c, "bg_menu.bmp")

# ---------------- no-cover badge: baked into bg_wps.bmp (160x160, centred in the cover area) ----------------
# It is only visible when a track has no cover (the album art covers it otherwise), so it needs no
# separate skin image and no conditional in the WPS.
N = 160; S4 = 4
ov = Image.new("RGBA", (N * S4, N * S4), BG_RGB + (255,))
d = ImageDraw.Draw(ov)
m = N // 2
d.ellipse([(m - 78) * S4, (m - 78) * S4, (m + 78) * S4, (m + 78) * S4], fill=(22, 40, 43, 255),
          outline=(226, 80, 154, 255), width=3 * S4)
d.ellipse([(m - 64) * S4, (m - 64) * S4, (m + 64) * S4, (m + 64) * S4], outline=(57, 197, 187, 110), width=S4)
note = (57, 197, 187, 255)
d.ellipse([(m - 27) * S4, (m + 8) * S4, (m - 3) * S4, (m + 28) * S4], fill=note)
d.rectangle([(m - 7) * S4, (m - 32) * S4, (m - 2) * S4, (m + 20) * S4], fill=note)
d.polygon([(p[0] * S4, p[1] * S4) for p in [(m - 2, m - 32), (m + 22, m - 14), (m + 22, m + 2), (m - 2, m - 16)]], fill=note)
BADGE = np.asarray(ov.resize((N, N), Image.LANCZOS).convert("RGB"), float)

# ---------------- playback backdrop (bg_wps.bmp) ----------------
# Same hair wisps as the menu, then (all baked, nothing here is dynamic):
#   58..458   two dim LED ladders either side of the 400px cover (the live meters light them up)
#  462..520   title band: gradient, piano roll, glass plate, stencil-01 washi tape
#  590..626   three equal-outline info chips (format / bitrate / track)
#  640..652   seek-bar trough
#  700..800   control panel
ART_X, ART_Y, ART_S = 40, 58, 400
CHIPS = [(24, 112), (146, 128), (284, 172)]       # format | bitrate | playlist position (fits e.g. 1733/3471)
c = base()
strands(c, (560, -60), (470, 230), (230, 300), (-40, 560), 5, (16, 10), 70, TEAL, 0.075, 18, seed=3)
strands(c, (580, 120), (430, 420), (250, 520), (-30, 790), 4, (14, 12), 56, TEAL, 0.06, 18, seed=5)
strands(c, (560, 20), (440, 300), (240, 380), (-40, 640), 3, (20, 12), 22, MINT, 0.035, 14, seed=7)
strands(c, (565, 30), (455, 270), (235, 340), (-40, 600), 2, (30, 18), 9, MAG, 0.22, 10, seed=11)
yy = np.arange(H)
PANEL_TOP = np.array([0x19, 0x2E, 0x32], float); PANEL_BOT = np.array([0x0B, 0x15, 0x18], float)
g = np.clip((yy - 698) / 102.0, 0, 1)[:, None, None]
c[698:] = (PANEL_TOP * (1 - g) + PANEL_BOT * g)[698:]
c[698] = np.array([0x3A, 0x7F, 0x80])
A.hgrad(c, (0, 462, W, 520), A.BAND_A, A.BAND_B)
L = A.Layer()
for x in (8, 452):
    for y0, y1, f in A.ladder_rects(ART_Y, ART_S):
        L.rr((x, y0, x + A.MW, y1), 1.5, A.TEAL, 0.13)
A.pianoroll(L, 0, 462, 480, 520, lane=6, beat=30, notes=False, alpha=0.7)
A.pianoroll(L, 250, 462, 480, 520, lane=6, beat=24, notes=True)
A.plate(L, (14, 468, 408, 516))
A.washi(L, 380, 488, 76, 24, 28, glyph01=True)
L.rr((0, 462, 8, 520), 0, A.MAG)
for x, w in CHIPS:
    L.rr((x, 590, x + w, 626), 10, A.BAR, 0.9, outline=A.TEAL, ow=1.4)
L.rr((24, 640, 456, 652), 3, (0x2A, 0x5A, 0x58))
L.onto(c)
# no-cover badge, centred in the 400px cover area (only visible when a track has no cover art)
bx, by = ART_X + (ART_S - N) // 2, ART_Y + (ART_S - N) // 2
yy2, xx2 = np.mgrid[0:N, 0:N]
cm = np.clip(80.5 - np.hypot(xx2 - (N - 1) / 2, yy2 - (N - 1) / 2), 0, 1)[..., None]      # circular, soft edge
c[by:by + N, bx:bx + N] = c[by:by + N, bx:bx + N] * (1 - cm) + BADGE * cm
chrome(c, band=False)
save(c, "bg_wps.bmp")
if os.path.exists(os.path.join(OUT, "nocover.bmp")):
    os.remove(os.path.join(OUT, "nocover.bmp"))


