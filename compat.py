#!/usr/bin/env python3
"""The hakuX-lr compatibility list: one entry per game, one result per system.

  compat.py import <games dir>...       add games (every system Untested)
  compat.py ingest <run dir>            take a runner.py run into the list
  compat.py review <system> <game> ...  record what review found
  compat.py review --file <json>        the same for many games
  compat.py titleids                    each game's Xbox title ID, from its run's core log
  compat.py media                       thumbnails of each result's screenshots in media/
  compat.py report                      COMPATIBILITY.md, report.html, contact sheets

The list lives in compat.json next to this file. A result belongs to the
configuration it was tested with (emulator commit, device, backend, GPU and
driver, settings), which is stored with it; testing one system leaves the
others as they were.
"""
import argparse
import concurrent.futures
import urllib.parse
import datetime
import html
import json
import os
import re
import shutil
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "compat.json")
SYSTEMS = [("amd64-linux", "amd64 Linux"), ("aarch64-linux", "aarch64 Linux"), ("android", "Android")]
STAGES = ["Untested", "Boot", "Intro", "Menu", "In-game", "Playable"]
OUTCOMES = ["Completed", "Crash", "Timeout", "Needs manual input"]
REGIONS = {"U": "USA", "World": "World", "E": "Europe", "J": "Japan"}
SHOTS = ("boot", "mid", "final")
FONT = "DejaVu-Sans"
MEDIA = os.path.join(HERE, "media")
THUMB = (320, 240)
ISSUES = "https://github.com/portare-ch/hakuX-lr/issues"


def issue_search(g):
    """The hakuX-lr issue search for a game: "<title ID>" OR "<title>" (there may be no issue)."""
    q = f'"{g["title_id"]}" OR "{g["title"]}"' if g.get("title_id") else f'"{g["title"]}"'
    return ISSUES + "?q=" + urllib.parse.quote(q)


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")


def load():
    if os.path.exists(DB):
        return json.load(open(DB))
    return {"schema": 1, "systems": [{"id": i, "label": l} for i, l in SYSTEMS],
            "stages": STAGES, "outcomes": OUTCOMES, "games": {}}


def save(db):
    db["games"] = dict(sorted(db["games"].items(), key=lambda kv: kv[1]["title"].lower()))
    tmp = DB + ".tmp"
    with open(tmp, "w") as f:
        json.dump(db, f, indent=1, ensure_ascii=False)
    os.replace(tmp, DB)


def rel(p):
    return os.path.relpath(p, HERE)


def parse_name(stem):
    """'Beyond Good & Evil (U) (En,Fr,Es)' -> title, region, languages."""
    tags = re.findall(r"\(([^)]*)\)", stem)
    title = re.sub(r"\s*\([^)]*\)", "", stem).strip()
    region = languages = ""
    for t in tags:
        if t in REGIONS:
            region = REGIONS[t]
        elif re.fullmatch(r"[A-Z][a-z](,[A-Z][a-z])*", t):
            languages = t
    return title, region, languages


# --- title IDs ----------------------------------------------------------------

TITLE_RE = re.compile(r"xbe loaded: title ([0-9a-fA-F]{8})")


def title_id_of(log):
    """The first executable's title ID in a core log (the disc's default.xbe), or None."""
    try:
        with open(log, errors="replace") as f:
            for line in f:
                m = TITLE_RE.search(line)
                if m:
                    return m.group(1).upper()
    except OSError:
        pass
    return None


def cmd_titleids(args):
    db = load()
    found = missing = 0
    for g in db["games"].values():
        if g.get("title_id") and not args.force:
            continue
        for r in g["results"].values():
            log = r.get("captures", {}).get("log")
            tid = title_id_of(os.path.join(HERE, log)) if log else None
            if tid:
                g["title_id"] = tid
                found += 1
                break
        else:
            missing += any(r.get("captures") for r in g["results"].values())
    save(db)
    print(f"title IDs: {found} found, {missing} tested games without one in their log")


# --- media ----------------------------------------------------------------------

