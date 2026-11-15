#!/usr/bin/env python3
"""Run automated hakuX-lr compatibility tests.

Each game gets an isolated RetroArch profile, timed inputs, screenshots,
audio, logs and result.json. compat.py imports the results for review.
Uses the Python standard library.

  runner.py --system amd64-linux --core <hakux_libretro.so> --games <dir> --out <runs-dir>"""
import argparse
import array
import base64
import datetime
import json
import math
import os
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULT_PLAN = {
    "boot_wait": 10.0,         # seconds after launch before the first screenshot
    "input_time": 285.0,       # spaced presses after that
    "input_gap": 2.5,          # seconds between presses
    "buttons": ["start", "a"],  # pressed in turn
    "press_ms": 150,
    "settle": 5.0,             # after releasing everything, then the final screenshot (300 s)
    "mid_shot": 45.0,          # seconds after launch of one more screenshot (false: none)
    "watch_from": 30.0,        # first in-game check: a screenshot the judge looks at
    "watch_every": 20.0,       # seconds between checks
    "watch_needed": 2,         # in-game verdicts in a row that end the run early
    "unstick": ["b", "down"],  # pressed in turn, once each time a judged frame is unchanged and not in game
    "hard_limit": 330.0,       # from launch; the process is killed at this point
}
# With the judge on, Start is held back while the last judged frame showed gameplay (it would open
# a pause menu), and Start and A are held back after an unstick press until the next verdict.
JUDGE_SYSTEM = "You label screenshots from original Xbox games running in an emulator. Reply with one word."
JUDGE_ASK = (
    "Is the player in control of gameplay in this screenshot? Answer INGAME if it shows gameplay: the game "
    "world with the player's character, vehicle, cursor or pieces under the player's control, usually with a "
    "HUD (score, health, map, speedometer, ammo, timer), including a pause menu drawn over gameplay. Answer "
    "OTHER for anything else: black or blank screens, logos, legal or warning screens, videos and cutscenes "
    "(including in-engine scenes with letterbox bars or no HUD), title screens, menus, character, car or level "
    "selection, profile and save prompts, loading screens and briefings. Answer with one word: INGAME or OTHER.")
GUIDE_BUTTONS = ("a", "b", "x", "y", "start", "back", "up", "down", "left", "right", "lt", "rt", "white", "black")
GUIDE_SYSTEM = ("You operate the gamepad of an original Xbox game running in an emulator, to get from its menus "
                "into gameplay. Reply with one JSON object only.")
GUIDE_ASK = (
    "This screenshot shows where the game is now. It is not gameplay yet, and pressing Start and A in turn "
    "did not get past it. Give the button presses, in order, that most likely move on toward gameplay from "
    "exactly this screen: start a new single-player game with the defaults, accept the default name, "
    "character, car, team, difficulty and settings, confirm prompts, skip videos. Rules: read the button "
    "hints on the screen and use the button they name for confirm, done, accept, next or continue. On an "
    "on-screen keyboard, do not type: move the highlighted cursor to DONE, OK, ACCEPT, ENTER or END with the "
    "direction buttons and press A, or press the button the screen names for it (often Start or Y); if the "
    "name is empty, press A once on a letter first. On a prompt that asks whether to continue without "
    "saving, without a profile or without signing in, choose the answer that continues. On a prompt that "
    "asks whether to overwrite or delete saved data, do not overwrite or delete; go back or pick another "
    "entry. Where a list offers a new game, a quick race, exhibition, arcade or practice mode, pick the one "
    "that reaches play soonest. If the screen is black, a logo, a loading screen or a video, reply with no "
    "presses, or Start to skip a video. At most 10 presses, counted from the cursor position visible in the "
    "screenshot. Buttons: a b x y start back up down left right lt rt white black. Reply as "
    '{"presses": ["down", "a"], "screen": "what the screen is, in a few words"}.')
GUIDE_AFTER = 100.0  # seconds: with no gameplay by then the guide takes over even if the screen changes
GUIDE_MAX = 18       # guide answers per run
GUIDE_GAP = 0.45     # seconds between a guided plan's presses
SHOT_WAIT = 5.0      # seconds to wait for a requested screenshot file
QUIT_WAIT = 10.0     # seconds to wait for a clean exit after QUIT
GAP = 2.0            # pause between games
PORT = 55355       # RetroArch network commands; worker N uses PORT + 10 * N
CURRENT = {}       # this worker's running game: "proc" (RetroArch's process group) and "audio"

LOG_FLAGS = [
    ("stop", re.compile(r"hakuX-native-frontier: stop: (?!the front end stopped)")),
    ("unhandled-exception", re.compile(r"hakuX-native-frontier: stop: seh: unhandled exception")),
    ("guest-fault", re.compile(r"guest fault at")),
    ("host-fault", re.compile(r"host fault:")),
    ("boot-failing", re.compile(r"boot: failing after")),
    ("assertion", re.compile(r"assertion failed")),
    ("kvm-entry-failed", re.compile(r"entry failed: hardware reason")),
    ("xbe-parse-failed", re.compile(r"xbe: parse failed")),
    ("not-implemented", re.compile(r"not implemented")),
    ("vk-device-lost", re.compile(r"VK_ERROR_DEVICE_LOST|device lost", re.I)),
]
STAGE_RE = re.compile(r"hakuX-native-frontier: stage (S\d)")
FPS_RE = re.compile(r"hakuX-hle-disp: stats: ([\d.]+) new frames/s")
OPTIONS_RE = re.compile(r"hakuX-libretro: options: (.*)")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")


def sh(cmd, **kw):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20, **kw).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


# Input plan

def build_steps(p):
    """The default plan as timed steps: (seconds after launch, action, args...)."""
    steps = [(p["boot_wait"], "shot", "boot")]
    end_input = p["boot_wait"] + p["input_time"]
    t, k = p["boot_wait"] + 0.5, 0
    while t < end_input - 0.2:
        steps.append((round(t, 2), "tap", p["buttons"][k % len(p["buttons"])], p["press_ms"]))
        t += p["input_gap"]
        k += 1
    if p["mid_shot"]:
        mid = 45.0 if p["mid_shot"] is True else float(p["mid_shot"])
        steps.append((round(mid - 0.4, 2), "shot", "mid"))
    steps.append((end_input, "release"))
    final = end_input + p["settle"]
    steps.append((final, "shot", "final"))
    if p.get("watch_every"):
        t = p["watch_from"]
        while t < final - 1:
            steps.append((round(t - 0.2, 2), "watch", f"w{int(t):03d}"))
            t += p["watch_every"]
    return sorted(steps, key=lambda s: s[0])


# Gameplay detection

