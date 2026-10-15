#!/usr/bin/env python3
"""Structural lint for a Rockbox theme package (R1 480x800).  usage: lint.py <root> <id>"""
import re, os, sys
from PIL import Image
root, ID = sys.argv[1], sys.argv[2]
W = f"{root}/.rockbox/wps"; FN = f"{root}/.rockbox/fonts"; IM = f"{W}/{ID}"; bad = 0
def err(*a):
    global bad; bad += 1; print("  PROBLEM:", *a)
import glob
cfgs = glob.glob(f"{root}/.rockbox/themes/*.cfg"); assert len(cfgs) == 1, cfgs; print("cfg file:", os.path.basename(cfgs[0]))
cfg = open(cfgs[0]).read()
for k in ("wps", "sbs"):
    m = re.search(rf"^{k}:\s*(\S+)", cfg, re.M)
    if not m or not os.path.exists(root + m.group(1)): err("cfg", k, "target missing", m and m.group(1))
fm = re.search(r"^font:\s*(\S+)", cfg, re.M)
if not fm or not os.path.exists(root + fm.group(1)): err("cfg font missing")
if not os.path.exists(f"{FN}/COPYING-{ID}.txt"): err("COPYING file missing")
for name in (f"{ID}.sbs", f"{ID}.wps"):
    raw = open(f"{W}/{name}").read(); body = "\n".join(l for l in raw.splitlines() if not l.lstrip().startswith("#"))
    print(name, len(body.splitlines()), "lines")
    imgs = {}
    for m in re.finditer(r"%x[l]?\(([^,)]+),([^,)]+)(?:,(-?\d+),(-?\d+))?(?:,(\d+))?\)", body):
        lab, f, x, y, n = m.groups(); n = int(n or 1); p = os.path.join(IM, f)
        if lab in imgs: err(name, "duplicate image label", lab)
        if not os.path.exists(p): err(name, "missing image", f); continue
        w, h = Image.open(p).size; imgs[lab] = (w, h, n)
        if h % n: err(name, "image height not divisible by subimages", f, h, n)
        if Image.open(p).mode != "RGB": err(name, "image not 24-bit RGB", f)
    for m in re.finditer(r"^%X\(([^)]+)\)", body, re.M):
        p = os.path.join(IM, m.group(1)); 
        if not os.path.exists(p): err(name, "missing backdrop", m.group(1))
        elif Image.open(p).size != (480, 800): err(name, "backdrop size", Image.open(p).size)
    fonts = set()
    for m in re.finditer(r"%Fl\((\d+),([^,)]+)", body):
        fonts.add(int(m.group(1)))
        if not os.path.exists(f"{FN}/{m.group(2)}"): err(name, "missing font", m.group(2))
    # viewport bounds + label sets
    vls, vis = set(), set()
    for m in re.finditer(r"%V(l|i)?\(((?:[A-Za-z_0-9]+,)?)(-?\d+),(-?\d+),(-?\d+|-),(-?\d+|-),([^)]*)\)", body):
        kind, lab, x, y, w, h, font = m.groups(); lab = lab.rstrip(",")
        if kind == "l": vls.add(lab)
        if kind == "i": vis.add(lab)
        x, y = int(x), int(y); w = 480 - x if w == "-" else int(w); h = 800 - y if h == "-" else int(h)
        if kind == "i" and lab == "ui_usb": continue
        if x < 0 or y < 0 or x + w > 480 or y + h > 800: err(name, "viewport off-screen", m.group(0))
        if font.strip().isdigit() and int(font) >= 2 and int(font) not in fonts: err(name, "viewport font id not loaded", m.group(0))
    for m in re.finditer(r"%Vd\(([^)]+)\)", body):
        if m.group(1) not in vls: err(name, "%Vd of undefined viewport", m.group(1))
    for m in re.finditer(r"%VI\(([^)]+)\)", body):
        if m.group(1) not in vis: err(name, "%VI of undefined ui viewport", m.group(1))
    for m in re.finditer(r"%Lb\(([^,]+),", body):
        if m.group(1) not in vls: err(name, "%Lb viewport label not defined", m.group(1))
    # image refs in %xd / bars
    for m in re.finditer(r"%xd\(([^,)]+)(?:,([^)]*))?\)", body):
        lab = m.group(1)
        if lab not in imgs: err(name, "%xd of unknown image", lab); continue
        sub = m.group(2)
        if sub and sub.strip().isdigit() and int(sub) > imgs[lab][2]: err(name, "subimage out of range", m.group(0))
        if (m.group(2) is None) and len(lab) <= 2: err(name, "ambiguous short image label", lab)
    for m in re.finditer(r"%(?:pb|bl|LB)\(([^)]*)\)", body):
        for t in m.group(1).split(",")[4:]:
            t = t.strip()
            if t and t not in ("slider", "backdrop", "invert", "nobar", "nofill", "noborder", "notouch", "image", "vertical", "horizontal") and t not in imgs and not t.endswith(".bmp"): err(name, "bar references unknown image/option", t, "in", m.group(0))
    # touch region names unique
    names = re.findall(r"%T\(([^,]+),", body)
    if len(names) != len(set(names)): err(name, "duplicate touch region names", [n for n in set(names) if names.count(n) > 1])
    # balanced conditionals
    depth = 0
    for ch in re.sub(r"%\?[A-Za-z]+(\([^)]*\))?<", "\x01", body).replace("%<", "").replace("%>", ""):
        if ch == "\x01": depth += 1
        elif ch == ">": depth -= 1
        if depth < 0: err(name, "unbalanced >"); break
    if depth: err(name, "unclosed conditional", depth)
    # unused images
    for lab in imgs:
        if not re.search(rf"[(,]{lab}[,)]", body.split("%xl(" + lab, 1)[1]): err(name, "image loaded but never used:", lab)
print("LINT PROBLEMS:", bad); sys.exit(1 if bad else 0)