def result_shots(r):
    """{name: source image} for a result: boot, mid, final and the first frame the in-game judge
    called gameplay (ingame), when it isn't the final one."""
    caps = r.get("captures", {})
    shots = {s: os.path.join(HERE, caps[s]) for s in SHOTS if s in caps}
    res_path = os.path.join(HERE, caps["result"]) if "result" in caps else None
    if res_path and os.path.exists(res_path):
        res = json.load(open(res_path))
        files = {k: v.get("file") for k, v in res.get("shots", {}).items()}
        for v in (res.get("watch") or {}).get("verdicts", []):
            if v.get("verdict") == "INGAME":
                f = files.get(v.get("shot"))
                if f and f != files.get("final"):
                    shots["ingame"] = os.path.join(os.path.dirname(res_path), f)
                break
    return {k: v for k, v in shots.items() if os.path.exists(v)}


def cmd_media(args):
    """media/<system>/<game>/<shot>.jpg, 320x240: the screenshots of the result each game has now.
    media/index.json keeps which result they came from, so a retested game's are made again."""
    db = load()
    index_path = os.path.join(MEDIA, "index.json")
    index = json.load(open(index_path)) if os.path.exists(index_path) else {}
    want, jobs = {}, []
    for slug, g in db["games"].items():
        for sid, r in g["results"].items():
            if r.get("stage", "Untested") == "Untested" or not r.get("captures"):
                continue
            key = f"{r.get('config', {}).get('run_id')}|{r.get('tested_at')}"
            d = os.path.join(MEDIA, sid, slug)
            shots = result_shots(r)
            want[f"{sid}/{slug}"] = {"key": key, "shots": sorted(shots)}
            fresh = index.get(f"{sid}/{slug}", {}).get("key") == key
            for name, src in shots.items():
                dst = os.path.join(d, name + ".jpg")
                if not (fresh and os.path.exists(dst)):
                    jobs.append((src, dst))
    for k in set(index) - set(want):         # results no longer in the list
        shutil.rmtree(os.path.join(MEDIA, k), ignore_errors=True)
    for k, v in want.items():                # shots a result no longer has
        d = os.path.join(MEDIA, k)
        for f in os.listdir(d) if os.path.isdir(d) else []:
            if f.endswith(".jpg") and f[:-4] not in v["shots"]:
                os.remove(os.path.join(d, f))

    def make(job):
        src, dst = job
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        subprocess.run(["nice", "-n", "19", "ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
                        f"scale={THUMB[0]}:{THUMB[1]}:flags=lanczos", "-q:v", "6", dst], check=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        list(ex.map(make, jobs))
    os.makedirs(MEDIA, exist_ok=True)
    with open(index_path, "w") as f:
        json.dump(dict(sorted(want.items())), f, indent=0)
    print(f"media: {len(jobs)} thumbnails made, {len(want)} results")


# --- import -------------------------------------------------------------------

def cmd_import(args):
    db = load()
    added = 0
    for d in args.dirs:
        for n in sorted(os.listdir(d)):
            if not n.lower().endswith(".chd"):
                continue
            stem = os.path.splitext(n)[0]
            slug = slugify(stem)
            title, region, langs = parse_name(stem)
            g = db["games"].setdefault(slug, {"results": {}})
            if "file" not in g:
                added += 1
            g.update(title=title, file=n, region=region, languages=langs,
                     size=os.path.getsize(os.path.join(d, n)))
            for sid, _ in SYSTEMS:
                g["results"].setdefault(sid, {"stage": "Untested"})
    save(db)
    print(f"{added} added, {len(db['games'])} games in the list")


# --- ingest -------------------------------------------------------------------

def magick(*a):
    r = subprocess.run(["magick", *a], capture_output=True, text=True)
    return r.stdout.strip() or r.stderr.strip()


def image_stats(png):
    out = magick(png, "-colorspace", "Gray", "-format", "%[fx:mean] %[fx:standard_deviation]", "info:")
    try:
        mean, sd = (float(x) for x in out.split())
    except ValueError:
        return None
    return {"mean": round(mean, 3), "sd": round(sd, 3), "black": mean < 0.03 and sd < 0.03}


def image_diff(a, b):
    out = magick("compare", "-metric", "RMSE", a, b, "null:")
    m = re.search(r"\(([\d.e-]+)\)", out)
    return round(float(m.group(1)), 3) if m else None


DISP_RE = re.compile(r"hakuX-hle-disp: stats: ([\d.]+) new frames/s")
SWAP_RE = re.compile(r"hakuX-hle-fps: ([\d.]+) fps")
HANG_RE = re.compile(r"HANG ongoing ([\d.]+) s since frame (\d+)")


def longest_hang(path):
    """The longest guest hang the core reported: (seconds, frame it started after)."""
    best = (0.0, None)
    try:
        with open(path, errors="replace") as f:
            for line in f:
                m = HANG_RE.search(line)
                if m and float(m.group(1)) > best[0]:
                    best = (float(m.group(1)), int(m.group(2)))
    except OSError:
        pass
    return best


def log_rates(path):
    disp, swaps = [], []
    try:
        with open(path, errors="replace") as f:
            for line in f:
                m = DISP_RE.search(line)
                if m:
                    disp.append(float(m.group(1)))
                m = SWAP_RE.search(line)
                if m:
                    swaps.append(float(m.group(1)))
    except OSError:
        pass
    return disp, swaps


def config_of(run_cfg, res):
    emu = run_cfg.get("emulator", {})
    gpu = run_cfg.get("gpu", {})
    return {
        "run_id": run_cfg.get("run_id"),
        "emulator": f"hakuX-lr {emu.get('version', '?')}",
        "commit": emu.get("commit"),
        "device": run_cfg.get("device"),
        "cpu": run_cfg.get("cpu"),
        "arch": run_cfg.get("arch"),
        "cpu_backend": run_cfg.get("cpu_backend"),
        "gpu": gpu.get("deviceName"),
        "driver": gpu.get("driverInfo") or gpu.get("driverName"),
        "vulkan": gpu.get("apiVersion"),
        "kernel": run_cfg.get("kernel"),
        "frontend": run_cfg.get("frontend"),
        "display": run_cfg.get("display"),
        "audio": run_cfg.get("audio"),
        "input": run_cfg.get("input"),
        "core_options": res.get("core_log", {}).get("options"),
        "plan": res.get("plan"),
    }


def cmd_ingest(args):
    db = load()
    run_dir = os.path.abspath(args.run_dir)
    run_cfg = json.load(open(os.path.join(run_dir, "config.json")))
    sid = run_cfg["system"]
    n = 0
    for slug in sorted(os.listdir(run_dir)):
        rpath = os.path.join(run_dir, slug, "result.json")
        if not os.path.exists(rpath):
            continue
        res = json.load(open(rpath))
        gdir = os.path.dirname(rpath)
        g = db["games"].get(slug)
        if g is None:
            print(f"{slug}: not in the list (run import first)", file=sys.stderr)
            continue
        old = g["results"].get(sid, {})
        keep_review = (old.get("config", {}).get("run_id") == run_cfg["run_id"] and old.get("reviewed")
                       and old.get("tested_at") == res.get("started") and not args.force)  # the same result, not a rerun
        caps, metrics = {}, {}
        thumbs = os.path.join(gdir, "thumbs")
        os.makedirs(thumbs, exist_ok=True)
        for s in SHOTS:
            png = os.path.join(gdir, f"{s}.png")
            if not os.path.exists(png):
                continue
            caps[s] = rel(png)
            th = os.path.join(thumbs, f"{s}.jpg")
            if not os.path.exists(th):
                magick(png, "-resize", "320x240", "-quality", "82", th)
            caps[f"{s}_thumb"] = rel(th)
            metrics[s] = image_stats(png)
        if "mid" in caps and "final" in caps:
            metrics["mid_final_rmse"] = image_diff(os.path.join(gdir, "mid.png"), os.path.join(gdir, "final.png"))
        for name, f in (("log", "hakux.log"), ("retroarch_log", "retroarch.log"), ("audio", "audio.opus"),
                        ("result", "result.json")):
            if os.path.exists(os.path.join(gdir, f)):
                if name == "audio" and audio_invalid(run_cfg["run_id"], res.get("started") or ""):
                    continue  # the recording is not this game's alone
                caps[name] = rel(os.path.join(gdir, f))
        cl = res.get("core_log", {})
        disp, swaps = log_rates(os.path.join(gdir, "hakux.log"))
        fps = disp or cl.get("fps") or []
        au = res.get("audio", {})
        bad = audio_invalid(run_cfg["run_id"], res.get("started") or "")
        if bad:
            au = {"invalid": bad}
        auto = {
            "outcome": res.get("outcome_auto"),
            "why": res.get("outcome_why"),
            "exit": res.get("exit"),
            "missing_shots": res.get("missing_shots"),
            "boot_stages": cl.get("stages"),
            "log_flags": sorted((cl.get("flags") or {}).keys()),
            "fps_median": round(statistics.median(fps), 1) if fps else None,
            "fps_min": round(min(fps), 1) if fps else None,
            "fps_source": "displayed frames (HAKUX_DISP_STATS)" if disp else "guest swaps",
            "guest_swaps_median": round(statistics.median(swaps), 1) if swaps else None,
            "longest_hang_s": longest_hang(os.path.join(gdir, "hakux.log"))[0],
            "longest_hang_after_frame": longest_hang(os.path.join(gdir, "hakux.log"))[1],
            "audio_peak_rms_dbfs": au.get("peak_rms_dbfs"),
            "audio_first_sound_s": au.get("first_sound_s"),
            "audio_audible_fraction": au.get("audible_fraction"),
            "audio_seconds": au.get("seconds"),
            "images": metrics,
        }
        w = res.get("watch")
        if w:
            auto["judge"] = {"model": w.get("model"), "ingame_at_s": w.get("ingame_at_s"),
                             "stopped_at_s": w.get("stopped_at_s"),
                             "verdicts": [[v.get("t"), v.get("verdict")] for v in w.get("verdicts", [])]}
        new = {
            "stage": "Unreviewed",
            "outcome": auto["outcome"],
            "reviewed": False,
            "observations": {"graphics": "", "audio": auto_audio_note(au), "notes": ""},
            "auto": auto,
            "captures": caps,
            "config": config_of(run_cfg, res),
            "tested_at": res.get("started"),
        }
        if keep_review:
            for k in ("stage", "outcome", "reviewed", "reviewed_by", "reviewed_at", "observations"):
                if k in old:
                    new[k] = old[k]
        g["results"][sid] = new
        n += 1
    save(db)
    print(f"{n} results from {run_cfg['run_id']} ({sid})")


def audio_invalid(run_id, started):
    """Why a result's audio recording can't be used (audio_invalid.json), or None."""
    path = os.path.join(HERE, "audio_invalid.json")
    if not os.path.exists(path):
        return None
    for w in json.load(open(path))["windows"]:
        if w["run_id"] == run_id and started >= w["from"] and (not w.get("to") or started < w["to"]):
            return w["why"]
    return None


def auto_audio_note(au):
    if au and au.get("invalid"):
        return au["invalid"][0].upper() + au["invalid"][1:] + "."
    if not au or "peak_rms_dbfs" not in au:
        return "not recorded"
    if au["peak_rms_dbfs"] <= -50:
        return "silent for the whole run (recorded)"
    return (f"sound from {au.get('first_sound_s')} s, audible in {int(au.get('audible_fraction', 0) * 100)} % "
            f"of the run, loudest {au['peak_rms_dbfs']} dBFS RMS (recorded; not judged by ear)")


# --- review -------------------------------------------------------------------

def apply_review(db, sid, key, rv, by):
    g = db["games"].get(key) or next((v for k, v in db["games"].items()
                                       if key.lower() in (v["title"].lower(), v["file"].lower())), None)
    if g is None:
        raise SystemExit(f"no game {key!r}")
    r = g["results"].get(sid)
    if not r or r.get("stage") == "Untested":
        raise SystemExit(f"{g['title']}: no {sid} result to review")
    if "stage" in rv:
        if rv["stage"] not in STAGES[1:]:
            raise SystemExit(f"stage must be one of {STAGES[1:]}")
        r["stage"] = rv["stage"]
    if "outcome" in rv:
        if rv["outcome"] not in OUTCOMES:
            raise SystemExit(f"outcome must be one of {OUTCOMES}")
        r["outcome"] = rv["outcome"]
    for k in ("graphics", "audio", "notes"):
        if k in rv:
            r["observations"][k] = rv[k]
    r["reviewed"] = True
    r["reviewed_by"] = by
    r["reviewed_at"] = now_iso()


def cmd_review(args):
    db = load()
    if args.file:
        items = json.load(open(args.file))
        for it in items:
            apply_review(db, it.get("system", args.system), it["game"], it, args.by)
    else:
        rv = {k: getattr(args, k) for k in ("stage", "outcome", "graphics", "audio", "notes")
              if getattr(args, k) is not None}
        apply_review(db, args.system, args.game, rv, args.by)
    save(db)
    print("saved")


# --- report -------------------------------------------------------------------

def cell(r):
    st = r.get("stage", "Untested")
    if st == "Untested":
        return "Untested"
    if st == "Unreviewed":
        return f"Unreviewed (auto: {r.get('outcome') or '?'})"
    return f"{st} · {r.get('outcome') or '?'}"


def contact_sheets(db, sid, out_dir, per_page=6):
    """PNG pages: a row per game with its boot, mid and final screenshots."""
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".png"):
            os.remove(os.path.join(out_dir, f))
    rows = []
    tmp = os.path.join(out_dir, "rows")
    os.makedirs(tmp, exist_ok=True)
    tested = [(k, g) for k, g in db["games"].items() if g["results"].get(sid, {}).get("stage") != "Untested"]
    blank = os.path.join(tmp, "_blank.png")
    magick("-size", "400x300", "xc:#333", "-fill", "#bbb", "-font", FONT, "-pointsize", "20",
           "-gravity", "center", "-annotate", "0", "no screenshot", blank)
    for i, (k, g) in enumerate(tested, 1):
        r = g["results"][sid]
        caps = r.get("captures", {})
        imgs = [os.path.join(HERE, caps[s]) if s in caps else blank for s in SHOTS]
        a = r.get("auto", {})
        fps = a.get("fps_median")
        label = (f"{i}. {g['title']}   [{cell(r)}]   auto: {a.get('outcome')}, "
                 f"fps {fps if fps is not None else '-'}, audio {a.get('audio_peak_rms_dbfs', '-')} dBFS")
        row = os.path.join(tmp, f"{i:03d}.png")
        magick(*imgs, "-resize", "400x300!", "-bordercolor", "#111", "-border", "2", "+append",
               "-background", "#111", "-fill", "white", "-font", FONT, "-pointsize", "17",
               "-gravity", "northwest", "-splice", "0x26", "-annotate", "+6+3", label, row)
        rows.append(row)
    pages = []
    for p in range(0, len(rows), per_page):
        page = os.path.join(out_dir, f"sheet-{p // per_page + 1:02d}.png")
        magick(*rows[p:p + per_page], "-background", "#111", "-append", page)
        pages.append(page)
    shutil.rmtree(tmp)
    return pages


