#!/bin/bash
# Two tagged test tracks: one Latin, one Japanese (checks CJK in the playback screen and footer).
set -e; OUT="${1:?usage: make-test-music.sh <dir>}"; mkdir -p "$OUT"; cd "$OUT"
ffmpeg -loglevel error -y -f lavfi -i "sine=frequency=220:duration=90" -f lavfi -i "sine=frequency=330:duration=90" \
  -filter_complex "[0][1]amerge=inputs=2,tremolo=f=3:d=0.8" -ar 44100 -metadata title="Midnight Radio" -metadata artist="The Sine Waves" \
  -metadata album="Test Tones" -metadata track="3/12" -b:a 192k 01-test.mp3
ffmpeg -loglevel error -y -f lavfi -i "sine=frequency=440:duration=90" -ar 44100 -metadata title="夜明けのスキャット" \
  -metadata artist="星野 ミドリ" -metadata album="深夜放送" 02-cjk.flac
