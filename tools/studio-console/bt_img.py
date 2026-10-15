"""Studio images: every static thing is baked into two backdrops; the live parts are small sprites cut from the same renders."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import kit
from parts import *
from dirF import track, leds
from dirD import led_col
from menus import icon, ITEMS
import bt_fonts
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np

AM = AMB                      # (255,176,56) amber LCD
TRAY = (14, 15, 14); BASE = (96, 106, 98); LCDC = (26, 20, 12); PAN = (52, 58, 54); LEDPAN = (24, 26, 24)
GLOW = (60, 235, 90)
CELLX, CELLY = 14, 72         # list viewport origin (tiles: 2 x 5 cells of 226x124; rows: cells of 452x76)

def canvas(w, h, base):
    ow, oh = kit.W, kit.H; kit.W, kit.H = w, h
    try: return Cv(base)
    finally: kit.W, kit.H = ow, oh
def down(cv): return cv.im.resize((cv.im.width // SS, cv.im.height // SS), Image.LANCZOS)
def save(im, path): im.convert("RGB").save(path, "BMP")
def stack(frames): 
    w, h = frames[0].size; out = Image.new("RGB", (w, h * len(frames)))
    for i, f in enumerate(frames): out.paste(f, (0, i * h))
    return out

# ---------- glyph blitting for baked ghost digits (same bitmaps as the .fnt, so unlit segments line up exactly) ----------
def blit(im, x, y, glyphs, text, col):
    px = im.load()
    for ch in text:
        w, a = glyphs[ord(ch)]
        ys, xs = np.nonzero(a)
        for yy, xx in zip(ys, xs): px[x + xx + 0, y + yy] = col
        x += w
    return x
def text_w(glyphs, text): return sum(glyphs[ord(c)][0] for c in text)

# ======================= menus =======================
def header_frame(cv):
    cv.brushed([0, 0, 480, 800], BASE, amt=4, seed=7)
    cv.shadow([10, 8, 470, 58], 8, 4, (0, 3), 150)
    cv.rect([10, 8, 470, 58], fill=(14, 14, 12), r=8); cv.rect([10, 8, 470, 58], outline=(70, 68, 60), w=2, r=8); cv.rect([15, 13, 465, 53], fill=LCDC, r=5)
    cv.line([(262, 18), (262, 48)], (70, 56, 36), 1.2); cv.line([(358, 18), (358, 48)], (70, 56, 36), 1.2)
BARCOLS = [(255, 60, 40), (255, 170, 30), (255, 170, 30)] + [(70, 230, 80)] * 7
def footer_frame(cv):
    cv.shadow([10, 704, 470, 790], 8, 4, (0, 3), 150)
    cv.rect([10, 704, 470, 790], fill=(44, 48, 46), r=8); cv.rect([10, 704, 470, 790], outline=(18, 20, 18), w=1.5, r=8)
    cv.rect([20, 712, 340, 760], fill=(14, 12, 8), r=5); cv.rect([20, 712, 340, 760], outline=(70, 68, 60), w=1.6, r=5); cv.rect([24, 716, 336, 756], fill=LCDC, r=3)
    cv.rect([350, 712, 460, 760], fill=(14, 12, 8), r=5); cv.rect([350, 712, 460, 760], outline=(70, 68, 60), w=1.6, r=5); cv.rect([354, 716, 456, 756], fill=LCDC, r=3)
    track(cv, (362, 748), "ELAPSED", 8, (200, 190, 160), "lm", 1.2)
    cv.rect([20, 770, 460, 777], fill=(6, 6, 6), r=3.5)
    for sx, sy in ((18, 712), (462, 712), (18, 782), (462, 782)): cv.screw(sx, sy, 3, (130, 128, 120), sx / 200)

def pad(cv, x, y, sel, glow=GLOW, w=226, h=124, ins=(11, 9), blur=4, lamp=True, box=None, plate=None):
    px0, py0, px1, py1 = (x + box[0], y + box[1], x + box[2], y + box[3]) if box else (x + ins[0], y + ins[1], x + w - ins[0], y + h - ins[1])
    if sel:
        m = Image.new("L", cv.im.size, 0); ImageDraw.Draw(m).rounded_rectangle([S(px0), S(py0), S(px1), S(py1)], radius=S(12), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(S(blur)))
        cv.im.paste(Image.new("RGB", cv.im.size, c3(mixc((0, 0, 0), glow, .75))), (0, 0), m.point(lambda v: int(v * .85))); cv.d = ImageDraw.Draw(cv.im)
    top = (58, 62, 66) if not sel else c3(mixc((58, 62, 66), glow, .30)); bot = (22, 24, 27) if not sel else c3(mixc((22, 24, 27), glow, .22))
    rr = 11 if h > 100 else 9
    cv.grad([px0, py0, px1, py1], top, bot, r=rr)
    cv.grad([px0 + 5, py0 + 5, px1 - 5, py1 - 5], c3(mixc(bot, (0, 0, 0), .15)), c3(mixc(top, (0, 0, 0), .35)), r=rr - 3)
    rim = glow if sel else (150, 160, 168)
    cv.rect([px0, py0, px1, py1], outline=c3(rim) if sel else c3(mixc((38, 42, 46), rim, .22)), w=3.2 if sel else 2.2, r=rr)
    if sel: cv.rect([px0 + 3.5, py0 + 3.5, px1 - 3.5, py1 - 3.5], outline=c3(mixc(glow, (255, 255, 255), .45)), w=1.2, r=rr - 3)
    gl = Image.new("L", cv.im.size, 0)
    ImageDraw.Draw(gl).rounded_rectangle([S(px0 + 8), S(py0 + 5), S(px1 - 8), S(py0 + (17 if h > 100 else 13))], radius=S(5), fill=46 if sel else 34)
    gl = gl.filter(ImageFilter.GaussianBlur(S(2.2))); cv.im.paste(Image.new("RGB", cv.im.size, (255, 255, 255)), (0, 0), gl); cv.d = ImageDraw.Draw(cv.im)
    if plate:     # recessed label slot: exactly the area the text viewport clears, so text sits on a clean flat plate
        a, b, c, d = plate; cv.rect([x + a - 1, y + b - 1, x + c + 1, y + d + 1], fill=(40, 44, 46)); cv.rect([x + a, y + b, x + c, y + d], fill=TRAY)
    if lamp: cv.led(px1 - (14 if h > 100 else 20), py0 + 14 if h > 100 else (py0 + py1) / 2, 3.6 if h > 100 else 4.5, glow if sel else (60, 60, 60), on=sel)
    return bot

TILEPLATE = (13, 87, 213, 111); ROWPLATE = (26, 22, 396, 54)
ICONBOX = (83, 19, 143, 75)   # 60 x 56 around the icon centre (113,47)
NAMES = ["Recent Bookmarks", "Files", "Database", "Now Playing", "Settings", "Playlists", "Bluetooth", "Plugins", "System", "Shortcuts"]
def tile_sprites():
    pads, ics = [], {False: [], True: []}
    for sel in (False, True):
        cv = canvas(226, 124, TRAY); bot = pad(cv, 0, 0, sel, plate=TILEPLATE); pads.append(down(cv))
        for k, kind in [(n, kd) for n, kd in ITEMS] + [("gear", "gear")]:
            cv = canvas(226, 124, TRAY); bot = pad(cv, 0, 0, sel, plate=TILEPLATE)
            icon(cv, kind, 113, 47, 50, c3((240, 255, 244) if sel else (196, 202, 206)), c3(bot))
            ics[sel].append(down(cv).crop(ICONBOX))
    return stack(pads), stack(ics[False]), stack(ics[True])
def row_sprites():
    fr = []
    for sel in (False, True):
        cv = canvas(452, 76, TRAY); pad(cv, 0, 0, sel, w=452, h=76, box=(4, 5, 424, 71), blur=3, plate=ROWPLATE); fr.append(down(cv))
    return stack(fr)
def thumb():
    cv = canvas(14, 64, TRAY); cv.grad([0, 0, 14, 64], (150, 158, 164), (74, 80, 86), r=6); cv.rect([0, 0, 14, 64], outline=(30, 32, 34), w=1.2, r=6)
    cv.rect([5, 26, 9, 38], fill=(40, 44, 46), r=1); return down(cv)
def menu_bg():
    cv = Cv(BASE); header_frame(cv); footer_frame(cv)
    cv.rect([10, 66, 470, 696], fill=TRAY, r=8); cv.rect([10, 66, 470, 696], outline=(6, 6, 6), w=1.5, r=8)
    for i, col in enumerate(BARCOLS): x = 366 + i * 3.6; cv.rect([x, 22, x + 2.6, 44], fill=c3(mixc(col, (0, 0, 0), .8)), r=1)
    return down(cv)
def header_bars():
    cv = canvas(36, 22, LCDC)
    for i, col in enumerate(BARCOLS): x = i * 3.6; cv.rect([x, 0, x + 2.6, 22], fill=c3(col), r=1)
    return down(cv)
def footer_fill():
    cv = canvas(440, 7, (6, 6, 6)); cv.grad([0, 0, 440, 7], (255, 176, 80), (232, 120, 24), r=3.5); return down(cv)

# ======================= playback screen =======================
SEG = {}
def segf(n):
    if n not in SEG: SEG[n] = bt_fonts.seg7_glyphs(n)
    return SEG[n]
SEG_LAY = {  # name: (font size, x, top y, ghost text)   (live text is right-aligned inside the ghost's rectangle, except the clock which is left-aligned)
    "clock": (20, 280, 25, "88:88"), "elap": (14, 32, 443, "88:88"), "rem": (14, 390, 443, "-88:88"), "batt": (13, 410, 40, "888")}
def seg_rect(name):
    n, x, y, g = SEG_LAY[name]; H, asc, gl = segf(n); return x, y, text_w(gl, g), H
def vtrack(cv, cx, y0, y1):
    cv.rect([cx - 5, y0, cx + 5, y1], fill=(8, 8, 8), r=5); cv.rect([cx - 4, y0 + 1, cx - 1, y1 - 1], fill=(0, 0, 0), r=2)
    for i in range(11):
        y = y0 + 12 + (y1 - y0 - 24) * i / 10
        cv.line([(cx - 26, y), (cx - (17 if i % 5 else 14), y)], CREAM, 1.3 if i % 5 else 1.8); cv.line([(cx + 17 if i % 5 else cx + 14, y), (cx + 26, y)], CREAM, 1.3 if i % 5 else 1.8)
def vknob(cv, cx, ty, cap=(214, 96, 52)):
    cv.grad([cx - 22, ty - 15, cx + 22, ty + 15], c3(mixc(cap, (255, 255, 255), .28)), c3(mixc(cap, (0, 0, 0), .24)), r=4)
    cv.rect([cx - 22, ty - 15, cx + 22, ty + 15], outline=c3(mixc(cap, (0, 0, 0), .55)), w=1.1, r=4)
    for dx in (-13, -8, 8, 13): cv.line([(cx + dx, ty - 11), (cx + dx, ty + 11)], c3(mixc(cap, (0, 0, 0), .3)), 1.2)
    cv.line([(cx - 18, ty), (cx + 18, ty)], (250, 240, 220), 2.2)
def htrack(cv, x0, x1, y):
    cv.rect([x0, y - 5, x1, y + 5], fill=(10, 10, 10), r=5); cv.rect([x0 + 1, y - 5, x1 - 1, y - 1], fill=(0, 0, 0), r=3)
    cv.line([(x0 + 6, y + 6.6), (x1 - 6, y + 6.6)], (70, 70, 66), 1)
    for i in range(11):
        x = x0 + 8 + (x1 - x0 - 16) * i / 10; cv.line([(x, y - 14), (x, y - (22 if i % 5 == 0 else 18))], CREAM, 1.3)
def hknob(cv, cx, y, cap=CREAM):
    cv.grad([cx - 15, y - 21, cx + 15, y + 21], c3(mixc(cap, (255, 255, 255), .25)), c3(mixc(cap, (0, 0, 0), .22)), r=4)
    cv.rect([cx - 15, y - 21, cx + 15, y + 21], outline=c3(mixc(cap, (0, 0, 0), .55)), w=1.1, r=4)
    for dy in (-12, -7, 7, 12): cv.line([(cx - 11, y + dy), (cx + 11, y + dy)], c3(mixc(cap, (0, 0, 0), .3)), 1.2)
    cv.line([(cx, y - 18), (cx, y + 18)], (180, 40, 30), 2.2)
def placeholder(cv, b):
    x0, y0, x1, y1 = b; cv.rect(b, fill=(22, 24, 22)); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for sx in (-48, 48):
        cv.ell(cx + sx, cy - 6, 36, outline=(70, 66, 56), w=3); cv.ell(cx + sx, cy - 6, 10, fill=(70, 66, 56))
        for k in range(3):
            a = k * 2 * math.pi / 3 + .5; cv.line([(cx + sx + math.cos(a) * 12, cy - 6 + math.sin(a) * 12), (cx + sx + math.cos(a) * 33, cy - 6 + math.sin(a) * 33)], (70, 66, 56), 3)
    cv.rect([x0 + 20, y1 - 52, x1 - 20, y1 - 22], outline=(70, 66, 56), w=2.5, r=4); cv.line([(x0 + 40, y1 - 37), (x1 - 40, y1 - 37)], (70, 66, 56), 2.5)
TKEYS = [("prev", (206, 200, 178), (30, 28, 24)), ("rew", (206, 200, 178), (30, 28, 24)), ("none", (200, 56, 44), (250, 240, 228)), ("ff", (206, 200, 178), (30, 28, 24)), ("next", (206, 200, 178), (30, 28, 24))]
KW = 70; KGAP = (420 - 5 * KW) / 4
def key_rect(i): x = 30 + i * (KW + KGAP); return [x - (6 if i == 2 else 0), 556, x + KW + (6 if i == 2 else 0), 668]
TOG = {"shuf": [30, 712, 100, 758], "rept": [180, 712, 250, 758]}
OFFG = (128, 112, 84); ONG = (255, 176, 56)
def toggle(cv, kind, state, txt=None):
    b = TOG[kind]; key(cv, b, (60, 64, 62), kind if txt is None else "none", ONG if state else OFFG, r=5)
    if txt: cv.text(((b[0] + b[2]) / 2, (b[1] + b[3]) / 2), txt, F("Liberation Sans", 15, "Bold"), c3(ONG), "mm")
    if state is not None: cv.led(b[0] + 62, 718, 2.8, ONG, on=bool(state))
def wps_static(cv, with_dynamic_defaults=False):
    L, R = 12, 468
    cv.brushed([0, 0, 480, 800], BASE, amt=4, seed=7)
    # ---- left column: art (from the top of the screen), song display, info plates ----
    cv.rect([L, 12, 260, 258], fill=(34, 36, 34), r=8); cv.rect([L, 12, 260, 258], outline=(16, 16, 16), w=1.5, r=8)
    cv.shadow([20, 20, 252, 250], 4, 5, (0, 3), 190); cv.rect([18, 20, 254, 250], fill=(16, 16, 16), r=4); placeholder(cv, [26, 28, 246, 248]); cv.rect([26, 28, 246, 248], outline=(90, 88, 80), w=1.2)
    cv.shadow([L, 266, 260, 388], 8, 4, (0, 3), 150)
    cv.rect([L, 266, 260, 388], fill=(14, 14, 12), r=8); cv.rect([L, 266, 260, 388], outline=(70, 68, 60), w=2, r=8); cv.rect([18, 271, 254, 383], fill=LCDC, r=5)
    for t, x, w in (("FLAC", 12, 62), ("1419k", 79, 70), ("1756/3471", 154, 106)):
        cv.rect([x, 394, x + w, 422], fill=(30, 32, 30), r=4); cv.rect([x, 394, x + w, 422], outline=(18, 18, 18), w=1, r=4)
    # ---- right column: two separate LCD modules (clock, battery) above the PEAK and LEVEL panels ----
    for x0, x1 in ((268, 360), (366, 468)):
        cv.shadow([x0, 12, x1, 62], 8, 4, (0, 3), 150)
        cv.rect([x0, 12, x1, 62], fill=(14, 14, 12), r=8); cv.rect([x0, 12, x1, 62], outline=(70, 68, 60), w=2, r=8); cv.rect([x0 + 5, 17, x1 - 5, 57], fill=LCDC, r=5)
    cv.rect([275, 22, 353, 52], fill=(8, 8, 8), r=4); cv.rect([275, 22, 353, 52], outline=(52, 44, 30), w=1.2, r=4)
    for i, col in enumerate(BARCOLS):
        x = 376 + i * 8.2; cv.rect([x, 22, x + 5.8, 34], fill=c3(mixc(col, (0, 0, 0), .8)), r=1.8)
    track(cv, (378, 48), "BATT", 8, (226, 218, 196), "lm", 1.0); track(cv, (458, 48), "%", 10, (220, 214, 196), "rm", 0)
    cv.rect([268, 68, 360, 422], fill=LEDPAN, r=6); cv.rect([268, 68, 360, 422], outline=(12, 12, 12), w=1.2, r=6)
    track(cv, (314, 82), "PEAK", 10, (150, 146, 132)); leds(cv, 292, 380, 108, 19, 0); leds(cv, 336, 380, 108, 19, 0)
    track(cv, (292, 404), "L", 11, (210, 206, 188)); track(cv, (336, 404), "R", 11, (210, 206, 188))
    cv.rect([366, 68, 468, 422], fill=PAN, r=6); cv.rect([366, 68, 468, 422], outline=(16, 18, 16), w=1.2, r=6)
    track(cv, (417, 82), "LEVEL", 10, (210, 206, 188)); vtrack(cv, 417, 98, 386)
    cv.rect([L, 430, R, 518], fill=PAN, r=8); cv.rect([L, 430, R, 518], outline=(20, 22, 20), w=1.5, r=8)
    for b in ([26, 440, 96, 464], [384, 440, 454, 464]): cv.rect(b, fill=(14, 12, 8), r=3); cv.rect(b, outline=(70, 68, 60), w=1.2, r=3)
    track(cv, (104, 452), "ELAPSED", 8, (210, 206, 188), "lm"); track(cv, (376, 452), "REMAIN", 8, (210, 206, 188), "rm")
    htrack(cv, 26, 454, 496)
    for sx, sy in ((20, 438), (460, 438), (20, 510), (460, 510)): cv.screw(sx, sy, 3.6, (130, 128, 120), .8 + sy / 400)
    cv.rect([L, 528, R, 790], fill=(44, 48, 46), r=8); cv.rect([L, 528, R, 790], outline=(18, 20, 18), w=1.5, r=8)
    for i, (k, face, g) in enumerate(TKEYS):
        key(cv, key_rect(i), face, k, g); x = 30 + i * (KW + KGAP)
        track(cv, (x + KW / 2, 686), ["PREV", "REW", "PLAY/PAUSE", "FF", "NEXT"][i], 9, (200, 196, 176))
    cv.led(240, 543, 3.6, (255, 60, 40), on=False)
    for kind, t in (("shuf", "SHUFFLE"), ("rept", "REPEAT")):
        toggle(cv, kind, None, "") ; track(cv, (TOG[kind][2] + 10, 735), t, 9, (190, 186, 170), "lm")
    cv.knob(404, 735, 21, ang=35); track(cv, (404, 770), "MENU", 8, (190, 186, 170)); cv.led(444, 720, 2.8, (80, 220, 90))
    for sx, sy in ((20, 536), (460, 536), (20, 782), (460, 782)): cv.screw(sx, sy, 3.6, (130, 128, 120), 1.1 + sx / 300)
def wps_bg():
    cv = Cv(BASE); wps_static(cv); im = down(cv)
    for name in SEG_LAY:
        n, x, y, g = SEG_LAY[name]; H, asc, gl = segf(n); blit(im, x, y, gl, g, c3(mixc((12, 8, 4), AM, .16)))
    return im
def led_round(cv, cx, cy, r, col):
    """a lit LED that stays round: a tight halo (never reaches the neighbouring LED), a solid body and a small highlight"""
    g = Image.new("RGB", cv.im.size, (0, 0, 0)); ImageDraw.Draw(g).ellipse([S(cx - r * 1.45), S(cy - r * 1.45), S(cx + r * 1.45), S(cy + r * 1.45)], fill=c3(mixc((0, 0, 0), col, .45)))
    g = g.filter(ImageFilter.GaussianBlur(S(r * .35))); cv.im = ImageChops.add(cv.im, g); cv.d = ImageDraw.Draw(cv.im)
    cv.ell(cx, cy, r, fill=c3(col)); cv.ell(cx - r * .3, cy - r * .35, r * .35, fill=c3(mixc(col, (255, 255, 255), .7)))
def wps_sprites():
    out = {}
    cv = canvas(36, 296, LEDPAN)
    for i in range(19): led_round(cv, 18, 283 - i * (272 / 18), 5.2, led_col(i, 19))
    out["ml"] = down(cv).crop((0, 1, 36, 295))   # canvas y = absolute y - 97; shown in a 36 x 294 viewport at y 98
    pass
    cv = canvas(82, 12, (4, 4, 4))
    for i, col in enumerate(BARCOLS):
        x = i * 8.2; cv.rect([x, 0, x + 5.8, 12], fill=c3(col), r=1.8); cv.rect([x + 1, 1.2, x + 2.6, 10.8], fill=c3(mixc(col, (255, 255, 255), .45)), r=0.8)
    out["bf"] = down(cv)
    cv = canvas(44, 30, PAN); vknob(cv, 22, 15); out["vk"] = down(cv)
    cv = canvas(30, 42, PAN); hknob(cv, 15, 21); out["hk"] = down(cv)
    fr = []
    for k in ("play", "pause"):                     # play/pause glyph on the red key, cut from a real render of that key
        cv = Cv((44, 48, 46)); i = 2; key(cv, key_rect(i), TKEYS[2][1], k, TKEYS[2][2]); fr.append(down(cv).crop((216, 590, 264, 634)))
    out["pp"] = stack(fr)
    sh, rp = [], []
    for st in (False, True):
        cv = Cv((44, 48, 46)); toggle(cv, "shuf", st); sh.append(down(cv).crop(tuple(TOG["shuf"])))
    for st, txt in ((False, None), (True, None), (True, "1"), (True, None), (True, "A-B")):
        cv = Cv((44, 48, 46)); toggle(cv, "rept", st, txt) if txt is None else toggle(cv, "rept", st, txt); rp.append(down(cv).crop(tuple(TOG["rept"])))
    out["sh"], out["rp"] = stack(sh), stack(rp)
    fr = []
    for on in (False, True):                        # play lamp above the red key: lit while playing
        cv = Cv((44, 48, 46))
        if on: led_round(cv, 240, 543, 3.6, (255, 60, 40))
        else: cv.led(240, 543, 3.6, (255, 60, 40), on=False)
        fr.append(down(cv).crop((231, 536, 249, 550)))
    out["lp"] = stack(fr)
    return out
