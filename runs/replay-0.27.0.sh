#!/bin/bash
# Usage: replay-0.27.0.sh <worker> <emulator-cpus> <file of game file names>
# Run games again from the overrides recorded from their guided runs
# (runs/record-overrides.py), without the guide, into the replay run.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261115-0.27.0-replay
CORE=${HAKUX_CORES:-$HOME/projects/hakux-compat/cores}/0.27.0-x86_64/hakux-0.27.0/lib/libretro/hakux_libretro.so
SAVES=${HAKUX_SAVES:-$HOME/projects/xbox-save-archive/repo/Xbox saves}
CHD=${HAKUX_CHD:-$HOME/projects/fetch_games/downloads/xbox-ntsc-u/CHD}
mapfile -t G < <(sed "s|^|$CHD/|" "$3")
exec taskset -c 6,7,14,15 python3 runner.py --system amd64-linux --core "$CORE" --games "${G[@]}" --out runs \
  --run-id "$RID" --worker "$1" --display gamescope --cpus "$2" --claims --audio-dump --saves "$SAVES" \
  --retroarch /opt/retroarch-hakux/bin/retroarch
