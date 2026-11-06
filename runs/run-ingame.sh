#!/bin/bash
# The 0.19.1 pass with the in-game plan (up to 5 min per game). Order, for the most
# in-game results soonest (2026-11-05 16:10): the top-100 matches, then sports, racing
# and fighting games (85 % reached gameplay so far, against 52 % for the rest), then
# the rest, then the top-100 games run before the input adapted that did not reach
# the game, again.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261105-0.19.1-ingame
CORE=cores/0.19.1-x86_64/hakux-0.19.1/lib/libretro/hakux_libretro.so
run() { python3 runner.py --system amd64-linux --core "$CORE" --games "$@" --out runs --run-id "$RID"; }
for q in top priority other; do
  mapfile -t G < runs/queue-ingame-$q.txt; run "${G[@]}" || exit $?
done
python3 -I - "runs/$RID" runs/queue-ingame-top.txt > runs/queue-ingame-again.txt <<'PY'
import json, os, re, sys
run_dir, queue = sys.argv[1], [l.strip() for l in open(sys.argv[2]) if l.strip()]
for path in queue:
    slug = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(path))[0].lower()).strip("-")
    rp = os.path.join(run_dir, slug, "result.json")
    if os.path.exists(rp):
        w = json.load(open(rp)).get("watch") or {}
        if "unstuck" not in w and w.get("ingame_at_s") is None:
            print(path)
PY
mapfile -t G < runs/queue-ingame-again.txt; [ ${#G[@]} -gt 0 ] && { run "${G[@]}" --redo || exit $?; }
