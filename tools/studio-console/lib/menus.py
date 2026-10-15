from parts import *
import parts
from dirF import track
from dirG import seg, mixed, SG, CJ
from kit import SS
AM = AMB
CREAMK = (222, 214, 190)
def icon(cv, kind, cx, cy, s, col, bg=None):
    w = max(2.0, s * .075)
    if kind == "bookmark":
        cv.poly([(cx - .34 * s, cy - .46 * s), (cx + .34 * s, cy - .46 * s), (cx + .34 * s, cy + .46 * s), (cx, cy + .22 * s), (cx - .34 * s, cy + .46 * s)], col)
    elif kind == "folder":
        cv.rect([cx - .5 * s, cy - .32 * s, cx - .08 * s, cy - .18 * s], fill=col, r=2); cv.rect([cx - .5 * s, cy - .24 * s, cx + .5 * s, cy + .38 * s], fill=col, r=3)
    elif kind == "db":
        for k in range(3):
            y = cy - .3 * s + k * .3 * s
            cv.rect([cx - .42 * s, y - .12 * s, cx + .42 * s, y + .14 * s], fill=col, r=.12 * s)
            cv.rect([cx - .34 * s, y + .01 * s, cx + .34 * s, y + .03 * s], fill=bg or (0, 0, 0))
    elif kind == "play":
        cv.ell(cx, cy, .5 * s, fill=col); cv.poly([(cx - .14 * s, cy - .26 * s), (cx - .14 * s, cy + .26 * s), (cx + .28 * s, cy)], bg or (0, 0, 0))
    elif kind == "settings":
        for k, p in enumerate((.3, .65, .45)):
            x = cx - .36 * s + k * .36 * s
            cv.rect([x - w / 2, cy - .45 * s, x + w / 2, cy + .45 * s], fill=col, r=1)
            ky = cy - .45 * s + p * .9 * s; cv.rect([x - .13 * s, ky - .08 * s, x + .13 * s, ky + .08 * s], fill=col, r=2)
    elif kind == "list":
        for k in range(4):
            y = cy - .36 * s + k * .24 * s; cv.ell(cx - .4 * s, y, .06 * s, fill=col); cv.rect([cx - .26 * s, y - w / 2, cx + .46 * s, y + w / 2], fill=col, r=1)
    elif kind == "wireless":
        cv.rect([cx - w / 2, cy - .1 * s, cx + w / 2, cy + .46 * s], fill=col); cv.ell(cx, cy - .12 * s, .09 * s, fill=col)
        for r_ in (.28, .46):
            cv.d.arc([S(cx - r_ * s), S(cy - .12 * s - r_ * s), S(cx + r_ * s), S(cy - .12 * s + r_ * s)], 215, 325, fill=col, width=S(w))
            cv.d.arc([S(cx - r_ * s), S(cy - .12 * s - r_ * s), S(cx + r_ * s), S(cy - .12 * s + r_ * s)], 35, 145 - 180 + 180, fill=None) if False else None
    elif kind == "plugin":
        cv.rect([cx - .26 * s, cy - .08 * s, cx + .26 * s, cy + .32 * s], fill=col, r=.1 * s)
        cv.rect([cx - .16 * s, cy - .44 * s, cx - .08 * s, cy - .06 * s], fill=col); cv.rect([cx + .08 * s, cy - .44 * s, cx + .16 * s, cy - .06 * s], fill=col)
        cv.rect([cx - w / 2, cy + .32 * s, cx + w / 2, cy + .5 * s], fill=col)
    elif kind == "gear":
        cv.ell(cx, cy, .3 * s, fill=col)
        for k in range(8):
            a = k * math.pi / 4; px, py = math.cos(a), math.sin(a); qx, qy = -py, px
            r0, r1, hw = .26 * s, .46 * s, .11 * s
            cv.poly([(cx + px * r0 + qx * hw, cy + py * r0 + qy * hw), (cx + px * r1 + qx * hw * .8, cy + py * r1 + qy * hw * .8), (cx + px * r1 - qx * hw * .8, cy + py * r1 - qy * hw * .8), (cx + px * r0 - qx * hw, cy + py * r0 - qy * hw)], col)
        cv.ell(cx, cy, .12 * s, fill=bg or (0, 0, 0))
    elif kind == "bolt":
        cv.poly([(cx + .1 * s, cy - .5 * s), (cx - .3 * s, cy + .08 * s), (cx - .02 * s, cy + .08 * s), (cx - .12 * s, cy + .5 * s), (cx + .3 * s, cy - .1 * s), (cx + .02 * s, cy - .1 * s)], col)
    elif kind == "resume":
        cv.poly([(cx - .36 * s, cy - .3 * s), (cx - .36 * s, cy + .3 * s), (cx - .02 * s, cy)], col); cv.poly([(cx + .04 * s, cy - .3 * s), (cx + .04 * s, cy + .3 * s), (cx + .38 * s, cy)], col)
