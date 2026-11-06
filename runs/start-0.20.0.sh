#!/bin/bash
# Usage: start-0.20.0.sh [workers=8] [kms|gamescope]
# Worker 0 uses the second argument (default kms, on the screen); the others
# run under headless gamescope. Worker w pins the emulator to CPUs w,w+8.
# Unfinished claims are cleared; games with a result.json are skipped.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261106-0.20.0
rm -rf "runs/$RID/claims"
for ((w = 0; w < ${1:-8}; w++)); do
  d=gamescope; [ $w -eq 0 ] && d=${2:-kms}
  setsid nohup runs/run-worker-0.20.0.sh $w $d "$w,$((w + 8))" >> runs/$RID.w$w.out 2>&1 < /dev/null &
  sleep 4
done
