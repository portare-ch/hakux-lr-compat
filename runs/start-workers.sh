#!/bin/bash
# start-workers.sh <count>: worker 0 on the screen (KMS), the others under headless gamescope.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261105-0.19.1-ingame
rm -rf "runs/$RID/claims"   # Clear unfinished claims; result.json marks completed games.
for ((w = 0; w < ${1:-3}; w++)); do
  d=kms; [ $w -gt 0 ] && d=gamescope
  setsid nohup runs/run-worker.sh $w $d >> runs/$RID.w$w.out 2>&1 < /dev/null &
  sleep 4
done
