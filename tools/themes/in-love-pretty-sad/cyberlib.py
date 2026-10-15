"""Drawing kit shared by the three cyber themes (Pillow + numpy). Supersampled shapes on a 480x800 canvas."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H, S = 480, 800, 3
fc = lambda h: tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

class Cv:
    def __init__(s, bg):
        s.im = Image.new("RGB", (W*S, H*S), bg)
    def mask(s, fn):
        m = Image.new("L", (W*S, H*S), 0); fn(ImageDraw.Draw(m)); return m
    def paint(s, m, color, alpha=1.0):
        if alpha < 1: m = m.point(lambda v: int(v*alpha))
        s.im.paste(Image.new("RGB", s.im.size, color), (0, 0), m)
    def paint_grad(s, m, top, bot, y0, y1):
        g = np.linspace(0, 1, H*S)[:, None, None]
        t = np.clip((np.arange(H*S)[:, None, None]/S - y0)/(y1 - y0), 0, 1)
        arr = (np.array(top, float)*(1-t) + np.array(bot, float)*t) * np.ones((H*S, W*S, 3))
        s.im.paste(Image.fromarray(arr.astype(np.uint8)), (0, 0), m)
    def rr(s, box, r, color, alpha=1.0, outline=None, ow=0):
        x0, y0, x1, y1 = [v*S for v in box]
        s.paint(s.mask(lambda d: d.rounded_rectangle([x0, y0, x1, y1], radius=r*S, fill=255)), color, alpha)
        if outline: s.paint(s.mask(lambda d: (d.rounded_rectangle([x0, y0, x1, y1], radius=r*S, fill=255),
                            d.rounded_rectangle([x0+ow*S, y0+ow*S, x1-ow*S, y1-ow*S], radius=max(r-ow,0)*S, fill=0))), outline)
    def rr_grad(s, box, r, top, bot):
        x0, y0, x1, y1 = [v*S for v in box]
        s.paint_grad(s.mask(lambda d: d.rounded_rectangle([x0, y0, x1, y1], radius=r*S, fill=255)), top, bot, box[1], box[3])
    def ell(s, cx, cy, r, color, alpha=1.0):
        s.paint(s.mask(lambda d: d.ellipse([(cx-r)*S, (cy-r)*S, (cx+r)*S, (cy+r)*S], fill=255)), color, alpha)
    def ring(s, cx, cy, r, w, color):
        s.paint(s.mask(lambda d: (d.ellipse([(cx-r)*S, (cy-r)*S, (cx+r)*S, (cy+r)*S], fill=255),
                                  d.ellipse([(cx-r+w)*S, (cy-r+w)*S, (cx+r-w)*S, (cy+r-w)*S], fill=0))), color)
    def poly(s, pts, color, alpha=1.0):
        s.paint(s.mask(lambda d: d.polygon([(x*S, y*S) for x, y in pts], fill=255)), color, alpha)
    def line(s, pts, color, w=1.0):
        s.paint(s.mask(lambda d: d.line([(x*S, y*S) for x, y in pts], fill=255, width=int(w*S), joint="curve")), color)
    def shadow(s, box, r, off=(0, 3), blur=4, alpha=0.5):
        x0, y0, x1, y1 = box
        m = s.mask(lambda d: d.rounded_rectangle([(x0+off[0])*S, (y0+off[1])*S, (x1+off[0])*S, (y1+off[1])*S], radius=r*S, fill=255))
        m = m.filter(ImageFilter.GaussianBlur(blur*S)); s.paint(m, (0, 0, 0), alpha)
    def text(s, xy, t, color, size, font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", anchor="la", spacing=0):
        f = ImageFont.truetype(font, int(size*S)); d = ImageDraw.Draw(s.im)
        if spacing:
            x, y = xy[0]*S, xy[1]*S
            for ch in t:
                d.text((x, y), ch, font=f, fill=color, anchor=anchor); x += f.getlength(ch) + spacing*S
        else:
            d.text((xy[0]*S, xy[1]*S), t, font=f, fill=color, anchor=anchor)
    def out(s): return s.im.resize((W, H), Image.LANCZOS)

def chamfer_pts(box, cut, corners="tl,br"):
    x0, y0, x1, y1 = box; cs = corners.split(",")
    pts = []
    pts += [(x0+cut, y0), (x1-(cut if "tr" in cs else 0), y0)] if "tl" in cs else [(x0, y0), (x1-(cut if "tr" in cs else 0), y0)]
    if "tr" in cs: pts += [(x1, y0+cut)]
    pts += [(x1, y1-(cut if "br" in cs else 0))]
    if "br" in cs: pts += [(x1-cut, y1)]
    pts += [(x0+(cut if "bl" in cs else 0), y1)]
    if "bl" in cs: pts += [(x0, y1-cut)]
    if "tl" in cs: pts += [(x0, y0+cut)]
    return pts

def glow(c, pts, color, w=1.6, closed=True, strength=0.55, blur=3.5):
    P = pts + [pts[0]] if closed else pts
    m = c.mask(lambda d: d.line([(x*S, y*S) for x, y in P], fill=255, width=int(w*S*2.2), joint="curve"))
    c.paint(m.filter(ImageFilter.GaussianBlur(blur*S)), color, strength)
    c.line(P, color, w)

def scan_bg(p, seed=3):
    c = Cv(p["bg"])
    arr = np.asarray(c.im, float)
    # faint grid + scanlines + vignette baked into the backdrop
    ys = np.arange(H*S)[:, None]; xs = np.arange(W*S)[None, :]
    grid = (((xs // (S*40)) != ((xs-1) // (S*40))) | ((ys // (S*40)) != ((ys-1) // (S*40)))).astype(float)
    scan = ((ys // S) % 3 == 0).astype(float)
    arr = arr*(1 - 0.0) + (grid[..., None]*np.array(p["line"], float)*0.05) + scan[..., None]*(-3.0)
    v = np.clip(1 - (((xs/S-240)/340)**2 + ((ys/S-400)/560)**2), 0.55, 1)[..., None]
    arr = arr*v
    c.im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return c

def brackets(c, box, color, L=22, w=2.4, off=8):
    x0, y0, x1, y1 = box[0]-off, box[1]-off, box[2]+off, box[3]+off
    for (px, py, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        glow(c, [(px, py+dy*L), (px, py), (px+dx*L, py)], color, w, closed=False, strength=0.5)

def glyph(c, g, kind, cx, cy, act=False, accent=None):
    ac = accent or g
    col = ac if act else g
    if kind == "play": c.poly([(cx-12, cy-17), (cx-12, cy+17), (cx+19, cy)], g)
    elif kind == "pause": c.rr((cx-13, cy-16, cx-4, cy+16), 1, g); c.rr((cx+4, cy-16, cx+13, cy+16), 1, g)
    elif kind == "prev":
        c.poly([(cx+13, cy-13), (cx+13, cy+13), (cx-3, cy)], g); c.poly([(cx-2, cy-13), (cx-2, cy+13), (cx-18, cy)], g); c.rr((cx-22, cy-13, cx-19, cy+13), 0, g)
    elif kind == "next":
        c.poly([(cx-13, cy-13), (cx-13, cy+13), (cx+3, cy)], g); c.poly([(cx+2, cy-13), (cx+2, cy+13), (cx+18, cy)], g); c.rr((cx+19, cy-13, cx+22, cy+13), 0, g)
    elif kind == "rep":
        c.line([(cx-13, cy+3), (cx-13, cy-7), (cx+8, cy-7)], col, 2.4); c.poly([(cx+7, cy-13), (cx+7, cy-1), (cx+17, cy-7)], col)
        c.line([(cx+13, cy-3), (cx+13, cy+7), (cx-8, cy+7)], col, 2.4); c.poly([(cx-7, cy+1), (cx-7, cy+13), (cx-17, cy+7)], col)
    elif kind == "shuf":
        c.line([(cx-15, cy+8), (cx-6, cy+8), (cx+6, cy-8), (cx+10, cy-8)], col, 2.4); c.poly([(cx+8, cy-14), (cx+8, cy-2), (cx+18, cy-8)], col)
        c.line([(cx-15, cy-8), (cx-6, cy-8), (cx+6, cy+8), (cx+10, cy+8)], col, 2.4); c.poly([(cx+8, cy+2), (cx+8, cy+14), (cx+18, cy+8)], col)
    elif kind == "dots":
        for dx in (-10, 0, 10): c.ell(cx+dx, cy, 3.4, g)

def skew(box, k=18): x0, y0, x1, y1 = box; return [(x0+k, y0), (x1, y0), (x1-k, y1), (x0, y1)]

def hazard(c, box, p):
    x0, y0, x1, y1 = box
    m = c.mask(lambda d: [d.polygon([((x+j)*S, y0*S), ((x+j+10)*S, y0*S), ((x+j+10-(y1-y0))*S, y1*S), ((x+j-(y1-y0))*S, y1*S)], fill=255) for j in (0,) for x in range(int(x0), int(x1)+20, 22)])
    clip = c.mask(lambda d: d.rectangle([x0*S, y0*S, x1*S, y1*S], fill=255))
    from PIL import ImageChops
    c.paint(ImageChops.multiply(m, clip), p["mag"], 0.9)

def synth_bg(p):
    c = Cv(p["bg"])
    top, bot = np.array(fc("0F0B22"), float), np.array(fc("2D1840"), float)
    t = np.clip(np.linspace(0, 1, H*S)[:, None, None]*1.2, 0, 1)
    arr = (top*(1-t) + bot*t)*np.ones((H*S, W*S, 3))
    c.im = Image.fromarray(arr.astype(np.uint8))
    # horizon sun + perspective grid in the lower third (kept dim)
    c.ell(240, 690, 150, fc("5A2458"), 0.55)
    m = c.mask(lambda d: d.rectangle([0, 0, W*S, 690*S], fill=255)); inv = Image.eval(m, lambda v: 255-v)
    c.paint(c.mask(lambda d: [d.rectangle([0, (700+i*i*1.6)*S, W*S, (700+i*i*1.6+1.5)*S], fill=255) for i in range(1, 8)]), p["mag"], 0.22)
    for k in range(-8, 9):
        c.paint(c.mask(lambda d: d.line([(240*S, 700*S), ((240+k*60)*S, 810*S)], fill=255, width=S)), p["mag"], 0.2)
    return c
