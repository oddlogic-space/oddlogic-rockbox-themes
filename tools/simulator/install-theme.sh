#!/bin/bash
# usage: install-theme.sh <dir containing .rockbox/> <theme id>     (theme id = the cfg file name without .cfg)
set -e; WORK="${WORK:-$HOME/rockbox-sim}"; BLD="$WORK/bld"; SRC="$1"; ID="$2"
rm -rf "$BLD/simdisk/.rockbox/wps/$ID"* "$BLD/simdisk/.rockbox/themes/$ID.cfg"
cp -r "$SRC/.rockbox/"* "$BLD/simdisk/.rockbox/"
{ grep -v '^#' "$SRC/.rockbox/themes/$ID.cfg" | grep -v '^$'; echo "touchscreen mode: point"; echo "start directory: /Music"; echo "resume: off"; } > "$BLD/simdisk/.rockbox/config.cfg"
