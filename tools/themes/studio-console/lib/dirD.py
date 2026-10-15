from parts import *
def led_col(i, n):
    t = i / (n - 1)
    return (255, 70, 50) if t > .84 else (255, 184, 50) if t > .62 else (96, 226, 100)
def led_ladder(cv, cx, y_bottom, n, lit, step=16.2, r=5.6):
    for i in range(n):
        cv.led(cx, y_bottom - i * step, r, led_col(i, n), on=i < lit)
def vfader(cv, cx, y0, y1, pos, cap=(214, 96, 52)):
    cv.rect([cx - 5, y0, cx + 5, y1], fill=(8, 8, 8), r=5); cv.rect([cx - 4, y0 + 1, cx - 1, y1 - 1], fill=(0, 0, 0), r=2)
    for i in range(11):
        y = y0 + 12 + (y1 - y0 - 24) * i / 10
        cv.line([(cx - 26, y), (cx - (17 if i % 5 else 14), y)], CREAM, 1.3 if i % 5 else 1.8); cv.line([(cx + 17 if i % 5 else cx + 14, y), (cx + 26, y)], CREAM, 1.3 if i % 5 else 1.8)
    ty = y1 - 12 - (y1 - y0 - 24) * pos
    cv.shadow([cx - 22, ty - 15, cx + 22, ty + 15], 3, 3, (0, 3), 160)
    cv.grad([cx - 22, ty - 15, cx + 22, ty + 15], c3(mixc(cap, (255, 255, 255), .28)), c3(mixc(cap, (0, 0, 0), .24)), r=4)
    cv.rect([cx - 22, ty - 15, cx + 22, ty + 15], outline=c3(mixc(cap, (0, 0, 0), .55)), w=1.1, r=4)
    for dx in (-13, -8, 8, 13): cv.line([(cx + dx, ty - 11), (cx + dx, ty + 11)], c3(mixc(cap, (0, 0, 0), .3)), 1.2)
    cv.line([(cx - 18, ty), (cx + 18, ty)], (250, 240, 220), 2.2)
