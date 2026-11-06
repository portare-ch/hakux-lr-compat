#!/bin/bash
# One worker of the parallel 0.19.1 in-game pass: run-worker-pinned.sh <worker> <kms|gamescope> <emulator cpus>
# The emulator runs on its own core (both SMT threads); the runner, the judge and the audio recorder
# run on the cores kept free for them (6, 7 and their siblings 14, 15). All workers take games from the
# same queues in the same order; runs/<id>/claims makes sure each game is run once.
cd "$(dirname "$0")/.."
RID=amd64-linux-20261105-0.19.1-ingame
CORE=cores/0.19.1-x86_64/hakux-0.19.1/lib/libretro/hakux_libretro.so
for q in top priority other; do
  mapfile -t G < runs/queue-ingame-$q.txt
  taskset -c 6,7,14,15 python3 runner.py --system amd64-linux --core "$CORE" --games "${G[@]}" --out runs \
    --run-id "$RID" --worker "$1" --display "$2" --cpus "$3" --claims || exit $?
done
