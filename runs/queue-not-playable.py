#!/usr/bin/env python3
"""Print the CHD paths whose amd64-linux stage in compat.json is tested but not Playable.

Usage: runs/queue-not-playable.py [CHD dir] > runs/queue-<name>.txt
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/projects/fetch_games/downloads/xbox-ntsc-u/CHD")

games = json.load(open(os.path.join(HERE, "..", "compat.json")))["games"]
for g in sorted(games.values(), key=lambda g: g["file"].lower()):
    stage = g.get("results", {}).get("amd64-linux", {}).get("stage", "Untested")
    path = os.path.join(CHD, g["file"])
    if stage not in ("Playable", "Untested") and os.path.exists(path):
        print(path)
