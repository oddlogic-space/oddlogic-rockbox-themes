"""Simulated screens: real backdrops + sprites + the real .fnt files, at the positions written in the skins."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from PIL import Image
from fntlib import Fnt
import bt_img as I
ROOT, ID, OUT = sys.argv[1:4]
IM = f"{ROOT}/.rockbox/wps/{ID}/"
img = lambda n: Image.open(IM + n).convert("RGB")
fn = {k: Fnt(f"{ROOT}/.rockbox/fonts/{ID}-{k}.fnt") for k in ("16", "24", "32", "s20", "s14", "s13")}
AM = (255, 176, 56); DIM = (192, 124, 32); CR = (210, 206, 188)
def frame(src, i, n): h = src.height // n; return src.crop((0, i * h, src.width, (i + 1) * h))
def put(im, src, xy, i=0, n=1): im.paste(frame(src, i, n), xy)
def hdr(im, title):
    fn["24"].draw(im, 24, 21, title, AM); fn["24"].draw(im, 272, 21, "12:09", AM); put(im, img("hbat.bmp").crop((0, 0, 29, 22)), (366, 22)); fn["24"].draw(im, 404, 21, "80%", AM)
def ftr(im, playing=True):
    if playing:
        fn["24"].draw(im, 32, 717, "Song Title", AM); fn["16"].draw(im, 32, 741, "Artist Name", DIM); fn["24"].draw(im, 358, 718, "1:24", AM, "r", 94)
        im.paste(img("pbf.bmp").crop((0, 0, 190, 7)), (20, 770))
    else: fn["16"].draw(im, 32, 728, "NOTHING PLAYING", DIM)
def menu(names, sel, playing=True):
    im = img("bg_menu.bmp"); pad, ic, ics = img("pad.bmp"), img("ic.bmp"), img("ics.bmp")
    order = ["Recent Bookmarks", "Files", "Database", "Now Playing", "Settings", "Playlists", "Bluetooth", "Plugins", "System", "Shortcuts"]
    for i, (nm, k) in enumerate(names):
        cx, cy = I.CELLX + (i % 2) * 226, I.CELLY + (i // 2) * 124; s = i == sel
        put(im, pad, (cx, cy), int(s), 2); put(im, ics if s else ic, (cx + 83, cy + 19), k - 1, 11)
        f = fn["16"]; f.draw(im, cx + 13, cy + 85, nm, (242, 255, 244) if s else (180, 186, 192), "c", 200)
    hdr(im, "Rockbox"); ftr(im, playing); return im
def rows(names, sel, title):
    im = img("bg_menu.bmp"); rw = img("rows.bmp")
    for i, nm in enumerate(names):
        cy = I.CELLY + i * 76; s = i == sel; put(im, rw, (I.CELLX, cy), int(s), 2)
        fn["24"].draw(im, I.CELLX + 26, cy + 26, nm, (242, 255, 244) if s else (180, 186, 192))
    im.paste(img("thumb.bmp"), (450, 80 + 40)); hdr(im, title); ftr(im); return im
def wps(cjk=False, vol=.62, pos=.38, lvl=(15, 11)):
    im = img("bg_wps.bmp"); T = ("夜明けのスキャット", "星野 ミドリ", "深夜放送") if cjk else ("Song Title", "Artist Name", "Album Name")
    ml = img("ml.bmp")
    for x, n in ((274, lvl[0]), (318, lvl[1])):
        h = int(294 * n / 19); im.paste(ml.crop((0, 294 - h, 36, 294)), (x, 98 + 294 - h))
    ty = 95 + int((294 - 30) * (1 - vol)); im.paste(img("vk.bmp"), (395, ty)); fn["16"].draw(im, 366, 396, "-18 dB", AM, "c", 102)
    fn["32"].draw(im, 26, 278, T[0], AM); fn["24"].draw(im, 26, 322, T[1], DIM); fn["16"].draw(im, 26, 352, T[2], DIM)
    im.paste(img("bf.bmp").crop((0, 0, 66, 12)), (376, 22)); x, y, w, h = I.seg_rect("batt"); fn["s13"].draw(im, x, y, "80", AM, "r", w)
    for t, x0, w in (("FLAC", 12, 62), ("1419k", 79, 70), ("1756/3471", 154, 106)): fn["16"].draw(im, x0, 400, t, CR, "c", w)
    x, y, w, h = I.seg_rect("clock"); fn["s20"].draw(im, x, y, "12:09", AM)
    x, y, w, h = I.seg_rect("elap"); fn["s14"].draw(im, x, y, "1:24", AM, "r", w); x, y, w, h = I.seg_rect("rem"); fn["s14"].draw(im, x, y, "-2:17", AM, "r", w)
    cx = int(34 + (446 - 34) * pos) - 15; im.paste(img("hk.bmp"), (cx, 475))
    put(im, img("pp.bmp"), (216, 590), 1, 2); put(im, img("lp.bmp"), (231, 536), 1, 2); put(im, img("sh.bmp"), (30, 712), 1, 2); put(im, img("rp.bmp"), (180, 712), 1, 5)
    return im
BT = ["Status", "Devices", "Disconnect", "Auto Connect", "Pairing", "Audio Codec", "Rename", "Advanced"]
BTJ = ["状態", "デバイス", "接続を切る", "自動接続", "ペアリング", "音声コーデック", "名前の変更", "詳細設定"]
names = [("Recent Bookmarks", 1), ("Files", 2), ("Database", 3), ("Now Playing", 4), ("Settings", 5), ("Playlists", 6), ("Bluetooth", 7), ("Plugins", 8), ("System", 9), ("Shortcuts", 10)]
namesj = [("最近のしおり", 1), ("ファイル", 2), ("データベース", 3), ("再生中", 4), ("設定", 5), ("プレイリスト", 6), ("Bluetooth", 7), ("プラグイン", 8), ("システム", 9), ("ショートカット", 10)]
S = {"menu": menu(names, 3), "menu_jp": menu(namesj, 4), "list": rows(BT, 1, "Bluetooth"), "list_jp": rows(BTJ, 2, "ブルートゥース"), "wps": wps(), "wps_jp": wps(True)}
for k, v in S.items(): v.save(f"{OUT}_{k}.png")
sh = Image.new("RGB", (3 * 490 + 10, 2 * 810 + 10), (30, 30, 30))
for i, k in enumerate(("menu", "list", "wps", "menu_jp", "list_jp", "wps_jp")): sh.paste(S[k], (10 + (i % 3) * 490, 10 + (i // 3) * 810))
sh.save(OUT + "_sheet.png")
