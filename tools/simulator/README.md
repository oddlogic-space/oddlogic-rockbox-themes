# Rockbox UI simulator for HiBy R1 themes

Headless test rig so a theme can be checked (menus, playback, touch, CJK) without plugging in the device.
The built simulator and the Rockbox source (GPL, large) are **not** stored here. `build-simulator.sh` fetches and builds them.

## Requirements
- Linux with gcc, make, git, python3 (Pillow), ffmpeg
- SDL2 (the script builds it from source with no X11 if it is missing; uses the dummy video/audio drivers)

## Quick start
```sh
./build-simulator.sh                         # once; WORK defaults to ~/rockbox-sim
./install-theme.sh path/to/dir-with-.rockbox <theme-id>
./run-scenario.sh scenarios/menu-and-settings.txt out/menu
```
`run-scenario.sh` runs the sim headless with `RB_SIMCMD` and converts each F5 screendump to `<prefix>_N.png` (480x800).

## One-shot theme check
```sh
./test-theme.sh path/to/theme.zip <theme-id> list|tile [row1_y row2_y] [outdir]
```
Unzips, installs, plays the Latin track, pauses (PLAY), presses NEXT to the Japanese track, and writes a contact sheet `<id>_sheet.png` (menu, Files, playing, paused, CJK) plus the individual shots. Use `list` for list-style main menus (row Y defaults 176/248; Teal/Waveform use 140/196) or `tile` for tile menus. Run one theme at a time: two simulators sharing the same disk overwrite each other's settings.

## What the scripts do
| File | Purpose |
|---|---|
| `build-simulator.sh` | Clones Rockbox at a pinned commit, applies `patches/`, configures `--target=hibyr1 --type=s`, strips `-lasound`, builds, `make fullinstall`, makes test music |
| `make-test-music.sh` | ffmpeg-generated `01-test.mp3` (Latin tags) and `02-cjk.flac` (Japanese tags) |
| `install-theme.sh` | Copies the theme into the sim disk, writes `config.cfg` from the theme cfg plus `touchscreen mode: point`, `start directory: /Music`, `resume: off` |
| `run-scenario.sh` | Runs a scenario file (use an absolute path) and produces PNGs; clears stale settings/resume files first |
| `test-theme.sh` | One-shot regression check of a theme zip (see above) |

## Patches
- `0001`: a command-driver thread in `button-sdl.c` (scripted input), touch debug output, extra keys (tab, pgup, pgdn).
- `0002`: key map for the R1 hardware buttons (reuses the R3 Pro II map file).

## Scenario syntax
One command per line:
```
sleep MS
down X Y
move X Y
up X Y
key NAME        # tab, f5 (screendump), esc, enter, left, right, up, down, pgup, pgdn
quit
```
Always begin with `key tab`: it disables the sim "background" that otherwise offsets touch coordinates by (77,74).
Screendumps land in `simdisk/dump YYMMDD-HHMMSS.bmp` (note the space).

### Keyboard map (hardware buttons)
`esc` = POWER (short press = back/cancel; in the WPS = menu), `enter` = PLAY, `left` = PREV, `right` = NEXT, `pgup`/`pgdn` = VOL_UP/VOL_DOWN (patch 0002).

### Coordinates used by the studio theme (tile menu / WPS)
Files tile (127,135); Settings tile (353,260); list rows (240,110), (240,186); volume fader x=417, y 93-389 (v1.1 layout); position fader y=496; play (240,612); next (415,612); shuffle (65,735); repeat (215,735). Adjust for other themes.

## Skin-engine gotchas found with the sim
- Each `%Vl` layer clears to the backdrop/bg colour, so text over art needs a flat plate baked into the backdrop that matches the viewport rect exactly.
- Item viewports cannot combine `%xd` images and text on one line.
- A conditional `%Vf` (else branch) hides the selected item's text; use a static `%Vf`.
- Viewport height must be slightly more than the font height (16px font: 18px viewport).
- `%pL`/`%pR` meters with an image fill work, and one image label can be reused for both channels.
- `%pv(...,nobar,slider,knob)` gives a vertical touch volume fader; `%pb(...,notouch)` plus a separate `%T(seek,...,progressbar)` gives a horizontal position fader.
- `%LN` falls back to the icon sprite index in default menu order for non-English names.

## What the simulator cannot prove
Real hardware buttons and firmware behaviour, device colour depth, the vertical slider on device firmware, the USB screen, and performance/memory on the device. Do a final device check before release.
