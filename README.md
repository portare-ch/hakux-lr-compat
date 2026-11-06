# hakuX-lr compatibility list

Compatibility data for [hakuX-lr](https://github.com/portare-ch/hakuX-lr), the
libretro Xbox core: every NTSC-U disc in the test library, run on each core
release and reviewed from screenshots. The browsable list is
[COMPATIBILITY.md](COMPATIBILITY.md); the same data with screenshots, the tested
hardware and recordings is published as a page (see Shareable page below).

This repository holds:

| Path | What |
|---|---|
| `compat.json` | The list: one entry per game (title, Xbox title ID, file, region) and one result per system |
| `COMPATIBILITY.md` | The list as a table, with the setup of every run |
| `media/<system>/<game>/` | 320x240 screenshots of each result: `boot`, `mid`, `final`, and `ingame` (the first frame the judge called gameplay) |
| `runs/<run-id>/` | Each run's `config.json` and every game's `result.json` (timings, judge verdicts, inputs, log tail) |
| `reviews/` | The review verdicts, as applied with `compat.py review --file` |
| `overrides.json` | Per-game input plans for games that stall on a menu |
| `runner.py`, `compat.py`, `export_page.py`, `page_template.html`, `vpad.py` | The harness, the list tool and the page export |
| `issues/` | Drafts of the hakuX-lr issues filed from the list |

Full captures (PNG screenshots, recordings, core and RetroArch logs) stay on the
test machine.

Each game's **Issues** link (page and table) searches the hakuX-lr issues for
`"<title ID>" OR "<title>"`; there may be no issue yet.

The compatibility list (`compat.json`) has one entry per game and one result per
system: amd64 Linux, aarch64 Linux and Android. A result holds:

- **Stage:** Untested, Boot, Intro, Menu, In-game or Playable. This is the
  furthest stage reached, confirmed by review.
- **Outcome:** Completed, Crash, Timeout or Needs manual input.
- **Observations:** graphics, audio and notes, plus screenshots, logs and the
  audio recording.
- **Configuration:** emulator version and commit, device, CPU, architecture and
  CPU backend, GPU and driver, frontend, display, input and core options.

A result applies only to the configuration it was tested with. Testing one
system leaves the others unchanged.

Generated views: `COMPATIBILITY.md` (the table), `media/` (thumbnails), and on
the test machine `report.html` (linked to the full captures and logs) and
`contact-sheets/<system>/sheet-NN.png`.

## Stage meanings

| Stage | Meaning |
|---|---|
| Boot | The game started, but nothing past booting was seen: a black screen, a loading screen or a hang. A game that fails earlier is also listed here, with a Crash outcome. |
| Intro | Logos, movies, a legal or warning screen, or attract mode. |
| Menu | A title screen ("Press Start") or a menu. |
| In-game | Gameplay was reached, but the run showed a problem that gets in the way of play: a crash or freeze, no sound, a low frame rate (around 20 fps) or a major graphics fault (missing textures, broken sprites, a covered or half-drawn view, missing menu text). |
| Playable | Gameplay was reached and nothing seen gets in the way of play. |

A Timeout does not establish that a game is incompatible. Playable is judged
from one short run (screenshots, measured frame rate and sound, the log), not
from playing a game through.

## Automated first pass (`runner.py`)

Each game in the queue runs in a fresh RetroArch process with a disposable
profile. The profile has its own RetroArch config, saves, console disk, shader
caches, core options and screenshots. Default plan (seconds after launch):

| Time | Step |
|---|---|
| 10 | Screenshot `boot` |
| from 10.5 | Start and A in turn, every 2.5 s (150 ms presses), until 293 |
| from 30, every 20 | Screenshot `wNNN` for the in-game judge (below) |
| 45 | Screenshot `mid` |
| 295 | Release everything |
| 300 | Screenshot `final`, then close RetroArch over the network command interface |
| 330 | Hard limit: the process group is killed (SIGTERM, then SIGKILL) |

A run ends early once gameplay is reached. The **in-game judge** sends each
`wNNN` screenshot (scaled to 768x432) to a small model through the Claude Code
CLI (`claude -p`, the logged-in user's account; `--judge-model`, default
`haiku`) and asks whether it shows gameplay under the player's control. Two
in-game verdicts in a row (`watch_needed`) end the run: that frame becomes
`final.png` and RetroArch is closed. A blank frame (nothing brighter than 10 % grey) counts as not in game, and a
frame unchanged since the last one judged takes the last verdict, both without a
call. The verdicts are in
`result.json` under `watch`; the watch frames are kept as `wNNN.jpg`.
`--judge-model none` turns the checks off (every run lasts 300 s).

With the judge on, the input adapts: Start is held back while the last judged
frame showed gameplay (Start would open a pause menu that A often doesn't
close), and when a judged frame is unchanged and not gameplay, the next press is
replaced by one of `unstick` (`b`, then `down`, in turn) and Start and A are
held back until the next verdict, so the next check sees what the press did. These presses are in `result.json` under
`watch.unstuck` and in `steps_done`. Runs of
hakuX-lr 0.19.0 used the earlier 45 s plan with no judge.

The runner records the core's log (with `HAKUX_LR_STATS` / `HAKUX_DISP_STATS`),
RetroArch's log, the core options RetroArch wrote, `GET_STATUS` once a second
and the audio output. The audio is recorded as Opus with loudness per window.
The runner also sets an automatic outcome:

- **Crash:** RetroArch exited by itself, or the core unloaded.
- **Timeout:** the hard limit was reached, or RetroArch stopped answering and
  the final screenshot never arrived.
- **Completed:** the whole plan ran, or the judge saw gameplay, and RetroArch
  closed.

**Needs manual input** and the stage are set during review.

Input uses RetroArch's network RetroPad (`network_remote_enable`, UDP 55400)
for player 1, so no device node or root access is needed. `--input uinput`
uses `vpad.py` instead, a uinput gamepad (not a keyboard, whose keys would also
reach the active console). The uinput path needs write access to
`/dev/uinput`.

```sh
python3 runner.py --system amd64-linux \
  --core cores/0.19.1-x86_64/hakux-0.19.1/lib/libretro/hakux_libretro.so \
  --games <CHD dir> --out runs [--run-id <id>] [--only <name part>] [--limit N] [--redo]
```

Rerunning with the same `--run-id` skips games that already have a
`result.json`. `--redo` runs them again.

### Per-game overrides

Overrides go in `overrides.json`, keyed by file name, file stem or slug. An
override can change any default (`boot_wait`, `input_time`, `input_gap`,
`buttons`, `press_ms`, `settle`, `mid_shot`, `hard_limit`). It can also replace
the plan with explicit `steps` (`[[seconds, "shot", name]`,
`[s, "tap", btn, ms]`, `[s, "down", btn...]`, `[s, "up", btn...]`,
`[s, "release"]`), add `extra_steps`, or set `skip` with a reason.

Buttons: `a b x y black white back start up down left right lt rt ls rs`.

## Updating the list

```sh
python3 compat.py import <CHD dir>      # new CHDs get Untested on every system
python3 compat.py ingest runs/<run-id>  # results become "Unreviewed" with the automatic outcome
python3 compat.py review amd64-linux "Halo 2" --stage Menu --outcome Completed --graphics "..." --notes "..."
python3 compat.py review --file reviews.json --by <name>
python3 compat.py titleids              # each game's Xbox title ID, from its run's core log
python3 compat.py media                 # media/ thumbnails of the current results
python3 compat.py report
```

Re-ingesting the same run keeps reviewed entries. Use `--force` to replace them.

## Shareable page

`python3 export_page.py <dir>` writes `<dir>/index.html` from `compat.json`
(the list as embedded JSON, from `page_template.html`) and `<dir>/packs/`.
That directory is what is published as the artifact
https://claude.ai/artifact/XHkeBBWZiDSu6znZzXbE76. Republish to the same URL
after re-exporting.

An artifact version holds at most 511 files and 256 MB (one publish: 255
files, 64 MB), so captures are packed six games to a group:
`packs/gNNN-<hash>-t.webp` (320x240 thumbnails, a row per game: boot, mid,
final), `-f.webp` (the same at 800x600, loaded by the screenshot viewer) and
`.ogg` (the recordings back to back, 46 s each, re-encoded at 32 kbit/s
Opus). `packs.json` keeps the group assignment in test order, so a group's
files change (under a new hash) only while it fills; a retested game gets a new
row, its old row stays unused, and a group with no row in use is dropped. When republishing, send the pack files that are new and `null` for
the ones that disappeared: files left out of a publish are kept.

Reviews are recorded in `reviews/<run-id>.json` and applied with
`compat.py review <system> --file`.

## Systems

- **amd64 Linux:** zenbox (Ryzen 7 9800X3D, KVM backend, RX 9070 XT on RADV),
  RetroArch on KMS at 1920x1080. Audio goes to a private PulseAudio null sink
  (`hakux_compat`), so nothing plays on the speakers during a run.
- **aarch64 Linux and Android:** not tested by decision (only amd64 is tested
  for now), so every entry is Untested. The runner has only the `amd64-linux`
  adapter. A device adapter would subclass `System` in `runner.py`.
