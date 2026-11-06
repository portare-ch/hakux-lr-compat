#!/bin/bash
# One worker of the master-build pass over the games not yet run: run-worker-master.sh <worker> <kms|gamescope> <emulator cpus>
# Core: hakuX-lr master 8b4c43ff23 (0.19.1 + the memory fix, PR #104). Queue: runs/queue-master-untested.txt (easy-first);
# runs/<id>/claims makes sure each game is run once. Pinning as in run-worker-pinned3.sh.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261105-master-8b4c43f
CORE=cores/master-8b4c43ff23-x86_64/hakux-master/lib/libretro/hakux_libretro.so
mapfile -t G < runs/queue-master-untested.txt
exec taskset -c 6,7,14,15 python3 runner.py --system amd64-linux --core "$CORE" --games "${G[@]}" --out runs \
  --run-id "$RID" --worker "$1" --display "$2" --cpus "$3" --claims --audio-dump --retroarch /opt/retroarch-hakux/bin/retroarch
