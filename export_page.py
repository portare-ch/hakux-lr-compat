#!/usr/bin/env python3
"""Build the shareable compatibility page from compat.json.

  export_page.py <out dir>

Writes <out>/index.html (the list as embedded JSON, from page_template.html),
<out>/web.html (the same page as a whole HTML document, for a web server, as
https://hakuxlr.portareos.org serves it next to packs/) and <out>/packs/. An artifact holds at most 511 files, so the captures are
packed in groups of GROUP games, in the order the games were tested:

  packs/gNNN-<hash>-t.webp  thumbnails, 320x240, a row per game (boot, mid, final)
  packs/gNNN-<hash>-f.webp  the same at 800x600, loaded by the screenshot viewer
  packs/gNNN-<hash>.ogg     the last SLOT s of each game's recording, back to
                            back, re-encoded as 32 kbit/s Opus

packs.json (next to this script) keeps the assignment, so a group's files
change (under a new hash) only while the group fills. A retested game gets a
new row; its old row stays in place, unused, and a group with no row in use is
dropped. Pack files no longer used are deleted from <out>/packs.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compat  # noqa: E402  (issue_search)
PACKS = os.path.join(HERE, "packs.json")
SHOTS = ("boot", "mid", "final")
GROUP = 6
SLOT = 46.0
THUMB, FULL = "320x240", "800x600"
FORMAT = 1  # bump to rebuild every pack


# The artifact host wraps the page in a document with this reset; a web server gets it written out.
WEB_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Which original Xbox games run on hakuX-lr: status, screenshots and tested hardware for every NTSC-U disc.">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px system-ui,-apple-system,"Segoe UI",sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
"""


