from kit import *
CREAM = (232, 224, 200); INKD = (26, 24, 22); AMB = (255, 176, 56); RED = (210, 52, 40)
def cover(size):
    w = h = size; a = np.zeros((h, w, 3), float)
    y = np.linspace(0, 1, h)[:, None]
    a[:] = (np.array((46, 118, 190)) * (1 - y[..., None]) + np.array((190, 220, 240)) * y[..., None])
    im = Image.fromarray(a.clip(0, 255).astype("uint8")); d = ImageDraw.Draw(im)
    for i in range(7):
        d.arc([-w * .2, h * (.25 + i * .012), w * 1.2, h * (1.1 + i * .012)], 200, 340, fill=(20, 38, 90), width=max(1, int(w / 60)))
    for cx, cy, r in ((.35, .72, .2), (.55, .78, .22), (.2, .8, .16), (.7, .72, .14)):
        d.ellipse([w * (cx - r), h * (cy - r), w * (cx + r), h * (cy + r)], fill=(246, 249, 255))
    return im.filter(ImageFilter.GaussianBlur(.6))
def paste_cover(cv, b, r=0):
    x0, y0, x1, y1 = [int(v) for v in b]
    im = cover(S(x1 - x0)).resize((S(x1 - x0), S(y1 - y0)))
    cv.im.paste(im, (S(x0), S(y0))); cv.d = ImageDraw.Draw(cv.im)
def fader_h(cv, x0, x1, y, pos, cap=CREAM, label=None, scale=True, trk=(10, 10, 10)):
    cv.rect([x0, y - 5, x1, y + 5], fill=c3(trk), r=5); cv.rect([x0 + 1, y - 5, x1 - 1, y - 1], fill=(0, 0, 0), r=3)
    cv.line([(x0 + 6, y + 6.6), (x1 - 6, y + 6.6)], (70, 70, 66), 1)
    if scale:
        for i in range(11):
            x = x0 + 8 + (x1 - x0 - 16) * i / 10
            cv.line([(x, y - 14), (x, y - (22 if i % 5 == 0 else 18))], CREAM, 1.3)
    cx = x0 + 8 + (x1 - x0 - 16) * pos
    cv.shadow([cx - 15, y - 21, cx + 15, y + 21], 3, 3, (0, 3), 150)
    cv.grad([cx - 15, y - 21, cx + 15, y + 21], c3(mixc(cap, (255, 255, 255), .25)), c3(mixc(cap, (0, 0, 0), .22)), r=4)
    cv.rect([cx - 15, y - 21, cx + 15, y + 21], outline=c3(mixc(cap, (0, 0, 0), .55)), w=1.1, r=4)
    for dy in (-12, -7, 7, 12): cv.line([(cx - 11, y + dy), (cx + 11, y + dy)], c3(mixc(cap, (0, 0, 0), .3)), 1.2)
    cv.line([(cx, y - 18), (cx, y + 18)], (180, 40, 30), 2.2)
    return cx
def glyph(cv, kind, cx, cy, col, s=1.0):
    if kind == "play": cv.poly([(cx - 9 * s, cy - 12 * s), (cx - 9 * s, cy + 12 * s), (cx + 12 * s, cy)], col)
    elif kind == "pause": cv.rect([cx - 10 * s, cy - 12 * s, cx - 3 * s, cy + 12 * s], fill=col, r=1); cv.rect([cx + 3 * s, cy - 12 * s, cx + 10 * s, cy + 12 * s], fill=col, r=1)
    elif kind == "stop": cv.rect([cx - 10 * s, cy - 10 * s, cx + 10 * s, cy + 10 * s], fill=col, r=1)
    elif kind == "rew": cv.poly([(cx + 1 * s, cy - 11 * s), (cx + 1 * s, cy + 11 * s), (cx - 13 * s, cy)], col); cv.poly([(cx + 14 * s, cy - 11 * s), (cx + 14 * s, cy + 11 * s), (cx, cy)], col)
    elif kind == "ff": cv.poly([(cx - 1 * s, cy - 11 * s), (cx - 1 * s, cy + 11 * s), (cx + 13 * s, cy)], col); cv.poly([(cx - 14 * s, cy - 11 * s), (cx - 14 * s, cy + 11 * s), (cx, cy)], col)
    elif kind == "prev": cv.rect([cx - 13 * s, cy - 11 * s, cx - 9 * s, cy + 11 * s], fill=col); cv.poly([(cx + 13 * s, cy - 11 * s), (cx + 13 * s, cy + 11 * s), (cx - 7 * s, cy)], col)
    elif kind == "next": cv.rect([cx + 9 * s, cy - 11 * s, cx + 13 * s, cy + 11 * s], fill=col); cv.poly([(cx - 13 * s, cy - 11 * s), (cx - 13 * s, cy + 11 * s), (cx + 7 * s, cy)], col)
    elif kind == "rec": cv.ell(cx, cy, 11 * s, fill=col)
    elif kind == "shuf":
        cv.line([(cx - 13, cy + 8), (cx - 4, cy + 8), (cx + 4, cy - 8), (cx + 11, cy - 8)], col, 2.4); cv.line([(cx - 13, cy - 8), (cx - 4, cy - 8), (cx + 4, cy + 8), (cx + 11, cy + 8)], col, 2.4)
        cv.poly([(cx + 9, cy - 13), (cx + 15, cy - 8), (cx + 9, cy - 3)], col); cv.poly([(cx + 9, cy + 3), (cx + 15, cy + 8), (cx + 9, cy + 13)], col)
    elif kind == "rept":
        cv.line([(cx - 12, cy + 4), (cx - 12, cy - 6), (cx + 8, cy - 6)], col, 2.4); cv.line([(cx + 12, cy - 4), (cx + 12, cy + 6), (cx - 8, cy + 6)], col, 2.4)
        cv.poly([(cx + 6, cy - 12), (cx + 13, cy - 6), (cx + 6, cy)], col); cv.poly([(cx - 6, cy), (cx - 13, cy + 6), (cx - 6, cy + 12)], col)