ITEMS = [("Recent Bookmarks", "bookmark"), ("Files", "folder"), ("Database", "db"), ("Now Playing", "play"), ("Settings", "settings"), ("Playlists", "list"), ("Bluetooth", "wireless"), ("Plugins", "plugin"), ("System", "gear"), ("Shortcuts", "bolt")]
def header(cv, title, jp=False):
    cv.brushed([0, 0, 480, 800], (96, 106, 98), amt=4, seed=7)
    cv.shadow([10, 8, 470, 58], 8, 4, (0, 3), 150)
    cv.rect([10, 8, 470, 58], fill=(14, 14, 12), r=8); cv.rect([10, 8, 470, 58], outline=(70, 68, 60), w=2, r=8); cv.rect([15, 13, 465, 53], fill=(26, 20, 12), r=5)
    mixed(cv, (26, 34), title, 24, AM)
    cv.rect([318, 15, 396, 51], fill=(14, 12, 8), r=3); seg(cv, (326, 33), "88:88", "12:09", 14, AM)
    # mini battery gauge
    cols = [(255, 60, 40), (255, 170, 30), (255, 170, 30)] + [(70, 230, 80)] * 7
    cv.rect([404, 17, 460, 49], fill=(4, 4, 4), r=3)
    for i, col in enumerate(cols):
        x = 407 + i * 5.0; on = i < 8
        cv.rect([x, 23, x + 3.6, 43], fill=c3(col if on else mixc(col, (0, 0, 0), .8)), r=1)
def footer(cv):
    cv.shadow([10, 704, 470, 790], 8, 4, (0, 3), 150)
    cv.rect([10, 704, 470, 790], fill=(44, 48, 46), r=8); cv.rect([10, 704, 470, 790], outline=(18, 20, 18), w=1.5, r=8)
    cv.rect([20, 712, 340, 760], fill=(14, 12, 8), r=5); cv.rect([20, 712, 340, 760], outline=(70, 68, 60), w=1.6, r=5)
    cv.rect([24, 716, 336, 756], fill=(26, 20, 12), r=3)
    mixed(cv, (32, 730), "Song Title", 18, AM); mixed(cv, (32, 749), "Artist Name", 12, c3(mixc(AM, (0, 0, 0), .3)))
    cv.rect([350, 712, 460, 760], fill=(14, 12, 8), r=5); cv.rect([350, 712, 460, 760], outline=(70, 68, 60), w=1.6, r=5)
    seg(cv, (360, 730), "88:88", "01:24", 17, AM); track(cv, (360, 750), "ELAPSED", 8, (200, 190, 160), "lm", 1.2)
    cv.rect([20, 770, 460, 777], fill=(6, 6, 6), r=3.5); cv.rect([20, 770, 190, 777], fill=(255, 150, 40), r=3.5)
    for sx, sy in ((18, 712), (462, 712), (18, 782), (462, 782)): cv.screw(sx, sy, 3, (130, 128, 120), sx / 200)
def tile_key(cv, x, y, name, kind, sel):
    w, h = 226, 124
    cv.rect([x, y, x + w, y + h], fill=(30, 34, 32), r=6); cv.rect([x, y, x + w, y + h], outline=(14, 16, 14), w=1.2, r=6)
    dy = 3 if sel else 0
    face = (234, 226, 200) if not sel else (250, 240, 205)
    cv.shadow([x + 8, y + 8 + dy, x + w - 8, y + h - 8 + dy], 5, 3, (0, 3), 150 if not sel else 70)
    cv.grad([x + 8, y + 8 + dy, x + w - 8, y + h - 8 + dy], c3(mixc(face, (255, 255, 255), .25)), c3(mixc(face, (0, 0, 0), .16 if not sel else .08)), r=5)
    cv.rect([x + 8, y + 8 + dy, x + w - 8, y + h - 8 + dy], outline=c3(mixc(face, (0, 0, 0), .55)), w=1.2, r=5)
    icon(cv, kind, x + w / 2, y + 44 + dy, 54, (40, 36, 30), face)
    mixed(cv, (x + w / 2 - F("FreeMono", 16, "Bold").getlength(name) / SS / 2, y + 96 + dy), name, 16, (40, 36, 30))
    if sel:
        cv.rect([x + 3, y + 3, x + w - 3, y + h - 3], outline=(255, 150, 40), w=3, r=7)
        cv.led(x + 20, y + 20, 4.2, (255, 90, 50))
    else: cv.led(x + 20, y + 20, 4.2, (255, 90, 50), on=False)
