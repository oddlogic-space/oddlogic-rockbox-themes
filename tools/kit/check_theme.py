#!/usr/bin/env python3
"""Check a built theme before release: the checks Rockbox and themes.rockbox.org apply.

    python3 tools/kit/check_theme.py THEME.zip|DIR [--previous OLD.zip] [--checkwps BIN]

DIR is a folder that contains .rockbox/. The checks:
  - zip layout: only the .rockbox/ tree, lowercase paths with no spaces, no OS junk files
  - checkwps (Rockbox's own skin engine parser for the HiBy R1) on every skin and cfg; it also
    loads every image and font a skin names, so a missing file fails here
  - RB12 font layout (a bad pad byte makes Rockbox drop the whole skin back to the stock screen)
  - files in the package that no skin or cfg uses
  - cfg rules for themes.rockbox.org: header links the GitHub repo, no email, colours set,
    no settings the upload site rejects
  - size table, largest first, and the change from --previous
Exit status 1 if any check fails.
"""
import argparse
import os
import re
import struct
import subprocess
import sys
import tempfile
import zipfile

REPO_URL = "github.com/oddlogic-space/oddlogic-rockbox-themes"
KIT = os.path.dirname(os.path.abspath(__file__))
JUNK = re.compile(r"(^|/)(__MACOSX|\.DS_Store|Thumbs\.db|desktop\.ini)(/|$)")
REJECTED_SETTINGS = re.compile(r"^(list separator colou?r|peak meter[^:]*):", re.M | re.I)
CFG_FILES = re.compile(r"^(wps|sbs|fms|rwps|rsbs|rfms|font|backdrop|iconset|viewers iconset|remote font):\s*(\S+)",
                       re.M | re.I)


def check_font(data):
    """Return None if `data` is a well-formed RB12 font, else the reason it is not."""
    if len(data) < 36 or data[:4] != b"RB12":
        return "not an RB12 font"
    _, _, _, _, _, _, size, nbits, noffset, nwidth = struct.unpack("<HHHHIIIIII", data[4:36])
    ow = 2 if nbits < 0xFFDB else 4
    pad = (-(36 + nbits)) % ow
    want = 36 + nbits + pad + noffset * ow + nwidth
    if len(data) != want:
        return f"length {len(data)}, expected {want} (bitmap pad before the offset table is wrong?)"
    if noffset not in (0, size) or nwidth not in (0, size):
        return "offset or width table size does not match the glyph count"
    return None


def skin_refs(text, skin_dir):
    """Package paths a skin file loads: backdrop, images and fonts."""
    refs = set()
    for name in re.findall(r"%X\(([^)]+)\)", text):
        if name != "-":
            refs.add(f".rockbox/wps/{skin_dir}/{name}")
    for name in re.findall(r"%xl?\([^,()]+,([^,()]+)", text):
        refs.add(f".rockbox/wps/{skin_dir}/{name}")
    for name in re.findall(r"%Fl\(\s*\d+\s*,([^,)]+)", text):
        refs.add(f".rockbox/fonts/{name.strip()}")
    return refs


