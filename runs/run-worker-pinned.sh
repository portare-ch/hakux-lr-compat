#!/bin/bash
# Usage: run-worker-pinned.sh <worker> <kms|gamescope> <emulator-cpus>
# Pin the emulator to both SMT threads; reserve CPUs 6,7,14,15 for tools.
# Shared queues and run claims prevent duplicate tests.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261105-0.19.1-ingame
CORE=cores/0.19.1-x86_64/hakux-0.19.1/lib/libretro/hakux_libretro.so
for q in top priority other; do
  mapfile -t G < runs/queue-ingame-$q.txt
  taskset -c 6,7,14,15 python3 runner.py --system amd64-linux --core "$CORE" --games "${G[@]}" --out runs \
    --run-id "$RID" --worker "$1" --display "$2" --cpus "$3" --claims || exit $?
done
