"""Drawing kit for Waveform Bot HUD: supersampled RGBA layers composited onto a numpy canvas."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

W, H, SS = 480, 800, 4
hx = lambda s: tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))

# palette: navy body, gold chest frame, silver keys, red peaks. ICE/PURP/MRED are for the battery icon only.
BG, BAR = hx("0C1230"), hx("0F1738")
BODY, BODY2, DARK = hx("1C2A66"), hx("26398A"), hx("090B14")
GOLD, GOLDL, GOLDD = hx("D3A52E"), hx("ECC95A"), hx("8B6A1C")
RED = hx("E0503C")
ICE, PURP, MRED = hx("A9C6F2"), hx("9A66E8"), hx("C45B5B")
SILVER, SILVD, INK = hx("CBD2DE"), hx("A4AEC2"), hx("26315A")
TXT, SEC, STEEL, ELAPSED = hx("E4E9F5"), hx("93A0C4"), hx("4A66B8"), hx("F0766C")
CH_L, CH_D = GOLDL, GOLDD
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def chamfer(box, cut, corners="tl,tr,br,bl"):
    x0, y0, x1, y1 = box
    cs = corners.split(","); c = lambda k: cut if k in cs else 0
    return [(x0 + c("tl"), y0), (x1 - c("tr"), y0), (x1, y0 + c("tr")), (x1, y1 - c("br")),
            (x1 - c("br"), y1), (x0 + c("bl"), y1), (x0, y1 - c("bl")), (x0, y0 + c("tl"))]


class Layer:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts): return [(x * SS, y * SS) for x, y in pts]

    def mask(self, fn):
        m = Image.new("L", self.im.size, 0); fn(ImageDraw.Draw(m)); return m

    def paint(self, mask, col, alpha=1.0):
        lay = Image.new("RGBA", self.im.size, tuple(col) + (0,))
        lay.putalpha(mask.point(lambda v: int(v * alpha)))
        self.im = Image.alpha_composite(self.im, lay); self.d = ImageDraw.Draw(self.im)

    def rr(self, box, r, fill=None, alpha=1.0, outline=None, ow=1.0):
        x0, y0, x1, y1 = box
        fl = None if fill is None else tuple(fill) + (int(255 * alpha),)
        ol = None if outline is None else tuple(outline) + (255,)
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS - 1, y1 * SS - 1], radius=r * SS, fill=fl, outline=ol,
                                 width=max(1, int(ow * SS)) if ol else 0)

    def ell(self, cx, cy, r, fill, alpha=1.0):
        self.d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=tuple(fill) + (int(255 * alpha),))

    def ring(self, cx, cy, r, w, col):
        self.d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], outline=tuple(col) + (255,), width=int(w * SS))

    def poly(self, pts, fill, alpha=1.0):
        self.d.polygon(self.P(pts), fill=tuple(fill) + (int(255 * alpha),))

    def line(self, pts, col, w=1.0):
        self.d.line(self.P(pts), fill=tuple(col) + (255,), width=max(1, int(w * SS)), joint="curve")

    def gpoly(self, pts, top, bot, y0, y1):
        m = self.mask(lambda d: d.polygon(self.P(pts), fill=255))
        rows = np.clip((np.arange(self.im.size[1])[:, None] / SS - y0) / max(1, y1 - y0), 0, 1)[..., None]
        arr = (np.array(top, float) * (1 - rows) + np.array(bot, float) * rows) * np.ones((1, self.im.size[0], 1))
        g = Image.fromarray(arr.astype(np.uint8)).convert("RGBA"); g.putalpha(m)
        self.im = Image.alpha_composite(self.im, g); self.d = ImageDraw.Draw(self.im)

    def grect(self, box, r, top, bot):
        x0, y0, x1, y1 = box
        m = self.mask(lambda d: d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS - 1, y1 * SS - 1], radius=r * SS, fill=255))
        rows = np.clip((np.arange(self.im.size[1])[:, None] / SS - y0) / max(1, y1 - y0), 0, 1)[..., None]
        arr = (np.array(top, float) * (1 - rows) + np.array(bot, float) * rows) * np.ones((1, self.im.size[0], 1))
        g = Image.fromarray(arr.astype(np.uint8)).convert("RGBA"); g.putalpha(m)
        self.im = Image.alpha_composite(self.im, g); self.d = ImageDraw.Draw(self.im)

    def shadow(self, pts, off=(0, 3), blur=3, alpha=0.5):
        m = self.mask(lambda d: d.polygon(self.P([(x + off[0], y + off[1]) for x, y in pts]), fill=255)).filter(ImageFilter.GaussianBlur(blur * SS))
        self.paint(m, (0, 0, 0), alpha)

    def glow(self, pts, col, w=1.4, strength=0.0, blur=3):
        P = pts + [pts[0]]
        if strength:
            m = self.mask(lambda d: d.line(self.P(P), fill=255, width=int(w * SS * 2.2), joint="curve")).filter(ImageFilter.GaussianBlur(blur * SS))
            self.paint(m, col, strength)
        self.line(P, col, w)

    def text(self, xy, t, col, size, anchor="mm"):
        f = ImageFont.truetype(FONT_B, int(size * SS), index=0)
        self.d.text((xy[0] * SS, xy[1] * SS), t, font=f, fill=tuple(col) + (255,), anchor=anchor)

    def onto(self, canvas, clip=None):
        small = self.im.resize((self.w, self.h), Image.LANCZOS)
        a = np.asarray(small, float); al = a[..., 3:4] / 255.0
        if clip:
            keep = np.zeros((self.h, 1, 1)); keep[clip[0]:clip[1]] = 1; al = al * keep
        canvas[:] = canvas * (1 - al) + a[..., :3] * al


def vgrad(canvas, box, a, b):
    x0, y0, x1, y1 = box
    t = np.linspace(0, 1, y1 - y0)[:, None, None]
    canvas[y0:y1, x0:x1] = np.array(a, float) * (1 - t) + np.array(b, float) * t


def hgrad(canvas, box, a, b):
    x0, y0, x1, y1 = box
    t = np.linspace(0, 1, x1 - x0)[None, :, None]
    canvas[y0:y1, x0:x1] = np.array(a, float) * (1 - t) + np.array(b, float) * t


# ---- segmented meter ladder (shared by the dim backdrop ladders and the live meter images) ----
MW, SEG, GAP = 18, 7, 4


def ladder_rects(y_top, height):
    n = int((height + GAP) // (SEG + GAP)); off = (height - (n * SEG + (n - 1) * GAP)) / 2.0
    for i in range(n):
        yb = y_top + height - off - i * (SEG + GAP)
        yield yb - SEG, yb, i / (n - 1)


def ladder_colour(f):
    return STEEL if f < 0.6 else (SILVER if f < 0.8 else RED)
