#!/bin/bash
# Usage: run-worker-0.20.0.sh <worker> <kms|gamescope> <emulator-cpus>
# Test the untested games on the hakuX-lr 0.20.0 release.
# Queue: runs/queue-0.20.0-untested.txt (from runs/queue-untested.py).
# Shared claims prevent duplicates; CPU pinning matches run-worker-master.sh.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261106-0.20.0
CORE=cores/0.20.0-x86_64/hakux-0.20.0/lib/libretro/hakux_libretro.so
mapfile -t G < runs/queue-0.20.0-untested.txt
exec taskset -c 6,7,14,15 python3 runner.py --system amd64-linux --core "$CORE" --games "${G[@]}" --out runs \
  --run-id "$RID" --worker "$1" --display "$2" --cpus "$3" --claims --audio-dump --retroarch /opt/retroarch-hakux/bin/retroarch
