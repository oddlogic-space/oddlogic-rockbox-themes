#!/usr/bin/env python3
"""Build the two album themes (In Love = "dream", Pretty Sad = "film") for the HiBy R1 (480x800). Needs Pillow + numpy.
Usage: build.py [dream|film ...]     Writes .rockbox/wps/<id>/*, <id>.wps|.sbs and .rockbox/themes/<Name>.cfg"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyberlib import *

ROOT = os.environ.get("OUT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__))); RB = os.path.join(ROOT, ".rockbox")   # OUT=<dir> to write elsewhere
PAL = {
 "dream": dict(name="In Love", bg="1E0F18", bg2="2E1625", panel="2A1521", line="E58DA5", pink="F2A0B5", cream="F7E9E3", text="F7E9E3",
               sec="C79AA9", dim="553345", chip="8A556B", sel_a="5A2338", sel_b="8A3A5A", sel_t="FFFFFF", gdark="3A1626"),
 "film":  dict(name="Pretty Sad", bg="17232A", panel="1D2E37", line="8CA7B2", pink="F0998A", cream="D9CCB9", text="EADFCF",
               sec="9FB3BB", dim="38515D", sel_a="2B4756", sel_b="456F80", sel_t="FFFFFF", ink="2B2420", ink2="5E5247", coral="B65A4C", tape="C9B28A", gdark="2A1A1A"),
}
def rgb(p): return {k: (fc(v) if isinstance(v, str) and len(v) == 6 else v) for k, v in p.items()}
rnd = np.random.default_rng(5)
ROW = [("shuf", 12, 90), ("prev", 98, 190), ("play", 198, 282), ("next", 290, 382), ("rep", 390, 468)]
COLS = [0, 94, 194, 286, 386, 480]

def save_bmp(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True); im.convert("RGB").save(path, format="BMP")

# ------------------------------------------------------------------ small helpers
def grain(c, amt):
    a = np.asarray(c.im, np.float32)
    n = rnd.normal(0, amt, (H*S//3, W*S//3)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n*8)+128).clip(0, 255).astype(np.uint8)).resize((W*S, H*S), Image.BILINEAR), np.float32)[..., None]
    c.im = Image.fromarray(np.clip(a + (n-128)/8, 0, 255).astype(np.uint8))
def vgrad(top, bot, glow=None):
    t = np.linspace(0, 1, H*S)[:, None, None]
    arr = (np.array(top, float)*(1-t) + np.array(bot, float)*t) * np.ones((H*S, W*S, 3))
    c = Cv(top); c.im = Image.fromarray(arr.astype(np.uint8))
    if glow:
        cx, cy, r, col, al = glow; c.ell(cx, cy, r, col, al); c.im = c.im.filter(ImageFilter.GaussianBlur(40*S))
    return c
def heart(c, cx, cy, s, col):
    pts = [(cx + 16*math.sin(t)**3*s/16, cy - (13*math.cos(t) - 5*math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t))*s/16) for t in np.linspace(0, 2*math.pi, 90)]
    c.poly(pts, col); return pts
def dashed(c, pts, col, w=2, dash=8, gap=6, closed=True):
    P = pts + [pts[0]] if closed else pts
    for (x0, y0), (x1, y1) in zip(P, P[1:]):
        L = math.hypot(x1-x0, y1-y0)
        if L < 0.01: continue
        for k in range(int(L // (dash+gap)) + 1):
            a = k*(dash+gap)/L; b = min(1, (k*(dash+gap)+dash)/L)
            if a < 1: c.line([(x0+(x1-x0)*a, y0+(y1-y0)*a), (x0+(x1-x0)*b, y0+(y1-y0)*b)], col, w)
def rbox(box, r=14, n=10):
    x0, y0, x1, y1 = box; pts = []
    for (cx, cy, a0) in ((x1-r, y0+r, -90), (x1-r, y1-r, 0), (x0+r, y1-r, 90), (x0+r, y0+r, 180)):
        for k in range(n+1):
            a = math.radians(a0 + 90*k/n); pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    return pts
def circle_pts(cx, cy, r, n=36): return [(cx+r*math.cos(a/n*2*math.pi), cy+r*math.sin(a/n*2*math.pi)) for a in range(n)]
def tape(c, cx, cy, w, h, ang, col, al=0.78):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    c.poly([(cx+dx*ca-dy*sa, cy+dx*sa+dy*ca) for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))], col, al)
def badge(c, cx, cy, r, fill, ring, note):
    c.ell(cx, cy, r, fill); c.ring(cx, cy, r, 3, ring); k = r/78.0
    c.ell(cx-15*k, cy+18*k, 12*k, note); c.rr((cx-7*k, cy-32*k, cx-2*k, cy+20*k), 0, note)
    c.poly([(cx-2*k, cy-32*k), (cx+22*k, cy-14*k), (cx+22*k, cy+2*k), (cx-2*k, cy-16*k)], note)
def cloud_pts(x, y, w, h):
    """Little cloud outline as a union of circles + flat base, for the battery."""
    return [(x+w*.22, y+h*.62, h*.30), (x+w*.45, y+h*.42, h*.40), (x+w*.72, y+h*.58, h*.32), (x+w*.5, y+h*.70, h*.30)]
CLOUD = (438, 14, 32, 22)          # battery cloud box on screen (x,y,w,h)
def cloud_mask(c, x, y, w, h, grow=0):
    return c.mask(lambda d: [d.ellipse([(cx-r-grow)*S, (cy-r-grow)*S, (cx+r+grow)*S, (cy+r+grow)*S], fill=255) for cx, cy, r in cloud_pts(x, y, w, h)]
                  + [d.rectangle([(x+w*.22)*S, (y+h*.62)*S, (x+w*.72)*S, (y+h*.92+grow)*S], fill=255)])

# ------------------------------------------------------------------ status bar (static part)
def status_static(c, p, t):
    c.rr((0, -10, 480, 50), 0, p["panel"])
    c.paint(c.mask(lambda d: d.rectangle([0, 50*S, W*S, 52*S], fill=255)), p["line"], 0.9)
    c.poly([(16, 21), (21, 21), (28, 15), (28, 35), (21, 29), (16, 29)], p["line"]); c.line([(32, 20), (35, 25), (32, 30)], p["line"], 2)
    c.rr((46, 23, 156, 27), 2, p["dim"])                                         # volume trough
    if t == "dream":                                                             # cloud battery (empty)
        x, y, w, h = CLOUD
        c.paint(cloud_mask(c, x, y, w, h), p["line"]); c.paint(cloud_mask(c, x, y, w, h, grow=-2), p["panel"])
    else:                                                                        # plain vertical battery
        c.rr((448, 13, 466, 41), 4, p["line"]); c.rr((453, 10, 461, 14), 1, p["line"]); c.rr((451, 16, 463, 38), 2, p["panel"])

# ------------------------------------------------------------------ backdrops
def base(p, t):
    if t == "dream": c = vgrad(p["bg"], p["bg2"], glow=(240, 770, 260, p["line"], 0.20)); grain(c, 2.0)
    else: c = Cv(p["bg"]); grain(c, 3.0)
    status_static(c, p, t); return c

HEAD_X = {"dream": 66, "film": 40}
def menu_backdrop(p, t):
    c = base(p, t)
    if t == "dream":
        heart(c, 38, 94, 16, p["pink"]); dashed(c, [(70, 126), (456, 126)], p["line"], 2, 9, 6, closed=False)
    else:
        c.shadow((16, 66, 330, 124), 4, (0, 5), 7, 0.5); c.rr((16, 66, 330, 124), 4, p["cream"]); tape(c, 40, 66, 70, 24, -18, p["tape"])
    return c.out()

def wps_backdrop(p, t):
    c = base(p, t)
    if t == "dream":
        dashed(c, rbox((44, 60, 436, 452), 22), p["line"], 2.2, 9, 6)
        badge(c, 240, 256, 70, p["panel"], p["line"], p["pink"])
        for a, b in ((24, 160), (172, 308), (320, 456)):
            dashed(c, rbox((a, 596, b, 632), 18, 6), p["chip"], 1.8, 6, 5)
        dashed(c, rbox((24, 648, 456, 668), 10, 6), p["dim"], 1.8, 6, 5)
    else:
        c.shadow((28, 66, 452, 600), 6, (0, 8), 10, 0.55); c.rr((28, 66, 452, 600), 6, p["cream"]); c.rr((50, 86, 430, 466), 1, p["dim"])
        badge(c, 240, 276, 70, p["panel"], p["line"], p["pink"])
        tape(c, 240, 62, 110, 30, -3, p["tape"])
        c.rr((92, 660, 388, 674), 7, p["panel"], outline=p["dim"], ow=1)
    return c.out()

# ------------------------------------------------------------------ controls
def key_rect(t, kind, x0, x1):
    cx = (x0+x1)/2
    if t == "dream":
        return (int(cx-42), 710, int(cx+42), 794) if kind == "play" else (x0, 716, x1, 788)
    m = 42 if kind == "play" else 36
    return (int(cx-m), 756-m, int(cx+m), 756+m)

def draw_key(c, p, t, kind, x0, x1, act=False, label=None, paused=False, dim=False):
    gk = ("pause" if paused else "play") if kind == "play" else kind
    cx = (x0+x1)/2; big = kind == "play"
    g = p["sec"] if dim else p["cream" if t == "dream" else "text"]
    if t == "dream":
        cy = 752
        if big:
            c.ell(cx, cy, 38, p["pink"]); dashed(c, circle_pts(cx, cy, 31, 40), p["cream"], 1.8, 5, 4); g = p["gdark"]
        else:
            dashed(c, rbox((x0, 716, x1, 788), 22, 8), p["line"] if (act and kind == "rep") else p["dim"], 2, 7, 5)
    else:
        cy = 756; r = 38 if big else 32
        c.ell(cx, cy, r, p["pink"] if big else p["panel"])
        if not big: c.ring(cx, cy, r, 2, p["dim"])
        if big: g = p["gdark"]
    if label == "A-B": c.text((cx, cy), "A-B", p["pink"], 19, BOLD, anchor="mm"); return
    glyph(c, g, gk, cx, cy, act=act, accent=p["pink"])
    if label: c.text((cx, cy), label, p["pink"], 13, BOLD, anchor="mm")

def canvas_over(bg):
    c = Cv((0, 0, 0)); c.im = bg.resize((W*S, H*S), Image.BICUBIC); return c

def build_controls(p, t, out, wb):
    def one(kind, x0, x1, **kw):
        c = canvas_over(wb); draw_key(c, p, t, kind, x0, x1, **kw); return c.out().crop(key_rect(t, kind, x0, x1))
    def sheet(frames, name):
        w, h = frames[0].size; s = Image.new("RGB", (w, h*len(frames)))
        for i, f in enumerate(frames): s.paste(f, (0, i*h))
        save_bmp(s, os.path.join(out, name))
    d = {k: (a, b) for k, a, b in ROW}
    save_bmp(one("prev", *d["prev"]), os.path.join(out, "prev.bmp")); save_bmp(one("next", *d["next"]), os.path.join(out, "next.bmp"))
    save_bmp(one("play", *d["play"], paused=False), os.path.join(out, "play.bmp")); save_bmp(one("play", *d["play"], paused=True), os.path.join(out, "pause.bmp"))
    sheet([one("shuf", *d["shuf"], dim=True), one("shuf", *d["shuf"], act=True)], "shuffle.bmp")
    a, b = d["rep"]
    sheet([one("rep", a, b, dim=True), one("rep", a, b, act=True), one("rep", a, b, act=True, label="1"),
           one("rep", a, b, act=True, label="S"), one("rep", a, b, act=True, label="A-B")], "repeat.bmp")

CTX = {"dream": (404, 464, 460, 520), "film": (386, 476, 438, 528)}
def build_ctx(p, t, out, wb):
    c = canvas_over(wb)
    if t == "dream":
        c.ell(432, 492, 26, p["panel"]); dashed(c, circle_pts(432, 492, 26), p["line"], 2, 5, 4); cx, cy, col = 432, 492, p["cream"]
    else:
        c.ell(412, 502, 24, p["ink"]); cx, cy, col = 412, 502, p["cream"]
    glyph(c, col, "dots", cx, cy); save_bmp(c.out().crop(CTX[t]), os.path.join(out, "menu.bmp"))

def build_misc(p, t, out):
    if t == "dream": w, h, col, r, bgc = 8, 20, p["cream"], 4, p["pink"]
    else:            w, h, col, r, bgc = 10, 14, p["cream"], 5, p["panel"]
    s = 4; im = Image.new("RGB", (w*s, h*s), bgc)
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w*s-1, h*s-1], radius=r*s, fill=col)
    save_bmp(im.resize((w, h), Image.LANCZOS), os.path.join(out, "pb_knob.bmp"))
    if t == "dream":                         # cloud: pink body + outline on the strip colour (drawn clipped from the bottom)
        x, y, w, h = CLOUD; c = Cv(p["panel"])
        c.paint(cloud_mask(c, x, y, w, h), p["line"]); c.paint(cloud_mask(c, x, y, w, h, grow=-2), p["pink"])
        save_bmp(c.out().crop((x, y, x+w, y+h)), os.path.join(out, "battery_fill.bmp"))
    else:
        Image.new("1", (12, 22), 0).save(os.path.join(out, "battery_fill.bmp"), format="BMP")

# ------------------------------------------------------------------ skins
def status_skin(p, t):
    L = [f"%V(46,23,110,4,-)%Vf({p['pink']})", "%pv(0,0,-,-,noborder)", "",
         f"%V(176,7,128,36,2)%Vf({p['text']})", "%ac%cH:%cM", "",
         f"%V(312,7,{116 if t == 'dream' else 124},36,2)%Vf({p['text']})", "%ar%bl%%", ""]
    if t == "dream":
        x, y, w, h = CLOUD
        L += [f"%V({x},{y},{w},{h},-)", "%bl(0,0,-,-,f,vertical)", ""]
    else:
        L += [f"%V(451,16,12,22,-)%Vf({p['pink']})", "%?bc<%Vf(F7D9A0)|%?bl<|%Vf(E06A5A)|||>>", "%bl(0,0,-,-,f,vertical)", ""]
    return "\n".join(L)

def controls_skin(t):
    y0, hh = {"dream": (706, 94), "film": (712, 88)}[t]
    off = {}
    for i, (kind, x0, x1) in enumerate(ROW):
        r = key_rect(t, kind, x0, x1); off[kind] = (r[0]-COLS[i], r[1]-y0)
    img = []
    for kind, nm, f, sub in (("shuf", "s", "shuffle.bmp", 2), ("prev", "prv", "prev.bmp", 0), ("play", "ply", "play.bmp", 0),
                             ("play", "pau", "pause.bmp", 0), ("next", "nxt", "next.bmp", 0), ("rep", "r", "repeat.bmp", 5)):
        ox, oy = off[kind]; img.append(f"%xl({nm},{f},{ox},{oy}{',' + str(sub) if sub else ''})")
    vp = lambda i: f"%V({COLS[i]},{y0},{COLS[i+1]-COLS[i]},{hh},-)"
    s = [vp(0), "%T(shuf,0,0,-,-,shuffle)", "%?ps<%xd(sb)|%xd(sa)>", "",
         vp(1), "%T(prev,0,0,-,-,wps_prev)", "%T(prevhold,0,0,-,-,rwd,repeat_press)", "%xd(prv)", "",
         vp(2), "%T(play,0,0,-,-,play)", "%T(stop,0,0,-,-,stop,long_press)", "%?mp<%xd(ply)|%xd(pau)|%xd(ply)|%xd(ply)|%xd(ply)>", "",
         vp(3), "%T(next,0,0,-,-,wps_next)", "%T(nexthold,0,0,-,-,ffwd,repeat_press)", "%xd(nxt)", "",
         vp(4), "%T(mode,0,0,-,-,repmode)", "%?mm<%xd(ra)|%xd(rb)|%xd(rc)|%xd(rd)|%xd(re)>", ""]
    return img, "\n".join(s)

def ctx_skin(t):
    x0, y0, x1, y1 = CTX[t]
    vx, vy, vw, vh = {"dream": (400, 458, 80, 68), "film": (382, 470, 70, 64)}[t]
    return f"%V({vx},{vy},{vw},{vh},-)\n%T(menu,0,0,-,-,contextmenu)\n%xd(men)", (x0-vx, y0-vy)

def wps_text(p, t):
    ox, oy = ctx_skin(t)[1]; imgs, ctl = controls_skin(t)
    H_ = [f"# {p['name']} - While Playing Screen, 480x800 portrait (generated by tools/build.py).",
          "# Touch buttons need Settings > General Settings > Display > Touchscreen Settings > Touchscreen mode > Point.",
          "%wd", "", "%X(bg_wps.bmp)", "", "%Fl(2,28-GirlSans.fnt)", "%Fl(3,40-GirlSerif.fnt)", "",
          "%xl(pk,pb_knob.bmp,0,0)", f"%xl(men,menu.bmp,{ox},{oy})", "%xl(f,battery_fill.bmp,0,0)"] + imgs + ["",
          "%V(0,0,480,800,-)", "", "# ---- status bar ----", status_skin(p, t), ""]
    if t == "dream":
        B = ["# ---- cover ----", "%V(60,76,360,360,1)", "%Cl(0,0,360,360,c,c)", "%?C<%Cd>", "",
             f"%V(24,466,370,52,3)%Vf({p['text']})", "%s%al%?it<%it|%fn>", "", ctx_skin(t)[0], "",
             f"%V(24,516,432,37,2)%Vf({p['pink']})", "%s%al%ia", "", f"%V(24,552,432,37,2)%Vf({p['sec']})", "%s%al%id", ""]
        for x0, val in ((24, "%fc"), (172, "%fbk"), (320, "%pp/%pe")):
            B += [f"%V({x0},596,136,37,2)%Vf({p['text']})", f"%ac{val}", ""]
        B += ["# ---- progress ----", f"%V(24,640,432,36,1)%Vf({p['pink']})", "%pb(0,8,-,20,slider,pk,notouch)", "%T(seek,0,0,-,-,progressbar)", "",
              f"%V(24,672,200,37,2)%Vf({p['pink']})", "%al%pc", "", f"%V(256,672,200,37,2)%Vf({p['sec']})", "%ar%pt", ""]
    else:
        B = ["# ---- photo ----", "%V(50,86,380,380,1)", "%Cl(0,0,380,380,c,c)", "%?C<%Cd>", "",
             f"%V(50,474,330,52,3)%Vf({p['ink']})", "%s%al%?it<%it|%fn>", "", ctx_skin(t)[0], "",
             f"%V(50,524,330,37,2)%Vf({p['coral']})", "%s%al%ia", "", f"%V(50,560,380,37,2)%Vf({p['ink2']})", "%s%al%id", "",
             f"%V(20,608,440,37,2)%Vf({p['line']})", "%ac%fc · %fbk · %pp/%pe", "",
             "# ---- progress ----", f"%V(92,650,296,40,1)%Vf({p['pink']})", "%pb(0,10,-,14,slider,pk,notouch)", "%T(seek,0,0,-,-,progressbar)", "",
             f"%V(20,654,72,37,2)%Vf({p['pink']})", "%al%pc", "", f"%V(388,654,72,37,2)%Vf({p['sec']})", "%ar%pt", ""]
    return "\n".join(H_ + B + ["# ---- control row ----", ctl]) + "\n"

def sbs_text(p, t):
    hx = HEAD_X[t]; col = p["text"] if t == "dream" else p["ink"]
    ty, tw = (62, 380 if t == "dream" else 280)
    s = [f"# {p['name']} - base skin (menus, lists, USB screen), 480x800.", "%X(bg_menu.bmp)", "%Fl(2,28-GirlSans.fnt)", "%Fl(3,40-GirlSerif.fnt)",
         "%xl(f,battery_fill.bmp,0,0)", "", "%Vi(main,0,140,-,-,1)", "%Vi(ui_usb,0,152,2,2,1)", "%?if(%cs,=,21)<%VI(ui_usb)|%VI(main)>", "",
         "%?if(%cs,=,21)<%Vd(ut)%Vd(ub)|%?Lt<%Vd(ht)>>", "", "%V(0,0,480,800,-)", "", "# ---- status bar ----", status_skin(p, t), "",
         f"%Vl(ht,{hx},{ty+6 if t=='film' else ty},{tw},52,3)%Vf({col})", "%s%al%Lt", "",
         f"%Vl(ut,{hx},{ty+6 if t=='film' else ty},{tw},52,3)%Vf({col})", "%alUSB connected", "",
         f"%Vl(ub,20,230,440,190,2)%Vf({p['sec']})", "%acYour player is connected", "%acto a computer.", "%ac", "%acEject it there before", "%acunplugging the cable.", ""]
    return "\n".join(s)

def cfg_text(p, t):
    return f"""# {p['name']} - Rockbox theme for HiBy R1 (480x800)