def run(*cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def key_of(r):
    return f"{r.get('config', {}).get('run_id')}|{r.get('tested_at')}"


def has_recording(r):
    """A recording with samples in it (a game that never played a sample leaves an empty file)."""
    secs = (r or {}).get("auto", {}).get("audio_seconds")
    return bool(r) and "audio" in r.get("captures", {}) and (secs is None or secs > 0.5)  # None: ingested before it was kept


def audio_from(r):
    """Where the page's excerpt starts: the last SLOT seconds of the recording."""
    return round(max(0.0, (r.get("auto", {}).get("audio_seconds") or 0) - SLOT), 1)


def assign(db):
    """Give every tested result a (group, row) slot; returns the groups and {member id: (group, row)}."""
    st = json.load(open(PACKS)) if os.path.exists(PACKS) else {"group": GROUP, "groups": []}
    groups = st["groups"]
    todo = []
    for slug, g in db["games"].items():
        for sid, r in g["results"].items():
            if r.get("stage", "Untested") != "Untested" and r.get("captures"):
                todo.append((r.get("tested_at") or "", f"{sid}/{slug}", key_of(r)))
    current = {mid: k for _, mid, k in todo}
    slots = {}
    for gi, grp in enumerate(groups):
        for row, m in enumerate(grp):
            # a row whose game was retested stays in place, unused, so the pack's files don't change
            if m and current.get(m["id"]) == m["key"]:
                slots[m["id"]] = (gi, row)
    for _, mid, k in sorted(todo):
        if mid in slots:
            continue
        if not groups or len(groups[-1]) >= GROUP:
            groups.append([])
        groups[-1].append({"id": mid, "key": k})
        slots[mid] = (len(groups) - 1, len(groups[-1]) - 1)
    json.dump(st, open(PACKS, "w"), indent=0)
    return groups, slots


def build(gi, members, slots, db, out):
    """The group's files; rows that are no longer used are blank if the files have to be made again."""
    live = [bool(m) and slots.get(m["id"]) == (gi, row) for row, m in enumerate(members)]
    if not any(live):
        return None, []
    h = hashlib.sha1(json.dumps([FORMAT, members], sort_keys=True).encode()).hexdigest()[:8]
    base = f"packs/g{gi + 1:03d}-{h}"
    want = [base + "-t.webp", base + "-f.webp"]
    results = []
    for m, ok in zip(members, live):
        if ok:
            sid, slug = m["id"].split("/", 1)
            results.append(db["games"][slug]["results"][sid])
        else:
            results.append(None)
    has_audio = any(has_recording(r) for r in results)
    if has_audio:
        want.append(base + ".ogg")
    if all(os.path.exists(os.path.join(out, w)) for w in want):
        return base, want
    with tempfile.TemporaryDirectory() as tmp:
        blank = os.path.join(tmp, "blank.png")
        run("magick", "-size", FULL, "xc:#1d231f", blank)
        for size, suffix, q in ((THUMB, "-t.webp", "72"), (FULL, "-f.webp", "70")):
            args = []
            for r in results:
                caps = (r or {}).get("captures", {})
                imgs = [os.path.join(HERE, caps[s]) if s in caps else blank for s in SHOTS]
                args += ["(", *imgs, "-resize", size + "!", "+append", ")"]
            run("magick", *args, "-append", "-quality", q, os.path.join(out, base + suffix))
        if has_audio:
            cmd, filt = ["ffmpeg", "-v", "error", "-y"], ""
            for i, r in enumerate(results):
                caps = (r or {}).get("captures", {})
                if has_recording(r):
                    cmd += ["-ss", str(audio_from(r)), "-i", os.path.join(HERE, caps["audio"])]
                else:
                    cmd += ["-f", "lavfi", "-t", str(SLOT), "-i", "anullsrc=r=48000:cl=stereo"]
                filt += (f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,"
                         f"apad=whole_dur={SLOT},atrim=0:{SLOT},asetpts=N/SR/TB[a{i}];")
            filt += "".join(f"[a{i}]" for i in range(len(results))) + f"concat=n={len(results)}:v=0:a=1[o]"
            run(*cmd, "-filter_complex", filt, "-map", "[o]", "-c:a", "libopus", "-b:a", "32k",
                os.path.join(out, base + ".ogg"))
    return base, want


def main():
    out = os.path.abspath(sys.argv[1])
    os.makedirs(os.path.join(out, "packs"), exist_ok=True)
    db = json.load(open(os.path.join(HERE, "compat.json")))
    groups, slots = assign(db)
    bases, keep = {}, set()
    for gi, members in enumerate(groups):
        base, files = build(gi, members, slots, db, out)
        bases[gi] = (base, len(members))
        keep.update(files)
    for f in os.listdir(os.path.join(out, "packs")):
        if f"packs/{f}" not in keep:
            os.remove(os.path.join(out, "packs", f))
    configs, games = {}, []
    for slug, g in sorted(db["games"].items(), key=lambda kv: (kv[1]["title"].lower(), kv[0])):
        entry = {"slug": slug, "title": g["title"], "file": g["file"], "size": g.get("size"),
                 "region": g.get("region"), "title_id": g.get("title_id"), "issues": compat.issue_search(g),
                 "results": {}}
        for sid, r in g["results"].items():
            if r.get("stage", "Untested") == "Untested" or (
                    "result" in r.get("captures", {}) and not os.path.exists(os.path.join(HERE, r["captures"]["result"]))):
                entry["results"][sid] = {"stage": "Untested"}  # not run, or being run again right now
                continue
            caps, auto, cfg = r.get("captures", {}), r.get("auto", {}), r.get("config", {})
            run_id = cfg.get("run_id")
            if run_id and run_id not in configs:
                configs[run_id] = {k: v for k, v in cfg.items() if k != "plan"} | {"plan": cfg.get("plan"), "system": sid}
            res = json.load(open(os.path.join(HERE, caps["result"]))) if "result" in caps else {}
            gi, row = slots[f"{sid}/{slug}"]
            base, rows = bases[gi]
            shots = [{"name": s, "ok": s in caps, "t": res.get("shots", {}).get(s, {}).get("asked_s")} for s in SHOTS]
            audio = None
            if has_recording(r):
                start = audio_from(r)
                audio = {"at": row * SLOT, "from": start,
                         "dur": min(SLOT, (res.get("audio", {}).get("seconds") or SLOT) - start)}
            tail = [ln[:180] for ln in res.get("core_log", {}).get("tail", [])
                    if not ln.startswith(("hakuX-hle-pb:", "hakuX-hle-emit:", "hakuX-hle-back: ff3d"))][-14:]
            entry["results"][sid] = {
                "stage": r["stage"], "outcome": r.get("outcome"), "reviewed": r.get("reviewed", False),
                "reviewed_by": r.get("reviewed_by"), "obs": r.get("observations", {}),
                "auto": {k: auto.get(k) for k in ("outcome", "why", "fps_median", "fps_min", "fps_source",
                                                  "guest_swaps_median", "longest_hang_s", "longest_hang_after_frame",
                                                  "audio_peak_rms_dbfs", "audio_first_sound_s",
                                                  "audio_audible_fraction", "log_flags", "boot_stages", "exit",
                                                  "judge")},
                "pack": base, "row": row, "rows": rows, "shots": shots, "audio": audio,
                "run": run_id, "tested_at": r.get("tested_at"), "log_tail": tail,
            }
        games.append(entry)
    data = {"systems": db["systems"], "configs": configs, "games": games}
    tpl = open(os.path.join(HERE, "page_template.html")).read()
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = tpl.replace("/*DATA*/null", blob)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(page)
    cut = page.index("</style>") + len("</style>")   # the page's title, fonts and styles go in the head
    with open(os.path.join(out, "web.html"), "w") as f:
        f.write(WEB_HEAD + page[:cut] + "\n</head>\n<body>\n" + page[cut:].lstrip("\n") + "\n</body>\n</html>\n")
    print(f"{len(games)} games, {len(groups)} packs ({len(keep)} files) -> {out}")


if __name__ == "__main__":
    main()
