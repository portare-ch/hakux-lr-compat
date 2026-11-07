## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Star Wars - Jedi Knight - Jedi Academy (Japan, Asia) (En,Fr,De).chd`, NTSC-J, CHD (`chdman createdvd` from an XISO); XBE title ID `4c41000b`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s; an override in [overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json) stops the presses from 132 s so they don't interrupt the mission load. A screenshot every 20 s from 30 s; a run lasts up to 5 min, ending early once in game. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/star-wars-jedi-knight-jedi-academy-japan-asia-en-fr-de/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The LucasArts logo, the shuttle scenes of the in-engine intro and the first mission (Yavin, with HUD, from about 150 s) render at 55–60 fps, with sound. The run stopped at 176 s once it was in game. Two things are drawn wrong:

- **Character models in the intro.** At 30 s a face floats on a box-shaped body with dark shards around it; at 70 s a body is torn into long, stretched triangles that reach across the scene.
- **A patch on the ground in the level.** At 150 s, 170 s and in the final shot (176 s) a flat rectangle filled with a blurry, low-resolution jungle picture covers the ground in front of Jaden, from the middle of the screen down to the HUD.

The core logs no errors at those moments. Guest RAM is nearly full the whole run (about 400 KiB free), and the core refuses some commits and contiguous allocations at boot, at about 10 s, at about 22–24 s (before the intro) and at about 125–128 s (the mission load), without a crash:

```
hakuX-native-mm: commit 00c45000+81000: out of physical memory (#1, 404 KiB free)
hakuX-native-mm: commit 029b0000+82000: out of physical memory (#2, 404 KiB free)
hakuX-native-mm: commit 029b0000+13a000: out of physical memory (#1, 404 KiB free)
hakuX-native: mm: contiguous allocation of 1204 KiB failed (#1; from 0023ebb0, 00000000-04000000, align 40; free 404 KiB: 50000+268K 297c000+72K | 4 runs, largest 268 KiB)
```

## Expected

Whole character models in the intro, and the level's ground without the patch.

## Notes

- The U disc (`Star Wars - Jedi Knight - Jedi Academy (U) (En,Fr,De).chd`, same title ID), run on 0.19.1 with #104, the fix for the out-of-memory crash in #92, shows the same two faults: torn models at 50 s and 70 s and the same ground patch at 150 s and in the final shot ([result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261105-0.19.1-mmfix/star-wars-jedi-knight-jedi-academy-u-en-fr-de/result.json)). That run also logged refused commits without a crash.
- The first 0.20.0 run of this disc, without the override, shows the same torn models in the intro (identical 70 s shot); it then sat on LOAD GAME from about 150 s and never reached the level.
- 28–60 new frames/s; five stalls of 0.6–1.4 s (frames 2, 1017, 6987, 6989 and 7430).