class Judge:
    """Detect gameplay in watch frames using Claude Code and the user's login.
    Blank frames count as no gameplay; unchanged frames reuse the last verdict.
    Set `ingame` after `needed` consecutive gameplay verdicts."""

    def __init__(self, model, needed, confirm_model=None, guide_model=None):
        self.model, self.needed, self.confirm_model = model, needed, confirm_model
        self.guide_model = guide_model
        self.guide_on = False     # the guide's presses replace the planned ones from here on
        self.busy = False         # a frame is being judged (or its presses asked for)
        self.plan = None          # presses for the frame last judged, until the run takes them
        self.guided = []          # [{"shot", "t", "presses", "screen"}]
        self.magick = shutil.which("magick")
        self.lock = threading.Lock()
        self.todo = None
        self.wake = threading.Event()
        self.ingame = threading.Event()
        self.ingame_at = None
        self.verdicts = []
        self.streak = []
        self.last = None  # (jpg, verdict)
        self.confirmed_by = None
        self.latest = None
        self.stuck = False
        self.closed = False
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def submit(self, name, png, t):
        with self.lock:
            self.todo = (name, png, t)  # only the newest frame matters
            self.busy = True
        self.wake.set()

    def take_plan(self):
        with self.lock:
            plan, self.plan = self.plan, None
        return plan

    def _guide(self, img, media):
        """The presses the guide model gives for this frame: (list, what the screen is) or (None, error)."""
        with open(img, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        msg = {"type": "user", "message": {"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}},
            {"type": "text", "text": GUIDE_ASK}]}}
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("CLAUDECODE", "CLAUDE_CODE_", "CLAUDE_PID", "CLAUDE_EFFORT"))}
        cmd = ["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
               "--model", self.guide_model, "--system-prompt", GUIDE_SYSTEM, "--tools", "", "--strict-mcp-config",
               "--disable-slash-commands", "--no-session-persistence"]
        try:
            r = subprocess.run(cmd, input=json.dumps(msg) + "\n", capture_output=True, text=True, env=env,
                               timeout=90, cwd=HERE)
        except (OSError, subprocess.TimeoutExpired) as e:
            return None, f"guide failed: {e}"
        for line in r.stdout.splitlines():
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get("type") == "result":
                text = o.get("result") or ""
                m = re.search(r"\{.*\}", text, re.S)
                try:
                    ans = json.loads(m.group(0)) if m else {}
                except ValueError:
                    ans = {}
                presses = [str(b).lower() for b in ans.get("presses", []) if str(b).lower() in GUIDE_BUTTONS]
                return presses[:10], str(ans.get("screen", ""))[:120]
        return None, f"no answer (exit {r.returncode})"

    def close(self, wait=10):
        with self.lock:
            self.todo = None
        self.closed = True
        self.wake.set()
        self.thread.join(wait)

    def _magick(self, *a):
        r = subprocess.run([self.magick, *a], capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).strip()

    def _ask(self, img, media, model=None):
        with open(img, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        msg = {"type": "user", "message": {"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}},
            {"type": "text", "text": JUDGE_ASK}]}}
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("CLAUDECODE", "CLAUDE_CODE_", "CLAUDE_PID", "CLAUDE_EFFORT"))}
        cmd = ["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
               "--model", model or self.model, "--system-prompt", JUDGE_SYSTEM, "--tools", "", "--strict-mcp-config",
               "--disable-slash-commands", "--no-session-persistence"]
        try:
            r = subprocess.run(cmd, input=json.dumps(msg) + "\n", capture_output=True, text=True, env=env,
                               timeout=60, cwd=HERE)
        except (OSError, subprocess.TimeoutExpired) as e:
            return None, f"judge failed: {e}"
        for line in r.stdout.splitlines():
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get("type") == "result":
                text = (o.get("result") or "").upper()
                if "INGAME" in text:
                    return "INGAME", None
                if "OTHER" in text:
                    return "OTHER", None
                return None, f"unclear answer: {text[:80]}"
        return None, f"no answer (exit {r.returncode}): {r.stderr.strip()[-160:]}"

    def _judge(self, name, png, t):
        t_start = time.monotonic()
        img, media, how = png, "image/png", "model"
        verdict, err, unchanged = None, None, False
        if self.magick:
            jpg = os.path.splitext(png)[0] + ".jpg"
            self._magick(png, "-resize", "768x432!", "-quality", "85", jpg)
            if os.path.exists(jpg):
                img, media = jpg, "image/jpeg"
                if self.last:
                    m = re.search(r"\(([\d.e-]+)\)", self._magick("compare", "-metric", "RMSE", jpg, self.last[0],
                                                                   "null:"))
                    unchanged = bool(m) and float(m.group(1)) < 0.01
                if unchanged:
                    verdict, err, how = self.last[1], None, "same as the last frame"
                else:
                    try:  # Brightest pixel distinguishes blank frames from dark menus with text.
                        peak = float(self._magick(jpg, "-colorspace", "Gray", "-format", "%[fx:maxima]", "info:"))
                    except ValueError:
                        peak = 1.0
                    if peak < 0.1:
                        verdict, err, how = "OTHER", None, "blank frame"
        if how == "model":
            verdict, err = self._ask(img, media)
        if verdict and img != png:
            self.last = (img, verdict)
        rec = {"shot": name, "t": t, "verdict": verdict, "how": how, "s": round(time.monotonic() - t_start, 1)}
        if err:
            rec["error"] = err
        self.verdicts.append(rec)
        self.latest = verdict
        self.stuck = verdict == "OTHER" and unchanged
        if self.guide_model and verdict == "OTHER" and len(self.guided) < GUIDE_MAX and (
                self.guide_on or self.stuck or t >= GUIDE_AFTER):
            self.guide_on = True
            presses, screen = ([], "blank frame") if how == "blank frame" else self._guide(img, media)
            self.guided.append({"shot": name, "t": t, "presses": presses, "screen": screen})
            with self.lock:
                self.plan = presses or []
        elif self.guide_on and len(self.guided) >= GUIDE_MAX:
            self.guide_on = False       # out of answers: the planned presses again
        if verdict == "INGAME":
            self.streak.append((name, t))
            if len(self.streak) >= self.needed and not self.ingame.is_set():
                # Confirm with a stronger model to catch in-engine cutscenes.
                ok, cerr = ("INGAME", None) if not self.confirm_model else self._ask(img, media, self.confirm_model)
                if self.confirm_model:
                    self.verdicts.append({"shot": name, "t": t, "verdict": ok, "how": f"confirm ({self.confirm_model})",
                                          **({"error": cerr} if cerr else {})})
                if ok == "OTHER":
                    self.streak = []
                    self.latest = "OTHER"
                else:  # Keep the small model's verdict if confirmed or confirmation failed.
                    self.ingame_at = self.streak[0][1]
                    self.confirmed_by = self.streak[-1][0]
                    self.ingame.set()
        elif verdict == "OTHER":
            self.streak = []

    def _loop(self):
        while True:
            self.wake.wait()
            self.wake.clear()
            while not self.closed:
                with self.lock:
                    job, self.todo = self.todo, None
                if not job:
                    break
                try:
                    self._judge(*job)
                except Exception as e:  # Continue the run if the judge fails.
                    self.verdicts.append({"shot": job[0], "t": job[2], "verdict": None, "error": repr(e)})
                with self.lock:
                    self.busy = self.todo is not None
            if self.closed:
                return


