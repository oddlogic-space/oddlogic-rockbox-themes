"""Shared drawing helpers for Teal Vocaldroid: title plate, piano roll, washi tape with a stencil '01',
segmented meter ladders. Everything is drawn on a supersampled RGBA layer and composited onto
the (numpy) backdrop, so edges stay smooth."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H, SS = 480, 800, 4
TEAL = (0x39, 0xC5, 0xBB); MINT = (0xB8, 0xF0, 0xEA); MAG = (0xE2, 0x50, 0x9A)
BAR = (0x16, 0x28, 0x2B); BAND_A = (0x1A, 0x30, 0x34); BAND_B = (0x1F, 0x5F, 0x5A)
TAPE = (0x8F, 0xE3, 0xD8)


class Layer:
    """Full-screen supersampled RGBA layer."""
    def __init__(self):
        self.im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def rr(self, box, r, fill=None, alpha=1.0, outline=None, ow=1.0):
        x0, y0, x1, y1 = box
        fl = None if fill is None else tuple(fill) + (int(255 * alpha),)
        ol = None if outline is None else tuple(outline) + (255,)
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS - 1, y1 * SS - 1], radius=r * SS, fill=fl,
                                 outline=ol, width=max(1, int(ow * SS)) if ol else 0)

    def poly(self, pts, fill, alpha=1.0):
        self.d.polygon(self.P(pts), fill=tuple(fill) + (int(255 * alpha),))

    def line(self, pts, fill, w=1.0):
        self.d.line(self.P(pts), fill=tuple(fill) + (255,), width=max(1, int(w * SS)), joint="curve")

    def mask(self, fn):
        m = Image.new("L", self.im.size, 0)
        fn(ImageDraw.Draw(m))
        return m

    def paint(self, mask, col, alpha):
        lay = Image.new("RGBA", self.im.size, tuple(col) + (0,))
        lay.putalpha(mask.point(lambda v: int(v * alpha)))
        self.im = Image.alpha_composite(self.im, lay)
        self.d = ImageDraw.Draw(self.im)

    def onto(self, canvas, clip=None):
        """Composite onto a float HxWx3 numpy canvas. clip = (y0, y1) keeps only those rows."""
        small = self.im.resize((W, H), Image.LANCZOS)
        a = np.asarray(small, float)
        al = a[..., 3:4] / 255.0
        if clip:
            keep = np.zeros((H, 1, 1)); keep[clip[0]:clip[1]] = 1; al = al * keep
        canvas[:] = canvas * (1 - al) + a[..., :3] * al


def hgrad(canvas, box, a, b):
    x0, y0, x1, y1 = box
    t = np.linspace(0, 1, x1 - x0)[None, :, None]
    canvas[y0:y1, x0:x1] = np.array(a, float) * (1 - t) + np.array(b, float) * t


NOTES = [(0, 0, 1), (1, 1, 2), (3, 3, 1), (4, 2, 2), (6, 4, 1), (7, 1, 1), (8, 3, 2), (10, 5, 1), (11, 2, 2), (13, 4, 1)]


def pianoroll(L, x0, y0, x1, y1, lane=7, beat=30, notes=True, alpha=1.0):
    for i, y in enumerate(range(y0, y1, lane)):
        if i % 2 == 0:
            L.rr((x0, y, x1, min(y + lane, y1)), 0, TEAL, 0.05 * alpha)
    for k, x in enumerate(range(x0, x1, beat)):
        L.rr((x, y0, x + 1, y1), 0, TEAL, (0.16 if k % 4 == 0 else 0.07) * alpha)
    if not notes:
        return
    lanes = (y1 - y0) // lane
    for i, (b, ln, ln2) in enumerate(NOTES):
        nx = x0 + 8 + b * beat * 0.5; ny = y0 + (ln % lanes) * lane + 1; nw = ln2 * beat * 0.5 + 10
        if nx + nw > x1:
            continue
        col = MAG if i % 3 == 1 else (MINT if i % 3 == 2 else TEAL)
        L.rr((nx, ny, nx + nw, ny + lane - 2), 2.5, col, 0.95 * alpha)


def plate(L, box, r=14):
    L.rr(box, r, BAR, 0.9, outline=TEAL, ow=1.6)


def washi(L, cx, cy, w, h, ang, glyph01=False):
    """Mint washi tape: serrated ends, soft shadow, pale stripes. glyph01 stencils a magenta '01' on it."""
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    rot = lambda dx, dy: (cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)
    zig = 3.0; n = max(2, int(h / (zig * 2))); pts = []
    for k in range(n + 1):
        pts.append(rot(-w / 2 + (zig if k % 2 else 0), -h / 2 + k * (h / n)))
    for k in range(n, -1, -1):
        pts.append(rot(w / 2 - (zig if k % 2 else 0), -h / 2 + k * (h / n)))
    sh = L.mask(lambda d: d.polygon(L.P([(x, y + 3) for x, y in pts]), fill=255)).filter(ImageFilter.GaussianBlur(3 * SS))
    L.paint(sh, (0, 0, 0), 0.4)
    L.poly(pts, TAPE, 0.92)
    body = L.mask(lambda d: d.polygon(L.P(pts), fill=255))
    def stripes(d):
        for x in range(int(-w / 2 + 6), int(w / 2), 12):
            d.polygon(L.P([rot(x, -h / 2), rot(x + 3, -h / 2), rot(x + 3, h / 2), rot(x, h / 2)]), fill=255)
    L.paint(ImageChops.multiply(body, L.mask(stripes)), (255, 255, 255), 0.22)
    L.line(pts[: n + 1], (0xD6, 0xFF, 0xF8), 1.0)
    if glyph01:
        k = h / 20.0
        r2 = lambda dx, dy: rot(dx * k, dy * k)
        def half(inset):
            M = 8; g = 0.9
            def piece(hw, hh, rad):
                c0 = -10.5
                p = [(c0 - g, -hh), (c0 - hw + rad, -hh)]
                p += [(c0 - hw + rad - rad * math.sin(t * math.pi / 2 / M), -hh + rad - rad * math.cos(t * math.pi / 2 / M)) for t in range(1, M + 1)]
                p += [(c0 - hw, hh - rad)]
                p += [(c0 - hw + rad - rad * math.cos(t * math.pi / 2 / M), hh - rad + rad * math.sin(t * math.pi / 2 / M)) for t in range(1, M + 1)]
                p += [(c0 - g, hh)]
                return p
            return piece(8.5, 9.0, 5.0) + piece(4.6, 5.4, 1.8)[::-1]
        left = half(0)
        right = [(-21 - x, y) for x, y in left]
        one = [(1, -3), (5.5, -8), (10, -8), (10, 8), (6, 8), (6, -3.5), (1, -0.5)]
        for p in (left, right, one):
            L.poly([r2(x + 2, y) for x, y in p], MAG, 0.95)


# ---- segmented meter ladder (shared by the baked dim ladder and the live meter images) ----
MW, SEG, GAP, NSEG = 20, 7, 4, 36


def ladder_rects(y_top, height):
    """Yield (y0, y1, frac) from the bottom up; frac 0..1."""
    off = (height - (NSEG * SEG + (NSEG - 1) * GAP)) / 2.0
    y1 = y_top + height
    for i in range(NSEG):
        yb = y1 - off - i * (SEG + GAP)
        yield yb - SEG, yb, i / (NSEG - 1)


def ladder_colour(f):
    return TEAL if f < 0.62 else (MINT if f < 0.8 else MAG)
