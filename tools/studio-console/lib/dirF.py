from parts import *
import parts
from dirD import led_col, vfader
L, R = 12, 468
def track(cv, xy, t, size=9, col=(200, 196, 176), anchor="mm", sp=1.4, style="Bold", fam="Liberation Sans"):
    f = F(fam, size, style); ws = [f.getlength(ch) / SS for ch in t]; tot = sum(ws) + sp * (len(t) - 1)
    x = xy[0] - (tot / 2 if anchor[0] == "m" else tot if anchor[0] == "r" else 0)
    for ch, w in zip(t, ws):
        cv.text((x, xy[1]), ch, f, col, "l" + anchor[1]); x += w + sp
def leds(cv, cx, yb, yt, n, lit, r=5.2):
    step = (yb - yt) / (n - 1)
    for i in range(n): cv.led(cx, yb - i * step, r, led_col(i, n), on=i < lit)
def wheels(cv, x, y, text, cw, chh, size):
    """mechanical counter: one wheel per digit, ':' as a small plate"""
    xx = x; spans = []
    for ch in text:
        if ch == ":":
            cv.rect([xx, y, xx + cw * .5, y + chh], fill=(14, 14, 14)); cv.ell(xx + cw * .25, y + chh * .36, 1.8, fill=(220, 214, 196)); cv.ell(xx + cw * .25, y + chh * .66, 1.8, fill=(220, 214, 196)); xx += cw * .5; continue
        cv.grad([xx, y, xx + cw, y + chh / 2], (10, 10, 10), (58, 58, 56), r=0); cv.grad([xx, y + chh / 2, xx + cw, y + chh], (58, 58, 56), (6, 6, 6), r=0)
        cv.rect([xx, y + chh / 2 - .5, xx + cw, y + chh / 2 + .5], fill=(0, 0, 0))
        cv.text((xx + cw / 2, y + chh / 2 + 1), ch, F("Liberation Sans", size, "Bold"), (240, 236, 220), "mm")
        cv.rect([xx, y, xx + .8, y + chh], fill=(0, 0, 0)); xx += cw
    cv.rect([x - 2.5, y - 2.5, xx + 2.5, y + chh + 2.5], outline=(140, 138, 130), w=2, r=3)
    cv.rect([x - .5, y - .5, xx + .5, y + chh + .5], outline=(0, 0, 0), w=1)
    return xx
