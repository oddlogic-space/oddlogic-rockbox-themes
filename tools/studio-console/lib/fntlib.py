import struct
class Fnt:
    def __init__(s, path):
        d = open(path, "rb").read()
        s.maxw, s.h, s.asc, _ = struct.unpack("<HHHH", d[4:12])
        s.fc, s.dc, s.size, nbits, noff, nwid = struct.unpack("<IIIIII", d[12:36])
        ow = 4 if nbits >= 0xFFDB else 2
        pad = (-nbits) % 4 if ow == 4 else nbits % 2
        o = 36; s.bits = d[o:o+nbits]; o += nbits + pad
        s.offs = [struct.unpack("<I" if ow == 4 else "<H", d[o+i*ow:o+i*ow+ow])[0] for i in range(noff)]; o += noff*ow
        s.w = list(d[o:o+nwid])
    def width(s, t): return sum(s.w[ord(c)-s.fc] for c in t)
    def draw(s, im, x, y, t, col, align="l", box=None):
        if align != "l":
            tw = s.width(t); x = x + (box - tw)//2 if align == "c" else x + box - tw
        px = im.load()
        for ch in t:
            i = ord(ch)-s.fc; w = s.w[i]; a = s.offs[i]
            for xx in range(w):
                for yy in range(s.h):
                    if (s.bits[a+(yy//8)*w+xx] >> (yy % 8)) & 1:
                        X, Y = x+xx, y+yy
                        if 0 <= X < im.width and 0 <= Y < im.height: px[X, Y] = col
            x += w
