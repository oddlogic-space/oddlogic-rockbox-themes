import numpy as np, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
SS = 3
W, H = 480, 800
FP = {"inter": "/usr/share/fonts/truetype/inter/Inter-Medium.ttf"}
import glob, subprocess
def ff(name, style=None):
    q = name + (":style=" + style if style else "")
    p = subprocess.run(["fc-match", "-f", "%{file}", q], capture_output=True, text=True).stdout
    return p
_fc = {}
def F(name, size, style=None):
    k = (name, size, style)
    if k not in _fc: _fc[k] = ImageFont.truetype(ff(name, style), int(size * SS))
    return _fc[k]
def c3(c, a=1.0): return tuple(int(max(0, min(255, v))) for v in c)
def mixc(a, b, t): return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))
def S(v): return int(round(v * SS))
def box(b): return [S(b[0]), S(b[1]), S(b[2]), S(b[3])]

class Cv:
    def __init__(s, base):
        s.im = Image.new("RGB", (W * SS, H * SS), c3(base)); s.d = ImageDraw.Draw(s.im)
    def rect(s, b, fill=None, outline=None, w=1, r=0):
        if r: s.d.rounded_rectangle(box(b), radius=S(r), fill=fill, outline=outline, width=S(w) if outline else 0)
        else: s.d.rectangle(box(b), fill=fill, outline=outline, width=S(w) if outline else 0)
    def line(s, pts, fill, w=1): s.d.line([(S(x), S(y)) for x, y in pts], fill=fill, width=S(w))
    def poly(s, pts, fill): s.d.polygon([(S(x), S(y)) for x, y in pts], fill=fill)
    def ell(s, cx, cy, rx, ry=None, fill=None, outline=None, w=1):
        ry = rx if ry is None else ry
        s.d.ellipse([S(cx - rx), S(cy - ry), S(cx + rx), S(cy + ry)], fill=fill, outline=outline, width=S(w) if outline else 0)
    def text(s, xy, t, font, fill, anchor="la"): s.d.text((S(xy[0]), S(xy[1])), t, font=font, fill=fill, anchor=anchor)
    def grad(s, b, top, bot, r=0, horiz=False):
        x0, y0, x1, y1 = [S(v) for v in b]; w, h = x1 - x0, y1 - y0
        t = np.linspace(0, 1, w if horiz else h)[:, None] if not horiz else np.linspace(0, 1, w)[None, :]
        a = np.array(top, float); bb = np.array(bot, float)
        if horiz: arr = a[None, None, :] * (1 - t[..., None]) + bb[None, None, :] * t[..., None]; arr = np.repeat(arr, h, 0)
        else: arr = a[None, None, :] * (1 - t[..., None]) + bb[None, None, :] * t[..., None]; arr = np.repeat(arr, w, 1)
        g = Image.fromarray(arr.clip(0, 255).astype("uint8"))
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=S(r), fill=255)
        s.im.paste(g, (x0, y0), m); s.d = ImageDraw.Draw(s.im)
    def brushed(s, b, base, amt=7, vert=False, seed=1):
        x0, y0, x1, y1 = [S(v) for v in b]; w, h = x1 - x0, y1 - y0
        rng = np.random.default_rng(seed)
        n = rng.normal(0, amt, (h, 1) if not vert else (1, w)); n = np.repeat(n, w if not vert else h, 1 if not vert else 0)
        n = n + rng.normal(0, amt * .25, (h, w))
        arr = np.array(base, float)[None, None, :] + n[..., None]
        s.im.paste(Image.fromarray(arr.clip(0, 255).astype("uint8")), (x0, y0)); s.d = ImageDraw.Draw(s.im)
    def wood(s, b, base, dark, seed=3, vert=True):
        x0, y0, x1, y1 = [S(v) for v in b]; w, h = x1 - x0, y1 - y0
        rng = np.random.default_rng(seed)
        yy, xx = np.mgrid[0:h, 0:w]
        u = xx if vert else yy; v = yy if vert else xx
        g = np.sin(u / (SS * 1.6) + 3 * np.sin(v / (SS * 38) + rng.random() * 6) + rng.random() * 6) * .5 + .5
        g += rng.normal(0, .08, (h, w)); g = g.clip(0, 1) ** 1.3
        a = np.array(base, float); d = np.array(dark, float)
        arr = a[None, None, :] * (1 - g[..., None]) + d[None, None, :] * g[..., None]
        s.im.paste(Image.fromarray(arr.clip(0, 255).astype("uint8")), (x0, y0)); s.d = ImageDraw.Draw(s.im)
    def shadow(s, b, r=0, blur=4, off=(0, 2), a=110):
        m = Image.new("L", s.im.size, 0); ImageDraw.Draw(m).rounded_rectangle([S(b[0] + off[0]), S(b[1] + off[1]), S(b[2] + off[0]), S(b[3] + off[1])], radius=S(r), fill=a)
        m = m.filter(ImageFilter.GaussianBlur(S(blur)))
        blk = Image.new("RGB", s.im.size, (0, 0, 0)); s.im.paste(blk, (0, 0), m); s.d = ImageDraw.Draw(s.im)
    def bevel(s, b, face, r=4, hi=.35, lo=.45, w=1.4):
        s.rect(b, fill=c3(face), r=r)
        x0, y0, x1, y1 = b
        s.line([(x0 + r, y0 + w / 2), (x1 - r, y0 + w / 2)], c3(mixc(face, (255, 255, 255), hi)), w)
        s.line([(x0 + r, y1 - w / 2), (x1 - r, y1 - w / 2)], c3(mixc(face, (0, 0, 0), lo)), w)
    def screw(s, cx, cy, r=5, col=(150, 148, 140), ang=.6):
        s.ell(cx + .6, cy + .9, r, fill=(0, 0, 0)); s.ell(cx, cy, r, fill=c3(col)); s.ell(cx, cy, r, outline=c3(mixc(col, (0, 0, 0), .5)), w=.8)
        dx, dy = math.cos(ang) * r * .8, math.sin(ang) * r * .8
        s.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], c3(mixc(col, (0, 0, 0), .65)), 1.2)
    def led(s, cx, cy, r, col, on=True):
        if on:
            glow = Image.new("RGB", s.im.size, (0, 0, 0)); gd = ImageDraw.Draw(glow); gd.ellipse([S(cx - r * 2.4), S(cy - r * 2.4), S(cx + r * 2.4), S(cy + r * 2.4)], fill=c3(mixc((0, 0, 0), col, .55)))
            glow = glow.filter(ImageFilter.GaussianBlur(S(r * 1.2)))
            s.im = ImageChops.add(s.im, glow); s.d = ImageDraw.Draw(s.im)
        s.ell(cx, cy, r, fill=c3(col if on else mixc(col, (0, 0, 0), .75)))
        if on: s.ell(cx - r * .3, cy - r * .35, r * .35, fill=c3(mixc(col, (255, 255, 255), .7)))
    def knob(s, cx, cy, r, face=(30, 30, 32), cap=(70, 70, 74), ang=-40, mark=(235, 230, 215)):
        s.shadow([cx - r, cy - r, cx + r, cy + r], r, 3, (0, 2), 140)
        s.ell(cx, cy, r, fill=c3(face)); s.ell(cx, cy, r, outline=c3(mixc(face, (255, 255, 255), .25)), w=.8)
        s.ell(cx, cy, r * .78, fill=c3(cap)); s.ell(cx - r * .12, cy - r * .16, r * .55, fill=c3(mixc(cap, (255, 255, 255), .12)))
        a = math.radians(ang - 90); s.line([(cx + math.cos(a) * r * .25, cy + math.sin(a) * r * .25), (cx + math.cos(a) * r * .72, cy + math.sin(a) * r * .72)], c3(mark), 2)
    def out(s, path):
        s.im.resize((W, H), Image.LANCZOS).save(path)
        return s.im.resize((W, H), Image.LANCZOS)

def noise(im, amt=3, seed=5):
    a = np.array(im, float); rng = np.random.default_rng(seed); a += rng.normal(0, amt, a.shape[:2])[..., None]
    return Image.fromarray(a.clip(0, 255).astype("uint8"))