def draw():
    cv = Cv((96, 106, 98)); cv.brushed([0, 0, 480, 800], (96, 106, 98), amt=4, seed=7)
    MONO = "FreeMono"
    # top bay
    cv.rect([L, 12, R, 262], fill=(34, 36, 34), r=8); cv.rect([L, 12, R, 262], outline=(16, 16, 16), w=1.5, r=8)
    cv.shadow([22, 22, 242, 252], 4, 5, (0, 3), 190); cv.rect([20, 22, 244, 252], fill=(16, 16, 16), r=4); parts.paste_cover(cv, [26, 30, 238, 242]); cv.rect([26, 30, 238, 242], outline=(90, 88, 80), w=1.2)
    cv.rect([254, 22, 346, 252], fill=(24, 26, 24), r=6); cv.rect([254, 22, 346, 252], outline=(12, 12, 12), w=1.2, r=6)
    track(cv, (300, 36), "PEAK", 10, (150, 146, 132))
    leds(cv, 282, 222, 56, 13, 9); leds(cv, 318, 222, 56, 13, 7)
    track(cv, (282, 240), "L", 11, (210, 206, 188)); track(cv, (318, 240), "R", 11, (210, 206, 188))
    cv.rect([356, 22, 458, 252], fill=(52, 58, 54), r=6); cv.rect([356, 22, 458, 252], outline=(16, 18, 16), w=1.2, r=6)
    track(cv, (407, 36), "LEVEL", 10, (210, 206, 188)); vfader(cv, 407, 52, 218, .62)
    cv.text((407, 238), "-18 dB", F(MONO, 14, "Bold"), (255, 176, 56), "mm")
    for sx, sy in ((20, 18), (460, 18), (20, 256), (460, 256)): cv.screw(sx, sy, 3.6, (130, 128, 120), .3 + sx / 300)
    # display
    cv.shadow([L, 274, R, 376], 8, 4, (0, 3), 150)
    cv.rect([L, 274, R, 376], fill=(14, 14, 12), r=8); cv.rect([L, 274, R, 376], outline=(70, 68, 60), w=2, r=8); cv.rect([19, 280, 461, 370], fill=(26, 20, 12), r=5)
    cv.text((32, 306), "Song Title", F(MONO, 34, "Bold"), AMB, "lm")
    cv.text((32, 337), "Artist Name", F(MONO, 20, "Bold"), c3(mixc(AMB, (0, 0, 0), .25)), "lm")
    cv.text((32, 359), "Album Name", F(MONO, 16, "Bold"), c3(mixc(AMB, (0, 0, 0), .5)), "lm")
    cv.text((450, 359), "07/12", F(MONO, 16, "Bold"), c3(mixc(AMB, (0, 0, 0), .25)), "rm")
    # info row: plates + clock/battery counters
    for t, x, w in (("FLAC", 22, 64), ("1419k", 92, 72), ("1756/3471", 170, 104)):
        cv.rect([x, 386, x + w, 420], fill=(30, 32, 30), r=4); cv.rect([x, 386, x + w, 420], outline=(18, 18, 18), w=1, r=4)
        cv.text((x + w / 2, 403), t, F(MONO, 15, "Bold"), (210, 204, 182), "mm")
    cv.rect([284, 384, 458, 422], fill=(52, 58, 54), r=4)
    x1 = wheels(cv, 292, 389, "12:09", 17, 28, 22)
    x2 = wheels(cv, x1 + 12, 389, "80", 17, 28, 22)
    track(cv, (x2 + 9, 403), "%", 10, (220, 214, 196), "lm")
    # position bay with counters
    cv.rect([L, 430, R, 528], fill=(52, 58, 54), r=8); cv.rect([L, 430, R, 528], outline=(20, 22, 20), w=1.5, r=8)
    track(cv, (30, 442), "ELAPSED", 8, (210, 206, 188), "lm"); wheels(cv, 30, 450, "01:24", 20, 26, 22)
    track(cv, (450, 442), "REMAIN", 8, (210, 206, 188), "rm"); wheels(cv, 450 - 2.5 - (4 * 20 + 10) , 450, "02:17", 20, 26, 22)
    fader_h(cv, 26, 454, 506, .38)
    for sx, sy in ((20, 438), (460, 438), (20, 520), (460, 520)): cv.screw(sx, sy, 3.6, (130, 128, 120), .8 + sy / 400)
    # transport
    cv.rect([L, 538, R, 790], fill=(44, 48, 46), r=8); cv.rect([L, 538, R, 790], outline=(18, 20, 18), w=1.5, r=8)
    spec = [("prev", (206, 200, 178), (30, 28, 24)), ("rew", (206, 200, 178), (30, 28, 24)), ("pause", (200, 56, 44), (250, 240, 228)), ("ff", (206, 200, 178), (30, 28, 24)), ("next", (206, 200, 178), (30, 28, 24))]
    kw = 70; gap = (420 - 5 * kw) / 4
    for i, (k, face, g) in enumerate(spec):
        x = 30 + i * (kw + gap)
        key(cv, [x - (6 if i == 2 else 0), 564, x + kw + (6 if i == 2 else 0), 668], face, k, g)
        track(cv, (x + kw / 2, 686), ["PREV", "REW", "PLAY/PAUSE", "FF", "NEXT"][i], 9, (200, 196, 176))
    cv.led(240, 553, 3.6, (255, 90, 50))
    for i, (k, t) in enumerate((("shuf", "SHUFFLE"), ("rept", "REPEAT"))):
        x = 30 + i * 150; key(cv, [x, 712, x + 70, 758], (60, 64, 62), k, (255, 176, 56), r=5)
        track(cv, (x + 80, 735), t, 9, (190, 186, 170), "lm"); cv.led(x + 62, 718, 2.8, (255, 176, 56), on=i == 1)
    cv.knob(404, 735, 21, ang=35); track(cv, (404, 770), "MENU", 8, (190, 186, 170)); cv.led(444, 720, 2.8, (80, 220, 90))
    for sx, sy in ((20, 546), (460, 546), (20, 782), (460, 782)): cv.screw(sx, sy, 3.6, (130, 128, 120), 1.1 + sx / 300)
    return cv
if __name__ == "__main__": draw().out("F.png")