def plan_for(game, overrides):
    """Apply an override keyed by file name, stem or slug to the default plan.
    Overrides can change defaults, replace steps, add extra_steps, set a skip
    reason, or suppress default inputs with quiet: [[from, to], ...].
    Steps: [seconds, action, args...]; actions: shot, tap, down, up, release."""
    stem = os.path.splitext(os.path.basename(game))[0]
    ov = {}
    for key in (os.path.basename(game), stem, slugify(stem)):
        if key in overrides:
            ov = overrides[key]
            break
    p = dict(DEFAULT_PLAN)
    p.update({k: v for k, v in ov.items() if k in DEFAULT_PLAN})
    steps = [tuple(s) for s in ov["steps"]] if "steps" in ov else build_steps(p)
    # Suppress default presses during quiet windows so extra_steps can run.
    quiet = ov.get("quiet", [])
    steps = [s for s in steps if not (s[1] == "tap" and any(a <= s[0] < b for a, b in quiet))]
    steps += [tuple(s) for s in ov.get("extra_steps", [])]
    steps.sort(key=lambda s: s[0])
    return p, steps, ov


# Saved games

def save_index(root):
    """Title ID (lower case) -> {"UDATA": dir, "TDATA": dir, "from": game folder} for an
    archive laid out as <game>/UDATA/<title id>/... (optionally TDATA beside it,
    or the title ID folder directly under the game's)."""
    idx = {}
    if not root or not os.path.isdir(root):
        return idx
    for game in sorted(os.listdir(root)):
        gd = os.path.join(root, game)
        if not os.path.isdir(gd):
            continue
        for sub in sorted(os.listdir(gd)):
            sd = os.path.join(gd, sub)
            if not os.path.isdir(sd):
                continue
            if sub.upper() in ("UDATA", "TDATA"):
                for tid in sorted(os.listdir(sd)):
                    if re.fullmatch(r"[0-9a-fA-F]{8}", tid) and os.path.isdir(os.path.join(sd, tid)):
                        e = idx.setdefault(tid.lower(), {"from": game})
                        e.setdefault(sub.upper(), os.path.join(sd, tid))
            elif re.fullmatch(r"[0-9a-fA-F]{8}", sub):
                idx.setdefault(sub.lower(), {"from": game}).setdefault("UDATA", sd)
    return idx


def title_ids():
    """Game file name -> title ID (lower case), from compat.json."""
    try:
        games = json.load(open(os.path.join(HERE, "compat.json")))["games"]
    except (OSError, ValueError, KeyError):
        return {}
    return {g["file"]: g["title_id"].lower() for g in games.values() if g.get("file") and g.get("title_id")}


def seed_save(saves_dir, entry):
    """Copy an archived save onto the fresh console disk (E: is Partition1).
    Regular files only; names as the archive has them."""
    n = 0
    for kind in ("UDATA", "TDATA"):
        src = entry.get(kind)
        if not src:
            continue
        dst = os.path.join(saves_dir, "hakuX", "hdd", "Partition1", kind, os.path.basename(src).lower())
        for d, subdirs, files in os.walk(src):
            subdirs[:] = [x for x in subdirs if not os.path.islink(os.path.join(d, x))]
            out = os.path.join(dst, os.path.relpath(d, src))
            os.makedirs(out, exist_ok=True)
            for f in files:
                fp = os.path.join(d, f)
                if os.path.isfile(fp) and not os.path.islink(fp):
                    shutil.copyfile(fp, os.path.join(out, f))
                    n += 1
    return n


SAVE_META = {"titlemeta.xbx", "titleimage.xbx", "savemeta.xbx", "saveimage.xbx", "datelinfo.xbx", "contentmeta.xbx"}


def _digest_like(b):
    """20 bytes that could be an HMAC-SHA1: many distinct values, no run of zeros, not text."""
    return (len(b) == 20 and len(set(b)) >= 15 and b"\0\0" not in b
            and sum(32 <= c < 127 for c in b) < 16)


