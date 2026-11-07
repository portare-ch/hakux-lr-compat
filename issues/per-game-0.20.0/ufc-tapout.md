## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `UFC - Ultimate Fighting Championship - Tapout (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `43560002`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/ufc-ultimate-fighting-championship-tapout-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The game runs and draws correctly, but too fast. Fights start at 45 s (Lajcik vs Mezger), a tap-out shows at 110 s, the UFC Mode menu at 130 s, and Lajcik vs Matt Hughes runs from 150 s to the stop at 177 s.

The round clock runs 4.5 to 7.7 times faster than real time:

| Screenshot | Time since launch | Round clock |
|---|---|---|
| `mid.png` | 48.6 s | RD 1 3:59 |
| `w050.jpg` | 53.0 s | RD 1 3:39 |
| `w150.jpg` | 153.6 s | RD 1 4:44 |
| `w170.jpg` | 173.4 s | RD 1 2:12 |

The title presents 72-97 frames per second during fights and 125-590 per second between them. RetroArch shows 27.7-37.4 new frames per second.

```
hakuX-hle-fps: 326.2 fps (1635 frames in 5.01 s)
hakuX-hle-fps: 468.9 fps (2349 frames in 5.01 s)
hakuX-hle-disp: stats: 29.3 new frames/s, age front to taken 6.65 ms (max 17.51), gap 34.08 ms (max 483.21, 225 over 25 ms)
...
hakuX-hle-fps: 92.4 fps (465 frames in 5.03 s)
hakuX-hle-fps: 97.1 fps (489 frames in 5.04 s)
hakuX-hle-disp: stats: 34.1 new frames/s, age front to taken 6.06 ms (max 41.31), gap 29.29 ms (max 68.98, 219 over 25 ms)
...
hakuX-hle-fps: 590.4 fps (2972 frames in 5.03 s)
hakuX-hle-disp: stats: 27.8 new frames/s, age front to taken 5.99 ms (max 19.03), gap 35.96 ms (max 584.38, 199 over 25 ms)
...
hakuX-hle-fps: 87.0 fps (438 frames in 5.03 s)
hakuX-hle-fps: 85.8 fps (432 frames in 5.03 s)
hakuX-hle-disp: stats: 32.9 new frames/s, age front to taken 6.41 ms (max 25.05), gap 30.35 ms (max 54.07, 214 over 25 ms)
```

## Expected

The round clock counts down in real time.

## Notes

- Seen in the only run; no earlier results for this title.
- RetroArch ran the core at 60.0 `retro_run` calls per second for the whole run.