def key(cv, b, face, kind, gcol, led=None, pressed=False, r=5):
    x0, y0, x1, y1 = b; cx = (x0 + x1) / 2
    cv.shadow(b, r, 3, (0, 3), 160 if not pressed else 60)
    if pressed: b = [x0, y0 + 3, x1, y1 + 3]; x0, y0, x1, y1 = b
    cv.grad(b, c3(mixc(face, (255, 255, 255), .28)), c3(mixc(face, (0, 0, 0), .20)), r=r)
    cv.rect(b, outline=c3(mixc(face, (0, 0, 0), .6)), w=1.2, r=r)
    cv.rect([x0 + 5, y0 + 5, x1 - 5, y1 - 5], outline=c3(mixc(face, (255, 255, 255), .18)), w=1, r=r - 1)
    glyph(cv, kind, cx, (y0 + y1) / 2, gcol)
    if led is not None: pass
def vu(cv, b, val=.35, face=(236, 226, 190), label="VU"):
    x0, y0, x1, y1 = b; w, h = x1 - x0, y1 - y0
    cv.shadow(b, 6, 4, (0, 3), 150); cv.rect(b, fill=(18, 18, 18), r=7)
    cv.rect([x0 + 5, y0 + 5, x1 - 5, y1 - 5], fill=c3(face), r=4)
    cv.grad([x0 + 5, y0 + 5, x1 - 5, y1 - 5], c3(mixc(face, (255, 255, 255), .25)), c3(mixc(face, (0, 0, 0), .12)), r=4)
    pcx, pcy = (x0 + x1) / 2, y1 - 12; R = h * .78
    a0, a1 = math.radians(-50), math.radians(50)
    for i in range(0, 41):
        t = i / 40; a = a0 + (a1 - a0) * t; major = i % 8 == 0
        r1 = R * (.86 if major else .92); r2 = R * 1.0
        col = (170, 30, 25) if t > .72 else (40, 36, 30)
        cv.line([(pcx + math.sin(a) * r1, pcy - math.cos(a) * r1), (pcx + math.sin(a) * r2, pcy - math.cos(a) * r2)], col, 1.8 if major else 1)
    cv.d.arc([S(pcx - R * .8), S(pcy - R * .8), S(pcx + R * .8), S(pcy + R * .8)], -90 + 40, -90 + 50, fill=(170, 30, 25), width=S(3))
    cv.text((x0 + w * .22, y0 + h * .55), "-20", F("DejaVu Sans", 8), (40, 36, 30), "mm")
    cv.text((x1 - w * .2, y0 + h * .55), "+3", F("DejaVu Sans", 8), (170, 30, 25), "mm")
    cv.text((pcx, y0 + h * .42), label, F("DejaVu Sans Mono", 11, "Bold"), (40, 36, 30), "mm")
    a = a0 + (a1 - a0) * val
    cv.line([(pcx, pcy), (pcx + math.sin(a) * R * .96, pcy - math.cos(a) * R * .96)], (20, 18, 16), 2)
    cv.rect([x0 + 5, y1 - 15, x1 - 5, y1 - 5], fill=(24, 22, 20)); cv.ell(pcx, pcy, 6, fill=(24, 22, 20))
def silk(cv, xy, t, size=10, col=CREAM, anchor="mm", bold=True): cv.text(xy, t, F("DejaVu Sans Mono", size, "Bold" if bold else None), col, anchor)
def status(cv, y0, y1, bg, fg, accent):
    cv.rect([14, y0, 466, y1], fill=c3(bg))
    cv.text((24, (y0 + y1) / 2), "VOL", F("DejaVu Sans Mono", 10, "Bold"), c3(mixc(fg, bg, .4)), "lm")
    cv.rect([52, (y0 + y1) / 2 - 3, 134, (y0 + y1) / 2 + 3], fill=c3(mixc(bg, (0, 0, 0), .5)), r=3); cv.rect([52, (y0 + y1) / 2 - 3, 98, (y0 + y1) / 2 + 3], fill=c3(accent), r=3)
    cv.text((240, (y0 + y1) / 2), "12:09", F("DejaVu Sans Mono", 20, "Bold"), c3(fg), "mm")
    cv.text((436, (y0 + y1) / 2), "80%", F("DejaVu Sans Mono", 15, "Bold"), c3(fg), "rm")
    bx = 446; cv.rect([bx - 2, (y0 + y1) / 2 - 6, bx + 14, (y0 + y1) / 2 + 6], outline=c3(fg), w=1.4, r=2); cv.rect([bx, (y0 + y1) / 2 - 4, bx + 10, (y0 + y1) / 2 + 4], fill=c3(accent), r=1)