def cmd_report(args):
    db = load()
    games = db["games"]
    labels = dict(SYSTEMS)
    sheets = {}
    for sid, _ in SYSTEMS:
        if not args.no_sheets and any(g["results"].get(sid, {}).get("stage") != "Untested" for g in games.values()):
            sheets[sid] = [rel(p) for p in contact_sheets(db, sid, os.path.join(HERE, "contact-sheets", sid))]

    # Markdown list
    md = ["# hakuX-lr compatibility", "",
          "Each result applies only to the configuration it was tested with (listed under "
          "Configurations). Stages: Boot, Intro, Menu, In-game, Playable; outcomes: Completed, Crash, Timeout, "
          "Needs manual input. A timeout does not establish incompatibility. Playable means gameplay "
          "was reached with nothing seen that gets in the way of play, judged from one short run, "
          "not from playing a game through.", ""]
    counts = []
    for sid, lab in SYSTEMS:
        c = {}
        for g in games.values():
            st = g["results"].get(sid, {}).get("stage", "Untested")
            c[st] = c.get(st, 0) + 1
        counts.append(f"- **{lab}:** " + ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: (STAGES + ['Unreviewed']).index(kv[0]) if kv[0] in STAGES + ['Unreviewed'] else 99)))
    md += counts + ["", "| Game | Title ID | " + " | ".join(l for _, l in SYSTEMS) + " | Issues |",
                    "|---|---|" + "---|" * len(SYSTEMS) + "---|"]
    for k, g in games.items():
        cells = []
        for sid, _ in SYSTEMS:
            r = g["results"].get(sid, {"stage": "Untested"})
            c = cell(r)
            if os.path.isdir(os.path.join(MEDIA, sid, k)):
                c += f" ([screenshots](media/{sid}/{k}/))"
            cells.append(c)
        md.append(f"| {g['title']} | {g.get('title_id', '')} | " + " | ".join(cells) + f" | [search]({issue_search(g)}) |")
    md += ["", "## Configurations", ""]
    seen = set()
    for g in games.values():
        for sid, lab in SYSTEMS:
            cfg = g["results"].get(sid, {}).get("config")
            if cfg and cfg["run_id"] not in seen:
                seen.add(cfg["run_id"])
                md.append(f"- **{lab}, run {cfg['run_id']}:** {cfg['emulator']} ({cfg['commit']}); "
                          f"{cfg['device']}, {cfg['cpu']}, {cfg['arch']}, CPU backend {cfg['cpu_backend']}; "
                          f"{cfg['gpu']}, {cfg['driver']}, Vulkan {cfg['vulkan']}; kernel {cfg['kernel']}; "
                          f"{cfg['frontend']}; {cfg['display']}; core options: {cfg['core_options']}; "
                          f"input {cfg['input']}; audio {cfg['audio']}.")
    md += ["", "## Notes per game", ""]
    for k, g in games.items():
        for sid, lab in SYSTEMS:
            r = g["results"].get(sid, {})
            o = r.get("observations") or {}
            if r.get("stage", "Untested") == "Untested":
                continue
            parts = [f"graphics: {o['graphics']}" if o.get("graphics") else "",
                     f"audio: {o['audio']}" if o.get("audio") else "",
                     o.get("notes", "")]
            md.append(f"- **{g['title']}** ({lab}, {cell(r)}): " + "; ".join(p for p in parts if p))
    with open(os.path.join(HERE, "COMPATIBILITY.md"), "w") as f:
        f.write("\n".join(md) + "\n")

    # HTML report with thumbnails
    e = html.escape
    h = ["<!doctype html><meta charset=utf-8><title>hakuX-lr compatibility</title>",
         "<meta name=viewport content='width=device-width,initial-scale=1'>",
         "<style>:root{color-scheme:light dark;--bg:#fff;--fg:#111;--mut:#666;--line:#ddd;--card:#f6f6f6}"
         "@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#eee;--mut:#999;--line:#333;--card:#1e1e1e}}"
         "body{font:14px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--fg);margin:0 auto;max-width:1400px;padding:16px}"
         "table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid var(--line);padding:6px;text-align:left;vertical-align:top}"
         ".s-Boot{color:#c0392b}.s-Intro{color:#d68910}.s-Menu{color:#2e86c1}.s-In-game{color:#1a7f86}.s-Playable{color:#239b56}.s-Unreviewed,.mut{color:var(--mut)}"
         ".shots img{width:128px;height:96px;object-fit:cover;margin-right:3px;border-radius:3px}"
         "details{margin:4px 0}code{font-size:12px}</style>",
         "<h1>hakuX-lr compatibility</h1>",
         "<p class=mut>Results apply only to the tested configuration. A timeout does not establish "
         "incompatibility; briefly reaching gameplay does not establish that a game is playable.</p>",
         "<ul>" + "".join(f"<li>{e(c[4:].replace('**', ''))}</li>" for c in counts) + "</ul>"]
    for sid, pages in sheets.items():
        h.append(f"<p>{e(labels[sid])} contact sheets: " +
                 " ".join(f"<a href='{e(p)}'>{e(os.path.basename(p))}</a>" for p in pages) + "</p>")
    h.append("<table><tr><th>Game</th>" + "".join(f"<th>{e(l)}</th>" for _, l in SYSTEMS) + "</tr>")
    for k, g in games.items():
        h.append(f"<tr><td><b>{e(g['title'])}</b><br><span class=mut>{e(g['file'])}</span></td>")
        for sid, _ in SYSTEMS:
            r = g["results"].get(sid, {"stage": "Untested"})
            st = r.get("stage", "Untested")
            if st == "Untested":
                h.append("<td class=mut>Untested</td>")
                continue
            caps, a, o, cfg = r.get("captures", {}), r.get("auto", {}), r.get("observations", {}), r.get("config", {})
            imgs = "".join(f"<a href='{e(caps[s])}'><img loading=lazy src='{e(caps[s + '_thumb'])}' alt='{s}'></a>"
                           for s in SHOTS if s in caps)
            links = " · ".join(f"<a href='{e(caps[n])}'>{n.replace('_', ' ')}</a>"
                               for n in ("log", "retroarch_log", "audio", "result") if n in caps)
            h.append(f"<td><span class='s-{e(st)}'><b>{e(st)}</b></span> · {e(r.get('outcome') or '?')}"
                     f"{'' if r.get('reviewed') else ' <span class=mut>(auto)</span>'}"
                     f"<div class=shots>{imgs}</div>"
                     f"<div>{e(o.get('graphics', ''))}</div><div class=mut>audio: {e(o.get('audio', ''))}</div>"
                     f"<div>{e(o.get('notes', ''))}</div>"
                     f"<details><summary>auto checks, configuration</summary><div>auto: {e(str(a.get('outcome')))} "
                     f"({e(str(a.get('why')))}); fps median {a.get('fps_median')}, min {a.get('fps_min')}; "
                     f"boot stages {e(','.join(a.get('boot_stages') or []))}; log flags {e(', '.join(a.get('log_flags') or []) or 'none')}</div>"
                     f"<div class=mut>{e(cfg.get('emulator', ''))} {e(str(cfg.get('commit', ''))[:10])} · {e(str(cfg.get('device')))} "
                     f"{e(str(cfg.get('arch')))} {e(str(cfg.get('cpu_backend')))} · {e(str(cfg.get('gpu')))} {e(str(cfg.get('driver')))}"
                     f" · run {e(str(cfg.get('run_id')))}</div><div>{links}</div></details></td>")
        h.append("</tr>")
    h.append("</table>")
    with open(os.path.join(HERE, "report.html"), "w") as f:
        f.write("\n".join(h))
    print("wrote COMPATIBILITY.md, report.html" + (", contact sheets" if sheets else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("import")
    p.add_argument("dirs", nargs="+")
    p.set_defaults(fn=cmd_import)
    p = sub.add_parser("ingest")
    p.add_argument("run_dir")
    p.add_argument("--force", action="store_true", help="replace reviewed entries of the same run")
    p.set_defaults(fn=cmd_ingest)
    p = sub.add_parser("review")
    p.add_argument("system", nargs="?", choices=[s for s, _ in SYSTEMS])
    p.add_argument("game", nargs="?", help="slug, title or file name")
    p.add_argument("--stage", choices=STAGES[1:])
    p.add_argument("--outcome", choices=OUTCOMES)
    p.add_argument("--graphics")
    p.add_argument("--audio")
    p.add_argument("--notes")
    p.add_argument("--file", help="JSON list of {game, system?, stage?, outcome?, graphics?, audio?, notes?}")
    p.add_argument("--by", default=os.environ.get("USER", "reviewer"))
    p.set_defaults(fn=cmd_review)
    p = sub.add_parser("titleids")
    p.add_argument("--force", action="store_true", help="look again for games that have one")
    p.set_defaults(fn=cmd_titleids)
    p = sub.add_parser("media")
    p.add_argument("--jobs", type=int, default=4)
    p.set_defaults(fn=cmd_media)
    p = sub.add_parser("report")
    p.add_argument("--no-sheets", action="store_true", help="leave the contact sheets as they are")
    p.set_defaults(fn=cmd_report)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
