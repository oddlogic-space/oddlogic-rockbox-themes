#!/bin/bash
# Builds a headless Rockbox UI simulator for the HiBy R1 (480x800 touch) in $WORK (default ~/rockbox-sim).
# Needs: git, gcc, make, cmake, perl, python3 (+ Pillow), ffmpeg (for the test music).  No root, no X11, no apt.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$HOME/rockbox-sim}"
ROCKBOX_COMMIT="f282ae203a6ed51e3fcb9c226e9d944a0240191a"      # the tree the patches were made against
mkdir -p "$WORK"; cd "$WORK"

# 1. SDL2 from source (only needed when sdl2-config is missing).  Video is not needed: the simulator runs with SDL's dummy driver.
if ! command -v sdl2-config >/dev/null 2>&1 && [ ! -x sdlprefix/bin/sdl2-config ]; then
  [ -d sdl ] || git clone --depth 1 --branch release-2.30.x https://github.com/libsdl-org/SDL.git sdl
  mkdir -p sdlb && (cd sdlb && cmake ../sdl -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$WORK/sdlprefix" \
     -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TEST=OFF -DSDL_X11=OFF -DSDL_WAYLAND=OFF -DSDL_OPENGL=OFF -DSDL_OPENGLES=OFF -DSDL_VULKAN=OFF \
     -DSDL_KMSDRM=OFF -DSDL_PULSEAUDIO=OFF -DSDL_ALSA=OFF -DSDL_PIPEWIRE=OFF -DSDL_JACK=OFF -DSDL_SNDIO=OFF -DSDL_DBUS=OFF -DSDL_IBUS=OFF \
     -DSDL_LIBUDEV=OFF -DSDL_HIDAPI=OFF && make -j"$(nproc)" install)
fi
[ -x sdlprefix/bin/sdl2-config ] && export PATH="$WORK/sdlprefix/bin:$PATH"

# 2. Rockbox source, pinned, with our two patches
if [ ! -d rockbox ]; then
  git clone https://github.com/Rockbox/rockbox.git rockbox
  (cd rockbox && git checkout "$ROCKBOX_COMMIT" && for p in "$HERE"/patches/*.patch; do git apply "$p"; done)
fi

# 3. configure for the R1 simulator and build
mkdir -p bld && cd bld
../rockbox/tools/configure --target=hibyr1 --type=s
# the R1 target asks for ALSA, which the simulator does not use
sed -i 's/^export LDOPTS=-lasound /export LDOPTS=/' Makefile
make -j"$(nproc)"
make fullinstall                      # fills bld/simdisk/.rockbox with fonts, codecs, default skins
"$HERE/make-test-music.sh" "$WORK/bld/simdisk/Music"
echo "simulator ready: $WORK/bld/rockboxui"
