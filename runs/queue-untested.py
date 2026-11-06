#!/usr/bin/env python3
"""Print the CHD paths that have no tested amd64-linux result in compat.json.

Usage: runs/queue-untested.py [CHD dir] > runs/queue-<name>.txt
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHD = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/projects/fetch_games/downloads/xbox-ntsc-u/CHD")

games = json.load(open(os.path.join(HERE, "..", "compat.json")))["games"]
tested = {g["file"] for g in games.values()
          if g.get("results", {}).get("amd64-linux", {}).get("stage", "Untested") != "Untested"}
for n in sorted(os.listdir(CHD)):
    if n.lower().endswith(".chd") and n not in tested:
        print(os.path.join(CHD, n))
