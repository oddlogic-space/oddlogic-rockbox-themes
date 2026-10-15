# Theme kit checks

Release checks shared by every theme. They run on a built zip (or a folder that contains `.rockbox/`).

```sh
tools/kit/build-checkwps.sh                        # once: builds Rockbox's checkwps for the HiBy R1, prints its path
python3 tools/kit/check_theme.py out.zip --previous themes/<slug>/download/<old>.zip --checkwps <path>
tools/kit/check-all.sh                             # every zip in themes/*/download/
```

## What is checked
| Check | Why |
|---|---|
| Only the `.rockbox/` tree, lowercase paths, no `.DS_Store`/`__MACOSX`/`Thumbs.db` | themes.rockbox.org rejects anything else (`COPYING-<name>.txt` licence files are allowed) |
| `checkwps` on every `.wps`, `.sbs` and `.cfg` | Rockbox's own skin engine parser at the simulator's pinned commit. It also loads every image and font a skin names, and catches parameter errors the syntax parser misses, such as an image bar with `noborder` |
| RB12 font layout | a missing pad byte before the offset table makes Rockbox drop the whole skin back to the stock screen; `checkwps` does not load font files |
| Files no skin or cfg uses | keeps the zip light |
| cfg header links the GitHub repo, no email, foreground and background colours set, no `peak meter ...` or `list separator color` settings | upload rules |
| Size table, largest first, and the change from `--previous` | report with every build |

## Requirements
gcc, make, git, perl and the SDL2 headers (`libsdl2-dev`) to build `checkwps`; Python 3.

## What it cannot prove
Runtime drawing (flashing images, text cleared by a later viewport, tile-list quirks). Use the simulator (`tools/simulator/test-theme.sh`) and a device test for those.

## Known findings on the 1.1 zips
In Love and Pretty Sad each ship an unused font (`40-inlove.fnt`, `40-prettysad.fnt`). They are removed in each theme's next version, so their checks report one problem until then.