def run(target, previous=None, checkwps=None):
    problems = []
    tmp = None
    if os.path.isfile(target):
        with zipfile.ZipFile(target) as z:
            names = z.namelist()
            for n in names:
                if not n.startswith(".rockbox/"):
                    problems.append(f"zip: {n} is outside .rockbox/")
                if JUNK.search(n):
                    problems.append(f"zip: {n} is an OS junk file")
            tmp = tempfile.TemporaryDirectory()
            z.extractall(tmp.name)
            root = tmp.name
    else:
        root = target
    files = sorted(os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
                   for d, _, fs in os.walk(os.path.join(root, ".rockbox")) for f in fs)
    licences = {f for f in files if re.match(r"\.rockbox/fonts/(copying|licen[cs]e)[^/]*$", f, re.I)}
    for f in files:
        if (f != f.lower() and f not in licences) or " " in f:  # the site accepts COPYING-<name>.txt
            problems.append(f"{f}: paths must be lowercase with no spaces")
        if JUNK.search(f):
            problems.append(f"{f}: OS junk file")

    skins = [f for f in files if re.search(r"\.(r?wps|r?sbs|r?fms)$", f)]
    cfgs = [f for f in files if f.startswith(".rockbox/themes/") and f.endswith(".cfg")]
    used = set(skins) | set(cfgs) | licences

    for s in skins:
        used |= skin_refs(open(os.path.join(root, s), encoding="utf-8", errors="replace").read(),
                          os.path.splitext(os.path.basename(s))[0])
    if not cfgs:
        problems.append("no .rockbox/themes/*.cfg")
    for c in cfgs:
        cfg = open(os.path.join(root, c), encoding="utf-8", errors="replace").read()
        header = "\n".join(l for l in cfg.splitlines() if l.startswith("#"))
        if REPO_URL not in header:
            problems.append(f"{c}: header does not link {REPO_URL}")
        if re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", cfg, re.I):
            problems.append(f"{c}: contains an email address")
        for key in ("foreground color", "background color"):
            if not re.search(rf"^{key}:", cfg, re.M):
                problems.append(f"{c}: '{key}' is not set")
        for m in REJECTED_SETTINGS.finditer(cfg):
            problems.append(f"{c}: themes.rockbox.org rejects the '{m.group(1)}' setting")
        for key, val in CFG_FILES.findall(cfg):
            if val != "-":
                rel = val.lstrip("/")
                used.add(rel)
                if rel not in files:
                    problems.append(f"{c}: {key} {val} is not in the package")

    for f in files:
        if f.endswith(".fnt"):
            why = check_font(open(os.path.join(root, f), "rb").read())
            if why:
                problems.append(f"{f}: {why}")
        if f not in used:
            problems.append(f"{f}: not used by any skin or cfg")

    if checkwps:
        for f in skins + cfgs:
            p = subprocess.run([checkwps, f], cwd=root, capture_output=True, text=True)
            if p.returncode != 0:
                detail = " | ".join(l.strip() for l in (p.stdout + p.stderr).splitlines()
                                    if l.strip() and not l.startswith("Checking") and set(l.strip()) != {"="})
                problems.append(f"{f}: checkwps failed: {detail}")
    else:
        problems.append("checkwps not run (pass --checkwps, or run tools/kit/build-checkwps.sh)")

    print(f"{'zipped':>9} {'raw':>9}  file")
    if os.path.isfile(target):
        with zipfile.ZipFile(target) as z:
            rows = sorted(((i.compress_size, i.file_size, i.filename) for i in z.infolist() if not i.is_dir()),
                          reverse=True)
        for c, r, n in rows:
            print(f"{c / 1024:8.1f}K {r / 1024:8.1f}K  {n}")
        size = os.path.getsize(target)
        line = f"zip: {size / 1024:.1f} KB"
        if previous:
            old = os.path.getsize(previous)
            line += f" ({(size - old) / 1024:+.1f} KB against {os.path.basename(previous)})"
        print(line)
    else:
        for f in sorted(files, key=lambda f: -os.path.getsize(os.path.join(root, f))):
            print(f"{'':>9} {os.path.getsize(os.path.join(root, f)) / 1024:8.1f}K  {f}")

    for p in problems:
        print("PROBLEM:", p)
    print(f"{len(problems)} problem(s): {target}")
    if tmp:
        tmp.cleanup()
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", help="theme zip, or a folder that contains .rockbox/")
    ap.add_argument("--previous", help="last released zip, for the size change")
    ap.add_argument("--checkwps", default=os.environ.get("CHECKWPS"),
                    help="checkwps.hibyr1 binary (default: $CHECKWPS)")
    a = ap.parse_args()
    sys.exit(1 if run(a.target, a.previous, a.checkwps) else 0)


if __name__ == "__main__":
    main()