def resign_blind(path):
    """Sign a console's save file as hakuX's kernel signs (XCalculateSignature with zero title
    keys: HMAC-SHA1 over the data with a 16-byte zero key). The console's keys are not known
    here, so where the old signature is cannot be checked: it is taken to be the one place
    among the usual ones (the file's first 20 bytes, 20 bytes at 4, or the last 20 bytes,
    before zero padding too) that looks like a digest while the others don't. Returns what it
    did ("start", "at4", "end", "end-unpadded") or None when no single place stands out.
    Saves locked to their console are not handled."""
    import hashlib
    import hmac
    try:
        d = bytearray(open(path, "rb").read())
    except OSError:
        return None
    n = len(d)
    if n <= 40 or n > (64 << 20):
        return None
    m = n
    while m > 0 and d[m - 1] == 0:
        m -= 1
    cands = []
    if _digest_like(d[0:20]):
        cands.append(("start", 0, 20, n))
    elif _digest_like(d[4:24]) and not _digest_like(d[24:44]):
        cands.append(("at4", 4, 24, n))
    if _digest_like(d[n - 20:n]):
        cands.append(("end", n - 20, 0, n - 20))
    elif m >= 60 and m < n and _digest_like(d[m - 20:m]):
        cands.append(("end-unpadded", m - 20, 0, m - 20))
    # a file that looks random throughout (packed or encrypted) gives no hint
    body = d[n // 2:n // 2 + 20]
    if len(cands) != 1 or (_digest_like(body) and _digest_like(d[40:60])):
        return None
    what, at, lo, hi = cands[0]
    d[at:at + 20] = hmac.new(bytes(16), bytes(d[lo:hi]), hashlib.sha1).digest()
    st = os.stat(path)
    with open(path, "wb") as f:
        f.write(d)
    os.utime(path, (st.st_atime, st.st_mtime))
    return what


def resign_saves(saves_dir):
    """Re-sign every seeded save file; returns {relative path: how} for those changed."""
    root = os.path.join(saves_dir, "hakuX", "hdd", "Partition1")
    done = {}
    for d, _, files in os.walk(root):
        for f in files:
            if f.lower() in SAVE_META:
                continue
            how = resign_blind(os.path.join(d, f))
            if how:
                done[os.path.relpath(os.path.join(d, f), root)] = how
    return done


def recorded_override(res, run_id=None):
    """The override that repeats a guided run without the guide: every press the run made, at the
    time it made it (the planned ones before the guide took over, those made to unstick, and the
    guide's), with the planned presses, the unstick presses and the guide all off. None unless the
    guide gave presses and the run then reached gameplay."""
    w = res.get("watch") or {}
    if not w.get("ingame_at_s") or not any(g.get("presses") for g in w.get("guided") or []):
        return None
    taps = [[round(s[0], 1), "tap", s[2]] for s in res.get("steps_done") or [] if len(s) > 2 and s[1] == "tap"]
    if not taps:
        return None
    screens = []
    for g in w["guided"]:
        if g.get("presses") and g.get("screen") and g["screen"] not in screens:
            screens.append(g["screen"])
    end = max(DEFAULT_PLAN["input_time"], taps[-1][0] + 40.0)
    ov = {k: v for k, v in (res.get("override") or {}).items() if k in ("save", "resign")}
    ov.update({
        "_why": ("Recorded from a guided run" + (f" ({run_id or res.get('run_id')})" if run_id or res.get("run_id") else "")
                 + f": gameplay from {w['ingame_at_s']} s. Screens the guide passed: " + "; ".join(screens)[:600]),
        "guide": False,
        "unstick": [],
        "quiet": [[0, 100000]],
        "input_time": end,
        "hard_limit": end + 45.0,
        "extra_steps": taps,
    })
    return ov


# RetroArch

def ra_send(msg, want_reply=False, timeout=0.5):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(msg.encode(), ("127.0.0.1", PORT))
        if want_reply:
            data, _ = s.recvfrom(4096)
            return data.decode(errors="replace").strip()
    except OSError:
        return None
    finally:
        s.close()
    return ""


AUTOCONFIG = """input_driver = "udev"
input_device = "hakuX compat pad"
input_vendor_id = "4617"
input_product_id = "30584"
input_b_btn = "0"
input_a_btn = "1"
input_x_btn = "2"
input_y_btn = "3"
input_l_btn = "4"
input_r_btn = "5"
input_select_btn = "6"
input_start_btn = "7"
input_l3_btn = "9"
input_r3_btn = "10"
input_up_btn = "h0up"
input_down_btn = "h0down"
input_left_btn = "h0left"
input_right_btn = "h0right"
input_l2_axis = "+2"
input_r2_axis = "+5"
input_l_x_plus_axis = "+0"
input_l_x_minus_axis = "-0"
input_l_y_plus_axis = "+1"
input_l_y_minus_axis = "-1"
input_r_x_plus_axis = "+3"
input_r_x_minus_axis = "-3"
input_r_y_plus_axis = "+4"
input_r_y_minus_axis = "-4"
"""


class System:
    """Define where and how RetroArch runs; subclasses implement device details."""
    name = "?"

    def __init__(self, args):
        self.args = args

    def retroarch(self):
        return getattr(self.args, "retroarch", None) or "/usr/bin/retroarch"

    def wrap(self, cmd):
        """The command line that starts RetroArch (a compositor may go in front)."""
        return cmd

    def display_cfg(self):
        return {}

    def audio_cfg(self):
        return {}

    def env(self):
        env = dict(os.environ)
        env["HAKUX_LR_STATS"] = "1"
        env["HAKUX_DISP_STATS"] = "1"
        return env

    def start_queue(self):
        pass

    def end_queue(self):
        pass

    def start_audio(self, path):
        return None

    def stop_audio(self, handle):
        pass

    def info(self):
        return {}


class Amd64Linux(System):
    """A Linux PC without a display server: RetroArch on KMS, KVM CPU backend."""
    name = "amd64-linux"

    def __init__(self, args):
        super().__init__(args)
        self.sink_module = None
        self.worker = getattr(args, "worker", 0)
        self.display = getattr(args, "display", "kms")
        self.SINK = "hakux_compat" + (str(self.worker) if self.worker else "")

    def wrap(self, cmd):
        if self.display != "gamescope":
            return cmd
        w, h = self.args.mode.split("x")
        # A private headless compositor lets workers run alongside the KMS session.
        return ["gamescope", "--backend", "headless", "-W", w, "-H", h, "-w", w, "-h", h, "-r", "60", "--"] + cmd

    def display_cfg(self):
        w, h = self.args.mode.split("x")
        if self.display == "gamescope":
            return {"video_driver": "vulkan", "video_fullscreen": "true", "video_fullscreen_x": w,
                    "video_fullscreen_y": h, "input_driver": "x"}
        return {
            "video_driver": "vulkan",
            "video_context_driver": "khr_display",
            "video_fullscreen": "true",
            "video_fullscreen_x": w,
            "video_fullscreen_y": h,
            "input_driver": "udev",
        }

    def audio_cfg(self):
        return {"audio_driver": "pulse", "audio_device": self.SINK}

    def env(self):
        env = super().env()
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["PULSE_SINK"] = self.SINK
        # Use a unique application name per worker so PipeWire keeps their outputs separate.
        env["PULSE_PROP_OVERRIDE"] = f"application.name={self.SINK}-game"
        return env

    def start_queue(self):
        # Record only this emulator's output.
        out = sh(["pactl", "load-module", "module-null-sink", f"sink_name={self.SINK}",
                  f"sink_properties=device.description={self.SINK}"]).strip()
        self.sink_module = out or None

    def end_queue(self):
        if self.sink_module:
            sh(["pactl", "unload-module", self.sink_module])

    def start_audio(self, path):
        f = open(path, "wb")
        p = subprocess.Popen(["parec", f"--device={self.SINK}.monitor", f"--client-name={self.SINK}-rec",
                              "--format=s16le", "--rate=48000", "--channels=2", "--raw"],
                             stdout=f, stderr=subprocess.DEVNULL)
        return (p, f, time.monotonic())

    def stop_audio(self, handle):
        if not handle or handle[0] == "dump":  # RetroArch writes audio dumps directly.
            return
        p, f, _ = handle
        p.terminate()
        try:
            p.wait(3)
        except subprocess.TimeoutExpired:
            p.kill()
        f.close()

    def info(self):
        build = {}
        bi = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(self.args.core))), "BUILD-INFO")
        if os.path.exists(bi):
            lines = open(bi).read().splitlines()
            build["version"] = lines[0].replace("hakuX ", "") if lines else ""
            for ln in lines:
                if ln.startswith("source "):
                    build["commit"] = ln.split()[1]
                if ln.startswith("DSP JIT"):
                    build["dsp_jit"] = ln[8:]
                if ln.startswith("CPU "):
                    build["cpu_backend"] = ln[4:]
        vk = sh(["vulkaninfo", "--summary"])
        gpu = {}
        for key in ("deviceName", "driverName", "driverInfo", "apiVersion"):
            m = re.search(rf"{key}\s*=\s*(.+)", vk)
            if m:
                gpu[key] = m.group(1).strip()
        cpu = re.search(r"Model name:\s*(.+)", sh(["lscpu"]))
        ra = sh(["pacman", "-Q", "retroarch"]).strip()
        return {
            "system": self.name,
            "device": os.uname().nodename,
            "cpu": cpu.group(1).strip() if cpu else "",
            "arch": os.uname().machine,
            "cpu_backend": build.get("cpu_backend", "KVM"),
            "gpu": gpu,
            "kernel": os.uname().release,
            "frontend": ra or "retroarch",
            "emulator": {"name": "hakuX-lr", **build, "core": self.args.core},
            "display": (f"gamescope headless, Vulkan, {self.args.mode}" if self.display == "gamescope"
                        else f"KMS (khr_display), Vulkan, {self.args.mode}"),
            "audio": f"pulse to a null sink ({self.SINK}), recorded",
            "input": ("RetroArch network RetroPad (UDP), player 1" if self.args.input == "netpad"
                      else "virtual gamepad through uinput (hakuX compat pad), port 1"),
        }


SYSTEMS = {c.name: c for c in (Amd64Linux,)}


NETPAD_PORT = 55400
# Xbox pad names to RetroPad ids, as hakuX maps them (RetroPad B is the Duke's A)
RETROPAD = {
    "a": 0, "x": 1, "back": 2, "start": 3, "up": 4, "down": 5, "left": 6, "right": 7,
    "b": 8, "y": 9, "white": 10, "lb": 10, "black": 11, "rb": 11, "lt": 12, "rt": 13,
    "ls": 14, "rs": 15,
}


