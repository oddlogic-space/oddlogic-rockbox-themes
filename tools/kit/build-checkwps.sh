#!/usr/bin/env bash
# Builds Rockbox's checkwps for the HiBy R1: the real skin engine parser, which also loads every image and font a skin names.
# usage: tools/kit/build-checkwps.sh      env: CHECKWPS_DIR (default ~/.cache/oddlogic/checkwps)
# Needs gcc, make, git, perl and SDL2 headers (Debian/Ubuntu: libsdl2-dev). Prints the binary path.
set -euo pipefail
ROCKBOX_COMMIT="f282ae203a6ed51e3fcb9c226e9d944a0240191a"   # same tree as tools/simulator
DIR="${CHECKWPS_DIR:-$HOME/.cache/oddlogic/checkwps}"
BIN="$DIR/checkwps.hibyr1"
if [ -x "$BIN" ] && [ "$(cat "$DIR/commit" 2>/dev/null)" = "$ROCKBOX_COMMIT" ]; then echo "$BIN"; exit 0; fi
mkdir -p "$DIR"
if [ ! -d "$DIR/rockbox/.git" ]; then
  git clone -q --filter=blob:none --no-checkout https://github.com/Rockbox/rockbox.git "$DIR/rockbox"
fi
git -C "$DIR/rockbox" fetch -q origin "$ROCKBOX_COMMIT" 2>/dev/null || true
git -C "$DIR/rockbox" checkout -q "$ROCKBOX_COMMIT"
mkdir -p "$DIR/build"
( cd "$DIR/build" && ../rockbox/tools/configure --target=hibyr1 --type=C >/dev/null && make -j"$(nproc)" >/dev/null )
cp "$DIR/build/checkwps.hibyr1" "$BIN"
echo "$ROCKBOX_COMMIT" > "$DIR/commit"
echo "$BIN"
