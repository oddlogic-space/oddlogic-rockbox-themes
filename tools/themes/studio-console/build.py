#!/usr/bin/env python3
"""build.py <outdir> <id> "<Theme Name>" """
import sys, os, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT, ID, NAME = sys.argv[1:4]
import bt_img as I, bt_fonts, bt_skin as K
shutil.rmtree(OUT, ignore_errors=True)
R = f"{OUT}/.rockbox"; IM = f"{R}/wps/{ID}"
for d in (IM, f"{R}/fonts", f"{R}/themes"): os.makedirs(d)
bt_fonts.build(f"{R}/fonts", ID)
I.save(I.menu_bg(), f"{IM}/bg_menu.bmp"); I.save(I.wps_bg(), f"{IM}/bg_wps.bmp")
pad, ic, ics = I.tile_sprites(); I.save(pad, f"{IM}/pad.bmp"); I.save(ic, f"{IM}/ic.bmp"); I.save(ics, f"{IM}/ics.bmp")
I.save(I.row_sprites(), f"{IM}/rows.bmp"); I.save(I.thumb(), f"{IM}/thumb.bmp"); I.save(I.header_bars(), f"{IM}/hbat.bmp"); I.save(I.footer_fill(), f"{IM}/pbf.bmp")
for k, im in I.wps_sprites().items(): I.save(im, f"{IM}/{ {'bfl':'bf'}.get(k,k) }.bmp")
open(f"{R}/wps/{ID}.sbs", "w").write(K.sbs(NAME, ID)); open(f"{R}/wps/{ID}.wps", "w").write(K.wps(NAME, ID))
open(f"{R}/themes/{ID}.cfg", "w").write(K.cfg(NAME, ID))
lic = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "licence", "COPYING-fonts.txt")).read().replace("Drift Mountain theme (dm-*.fnt)", f"{NAME} theme ({ID}-*.fnt)")
lic = lic.replace(" * GNU Unifont (dm-pix1/pix15/pix2/dots3.fnt)", f" * Noto Sans CJK JP Bold ({ID}-24.fnt, {ID}-32.fnt) - Copyright 2014-2021 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'. SIL Open Font License 1.1. https://github.com/notofonts/noto-cjk\n\n * GNU Unifont ({ID}-16.fnt)")
lic = lic.replace("dm-pix1/pix15/pix2/dots3.fnt", f"{ID}-16.fnt").replace("dm-seg20/22/24/28.fnt", f"{ID}-s13/s14/s20.fnt").replace("dm-*.fnt", f"{ID}-*.fnt")
open(f"{R}/fonts/COPYING-{ID}.txt", "w").write(lic)
print("built", OUT)
