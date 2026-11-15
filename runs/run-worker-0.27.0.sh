#!/bin/bash
# Usage: run-worker-0.27.0.sh <worker> <kms|gamescope> <emulator-cpus>
# Re-test the games not yet Playable on the hakuX-lr 0.27.0 release, with an
# archived save on the console disk where one exists (hakuX-lr issue 213).
# Queue: runs/queue-0.27.0-not-playable.txt (from runs/queue-not-playable.py).
# Shared claims prevent duplicates; CPU pinning matches run-worker-master.sh.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261115-0.27.0
CORE=${HAKUX_CORES:-$HOME/projects/hakux-compat/cores}/0.27.0-x86_64/hakux-0.27.0/lib/libretro/hakux_libretro.so
SAVES=${HAKUX_SAVES:-$HOME/projects/xbox-save-archive/repo/Xbox saves}
mapfile -t G < runs/queue-0.27.0-not-playable.txt
exec taskset -c 6,7,14,15 python3 runner.py --system amd64-linux --core "$CORE" --games "${G[@]}" --out runs \
  --run-id "$RID" --worker "$1" --display "$2" --cpus "$3" --claims --audio-dump --saves "$SAVES" --guide-model sonnet \
  --retroarch /opt/retroarch-hakux/bin/retroarch