class NetPad:
    """Send player 1's RetroPad buttons over UDP; no device access required.
    RetroArch processes one message per frame, so release only held buttons."""

    def __init__(self):
        self.held = set()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send(self, btn, on):
        # struct remote_message { int port, device, index, id; uint16_t state; }
        msg = struct.pack("=iiiiH2x", 0, 1, 0, RETROPAD[btn], 1 if on else 0)
        self.sock.sendto(msg, ("127.0.0.1", NETPAD_PORT))
        (self.held.add if on else self.held.discard)(btn)

    def cmd(self, line):
        words = line.split()
        try:
            if words[0] == "tap":
                self._send(words[1], True)
                time.sleep((int(words[2]) if len(words) > 2 else 150) / 1000)
                self._send(words[1], False)
            elif words[0] in ("down", "up"):
                for b in words[1:]:
                    self._send(b, words[0] == "down")
            elif words[0] == "release":
                for b in list(self.held):
                    self._send(b, False)
            return "ok"
        except (KeyError, IndexError, ValueError) as e:
            return f"err {e}"

    def close(self):
        self.cmd("release")
        self.sock.close()

    def ra_cfg(self):
        return {"network_remote_enable": "true", "network_remote_enable_user_p1": "true",
                "network_remote_base_port": str(NETPAD_PORT)}


class VPad:
    """Drive vpad.py; requires write access to /dev/uinput."""

    def __init__(self):
        if not os.access("/dev/uinput", os.W_OK):
            raise SystemExit("vpad: no write access to /dev/uinput (use --input netpad)")
        cmd = [sys.executable, "-I", os.path.join(HERE, "vpad.py")]
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  text=True, bufsize=1)
        line = self.p.stdout.readline().strip()
        if line != "ready":
            raise SystemExit(f"vpad: helper did not start ({line!r})")
        self.lock = threading.Lock()

    def cmd(self, line):
        with self.lock:
            self.p.stdin.write(line + "\n")
            self.p.stdin.flush()
            return self.p.stdout.readline().strip()

    def ra_cfg(self):
        return {}

    def close(self):
        try:
            self.cmd("quit")
            self.p.wait(3)
        except (OSError, subprocess.TimeoutExpired, BrokenPipeError):
            self.p.kill()


def write_profile(system, profile, core, pad):
    """A fresh RetroArch profile: every directory RetroArch or the core writes
    to lies inside it, so each game starts from nothing."""
    if os.path.exists(profile):
        shutil.rmtree(profile)
    dirs = {}
    for d in ("saves", "states", "system", "screenshots", "playlists", "cache",
              "config", "config/remaps", "logs", "autoconfig/udev"):
        dirs[d] = os.path.join(profile, d)
        os.makedirs(dirs[d])
    with open(os.path.join(dirs["autoconfig/udev"], "hakuX_compat_pad.cfg"), "w") as f:
        f.write(AUTOCONFIG)
    core_dir = os.path.dirname(core)
    cfg = {
        "config_save_on_exit": "false",
        "libretro_directory": core_dir,
        "libretro_info_path": core_dir,
        "core_options_path": os.path.join(profile, "core-options.cfg"),
        "game_specific_options": "false",
        "auto_overrides_enable": "false",
        "auto_remaps_enable": "false",
        "rgui_config_directory": dirs["config"],
        "input_remapping_directory": dirs["config/remaps"],
        "savefile_directory": dirs["saves"],
        "savestate_directory": dirs["states"],
        "system_directory": dirs["system"],
        "screenshot_directory": dirs["screenshots"],
        "playlist_directory": dirs["playlists"],
        "cache_directory": dirs["cache"],
        "joypad_autoconfig_dir": os.path.join(profile, "autoconfig"),
        "log_dir": dirs["logs"],
        "history_list_enable": "false",
        "log_verbosity": "true",
        "log_to_file": "true",
        "log_to_file_timestamp": "false",
        "video_vsync": "true",
        "video_threaded": "false",
        "video_smooth": "true",
        "video_font_enable": "false",
        "menu_enable_widgets": "false",
        "notification_show_screenshot": "false",
        "notification_show_autoconfig": "false",
        "fps_show": "false",
        "video_gpu_screenshot": "true",
        "screenshots_in_content_dir": "false",
        "auto_screenshot_filename": "true",
        "menu_driver": "ozone",
        "assets_directory": "/usr/share/retroarch/assets",
        "desktop_menu_enable": "false",
        "ui_companion_enable": "false",
        "ui_companion_start_on_boot": "false",
        "input_joypad_driver": "udev",
        "input_autodetect_enable": "true",
        "input_menu_toggle_gamepad_combo": "0",
        "quit_press_twice": "false",
        "pause_on_disconnect": "false",
        "network_cmd_enable": "true",
        "network_cmd_port": str(PORT),
        "audio_enable": "true",
        "rewind_enable": "false",
        "run_ahead_enabled": "false",
        "preemptive_frames_enable": "false",
        "savestate_auto_save": "false",
        "savestate_auto_load": "false",
    }
    cfg.update(system.display_cfg())
    cfg.update(system.audio_cfg())
    cfg.update(pad.ra_cfg())
    path = os.path.join(profile, "retroarch.cfg")
    with open(path, "w") as f:
        for k, v in cfg.items():
            f.write(f'{k} = "{v}"\n')
    return path, dirs


# Per-game run

def analyse_audio(raw, offset):
    """RMS per 0.5 s window of s16le stereo 48 kHz; offset = launch - recording start."""
    try:
        data = array.array("h")
        with open(raw, "rb") as f:
            data.frombytes(f.read())
    except OSError:
        return {"error": "no recording"}
    if sys.byteorder != "little":
        data.byteswap()
    win = 48000  # 0.5 s of stereo samples
    windows = []
    for i in range(0, len(data) - win + 1, win):
        chunk = data[i:i + win]
        ss = sum(x * x for x in chunk)
        rms = math.sqrt(ss / len(chunk)) / 32768
        windows.append(round(20 * math.log10(rms), 1) if rms > 0 else -120.0)
    audible = [i for i, db in enumerate(windows) if db > -50]
    peak = max(windows) if windows else -120.0
    first = round(audible[0] * 0.5 - offset, 1) if audible else None
    return {
        "seconds": round(len(data) / 96000, 1),
        "peak_rms_dbfs": peak,
        "first_sound_s": first,
        "audible_fraction": round(len(audible) / len(windows), 2) if windows else 0,
        "rms_dbfs_per_2s": [max(windows[i:i + 4]) for i in range(0, len(windows), 4)],
    }


def scan_log(path):
    flags, stages, fps, options, last = {}, [], [], None, []
    try:
        with open(path, errors="replace") as f:
            for line in f:
                for name, rx in LOG_FLAGS:
                    if rx.search(line):
                        flags.setdefault(name, line.strip()[:300])
                m = STAGE_RE.search(line)
                if m and m.group(1) not in stages:
                    stages.append(m.group(1))
                m = FPS_RE.search(line)
                if m:
                    fps.append(float(m.group(1)))
                m = OPTIONS_RE.search(line)
                if m:
                    options = m.group(1).strip()
                last.append(line.rstrip()[:300])
                if len(last) > 25:
                    last.pop(0)
    except OSError:
        pass
    return {"flags": flags, "stages": stages, "fps": fps, "options": options, "tail": last}