def draw():
    cv = Cv((70, 78, 72))
    cv.wood([0, 0, 14, 800], (120, 70, 36), (70, 38, 18), 2); cv.wood([466, 0, 480, 800], (120, 70, 36), (70, 38, 18), 5)
    cv.line([(14, 0), (14, 800)], (20, 12, 6), 1.5); cv.line([(466, 0), (466, 800)], (20, 12, 6), 1.5)
    cv.brushed([15, 0, 465, 800], (96, 106, 98), amt=4, seed=7)
    status(cv, 0, 40, (30, 32, 30), CREAM, (255, 150, 40)); cv.line([(15, 40), (465, 40)], (14, 14, 14), 2)
    # top bay: art | L R peak LEDs | volume fader
    cv.rect([22, 50, 458, 284], fill=(34, 36, 34), r=8); cv.rect([22, 50, 458, 284], outline=(16, 16, 16), w=1.5, r=8)
    cv.shadow([32, 60, 246, 274], 4, 5, (0, 3), 190); cv.rect([30, 58, 248, 276], fill=(16, 16, 16), r=4); paste_cover(cv, [36, 64, 242, 270])
    cv.rect([36, 64, 242, 270], outline=(90, 88, 80), w=1.2)
    # peak meters
    cv.rect([262, 60, 346, 274], fill=(24, 26, 24), r=6); cv.rect([262, 60, 346, 274], outline=(12, 12, 12), w=1.2, r=6)
    led_ladder(cv, 288, 252, 13, 9); led_ladder(cv, 320, 252, 13, 7)
    silk(cv, (288, 266), "L", 11, (210, 206, 188)); silk(cv, (320, 266), "R", 11, (210, 206, 188)); silk(cv, (304, 72), "PEAK", 9, (150, 146, 132))
    # volume fader
    cv.rect([358, 60, 452, 274], fill=(52, 58, 54), r=6); cv.rect([358, 60, 452, 274], outline=(16, 18, 16), w=1.2, r=6)
    vfader(cv, 405, 84, 246, .62)
    silk(cv, (405, 70), "LEVEL", 9, (210, 206, 188)); silk(cv, (405, 264), "-18 dB", 11, (255, 176, 56))
    for sx, sy in ((30, 52), (450, 52), (30, 282), (450, 282)): cv.screw(sx, sy, 3.8, (130, 128, 120), .3 + sx / 300)
    # display
    cv.shadow([24, 296, 456, 400], 8, 4, (0, 3), 150)
    cv.rect([24, 296, 456, 400], fill=(14, 14, 12), r=8); cv.rect([24, 296, 456, 400], outline=(70, 68, 60), w=2, r=8)
    cv.rect([30, 302, 450, 394], fill=(26, 20, 12), r=5)
    cv.text((42, 330), "Song Title", F("DejaVu Sans Mono", 30, "Bold"), AMB, "lm")
    cv.text((42, 360), "Artist Name", F("DejaVu Sans Mono", 17), c3(mixc(AMB, (0, 0, 0), .25)), "lm")
    cv.text((42, 382), "Album Name", F("DejaVu Sans Mono", 14), c3(mixc(AMB, (0, 0, 0), .5)), "lm")
    cv.text((438, 382), "07/12", F("DejaVu Sans Mono", 14, "Bold"), c3(mixc(AMB, (0, 0, 0), .25)), "rm")
    for i, t in enumerate(("FLAC", "1419k", "44.1k")):
        x = 28 + i * 106; cv.rect([x, 410, x + 98, 436], fill=(30, 32, 30), r=4); cv.rect([x, 410, x + 98, 436], outline=(18, 18, 18), w=1, r=4)
        cv.text((x + 49, 423), t, F("DejaVu Sans Mono", 13, "Bold"), (200, 196, 176), "mm")
    cv.rect([346, 410, 452, 436], fill=(30, 32, 30), r=4); cv.text((399, 423), "1756/3471", F("DejaVu Sans Mono", 11, "Bold"), (200, 196, 176), "mm")
    # position fader
    cv.rect([22, 448, 458, 530], fill=(52, 58, 54), r=8); cv.rect([22, 448, 458, 530], outline=(20, 22, 20), w=1.5, r=8)
    silk(cv, (38, 466), "POSITION", 10, (210, 206, 188), "lm"); silk(cv, (440, 466), "-2:17", 12, (255, 176, 56), "rm"); silk(cv, (150, 466), "1:24", 12, (255, 176, 56), "lm")
    fader_h(cv, 34, 446, 504, .38)
    for sx, sy in ((30, 456), (450, 456), (30, 522), (450, 522)): cv.screw(sx, sy, 3.8, (130, 128, 120), .8 + sy / 400)
    # transport (as A)
    cv.rect([22, 542, 458, 790], fill=(44, 48, 46), r=8); cv.rect([22, 542, 458, 790], outline=(18, 20, 18), w=1.5, r=8)
    spec = [("prev", (206, 200, 178), (30, 28, 24)), ("rew", (206, 200, 178), (30, 28, 24)), ("pause", (200, 56, 44), (250, 240, 228)), ("ff", (206, 200, 178), (30, 28, 24)), ("next", (206, 200, 178), (30, 28, 24))]
    kw = 68; gap = (400 - 5 * kw) / 4
    for i, (k, face, g) in enumerate(spec):
        x = 40 + i * (kw + gap)
        if i == 2: key(cv, [x - 6, 570, x + kw + 6, 680], face, k, g)
        else: key(cv, [x, 570, x + kw, 680], face, k, g)
        silk(cv, (x + kw / 2, 698), ["PREV", "REW", "PLAY/PAUSE", "FF", "NEXT"][i], 9, (200, 196, 176))
    cv.led(240, 560, 3.6, (255, 90, 50))
    for i, (k, t) in enumerate((("shuf", "SHUF"), ("rept", "REPT"))):
        x = 34 + i * 150; key(cv, [x, 722, x + 70, 766], (60, 64, 62), k, (255, 176, 56), r=5)
        cv.text((x + 84, 744), t, F("DejaVu Sans Mono", 10, "Bold"), (190, 186, 170), "lm"); cv.led(x + 62, 728, 2.8, (255, 176, 56), on=i == 1)
    cv.knob(396, 746, 20, ang=35); silk(cv, (396, 776), "MENU", 8, (190, 186, 170)); cv.led(440, 730, 2.8, (80, 220, 90))
    for sx, sy in ((30, 550), (450, 550), (30, 782), (450, 782)): cv.screw(sx, sy, 3.8, (130, 128, 120), 1.1 + sx / 300)
    return cv
if __name__ == "__main__": draw().out("D.png")
