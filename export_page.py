#!/usr/bin/env python3
"""Export the compatibility page and packed media from compat.json.

  export_page.py <output-dir>

Writes index.html for embedding, web.html for standalone hosting, and packs/.
Each pack holds GROUP games in test order:

  gNNN-<hash>-t.webp  320x240 thumbnails; boot, mid and final across each row
  gNNN-<hash>-f.webp  800x600 images for the screenshot viewer

packs.json preserves assignments. Retests get new rows; old rows stay unused.
Empty groups and unused images are removed. Existing audio packs are moved
to a private sibling directory; recordings are never included in the export."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compat  # noqa: E402  (issue_search)
PACKS = os.path.join(HERE, "packs.json")
SHOTS = ("boot", "mid", "final")
GROUP = 6
THUMB, FULL = "320x240", "800x600"
FORMAT = 1  # bump to rebuild every pack


# Match the artifact host reset in the standalone document.
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


def archive_recordings(out):
    """Move legacy audio packs outside the export without deleting them."""
    packs = os.path.join(out, "packs")
    extensions = (".ogg", ".oga", ".opus", ".mp3", ".wav", ".flac", ".m4a", ".aac", ".aif", ".aiff", ".wma")
    recordings = [name for name in os.listdir(packs) if name.lower().endswith(extensions)]
    if not recordings:
        return
    private = tempfile.mkdtemp(prefix=os.path.basename(out) + "-private-audio-", dir=os.path.dirname(out))
    for name in recordings:
        shutil.move(os.path.join(packs, name), os.path.join(private, name))
    print(f"Retained {len(recordings)} recordings outside the export: {private}")


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
            # Keep superseded rows to avoid rebuilding existing packs.
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
    return base, want


def main():
    out = os.path.abspath(sys.argv[1])
    os.makedirs(os.path.join(out, "packs"), exist_ok=True)
    archive_recordings(out)
    db = json.load(open(os.path.join(HERE, "compat.json")))
    groups, slots = assign(db)
    bases, keep = {}, set()
    for gi, members in enumerate(groups):
        base, files = build(gi, members, slots, db, out)
        bases[gi] = (base, len(members))
        keep.update(files)
    for f in os.listdir(os.path.join(out, "packs")):
        if f.lower().endswith(".webp") and f"packs/{f}" not in keep:
            os.remove(os.path.join(out, "packs", f))
    configs, games = {}, []
    for slug, g in sorted(db["games"].items(), key=lambda kv: (kv[1]["title"].lower(), kv[0])):
        entry = {"slug": slug, "title": g["title"], "file": g["file"], "size": g.get("size"),
                 "region": g.get("region"), "title_id": g.get("title_id"), "issues": compat.issue_search(g),
                 "results": {}}
        for sid, r in g["results"].items():
            if r.get("stage", "Untested") == "Untested" or (
                    "result" in r.get("captures", {}) and not os.path.exists(os.path.join(HERE, r["captures"]["result"]))):
                entry["results"][sid] = {"stage": "Untested"}  # Untested or currently being retested.
                continue
            caps, auto, cfg = r.get("captures", {}), r.get("auto", {}), r.get("config", {})
            run_id = cfg.get("run_id")
            if run_id and run_id not in configs:
                configs[run_id] = {k: v for k, v in cfg.items() if k != "plan"} | {"plan": cfg.get("plan"), "system": sid}
            res = json.load(open(os.path.join(HERE, caps["result"]))) if "result" in caps else {}
            gi, row = slots[f"{sid}/{slug}"]
            base, rows = bases[gi]
            shots = [{"name": s, "ok": s in caps, "t": res.get("shots", {}).get(s, {}).get("asked_s")} for s in SHOTS]
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
                "pack": base, "row": row, "rows": rows, "shots": shots,
                "run": run_id, "tested_at": r.get("tested_at"), "log_tail": tail,
            }
        games.append(entry)
    data = {"systems": db["systems"], "configs": configs, "games": games}
    tpl = open(os.path.join(HERE, "page_template.html")).read()
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = tpl.replace("/*DATA*/null", blob)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(page)
    cut = page.index("</style>") + len("</style>")   # Move the title, fonts and styles into the document head.
    with open(os.path.join(out, "web.html"), "w") as f:
        f.write(WEB_HEAD + page[:cut] + "\n</head>\n<body>\n" + page[cut:].lstrip("\n") + "\n</body>\n</html>\n")
    print(f"{len(games)} games, {len(groups)} packs ({len(keep)} files) -> {out}")


if __name__ == "__main__":
    main()