def tile_dark(cv, x, y, name, kind, sel):
    w, h = 226, 124
    if not sel:
        cv.grad([x + 4, y + 4, x + w - 4, y + h - 4], (40, 44, 42), (24, 26, 25), r=6); cv.rect([x + 4, y + 4, x + w - 4, y + h - 4], outline=(10, 10, 10), w=1.4, r=6)
        cv.rect([x + 8, y + 8, x + w - 8, y + h - 8], outline=(70, 74, 70), w=1, r=4)
        icon(cv, kind, x + w / 2, y + 44, 52, AM, (30, 32, 30)); mixed(cv, (x + w / 2 - F("FreeMono", 16, "Bold").getlength(name) / SS / 2, y + 96), name, 16, c3(mixc(AM, (0, 0, 0), .1)))
        cv.led(x + 20, y + 20, 4, (255, 90, 50), on=False)
    else:
        cv.grad([x + 4, y + 4, x + w - 4, y + h - 4], (255, 196, 90), (226, 140, 36), r=6); cv.rect([x + 4, y + 4, x + w - 4, y + h - 4], outline=(120, 60, 10), w=1.6, r=6)
        icon(cv, kind, x + w / 2, y + 44, 52, (36, 22, 8), (240, 170, 60)); mixed(cv, (x + w / 2 - F("FreeMono", 16, "Bold").getlength(name) / SS / 2, y + 96), name, 16, (36, 22, 8))
        cv.led(x + 20, y + 20, 4.2, (255, 60, 40))
def main_menu(style, sel=3):
    cv = Cv((96, 106, 98)); header(cv, "Rockbox"); footer(cv)
    cv.rect([10, 66, 470, 696], fill=(34, 36, 34), r=8); cv.rect([10, 66, 470, 696], outline=(16, 16, 16), w=1.5, r=8)
    for i, (n, k) in enumerate(ITEMS):
        x = 11 + (i % 2) * 226 + 2 * (i % 2); y = 72 + (i // 2) * 124
        (tile_key if style == "key" else tile_dark)(cv, x, y, n, k, i == sel)
    return cv
def list_screen(jp=False):
    cv = Cv((96, 106, 98)); header(cv, "ブルートゥース" if jp else "Bluetooth"); footer(cv)
    cv.rect([10, 66, 470, 696], fill=(34, 36, 34), r=8); cv.rect([10, 66, 470, 696], outline=(16, 16, 16), w=1.5, r=8)
    rows = ["状態", "デバイス", "接続を切る", "自動接続", "ペアリング", "音声コーデック", "名前の変更", "詳細設定"] if jp else ["Status", "Devices", "Disconnect", "Auto Connect", "Pairing", "Audio Codec", "Rename", "Advanced"]
    for i, t in enumerate(rows):
        y = 78 + i * 76; sel = i == 1
        if sel:
            cv.grad([18, y, 442, y + 66], (255, 200, 96), (230, 146, 40), r=6); cv.rect([18, y, 442, y + 66], outline=(120, 60, 10), w=1.6, r=6)
            cv.rect([18, y, 38, y + 66], fill=(200, 56, 44), r=6); cv.rect([32, y, 38, y + 66], fill=(200, 56, 44))
            mixed(cv, (56, y + 33), t, 24, (36, 22, 8)); cv.led(424, y + 33, 5, (255, 60, 40))
        else:
            cv.rect([18, y, 442, y + 66], fill=(26, 28, 26), r=6); cv.rect([18, y, 442, y + 66], outline=(60, 64, 60), w=1, r=6)
            cv.rect([18, y, 38, y + 66], fill=(52, 56, 52), r=6); cv.rect([32, y, 38, y + 66], fill=(52, 56, 52))
            mixed(cv, (56, y + 33), t, 24, AM); cv.led(424, y + 33, 5, (255, 60, 40), on=False)
    # scroll thumb
    cv.rect([452, 80, 464, 690], fill=(14, 14, 14), r=6); cv.grad([452, 80, 464, 250], (230, 220, 190), (150, 142, 120), r=6)
    return cv
if __name__ == "__main__":
    a = main_menu("key"); a.out("M1.png"); b = main_menu("dark"); b.out("M2.png"); list_screen().out("L1.png"); list_screen(True).out("L1jp.png")
