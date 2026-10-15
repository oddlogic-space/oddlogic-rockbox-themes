from parts import *
import parts, dirF
from dirD import led_col, vfader
from dirF import track, leds, wheels
from kit import SS
import subprocess
import os
SEG = os.path.join(os.environ.get("DSEG_DIR", os.path.expanduser("~/fonts/fonts-DSEG_v046")), "DSEG7-Classic", "DSEG7Classic-Bold.ttf")
from PIL import ImageFont
_sg = {}
def SG(size):
    if size not in _sg: _sg[size] = ImageFont.truetype(SEG, int(size * SS))
    return _sg[size]
_cj = {}
def CJ(size):
    if size not in _cj:
        p = subprocess.run(["fc-match", "-f", "%{file}|%{index}", "Noto Sans CJK JP:style=Bold"], capture_output=True, text=True).stdout.split("|")
        _cj[size] = ImageFont.truetype(p[0], int(size * SS), index=int(p[1]))
    return _cj[size]
def seg(cv, xy, ghost, text, size, col, anchor="lm"):
    cv.text(xy, ghost, SG(size), c3(mixc((12, 8, 4), col, .13)), anchor); cv.text(xy, text, SG(size), col, anchor)
def mixed(cv, xy, t, size, col, anchor="lm"):
    """typewriter Latin, Noto CJK for everything else (what the final bitmap font does)"""
    x = xy[0]
    fl = F("FreeMono", size, "Bold"); fc = CJ(size)
    for ch in t:
        f = fl if ord(ch) < 0x2000 else fc
        cv.text((x, xy[1]), ch, f, col, "l" + anchor[1]); x += f.getlength(ch) / SS
def draw(cjk=False):
    cv = Cv((96, 106, 98)); cv.brushed([0, 0, 480, 800], (96, 106, 98), amt=4, seed=7)
    MONO = "FreeMono"; AM = AMB
    cv.rect([L, 12, R, 262], fill=(34, 36, 34), r=8); cv.rect([L, 12, R, 262], outline=(16, 16, 16), w=1.5, r=8)
    cv.shadow([22, 22, 242, 252], 4, 5, (0, 3), 190); cv.rect([20, 22, 244, 252], fill=(16, 16, 16), r=4); parts.paste_cover(cv, [26, 30, 238, 242]); cv.rect([26, 30, 238, 242], outline=(90, 88, 80), w=1.2)
    cv.rect([254, 22, 346, 252], fill=(24, 26, 24), r=6); cv.rect([254, 22, 346, 252], outline=(12, 12, 12), w=1.2, r=6)
    track(cv, (300, 36), "PEAK", 10, (150, 146, 132)); leds(cv, 282, 222, 56, 13, 9); leds(cv, 318, 222, 56, 13, 7)
    track(cv, (282, 240), "L", 11, (210, 206, 188)); track(cv, (318, 240), "R", 11, (210, 206, 188))
    cv.rect([356, 22, 458, 252], fill=(52, 58, 54), r=6); cv.rect([356, 22, 458, 252], outline=(16, 18, 16), w=1.2, r=6)
    track(cv, (407, 36), "LEVEL", 10, (210, 206, 188)); vfader(cv, 407, 52, 218, .62); cv.text((407, 238), "-18 dB", F(MONO, 14, "Bold"), AM, "mm")
    for sx, sy in ((20, 18), (460, 18), (20, 256), (460, 256)): cv.screw(sx, sy, 3.6, (130, 128, 120), .3 + sx / 300)
    # display
    cv.shadow([L, 274, R, 376], 8, 4, (0, 3), 150)
    cv.rect([L, 274, R, 376], fill=(14, 14, 12), r=8); cv.rect([L, 274, R, 376], outline=(70, 68, 60), w=2, r=8); cv.rect([19, 280, 461, 370], fill=(26, 20, 12), r=5)
    T, A, B = ("夜明けのスキャット", "星野 ミドリ", "深夜放送") if cjk else ("Song Title", "Artist Name", "Album Name")
    mixed(cv, (32, 306), T, 34, AM); mixed(cv, (32, 337), A, 20, c3(mixc(AM, (0, 0, 0), .25))); mixed(cv, (32, 359), B, 16, c3(mixc(AM, (0, 0, 0), .5)))
    # info row
    for t, x, w in (("FLAC", 22, 60), ("1419k", 88, 70)):
        cv.rect([x, 386, x + w, 420], fill=(30, 32, 30), r=4); cv.rect([x, 386, x + w, 420], outline=(18, 18, 18), w=1, r=4)
        cv.text((x + w / 2, 403), t, F(MONO, 15, "Bold"), (210, 204, 182), "mm")
    track(cv, (168, 392), "TRACK", 7, (210, 206, 188), "lm")
    x1 = wheels(cv, 168, 398, "1756", 15, 22, 18); cv.text((x1 + 8, 410), "/3471", F(MONO, 14, "Bold"), (210, 204, 182), "lm")
    cv.rect([300, 384, 458, 422], fill=(14, 12, 8), r=4); cv.rect([300, 384, 458, 422], outline=(70, 68, 60), w=1.6, r=4)
    seg(cv, (310, 403), "88:88", "12:09", 23, AM); seg(cv, (400, 403), "888", " 80", 15, AM); cv.text((452, 408), "%", F(MONO, 11, "Bold"), c3(mixc(AM, (0, 0, 0), .2)), "rm")
    # position
    cv.rect([L, 430, R, 528], fill=(52, 58, 54), r=8); cv.rect([L, 430, R, 528], outline=(20, 22, 20), w=1.5, r=8)
    cv.rect([26, 440, 130, 478], fill=(14, 12, 8), r=4); cv.rect([326, 440, 454, 478], fill=(14, 12, 8), r=4); cv.rect([26, 440, 130, 478], outline=(70, 68, 60), w=1.4, r=4); cv.rect([326, 440, 454, 478], outline=(70, 68, 60), w=1.4, r=4)
    seg(cv, (34, 460), "88:88", "01:24", 24, AM); seg(cv, (334, 460), "-88:88", "-02:17", 24, AM)
    track(cv, (140, 450), "ELAPSED", 8, (210, 206, 188), "lm"); track(cv, (316, 450), "REMAIN", 8, (210, 206, 188), "rm")
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
from dirF import L, R
if __name__ == "__main__":
    draw().out("G.png"); draw(True).out("G_cjk.png")