def run_game(system, vpad, game, out_dir, profile_root, overrides, args):
    stem = os.path.splitext(os.path.basename(game))[0]
    plan, steps, ov = plan_for(game, overrides)
    res = {
        "game_file": os.path.basename(game),
        "game_size": os.path.getsize(game),
        "system": system.name,
        "started": now_iso(),
        "plan": plan,
        "override": ov or None,
        "steps": [list(s) for s in steps],
    }
    os.makedirs(out_dir, exist_ok=True)
    if ov.get("skip"):
        res.update(outcome_auto=None, skipped=ov["skip"])
        return res

    profile = os.path.join(profile_root, "profile" + (str(system.worker) if getattr(system, "worker", 0) else ""))
    cfg_path, dirs = write_profile(system, profile, args.core, vpad)
    tid = args.title_ids.get(os.path.basename(game))
    save = args.save_index.get(tid) if tid and ov.get("save", True) else None
    if save:
        res["save"] = {"title_id": tid, "from": save["from"], "files": seed_save(dirs["saves"], save)}
        if ov.get("resign", True):
            res["save"]["resigned"] = resign_saves(dirs["saves"])
    ra_log_out = open(os.path.join(out_dir, "retroarch.stdout"), "w")
    core_log = os.path.join(out_dir, "hakux.log")
    core_log_f = open(core_log, "w")
    audio_raw = os.path.join(out_dir, "audio.raw")
    if args.no_audio:
        audio = None
    elif args.audio_dump:
        open(audio_raw, "wb").close()  # An empty capture means the game played no samples.
        audio = ("dump", audio_raw, time.monotonic())
    else:
        audio = system.start_audio(audio_raw)
    CURRENT["audio"] = audio

    vpad.cmd("release")
    cmd = system.wrap([system.retroarch(), "--config", cfg_path, "--verbose", "-L", args.core, game])
    t0 = time.monotonic()
    cpus = {int(c) for c in args.cpus.split(",")} if getattr(args, "cpus", None) else None
    env = system.env()
    if audio and audio[0] == "dump":
        env["RETROARCH_AUDIO_DUMP"] = audio_raw
    proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=ra_log_out, stderr=core_log_f,
                            env=env, cwd=profile, start_new_session=True,
                            preexec_fn=(lambda: os.sched_setaffinity(0, cpus)) if cpus else None)
    CURRENT["proc"] = proc
    deadline = t0 + plan["hard_limit"]
    status, pending, shots, done_steps = [], [], {}, []
    seen = set()
    stop = threading.Event()
    judge = (Judge(args.judge_model, int(plan["watch_needed"]),
                   None if args.confirm_model == "none" else args.confirm_model,
                   # a game with timed presses of its own keeps them unless its override asks for the guide
                   args.guide_model if args.guide_model != "none" and ov.get(
                       "guide", not (ov.get("extra_steps") or ov.get("steps"))) else None)
             if args.judge_model != "none" and plan.get("watch_every") else None)
    stopped_ingame = None
    unstick = list(plan.get("unstick") or [])
    unstuck = []          # [seconds, button] presses made because the screen was stuck
    acted_on = -1         # verdict count when the last unstick press was made
    quiet_until = -1      # Start and A are held back while the verdict count is at or below this

    def poll_status():
        while not stop.wait(1.0):
            r = ra_send("GET_STATUS", want_reply=True, timeout=0.8)
            status.append((round(time.monotonic() - t0, 1), r))

    poller = threading.Thread(target=poll_status, daemon=True)
    poller.start()

    def collect():
        try:
            names = sorted(os.listdir(dirs["screenshots"]),
                           key=lambda n: os.path.getmtime(os.path.join(dirs["screenshots"], n)))
        except OSError:
            return
        for n in names:
            if n in seen or not pending:
                continue
            p = os.path.join(dirs["screenshots"], n)
            s1 = os.path.getsize(p)
            time.sleep(0.15)
            if s1 == 0 or os.path.getsize(p) != s1:
                continue  # still being written
            seen.add(n)
            name, asked = pending.pop(0)
            dest = os.path.join(out_dir, f"{name}.png")
            shutil.copyfile(p, dest)
            shots[name] = {"file": f"{name}.png", "asked_s": asked,
                           "got_s": round(time.monotonic() - t0, 1), "bytes": s1}
            if judge and name.startswith("w"):
                judge.submit(name, dest, asked)

    def wait_until(t_abs):
        while time.monotonic() < t_abs:
            if proc.poll() is not None or time.monotonic() >= deadline:
                return False
            if judge and judge.ingame.is_set():
                return True
            collect()
            time.sleep(0.05)
        return proc.poll() is None

    ended_early = None
    guide_idle, guide_shots = 0, 0
    for step in steps:
        t, action, rest = step[0], step[1], list(step[2:])
        if not wait_until(t0 + t):
            ended_early = round(time.monotonic() - t0, 1)
            break
        if judge and judge.ingame.is_set():
            stopped_ingame = round(time.monotonic() - t0, 1)
            break
        at = round(time.monotonic() - t0, 2)
        if action in ("shot", "watch"):
            if action == "watch" and not judge:
                continue
            pending.append((rest[0], at))
            ra_send("SCREENSHOT")
        elif action == "tap":
            btn = rest[0]
            if judge and judge.guide_on:
                # The guide plays: its presses for the frame last judged, then a new frame to judge.
                # Planned presses are held back, and nothing is pressed over gameplay.
                plan_now = judge.take_plan()
                if plan_now is not None:
                    for b in plan_now:
                        vpad.cmd(f"tap {b} 120")
                        done_steps.append([round(time.monotonic() - t0, 2), "tap", b, "guided"])
                        time.sleep(GUIDE_GAP)
                    guide_idle = 0
                elif not judge.busy and not any(n.startswith("w") for n, _ in pending):
                    guide_idle += 1
                    if guide_idle >= 2:     # the presses have had their effect: look again
                        guide_shots += 1
                        pending.append((f"wg{guide_shots:02d}", at))
                        ra_send("SCREENSHOT")
                        guide_idle = 0
                done_steps.append([at, "held", btn])
                continue
            if judge:
                nv = len(judge.verdicts)
                if unstick and judge.stuck and acted_on != nv:
                    btn = unstick[len(unstuck) % len(unstick)]
                    acted_on, quiet_until = nv, nv
                    unstuck.append([at, btn])
                elif (btn == "start" and judge.latest == "INGAME") or (btn in ("start", "a") and nv <= quiet_until):
                    # Avoid pausing gameplay; wait for a verdict after an unstick press.
                    done_steps.append([at, "held", btn])
                    continue
            vpad.cmd(f"tap {btn} {int(rest[1]) if len(rest) > 1 else plan['press_ms']}")
            if btn != rest[0]:
                done_steps.append([at, "tap", btn, "instead of", rest[0]])
                continue
        elif action in ("down", "up"):
            vpad.cmd(f"{action} {' '.join(rest)}")
        elif action == "release":
            vpad.cmd("release")
        done_steps.append([at, action] + rest)
    vpad.cmd("release")

    # the last screenshots
    t_end = min(deadline, time.monotonic() + SHOT_WAIT)
    while pending and time.monotonic() < t_end and proc.poll() is None:
        collect()
        time.sleep(0.1)
    collect()
    missing = [n for n, _ in pending if not n.startswith("w")]
    if judge:
        judge.close()
        if stopped_ingame is not None and judge.confirmed_by in shots:
            # Use the confirmed gameplay frame as the final screenshot.
            src = shots[judge.confirmed_by]
            shutil.copyfile(os.path.join(out_dir, src["file"]), os.path.join(out_dir, "final.png"))
            shots["final"] = dict(src, file="final.png", from_watch=judge.confirmed_by)
        for name in [n for n in shots if n.startswith("w")]:
            png, jpg = os.path.join(out_dir, f"{name}.png"), os.path.join(out_dir, f"{name}.jpg")
            if os.path.exists(jpg):  # Reuse the judge's 768x432 image for review.
                os.remove(png)
                shots[name]["file"] = f"{name}.jpg"
        res["watch"] = {"model": args.judge_model, "needed": judge.needed, "ingame_at_s": judge.ingame_at,
                        "confirmed_by": judge.confirmed_by, "stopped_at_s": stopped_ingame,
                        "unstuck": unstuck, "verdicts": judge.verdicts,
                        **({"guide_model": judge.guide_model, "guided": judge.guided} if judge.guide_model else {})}

    exit_how, forced = None, False
    if proc.poll() is not None:
        exit_how = "self"
    else:
        ra_send("QUIT")
        quit_at = time.monotonic()
        while proc.poll() is None and time.monotonic() < min(deadline, quit_at + QUIT_WAIT):
            time.sleep(0.1)
        if proc.poll() is None:
            forced = True
            exit_how = "killed"
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(proc.pid, sig)
                except ProcessLookupError:
                    break
                try:
                    proc.wait(3)
                    break
                except subprocess.TimeoutExpired:
                    pass
        else:
            exit_how = "quit"
    # Terminate child processes in the same group.
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    proc.wait()
    t_exit = round(time.monotonic() - t0, 1)
    stop.set()
    poller.join(2)
    system.stop_audio(audio)
    ra_log_out.close()
    core_log_f.close()

    rc = proc.returncode
    res["exit"] = {
        "how": exit_how, "at_s": t_exit,
        "code": rc if rc is not None and rc >= 0 else None,
        "signal": signal.Signals(-rc).name if rc is not None and rc < 0 else None,
    }
    res["ended_early_s"] = ended_early
    res["steps_done"] = done_steps
    rec = recorded_override(res, args.run_id)
    if rec:
        res["recorded_override"] = rec
    res["shots"] = shots
    res["missing_shots"] = missing
    res["status"] = status

    # Collect evidence from the run's logs.
    ra_log = os.path.join(dirs["logs"], "retroarch.log")
    if os.path.exists(ra_log):
        shutil.copyfile(ra_log, os.path.join(out_dir, "retroarch.log"))
    opts = os.path.join(profile, "core-options.cfg")
    if os.path.exists(opts):
        shutil.copyfile(opts, os.path.join(out_dir, "core-options.cfg"))
    pad = ""
    try:
        with open(os.path.join(out_dir, "retroarch.log"), errors="replace") as f:
            for line in f:
                if ("hakuX compat pad" in line and "port" in line.lower()) or "remote interface" in line:
                    pad = line.strip()
                    break
    except OSError:
        pass
    res["pad"] = pad
    res["core_log"] = scan_log(core_log)

    if audio:
        offset = t0 - audio[2]
        res["audio"] = analyse_audio(audio_raw, offset)
        if shutil.which("ffmpeg") and os.path.exists(audio_raw):
            r = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", "48000",
                                "-ac", "2", "-i", audio_raw, "-c:a", "libopus", "-b:a", "64k",
                                os.path.join(out_dir, "audio.opus")])
            if r.returncode == 0:
                os.remove(audio_raw)
                res["audio"]["file"] = "audio.opus"

    # Assign an automatic outcome; review determines the stage.
    states = [s for _, s in status]
    playing_then_not = False
    seen_playing = False
    for s in states:
        if s and "PLAYING" in s:
            seen_playing = True
        elif seen_playing and s and "CONTENTLESS" in s:
            playing_then_not = True
    tail_unresponsive = len(states) >= 3 and all(s is None for s in states[-3:])
    crashed = res["core_log"]["flags"].get("unhandled-exception")
    if ended_early is not None or exit_how == "self":
        outcome, why = "Crash", f"the emulator exited by itself at {ended_early or t_exit} s"
    elif playing_then_not:
        outcome, why = "Crash", "the core stopped (RetroArch reported no content)"
    elif crashed:  # Check logs for a core stop before the first status poll.
        outcome, why = "Crash", "the guest hit an exception no handler took, and the core stopped (core log)"
    elif forced:
        phase = "while closing" if not missing else "while running"
        outcome, why = "Timeout", f"hard limit reached {phase}; killed"
    elif missing and tail_unresponsive:
        outcome, why = "Timeout", "RetroArch stopped answering; no final screenshot"
    elif stopped_ingame is not None:
        outcome, why = "Completed", (f"in game from {judge.ingame_at} s (judged from screenshots); "
                                     f"stopped at {stopped_ingame} s and the emulator closed")
    else:
        outcome, why = "Completed", "the input plan ran to the end and the emulator closed"
    res["outcome_auto"] = outcome
    res["outcome_why"] = why
    res["duration_s"] = t_exit

    if not args.keep_profile:
        shutil.rmtree(profile, ignore_errors=True)
    return res


