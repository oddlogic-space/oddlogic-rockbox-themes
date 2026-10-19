"""Studio fonts -> Rockbox RB12 bitmap fonts: GNU Unifont 16 px, Noto Sans CJK JP Bold 21 and 28 px, DSEG7 digits.
The rasterisers and the RB12 writer are shared: see tools/themes/common/rbfont.py."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))
import rbfont  # noqa: E402
from rbfont import encode_glyph, write_fnt, jis0208, jis_level1 as jis_l1, seg7_glyphs as _seg7_glyphs  # noqa: E402,F401
DSEG = os.environ.get("DSEG_DIR", os.path.expanduser("~/fonts/fonts-DSEG_v046"))   # folder containing DSEG7-Classic/
LARGE = set(range(0x20, 0x7F)) | set(range(0xA0, 0x100)) | set(range(0x2010, 0x2030)) | set(range(0x3000, 0x3040)) \
      | set(range(0xFF01, 0xFF5F)) | jis_l1()
def seg7_glyphs(size, chars="0123456789:-/ "): return _seg7_glyphs(size, DSEG, chars)
def build(outdir, ID):
    os.makedirs(outdir, exist_ok=True)
    rbfont.pixel_font(f"{outdir}/{ID}-16.fnt", 1)
    rbfont.noto_ss_font(f"{outdir}/{ID}-24.fnt", 21)
    rbfont.noto_ss_font(f"{outdir}/{ID}-32.fnt", 28, only=LARGE)
    for s in (20, 14, 13): rbfont.seg7_font(f"{outdir}/{ID}-s{s}.fnt", s, DSEG)
if __name__ == "__main__": build("/tmp/fonttest", "t")
