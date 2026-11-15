# hakuX-lr compatibility list

Test results for [hakuX-lr](https://github.com/portare-ch/hakuX-lr), the original
Xbox libretro core. Browse the [compatibility list](https://hakuxlr.portareos.org/)
with screenshots and audio measurements, or use the [Markdown table](COMPATIBILITY.md).
The library contains 662 discs, primarily NTSC-U. Results apply only to the
listed configuration; a short test does not establish full-game compatibility.

| Path | Contents |
|---|---|
| `compat.json` | Games, title IDs and results by system |
| `COMPATIBILITY.md` | Generated results, notes and test configurations |
| `media/<system>/<game>/` | 320×240 screenshots: boot, mid, final and first detected gameplay |
| `runs/<run-id>/` | Run configuration and per-game results: timings, inputs, verdicts and log excerpts |
| `reviews/` | Review verdicts applied with `compat.py review --file` |
| `overrides.json` | Per-game input plans |
| `runner.py`, `compat.py`, `vpad.py` | Test runner, data tools and optional virtual gamepad |
| `export_page.py`, `page_template.html`, `packs.json` | Web export and media-pack assignments |
| `issues/` | Issue drafts and filing records |

Full PNG captures, recordings and logs stay on the test machine. Each game's
Issues link searches hakuX-lr by title ID or name; a matching issue may not exist.

## Results

Each result records a stage, outcome, graphics and audio observations, notes,
captures and the tested configuration: core version and commit, device, CPU
backend, GPU and driver, frontend, display, input and core options.

| Stage | Meaning |
|---|---|
| Untested | No test on this system. |
| Boot | Started but did not pass a black or loading screen, or crashed before boot. |
| Intro | Logos, movies, legal screens or attract mode. |
| Menu | Title screen or menus. |
| In-game | Gameplay with a crash, freeze, silence, low frame rate (around 20 fps) or major graphics fault. |
| Playable | Gameplay with no observed problem that prevents play. |

Stages are reviewed from screenshots, frame rates, audio measurements and logs.
Playable describes one short run, not a completed playthrough.

Outcomes are **Completed**, **Crash**, **Timeout** or **Needs manual input**.
A timeout alone does not establish incompatibility. Testing one system leaves
other systems' results unchanged.

## Test runner

`runner.py` starts each game in a fresh RetroArch process with an isolated
profile, saves, console disk, caches and core options. The default schedule is:

| Time after launch | Action |
|---|---|
| 10 s | Take the boot screenshot. |
| 10.5–293 s | Alternate Start and A every 2.5 s, held for 150 ms. |
| From 30 s, every 20 s | Capture a frame for gameplay detection. |
| 45 s | Take the mid screenshot. |
| 295 s | Release all buttons. |
| 300 s | Take the final screenshot and send Quit. |
| 330 s | Terminate the process group (SIGTERM, then SIGKILL). |

A background judge uses Claude Code (`claude -p`, the user's account;
`--judge-model haiku` by default) to detect player-controlled gameplay in
768×432 screenshots. Two consecutive gameplay verdicts end the run early;
the last frame becomes `final.png`. Blank frames count as no gameplay, and
unchanged frames reuse the last verdict. Watch frames and verdicts are saved
as `wNNN.jpg` and `result.json` → `watch`. Use `--judge-model none` to disable
these checks and run the full 300 s plan.

During detected gameplay, Start is suppressed to avoid pausing. If a frame is
unchanged and shows no gameplay, the runner alternates B and Down to unstick
it, then suppresses Start/A until the next verdict. These inputs are recorded
in `watch.unstuck` and `steps_done`. The 0.19.0 tests used a 45 s plan without
a judge.

### Guide

`--guide-model <model>` (off by default) lets a second model operate the pad
when a game does not reach gameplay with the planned presses. It takes over
when a judged frame is unchanged and shows no gameplay, or when no gameplay
has been seen by 100 s. From then on:

- the planned Start and A presses are held back;
- each judged frame that shows no gameplay is sent to the guide model, which
  answers with up to 10 presses for that screen (a prompt's answer, the way
  to Done on a name keyboard, the menu entry that starts play);
- the runner makes those presses 0.45 s apart, takes a new frame (`wgNN`)
  about 5 s later and has it judged;
- nothing is pressed while the last frame showed gameplay; two gameplay
  verdicts in a row end the run as usual;
- after 18 answers the planned presses resume.

A guided run presses for up to 420 s instead of 285 s (hard limit 470 s).
The guide's answers are saved in `result.json` → `watch.guided` (frame, time,
presses, what it took the screen to be), the presses made in `steps_done`
marked `guided`, and the prompt in the run's `config.json`. The guide is told
never to overwrite or delete saved data. A game whose override has
`extra_steps` or `steps` keeps its timed presses and is not guided unless the
override sets `"guide": true`; `"guide": false` turns it off for a game.

The guide is only for finding the way. A guided run that reaches gameplay
records it as an override: `result.json` → `recorded_override` holds every
press the run made, at the time it made it (the planned ones before the
guide took over, the unstick presses and the guide's), with the planned
presses, the unstick presses and the guide switched off. Results for the
list come from running the game again from that override, without the guide:

```sh
python3 runs/record-overrides.py runs/<guided run id> > games.txt   # writes overrides.json
mapfile -t G < <(sed "s|^|<CHD-dir>/|" games.txt)
python3 runner.py --system amd64-linux --core <core> --games "${G[@]}" --out runs --run-id <replay run id>
```

`record-overrides.py` leaves a game that already has an override alone
(`--force` replaces it; `--dry-run` only lists). The replay needs no model:
with `--judge-model none` it makes the recorded presses and runs to the end
of the plan. A replay that does not reach gameplay (a load that took longer
than in the guided run) leaves the game as it was.

### Saved games

`--saves <dir>` copies a game's saved game onto its fresh console disk before
the game starts, so that a title can be tested past profile creation. `<dir>`
is laid out as `<game>/UDATA/<title id>/...`, with `TDATA` beside it where a
save has one, as in the
[Xbox save archive](https://github.com/Triticum0/Xbox-save-archive)
(hakuX-lr issue 213). The title ID comes from `compat.json`. `result.json` →
`save` names the archive folder used and the files copied. An override's
`"save": false` leaves a game's save out.

Saves from a console are signed with keys hakuX-lr does not have, and a game
reports them as damaged. The runner therefore signs each copied file again as
hakuX-lr's kernel signs (HMAC-SHA1 with a zero title key). It has no console
key to check where the old signature is, so it replaces a signature only
where exactly one of the usual places (the file's first 20 bytes, 20 bytes at
offset 4, the last 20 bytes, also before zero padding) looks like a digest
and the file is not random-looking throughout. Files where that is not so are
left as they are, and saves locked to their console are not handled.
`save.resigned` lists the files changed and where; `"resign": false` in an
override turns it off. The archive itself is never modified.

The runner records core statistics (`HAKUX_LR_STATS`, `HAKUX_DISP_STATS`),
RetroArch logs, core options, one-second `GET_STATUS` samples and Opus audio
with loudness measurements. Automatic outcomes are:

- **Crash:** RetroArch exits unexpectedly or the core unloads.
- **Timeout:** the hard limit is reached, or RetroArch stops responding and
  the final screenshot is missing.
- **Completed:** the plan finishes or gameplay is detected, and RetroArch closes.

Stage and **Needs manual input** are set during review. Input uses player 1's
network RetroPad (UDP 55400), requiring no device access. `--input uinput`
uses `vpad.py` and requires write access to `/dev/uinput`.

```sh
python3 runner.py --system amd64-linux \
  --core cores/0.19.1-x86_64/hakux-0.19.1/lib/libretro/hakux_libretro.so \
  --games <CHD-dir> --out runs --run-id <id>
```

Use `--only <name-part>` or `--limit N` to restrict the queue. Existing
`result.json` files are skipped unless `--redo` is set.

### Input overrides

`overrides.json` keys are file names, stems or slugs. Entries can change
`DEFAULT_PLAN` settings (`boot_wait`, `input_time`, `input_gap`, `buttons`,
`press_ms`, `settle`, `mid_shot`, `hard_limit`), replace `steps`, add
`extra_steps`, suppress default inputs with `quiet: [[from, to], ...]`, set
`skip` to a reason, or set `guide`, `save` and `resign` (see above).

Steps use `[seconds, action, args...]`: `shot <name>`, `tap <button> [ms]`,
`down <buttons...>`, `up <buttons...>` or `release`.
Buttons: `a b x y black white back start up down left right lt rt ls rs`.

## Update results

```sh
python3 compat.py import <CHD-dir>      # Add games as Untested on every system.
python3 compat.py ingest runs/<run-id>  # Import automatic outcomes as Unreviewed.
python3 compat.py review amd64-linux "Halo 2" --stage Menu --outcome Completed --graphics "..." --notes "..."
python3 compat.py review --file reviews.json --by <name>
python3 compat.py titleids              # Read Xbox title IDs from core logs.
python3 compat.py media                 # Update thumbnails.
python3 compat.py report               # Update Markdown, HTML and contact sheets.
```

Re-ingesting a run preserves reviewed entries; `--force` replaces them.
Keep review files in `reviews/<run-id>.json`.
Generated local views include `report.html` and
`contact-sheets/<system>/sheet-NN.png`.

## Web export

`python3 export_page.py <dir>` writes `index.html` (an embedded page),
`web.html` (a standalone HTML document) and `packs/`. Serve `web.html` with
`packs/` at [hakuxlr.portareos.org](https://hakuxlr.portareos.org/).
The test server uses nginx on AlmaLinux, `/var/www/hakuxlr`, and
`/etc/nginx/conf.d/hakuxlr.conf`.

The embedded page can also be published as an artifact. Each image pack
holds six games:

- `gNNN-<hash>-t.webp`: 320×240 thumbnails, one row per game (boot, mid, final).
- `gNNN-<hash>-f.webp`: 800×600 images for the screenshot viewer.

Audio observations remain visible, but recordings are private. Exports contain
no audio or playback controls. Legacy audio packs are moved to a private
sibling directory named `<dir>-private-audio-*`; keep it outside deployments.
Raw recordings on the test machine are unchanged.

The web server must also block legacy audio URLs:

```nginx
location ~* \.(ogg|oga|opus|mp3|wav|flac|m4a|aac|aif|aiff|wma)$ {
    add_header Cache-Control "no-store" always;
    return 404;
}
```

Previously published copies on other hosts must be unpublished separately.

`packs.json` preserves assignments. Retests get new rows; old rows remain
unused, and empty groups are dropped. File hashes change when a pack changes.
When republishing the artifact, upload new packs and send `null` for deleted
files; omitted files remain on the host.

## Systems

- **amd64 Linux:** zenbox, Ryzen 7 9800X3D, KVM, Radeon RX 9070 XT with RADV;
  RetroArch on KMS at 1920×1080. Audio uses a private PulseAudio null sink
  (`hakux_compat`).
- **aarch64 Linux and Android:** untested. The runner currently implements only
  `amd64-linux`; other devices need a `System` adapter in `runner.py`.
