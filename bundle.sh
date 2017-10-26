#!/bin/sh

set -ex

NAME=lstm-results
for part in {0..4}; do 
  target="$NAME/results.$part"
  mkdir -p "$target"
  cp -l "results.$part/results.sqlite3" "$target"
done
mksquashfs "$NAME" "$NAME.squashfs" -comp xz
