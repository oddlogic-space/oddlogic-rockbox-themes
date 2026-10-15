#!/usr/bin/env python3
"""Build Waveform Bot HUD (HiBy R1, 480x800): backdrops, images, skins and cfg.

    python3 tools/build.py            # writes into ../.rockbox
If tools/emblem.png exists it is used as the battery shape (see README, "Using your own emblem").
Needs Pillow + numpy.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from art import *

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)   # usage: build.py [outdir]  (writes <outdir>/.rockbox)
RB = os.path.join(ROOT, ".rockbox")
IMG = os.path.join(RB, "wps", "waveformbot")
os.makedirs(IMG, exist_ok=True); os.makedirs(os.path.join(RB, "themes"), exist_ok=True)
EMBLEM = os.path.join(HERE, "emblem.png")


def hexs(c): return "%02X%02X%02X" % c


def save(canvas_or_img, name):
    im = canvas_or_img if isinstance(canvas_or_img, Image.Image) else Image.fromarray(np.clip(canvas_or_img, 0, 255).astype(np.uint8), "RGB")
    im.save(os.path.join(IMG, name), format="BMP")


# =============================================================== battery shape
BW, BH, BX, BY = 36, 40, 434, 5            # battery box in the status bar (36x40 at x434, y5)
K = 8


def battery_masks():
    """Return (fill_mask, ring_mask) as L images of size BWxBH at 8x supersampling.
    fill = the shape that fills up from the bottom; ring = the outline drawn around it (baked)."""
    size = (BW * K, BH * K)
    if os.path.exists(EMBLEM):
        im = Image.open(EMBLEM).convert("RGBA")
        a = np.asarray(im, float)
        if a[..., 3].min() < 250:                                   # transparent background: use alpha
            m = a[..., 3]
        else:                                                      # opaque: treat near-white as background
            lum = a[..., :3].mean(axis=2); m = np.where(lum < 235, 255.0, 0.0)
        m = Image.fromarray(m.astype(np.uint8))
        bb = m.point(lambda v: 255 if v > 127 else 0).getbbox()
        m = m.crop(bb)
        s = min((size[0] - 4 * K) / m.width, (size[1] - 4 * K) / m.height)
        m = m.resize((max(1, int(m.width * s)), max(1, int(m.height * s))), Image.LANCZOS)
        fill = Image.new("L", size, 0); fill.paste(m, ((size[0] - m.width) // 2, (size[1] - m.height) // 2))
        fill = fill.point(lambda v: 255 if v > 127 else 0)
        ring = fill.filter(ImageFilter.MaxFilter(2 * K // 2 * 2 + 1)).point(lambda v: 255 if v > 127 else 0)
        ring = ImageChops.subtract(ring, fill)
        return fill, ring
    sh = lambda i: [(5 + i, 3 + i * .6), (31 - i, 3 + i * .6), (34 - i * 1.1, 9), (34 - i * 1.1, 29), (18, 39 - i * 1.2), (2 + i * 1.1, 29), (2 + i * 1.1, 9)]
    P = lambda pts: [(x * K, y * K) for x, y in pts]
    outer = Image.new("L", size, 0); ImageDraw.Draw(outer).polygon(P(sh(0)), fill=255)
    inner = Image.new("L", size, 0); ImageDraw.Draw(inner).polygon(P(sh(2)), fill=255)
    gaps = Image.new("L", size, 255); gd = ImageDraw.Draw(gaps)
    for y in (9.5, 16.5, 23.5, 30.5): gd.rectangle([0, (y - 0.9) * K, size[0], (y + 0.9) * K], fill=0)
    fill = ImageChops.multiply(inner, gaps)
    return fill, ImageChops.subtract(outer, inner)


FILL_M, RING_M = battery_masks()


def paste_mask(canvas, mask, col, alpha, x, y):
    m = np.asarray(mask.resize((BW, BH), Image.LANCZOS), float)[..., None] / 255.0 * alpha
    reg = canvas[y:y + BH, x:x + BW]
    reg[:] = reg * (1 - m) + np.array(col, float) * m


def bake_battery(canvas):
    paste_mask(canvas, FILL_M, STEEL, 0.28, BX, BY)            # dim silhouette
    paste_mask(canvas, RING_M, SILVER, 1.0, BX, BY)            # outline


def fill_bmp():
    m = FILL_M.resize((BW, BH), Image.LANCZOS).point(lambda v: 255 if v > 127 else 0)
    ImageOps.invert(m).convert("1").save(os.path.join(IMG, "batt_fill.bmp"), format="BMP")      # black pixels = ink


# =============================================================== shared pieces
def base():
    c = np.ones((H, W, 3)); vgrad(c, (0, 0, W, H), hx("0F1638"), hx("080C22"))
    c[::4] *= 1.03                                              # faint scan-lines
    return c


def status_bar(L):
    L.rr((0, 0, 480, 50), 0, BAR); L.rr((0, 50, 480, 52), 0, CH_D)
    L.rr((14, 12, 42, 38), 6, BODY, outline=STEEL, ow=1.4)      # woofer = volume icon
    L.ring(28, 25, 8, 2, SILVER); L.ell(28, 25, 3.4, RED)
    L.rr((50, 19, 170, 31), 3, DARK)                            # volume trough


def bezel(L, outer, border=12, cut=18):
    x0, y0, x1, y1 = outer
    po = chamfer(outer, cut); L.shadow(po, (0, 4), 4, 0.55); L.gpoly(po, CH_L, CH_D, y0, y1)
    pi = chamfer((x0 + border, y0 + border, x1 - border, y1 - border), cut - 6); L.poly(pi, DARK); L.glow(pi, CH_D, 1.4)


def plate(L, box, cut, fill, edge, corners="tl,tr,br,bl", glow=0.2):
    p = chamfer(box, cut, corners); L.poly(p, fill, 0.97); L.glow(p, edge, 1.4, glow, 3)


def silver_poly(L, pts, y0, y1):
    L.shadow(pts, (0, 3), 3, 0.5); L.gpoly(pts, hx("D8DEE9"), SILVD, y0, y1); L.glow(pts, hx("8E99AF"), 1.2)


def key_face(L, box, active=False):
    x0, y0, x1, y1 = box
    L.shadow(chamfer(box, 0), (0, 2), 2, 0.5)
    L.grect(box, 5, hx("C4D8F6") if active else hx("D8DEE9"), hx("8FA9D6") if active else SILVD)
    L.rr(box, 5, None, outline=hx("8E99AF"), ow=1)
    if active: L.rr((x0 + 10, y1 - 5, x1 - 10, y1 - 2), 1, RED)


def g_shuf(L, cx, cy, col=INK):
    L.line([(cx - 13, cy + 7), (cx - 4, cy + 7), (cx + 4, cy - 7), (cx + 9, cy - 7)], col, 2.2); L.line([(cx - 13, cy - 7), (cx - 4, cy - 7), (cx + 4, cy + 7), (cx + 9, cy + 7)], col, 2.2)
    L.poly([(cx + 8, cy - 11), (cx + 8, cy - 3), (cx + 15, cy - 7)], col); L.poly([(cx + 8, cy + 3), (cx + 8, cy + 11), (cx + 15, cy + 7)], col)


def g_rep(L, cx, cy, col=INK):
    L.line([(cx - 12, cy + 3), (cx - 12, cy - 6), (cx + 5, cy - 6)], col, 2.2); L.poly([(cx + 4, cy - 11), (cx + 4, cy - 1), (cx + 13, cy - 6)], col)
    L.line([(cx + 12, cy - 3), (cx + 12, cy + 6), (cx - 5, cy + 6)], col, 2.2); L.poly([(cx - 4, cy + 1), (cx - 4, cy + 11), (cx - 13, cy + 6)], col)


# =============================================================== menu backdrop
c = base(); L = Layer()
status_bar(L)
L.rr((0, 52, 480, 110), 0, BODY, 0.9)
pb = chamfer((12, 58, 468, 106), 14); L.gpoly(pb, CH_L, CH_D, 58, 106)
L.poly(chamfer((17, 63, 463, 101), 10), DARK)
L.rr((300, 72, 450, 76), 2, RED, 0.9); L.rr((320, 82, 450, 84), 1, RED, 0.5)       # screen lines
L.rr((0, 110, 480, 112), 0, CH_D)
L.onto(c); bake_battery(c); save(c, "bg_menu.bmp")

# =============================================================== playback backdrop
c = base(); L = Layer()
status_bar(L)
L.rr((0, 52, 480, 486), 0, BODY, 0.55)                                              # chest panel
for y in (170, 188): L.rr((0, y, 12, y + 9), 0, GOLD); L.rr((468, y, 480, y + 9), 0, GOLD)   # side bands
bezel(L, (10, 54, 470, 474))
L.ell(30, 62, 3.6, RED); L.rr((40, 59, 66, 65), 2, SILVD)                         # lamp + label plate
for x in (32, 430):
    for y0, y1, f in ladder_rects(84, 360): L.rr((x, y0, x + MW, y1), 1.5, STEEL, 0.16)
L.rr((60, 452, 420, 456), 2, RED, 0.9)                                             # screen line under the cover
# no-cover badge, centred on the 360px cover
cx0, cy0 = 240, 264
L.ell(cx0, cy0, 80, hx("0F1638")); L.ring(cx0, cy0, 79, 3, RED); L.ring(cx0, cy0, 66, 1, STEEL)
note = GOLD
L.ell(cx0 - 15, cy0 + 18, 12, note); L.rr((cx0 - 5, cy0 - 32, cx0 + 1, cy0 + 20), 0, note)
L.poly([(cx0 + 1, cy0 - 32), (cx0 + 24, cy0 - 14), (cx0 + 24, cy0 + 2), (cx0 + 1, cy0 - 16)], note)
# title plate + context key
plate(L, (12, 482, 468, 538), 14, DARK, GOLD); L.rr((30, 487, 300, 491), 2, RED, 0.9)
key_face(L, (410, 492, 456, 532))
for dx in (-10, 0, 10): L.ell(433 + dx, 512, 3, INK)
for x, w in ((24, 104), (138, 116), (264, 192)): plate(L, (x, 604, x + w, 640), 8, DARK, STEEL, "tl,br", 0.0)
L.rr((84, 660, 396, 674), 3, DARK, outline=STEEL, ow=1)                           # seek groove
# lower body: belly plate + the two big silver arrow buttons
plate(L, (8, 694, 472, 796), 16, BODY, CH_D)
for left in (True, False):
    pts = [(14, 750), (116, 706), (116, 794)] if left else [(466, 750), (364, 706), (364, 794)]
    silver_poly(L, pts, 706, 794)
    cx = 70 if left else 410; d = -1 if left else 1
    for k in (0, 1): L.poly([(cx + d * (4 + k * 13), 750), (cx + d * (-8 + k * 13), 738), (cx + d * (-8 + k * 13), 762)], INK, 0.85)
L.onto(c); bake_battery(c); save(c, "bg_wps.bmp")
BGW = c.copy()

# =============================================================== images composited over the playback backdrop
def crop(canvas, box):
    x0, y0, x1, y1 = box
    return Image.fromarray(np.clip(canvas[y0:y1, x0:x1], 0, 255).astype(np.uint8), "RGB")


def over(fn, box):
    cv = BGW.copy(); Ly = Layer(); fn(Ly); Ly.onto(cv); return crop(cv, box)


# live meters: lit ladder over the pixels behind each column (the bar reveals it from the bottom)
for name, x in (("meter_l.bmp", 32), ("meter_r.bmp", 430)):
    def fn(Ly, x=x):
        for y0, y1, f in ladder_rects(84, 360): Ly.rr((x, y0, x + MW, y1), 1.5, ladder_colour(f), 1.0)
    save(over(fn, (x, 84, x + MW, 444)), name)

# PLAY / PAUSE key (148x40 at 166,706)
for name, label in (("play.bmp", "PLAY"), ("pause.bmp", "PAUSE")):
    def fn(Ly, label=label):
        key_face(Ly, (166, 706, 314, 746)); Ly.text((240, 727), label, INK, 21)
    save(over(fn, (166, 706, 314, 746)), name)

# shuffle: off | on (70x40 at 166,754)
frames = []
for on in (False, True):
    def fn(Ly, on=on):
        key_face(Ly, (166, 754, 236, 794), on); g_shuf(Ly, 201, 773)
    frames.append(over(fn, (166, 754, 236, 794)))
sheet = Image.new("RGB", (70, 80)); [sheet.paste(f, (0, 40 * i)) for i, f in enumerate(frames)]; save(sheet, "shuffle.bmp")

# repeat: off | all | one | shuffle | A-B (70x40 at 244,754)
frames = []
for i in range(5):
    def fn(Ly, i=i):
        key_face(Ly, (244, 754, 314, 794), i > 0)
        if i == 4: Ly.text((279, 774), "A-B", INK, 17)
        elif i in (2, 3): g_rep(Ly, 270, 773); Ly.text((296, 774), "1" if i == 2 else "S", INK, 15)
        else: g_rep(Ly, 279, 773)
    frames.append(over(fn, (244, 754, 314, 794)))
sheet = Image.new("RGB", (70, 200)); [sheet.paste(f, (0, 40 * i)) for i, f in enumerate(frames)]; save(sheet, "repeat.bmp")

# progress knob: a plain silver bar (no corners to show against the groove)
k = Image.new("RGB", (8, 14), SILVER); ImageDraw.Draw(k).rectangle([0, 0, 7, 13], outline=hx("6F7597")); save(k, "pb_knob.bmp")
fill_bmp()

# =============================================================== skins
C = {k: hexs(v) for k, v in dict(ice=ICE, gold=GOLD, purp=PURP, mred=MRED, txt=TXT, silver=SILVER, sec=SEC, elapsed=ELAPSED).items()}
STATUS = f'''# ---- status bar: woofer icon + volume bar, clock, battery %, emblem battery ----
%V(50,19,120,12,-)%Vf({C['gold']})
%pv(0,0,-,-,noborder)

%V(176,7,128,36,2)%Vf({C['txt']})
%ac%cH:%cM

%V(296,7,128,36,2)%Vf({C['txt']})
%ar%bl%%

# The battery outline and its dim silhouette are baked into the backdrop (a %xd frame image would be repainted on
# every level-meter tick and wipe the live fill). Only the fill is live: purple; icy blue while charging; muted red when low.
%V({BX},{BY},{BW},{BH},-)%Vb(0F1738)%Vf({C['purp']})
%?bc<%Vf({C['ice']})|%?bl<|%Vf({C['mred']})|||>>
%bl(0,0,{BW},{BH},f)
'''

SBS = f'''# Waveform Bot HUD - base skin (menus, lists, USB screen) for HiBy R1, 480x800.
# bg_menu.bmp carries the status bar, the chrome heading plate and the volume trough.
%X(bg_menu.bmp)
%Fl(2,28-waveformbot.fnt)
%Fl(3,40-waveformbot.fnt)
%xl(f,batt_fill.bmp,0,0)

%Vi(main,0,112,-,-,1)
%Vi(ui_usb,0,152,2,2,1)
%?if(%cs,=,21)<%VI(ui_usb)|%VI(main)>

%?if(%cs,=,21)<%Vd(ut)%Vd(ub)|%?Lt<%Vd(ht)>>

# ---- clear the whole screen to the backdrop ----
%V(0,0,480,800,-)

{STATUS}
# ---- heading, on the chrome plate ----
%Vl(ht,32,55,268,52,3)%Vf({C['txt']})
%s%al%Lt

# ---- USB screen ----
%Vl(ut,32,62,260,37,2)%Vf({C['txt']})
%alUSB connected

%Vl(ub,20,230,440,190,2)%Vf({C['sec']})
%acYour player is connected
%acto a computer.
%ac
%acEject it there before
%acunplugging the cable.
'''

WPS = f'''# Waveform Bot HUD - While Playing Screen, 480x800 portrait. Laid out like a robot body (chest frame, belly controls):
#
#    0..52   status bar
#   54..474  chest: chrome-framed screen, 360px cover (60,84) with a live level meter either side
#  482..538  title on a plate;  "..." context key on its right
#  538..604  artist / album;     604..640 chips: format | bitrate | playlist position
#  640..690  seek bar (whole band is the touch area)
#  694..796  belly: big rewind / fast-forward arrows, PLAY/PAUSE key, shuffle + repeat keys under it
#
# Everything static is baked into bg_wps.bmp. Touch buttons need Settings > ... > Touchscreen mode > Point.
%wd
%X(bg_wps.bmp)

%Fl(2,28-waveformbot.fnt)
%Fl(3,40-waveformbot.fnt)

%xl(f,batt_fill.bmp,0,0)
%xl(ml,meter_l.bmp,0,0)
%xl(mr,meter_r.bmp,0,0)
%xl(pk,pb_knob.bmp,0,0)
%xl(ply,play.bmp,0,0)
%xl(pau,pause.bmp,0,0)
%xl(s,shuffle.bmp,0,0,2)
%xl(r,repeat.bmp,0,0,5)

# ---- clear the whole screen to the backdrop ----
%V(0,0,480,800,-)

{STATUS}
# ---- live level meters either side of the cover (lit ladder: steel, silver, purple peak) ----
%V(32,84,{MW},360,-)%Vf({C['ice']})
%pL(0,0,{MW},360,ml)

%V(430,84,{MW},360,-)%Vf({C['ice']})
%pR(0,0,{MW},360,mr)

# ---- cover (the no-cover badge is baked into the backdrop) ----
%V(60,84,360,360,1)
%Cl(0,0,360,360,c,c)
%?C<%Cd>

# ---- title + context key ----
%V(28,485,374,52,3)%Vf({C['txt']})
%s%al%?it<%it|%fn>

%V(410,492,46,40,-)
%T(menu,0,0,-,-,contextmenu)

%V(22,538,436,37,2)%Vf({C['silver']})
%s%al%?ia<%ia|Unknown Artist>

%V(22,568,436,37,2)%Vf({C['sec']})
%s%al%?id<%id|Unknown Album>

# ---- chips: format | bitrate | playlist position (outlines baked) ----
%V(24,604,104,37,2)%Vf({C['txt']})
%ac%fc

%V(138,604,116,37,2)%Vf({C['txt']})
%ac%fbk

%V(264,604,192,37,2)%Vf({C['txt']})
%ac%pp/%pe

# ---- seek: contentless touch band first, then the bar between the times ----
%V(10,640,464,52,-)
%T(seek,0,0,-,-,progressbar)

%V(84,656,312,22,1)%Vf({C['gold']})
%pb(0,4,-,14,slider,pk,notouch)

%V(10,648,72,37,2)%Vf({C['elapsed']})
%al%pc

%V(398,648,76,37,2)%Vf({C['sec']})
%ar%pt

# ---- belly controls ----
%V(14,706,102,88,-)
%T(prev,0,0,-,-,wps_prev)
%T(prevhold,0,0,-,-,rwd,repeat_press)

%V(364,706,102,88,-)
%T(next,0,0,-,-,wps_next)
%T(nexthold,0,0,-,-,ffwd,repeat_press)

%V(166,706,148,40,-)
%T(play,0,0,-,-,play)
%T(stop,0,0,-,-,stop,long_press)
%?mp<%xd(ply)|%xd(pau)|%xd(ply)|%xd(ply)|%xd(ply)>

%V(166,754,70,40,-)
%T(shuf,0,0,-,-,shuffle)
%?ps<%xd(sb)|%xd(sa)>

%V(244,754,70,40,-)
%T(mode,0,0,-,-,repmode)
%?mm<%xd(ra)|%xd(rb)|%xd(rc)|%xd(rd)|%xd(re)>
'''

CFG = f'''# Theme:        Waveform Bot HUD
# Author:       Oddlogic
# Source:       https://github.com/oddlogic-space/oddlogic-rockbox-themes  (latest version, changelog, bug reports)
# Platform:     HiBy R1 (480x800 portrait touch), Rockbox hosted build (Unsupported/hosted)
# Version:      1.1
# License:      CC-BY-SA 4.0 (skins, graphics). Fonts: SIL Open Font License 1.1 (derived from Noto Sans CJK)
# Graphics:     All graphics generated by the author with a script (no third-party images)
# Last updated: 2026-10-14
#
# Navy body, gold chest frame, silver keys, red peak meters; battery icon in purple / icy blue / muted red.
# IMPORTANT: touch buttons need  Settings > General Settings > Display >
#   Touchscreen Settings > Touchscreen mode > Point
wps: /.rockbox/wps/waveformbot.wps
sbs: /.rockbox/wps/waveformbot.sbs
font: /.rockbox/fonts/32-waveformbot.fnt
backdrop: -
show icons: on
filetype colours: -
statusbar: top
scrollbar: off
foreground color: {hexs(TXT)}
background color: {hexs(BG)}
line selector start color: {hexs(BODY)}
line selector end color: {hexs(BODY2)}
line selector text color: F5F7FF
selector type: bar (gradient)
ui viewport: -
list padding: 14
'''
open(os.path.join(RB, "wps", "waveformbot.sbs"), "w").write(SBS)
open(os.path.join(RB, "wps", "waveformbot.wps"), "w").write(WPS)
open(os.path.join(RB, "themes", "waveformbot.cfg"), "w").write(CFG)
print("built", "(custom emblem)" if os.path.exists(EMBLEM) else "(default shield battery)")
