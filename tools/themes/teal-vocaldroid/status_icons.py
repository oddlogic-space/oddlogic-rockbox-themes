"""Status-bar icons: headset (volume) and the segmented-ladder battery (frame + 1-bit fill mask)."""
from PIL import Image, ImageDraw, ImageOps

BAR = (0x16, 0x28, 0x2B); TEAL = (0x39, 0xC5, 0xBB); LINE = (0x8F, 0xB3, 0xB0); MAG = (0xE2, 0x50, 0x9A)
S = 8
BATT_W, BATT_H = 30, 40                 # frame image; drawn at (444, 5)
FILL_BOX = (7, 8, 16, 28)               # fill viewport inside the frame: x, y, w, h  -> screen (451, 13)


def P(pts):
    return [(x * S, y * S) for x, y in pts]


def bez(p0, p1, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


def headset():
    w, h = 24, 20
    im = Image.new("RGB", (w * S, h * S), BAR); d = ImageDraw.Draw(im)
    d.arc([4 * S, 1.5 * S, 20 * S, 17.5 * S], 180, 360, fill=TEAL, width=int(2.2 * S))
    d.rounded_rectangle([1 * S, 8.5 * S, 6.5 * S, 16.5 * S], radius=2.2 * S, fill=TEAL)
    d.rounded_rectangle([17.5 * S, 8.5 * S, 23 * S, 16.5 * S], radius=2.2 * S, fill=TEAL)
    d.line(P(bez((3.5, 16.5), (4, 19.5), (10, 18.6))), fill=LINE, width=int(1.5 * S), joint="curve")
    d.ellipse([8.6 * S, 17.0 * S, 12.0 * S, 20.3 * S], fill=MAG)
    return im.resize((w, h), Image.LANCZOS)


def battery_frame():
    im = Image.new("RGB", (BATT_W * S, BATT_H * S), BAR); d = ImageDraw.Draw(im)
    d.rounded_rectangle([11 * S, 1 * S, 19 * S, 5 * S], radius=1.5 * S, fill=LINE)
    d.rounded_rectangle([4 * S, 4 * S, 26 * S - 1, 39 * S], radius=5 * S, fill=LINE)
    d.rounded_rectangle([6 * S, 6 * S, 24 * S - 1, 37 * S + S - 1], radius=3.2 * S, fill=BAR)
    return im.resize((BATT_W, BATT_H), Image.LANCZOS)


def battery_fill():
    """Five 4px segments with 2px gaps. 1-bit BMP: black pixels are the ink (drawn in the viewport's foreground)."""
    fx, fy, fw, fh = FILL_BOX
    m = Image.new("L", (fw * S, fh * S), 0); d = ImageDraw.Draw(m)
    for i in range(5):
        y0 = fh - (i + 1) * 4 - i * 2
        d.rounded_rectangle([0, y0 * S, fw * S - 1, (y0 + 4) * S - 1], radius=1 * S, fill=255)
    m = m.resize((fw, fh), Image.LANCZOS).point(lambda v: 255 if v > 127 else 0)
    return ImageOps.invert(m).convert("1")
