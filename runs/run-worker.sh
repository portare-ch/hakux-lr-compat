#!/bin/bash
# One worker of the parallel 0.19.1 in-game pass: run-worker.sh <worker number> <kms|gamescope>
# All workers take games from the same queues in the same order (top-100, then sports, racing
# and fighting, then the rest); runs/<id>/claims makes sure each game is run once.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261105-0.19.1-ingame
CORE=cores/0.19.1-x86_64/hakux-0.19.1/lib/libretro/hakux_libretro.so
for q in top priority other; do
  mapfile -t G < runs/queue-ingame-$q.txt
  python3 runner.py --system amd64-linux --core "$CORE" --games "${G[@]}" --out runs --run-id "$RID" \
    --worker "$1" --display "$2" --claims || exit $?
done