# Queue

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--system", required=True, choices=sorted(SYSTEMS))
    ap.add_argument("--core", required=True, help="hakux_libretro.so")
    ap.add_argument("--games", required=True, nargs="+", help="directories or .chd/.iso files")
    ap.add_argument("--out", required=True, help="runs directory; a run-id directory is made in it")
    ap.add_argument("--run-id", help="continue (or name) a run; default: system + time")
    ap.add_argument("--overrides", default=os.path.join(HERE, "overrides.json"))
    ap.add_argument("--only", action="append", default=[], help="substring of the file name (repeatable)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--redo", action="store_true", help="run games that already have a result in this run")
    ap.add_argument("--mode", default="1920x1080", help="output mode on KMS")
    ap.add_argument("--keep-profile", action="store_true")
    ap.add_argument("--input", choices=("netpad", "uinput"), default="netpad")
    ap.add_argument("--worker", type=int, default=0,
                    help="worker number when several run at once: its own ports, audio sink and profile")
    ap.add_argument("--display", choices=("kms", "gamescope"), default="kms",
                    help="kms: the screen (one worker only); gamescope: a headless compositor per worker")
    ap.add_argument("--cpus", help="CPUs the emulator may run on, e.g. 2,10 (a core and its SMT sibling)")
    ap.add_argument("--claims", action="store_true",
                    help="share the queue with other workers: take a game only if no worker has (runs/<id>/claims)")
    ap.add_argument("--confirm-model", default="sonnet",
                    help="model that checks the frame before an in-game verdict ends a run; none: no check")
    ap.add_argument("--no-audio", action="store_true", help="don't record the audio output")
    ap.add_argument("--audio-dump", action="store_true",
                    help="take the audio from inside RetroArch (a build with the RETROARCH_AUDIO_DUMP patch, see "
                         "--retroarch) instead of recording the sound server's sink: exact per process, so it "
                         "works with several workers")
    ap.add_argument("--retroarch", help="RetroArch binary (default /usr/bin/retroarch)")
    ap.add_argument("--judge-model", default="haiku",
                    help="model the in-game judge asks through `claude -p`; none: no checks, full-length runs")
    ap.add_argument("--guide-model", default="none",
                    help="model that, once a game is stuck short of gameplay (an unchanged frame, or none by "
                         f"{GUIDE_AFTER:.0f} s), reads each judged frame and gives the presses to make instead of the "
                         "planned ones; the run is then longer (input to 420 s). none: off. An override's "
                         "\"guide\": false leaves a game out")
    ap.add_argument("--saves", help="archive of saved games (<game>/UDATA/<title id>/...): a game's save is "
                                    "copied onto its fresh console disk; an override's \"save\": false leaves it out")
    args = ap.parse_args()
    args.core = os.path.abspath(args.core)
    if args.guide_model != "none":
        DEFAULT_PLAN.update(input_time=420.0, hard_limit=470.0)
    args.save_index = save_index(args.saves)
    args.title_ids = title_ids() if args.save_index else {}
    global PORT, NETPAD_PORT
    PORT += 10 * args.worker
    NETPAD_PORT += 10 * args.worker

    games = []
    for g in args.games:
        if os.path.isdir(g):
            games += sorted((os.path.join(g, n) for n in os.listdir(g) if n.lower().endswith((".chd", ".iso"))),
                            key=lambda p: os.path.basename(p).lower())
        else:
            games.append(g)
    # Preserve queue priority; sort directory entries alphabetically.
    games = list(dict.fromkeys(os.path.abspath(g) for g in games))
    if args.only:
        games = [g for g in games if any(o.lower() in os.path.basename(g).lower() for o in args.only)]
    if args.limit:
        games = games[:args.limit]
    if not games:
        raise SystemExit("no games")

    if args.display == "kms" and subprocess.run(["pgrep", "-x", "retroarch"], capture_output=True).returncode == 0:
        # Treat all RetroArch processes as display users; gamescope is indistinguishable here.
        if not args.claims:
            raise SystemExit("RetroArch is already running; it would hold the display")

    overrides = {}
    if os.path.exists(args.overrides):
        overrides = {k: v for k, v in json.load(open(args.overrides)).items() if not k.startswith("_")}

    system = SYSTEMS[args.system](args)
    run_id = args.run_id or f"{system.name}-{datetime.datetime.now():%Y%m%d-%H%M}"
    run_dir = os.path.join(os.path.abspath(args.out), run_id)
    os.makedirs(run_dir, exist_ok=True)
    info = system.info()
    info.update(run_id=run_id, started=now_iso(), plan_default=DEFAULT_PLAN,
                judge=None if args.judge_model == "none" else
                {"via": "claude -p (Claude Code CLI)", "model": args.judge_model, "confirm_model": args.confirm_model,
                 "system": JUDGE_SYSTEM, "ask": JUDGE_ASK,
                 **({"guide": {"model": args.guide_model, "system": GUIDE_SYSTEM, "ask": GUIDE_ASK,
                               "after_s": GUIDE_AFTER, "max_answers": GUIDE_MAX}}
                    if args.guide_model != "none" else {})})
    with open(os.path.join(run_dir, "config.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(f"run {run_id}: {len(games)} games -> {run_dir}", flush=True)

    vpad = NetPad() if args.input == "netpad" else VPad()
    system.start_queue()
    interrupted = False

    def on_term(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, on_term)
    try:
        for i, game in enumerate(games, 1):
            slug = slugify(os.path.splitext(os.path.basename(game))[0])
            out_dir = os.path.join(run_dir, slug)
            rpath = os.path.join(out_dir, "result.json")
            if os.path.exists(rpath) and not args.redo:
                print(f"[{i}/{len(games)}] {os.path.basename(game)}: done already", flush=True)
                continue
            pause = os.path.join(run_dir, "PAUSE")
            if os.path.exists(pause):  # Wait for the display to become available.
                print(f"paused ({pause} exists)", flush=True)
                while os.path.exists(pause):
                    time.sleep(5)
                print("resumed", flush=True)
            if args.claims:
                os.makedirs(os.path.join(run_dir, "claims"), exist_ok=True)
                try:
                    os.mkdir(os.path.join(run_dir, "claims", slug))
                except FileExistsError:
                    continue  # Claimed by another worker.
            if os.path.exists(out_dir):
                shutil.rmtree(out_dir)
            res = run_game(system, vpad, game, out_dir, run_dir, overrides, args)
            if (res.get("duration_s") or 0) < 2 and not res.get("shots"):
                # Retry exits before the first frame; temporary display loss can cause them.
                print(f"[{i}/{len(games)}] {os.path.basename(game)}: the emulator quit at {res.get('duration_s')} s "
                      "without a frame; retrying in 30 s", flush=True)
                time.sleep(30)
                shutil.rmtree(out_dir, ignore_errors=True)
                res = run_game(system, vpad, game, out_dir, run_dir, overrides, args)
            res["run_id"] = run_id
            with open(rpath, "w") as f:
                json.dump(res, f, indent=1)
            with open(os.path.join(run_dir, "summary.jsonl"), "a") as f:
                f.write(json.dumps({"game": res["game_file"], "outcome": res.get("outcome_auto"),
                                    "why": res.get("outcome_why"), "s": res.get("duration_s")}) + "\n")
            fps = res.get("core_log", {}).get("fps") or []
            au = res.get("audio", {})
            print(f"[{i}/{len(games)}] {res['game_file']}: {res.get('outcome_auto')} "
                  f"({res.get('outcome_why')}); shots {len(res.get('shots', {}))}, "
                  f"stages {','.join(res.get('core_log', {}).get('stages', []))}, "
                  f"fps {fps[-1] if fps else '-'}, audio {au.get('peak_rms_dbfs', '-')} dBFS, "
                  f"{res.get('duration_s')} s"
                  + (f", in game from {res['watch']['ingame_at_s']} s" if (res.get("watch") or {}).get("ingame_at_s")
                     is not None else ""), flush=True)
            time.sleep(GAP)
    except KeyboardInterrupt:
        interrupted = True
        if CURRENT.get("proc") and CURRENT["proc"].poll() is None:  # Stop only this worker's game.
            try:
                os.killpg(CURRENT["proc"].pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        system.stop_audio(CURRENT.get("audio"))
    finally:
        vpad.close()
        system.end_queue()
        shutil.rmtree(os.path.join(run_dir, "profile" + (str(args.worker) if args.worker else "")), ignore_errors=True)
    print("interrupted" if interrupted else "queue finished", flush=True)


if __name__ == "__main__":
    main()
