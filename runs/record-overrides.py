#!/usr/bin/env python3
"""Turn guided runs into overrides, so the games can be run again without the guide.

Usage: runs/record-overrides.py <run dir> [--force] [--dry-run]

For each game of the run that reached gameplay after the guide pressed for it, writes an
override to overrides.json under the game's slug: every press the run made, at the time it
made it, with the planned presses, the unstick presses and the guide off (runner.py
recorded_override). A game that already has an override keeps it unless --force is given.
Prints the games' file names, one per line, for the re-run (runner.py --games ... without
--guide-model, in a run of its own): only that re-run's results go on the list.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import runner  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--")]
force, dry = "--force" in sys.argv, "--dry-run" in sys.argv
if len(args) != 1:
    sys.exit(__doc__)
path = os.path.join(HERE, "..", "overrides.json")
overrides = json.load(open(path))
added = []
for p in sorted(glob.glob(os.path.join(args[0], "*", "result.json"))):
    res = json.load(open(p))
    ov = res.get("recorded_override") or runner.recorded_override(res, os.path.basename(os.path.normpath(args[0])))
    if not ov:
        continue
    stem = os.path.splitext(res["game_file"])[0]
    keys = (res["game_file"], stem, runner.slugify(stem))
    if any(k in overrides for k in keys) and not force:
        print(f"# {res['game_file']}: has an override already, left as it is", file=sys.stderr)
        continue
    for k in keys[:2]:
        overrides.pop(k, None)
    overrides[keys[2]] = ov
    added.append(res["game_file"])
if added and not dry:
    with open(path, "w") as f:
        json.dump(overrides, f, indent=1, ensure_ascii=False)
        f.write("\n")
print("\n".join(added))
print(f"# {len(added)} overrides {'would be ' if dry else ''}recorded", file=sys.stderr)