# IMPORTANT: touch buttons need  Settings > General Settings > Display >
#   Touchscreen Settings > Touchscreen mode > Point
wps: /.rockbox/wps/{t}.wps
sbs: /.rockbox/wps/{t}.sbs
font: /.rockbox/fonts/32-GirlSans.fnt
backdrop: -
show icons: on
filetype colours: -
statusbar: top
scrollbar: off
foreground color: {p['text']}
background color: {p['bg']}
line selector start color: {p['sel_a']}
line selector end color: {p['sel_b']}
line selector text color: {p['sel_t']}
selector type: bar (gradient)
ui viewport: -
list separator color: {p['dim']}
list padding: 30
"""

def build(t):
    p = PAL[t]; q = rgb(p); out = os.path.join(RB, "wps", t); os.makedirs(out, exist_ok=True); print("building", t)
    save_bmp(menu_backdrop(q, t), os.path.join(out, "bg_menu.bmp"))
    wb = wps_backdrop(q, t); save_bmp(wb, os.path.join(out, "bg_wps.bmp"))
    build_controls(q, t, out, wb); build_ctx(q, t, out, wb); build_misc(q, t, out)
    open(os.path.join(RB, "wps", t + ".wps"), "w").write(wps_text(p, t)); open(os.path.join(RB, "wps", t + ".sbs"), "w").write(sbs_text(p, t))
    os.makedirs(os.path.join(RB, "themes"), exist_ok=True); open(os.path.join(RB, "themes", p["name"] + ".cfg"), "w").write(cfg_text(p, t))

if __name__ == "__main__":
    for t in (sys.argv[1:] or PAL): build(t)
