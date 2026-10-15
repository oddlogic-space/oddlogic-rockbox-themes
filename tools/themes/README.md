# Theme build scripts

Every theme is generated from code, and `tools/verify-rebuild.sh` proves the scripts still reproduce the shipped zips file for file.

| Theme | Folder | Rebuild status |
|---|---|---|
| Studio Console | `studio-console/` | identical to the 1.1 zip |
| Waveform Bot HUD | `waveform-bot-hud/` | identical to the 1.1 zip |
| Teal Vocaldroid | `teal-vocaldroid/` | identical to the 1.1 zip |
| In Love, Pretty Sad | `in-love-pretty-sad/` (one generator draws both) | both identical to their 1.1 zips |
| Drift Mountain | not yet in the repo | pending a decision on its artwork |

## Check everything
```sh
export DSEG_DIR=~/fonts/fonts-DSEG_v046      # only Studio Console needs this (DSEG7 digit font, see studio-console/README.md)
tools/verify-rebuild.sh                      # all themes, about 1.5 minutes
tools/verify-rebuild.sh in-love pretty-sad   # selected themes
```
It rebuilds each theme into a scratch folder, unzips the zip from `themes/<slug>/download/` and compares the two `.rockbox` trees. PASS means identical.

## Layout
- `common/rbfont.py`: the one shared font module for every theme: character sets (JIS X 0208, JIS level 1), the four rasterisers (Noto, supersampled Noto, Unifont pixel, DSEG7 digits), the RB12 writer and a reader for previews.
- `common/make_fonts.py`: command-line front end for the Noto rasteriser (`make_fonts.py <font.ttc> <outdir> <name> [sizes]`). Sans themes use Noto Sans CJK Medium at 28, 32 and 40 px; In Love and Pretty Sad add Noto Serif CJK SemiBold at 40 px for titles.
- `<theme>/package.py <outdir>`: builds the full `.rockbox/` tree for the theme (Studio Console uses `build.py`).
- Generated: fonts, backdrops, sprites, and (where the skins are drawn by code) the `.wps`/`.sbs`/`.cfg` text.
- Authored text kept as files: Teal Vocaldroid's skin files and cfg (`teal-vocaldroid/static/`), and the font licence files (`licence/`).

## Releasing a new version
1. Change the scripts, then bump the version and date in the cfg header (in the script, or in `static/` for Teal Vocaldroid).
2. Build, zip with `cd <outdir> && zip -rqDX9 ../<slug>.zip .rockbox`, and copy the zip to `themes/<slug>/download/`.
3. Run `tools/verify-rebuild.sh <slug>`: it should PASS against the new zip.
4. Run the simulator check (`tools/simulator/test-theme.sh`) and a device test before publishing.

## Requirements
Python 3 with Pillow, numpy and fontTools; Noto Sans CJK and Noto Serif CJK in `/usr/share/fonts/opentype/noto/`.
