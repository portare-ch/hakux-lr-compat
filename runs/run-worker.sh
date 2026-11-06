#!/bin/bash
# Usage: run-worker.sh <worker> <kms|gamescope>
# Process top-100, sports/racing/fighting, then remaining games.
# Shared run claims prevent duplicate tests.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261105-0.19.1-ingame
CORE=cores/0.19.1-x86_64/hakux-0.19.1/lib/libretro/hakux_libretro.so
for q in top priority other; do
  mapfile -t G < runs/queue-ingame-$q.txt
  python3 runner.py --system amd64-linux --core "$CORE" --games "${G[@]}" --out runs --run-id "$RID" \
    --worker "$1" --display "$2" --claims || exit $?
done
