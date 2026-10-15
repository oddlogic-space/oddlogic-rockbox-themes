# Studio Console build scripts

Generates the whole Studio Console theme (fonts, backdrops, sprites, skin files, cfg, font licence) from code.
Rebuilding from these scripts gives a tree identical, file for file, to the shipped 1.1 build.

## Requirements
- Python 3 with `Pillow`, `numpy`, `fonttools`
- Fonts installed on the build machine:
  - Noto Sans CJK JP Bold (`/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc`)
  - GNU Unifont JP (`/usr/share/fonts/opentype/unifont/unifont_jp.otf`)
  - Inter (menus and mock-ups, found with `fc-match`)
- DSEG7 Classic Bold (digit font), not stored in this repo: download DSEG v0.46 from https://github.com/keshikan/DSEG, unpack it, and point `DSEG_DIR` at the folder that contains `DSEG7-Classic/`.

## Build
```sh
export DSEG_DIR=~/fonts/fonts-DSEG_v046
python3 build.py out/m studioconsole "Studio Console"   # writes out/m/.rockbox/...
python3 lint.py out/m studioconsole                   # structural lint
python3 preview.py out/m studioconsole out/prev          # screen mock-ups from the real assets
(cd out/m && zip -rqDX9 ../studioconsole.zip .rockbox)   # upload-ready zip
```
Then run the parser check and the simulator (`../simulator/test-theme.sh`) before releasing.

## Layout
| Path | Purpose |
|---|---|
| `build.py` | Entry point: writes the full `.rockbox/` tree |
| `bt_fonts.py` | RB12 bitmap fonts: Noto 21 and 28 px, Unifont 16 px, DSEG7 digits (sizes 20, 14, 13) |
| `bt_img.py` | Backdrops (menu, playback) and sprites, with the coordinates used by the skins |
| `bt_skin.py` | Generates the `.sbs`, `.wps` and `.cfg` text |
| `lint.py`, `preview.py` | Structural lint and screen previews |
| `lib/` | Drawing helpers shared by the image code (`kit`, `parts`, `dir*`, `menus`, `fntlib`) |
| `licence/COPYING-fonts.txt` | Font licence template filled in per build |

## Notes
- Font cell rules: Noto height = ceil(size x 1.09), ascent = round(size x 0.88); DSEG7 height = size + 4, ascent = size + 2.
- Fonts are 1-bit and subset (28 px covers JIS level 1 kanji only) to keep the zip small.
- Do not commit generated output (`out/`).
