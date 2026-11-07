#!/bin/bash
# Usage: rerun-0.20.0.sh <worker> <emulator-cpus>
# Re-run games with the current overrides.json, one CHD path per line taken from
# runs/queue-0.20.0-rerun.txt (append to it at any time). The previous result moves to
# runs/<RID>-superseded/<slug>. Waits when the queue is empty; stops when runs/<RID>/RERUN-STOP exists.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261106-0.20.0
CORE=cores/0.20.0-x86_64/hakux-0.20.0/lib/libretro/hakux_libretro.so
Q=runs/queue-0.20.0-rerun.txt
touch $Q
while [ ! -e runs/$RID/RERUN-STOP ]; do
  g=$(flock $Q.lock sh -c "head -n1 $Q; sed -i 1d $Q")
  if [ -z "$g" ]; then sleep 20; continue; fi
  slug=$(python3 -I -c 'import re,os,sys;print(re.sub(r"[^a-z0-9]+","-",os.path.splitext(os.path.basename(sys.argv[1]))[0].lower()).strip("-"))' "$g")
  if [ -d "runs/$RID/$slug" ]; then
    mkdir -p runs/$RID-superseded && rm -rf "runs/$RID-superseded/$slug" && mv "runs/$RID/$slug" "runs/$RID-superseded/$slug"
  fi
  taskset -c 6,7,14,15 python3 runner.py --system amd64-linux --core "$CORE" --games "$g" --out runs --run-id "$RID" \
    --worker "$1" --display gamescope --cpus "$2" --audio-dump --retroarch /opt/retroarch-hakux/bin/retroarch --redo
done
