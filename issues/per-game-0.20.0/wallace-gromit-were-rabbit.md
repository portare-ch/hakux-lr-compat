## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Wallace & Gromit - The Curse of the Were-Rabbit (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4b4e0034`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/wallace-gromit-the-curse-of-the-were-rabbit-u-en-fr-de-es-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Konami logo, the intro cutscene (30-210 s) and Wallace's first dialog over the manor (from about 210 s) render at 60 fps, but the bottom of the picture is always black. In each screenshot the picture ends at one of two heights: 67 % or 81 % of the frame (w030, w050, w070, w110, w210, w290 at 67 %; w090, w130-w190, w230-w270 at 81 %). Below that line the screen is black, in the cutscene and in the game view.

The game creates a 640x480 device, but hakuX logs its color surfaces as 640x409 and 640x339 and its depth surface as 640x268. The three surfaces are 1,228,800 bytes (640 x 480 x 4) apart. The two picture heights in the screenshots (289 and 352 of 432 rows) are in about the same ratio as 339 to 409.

```
hakuX-hle-pb: device 640x480
hakuX-hle-back: display 1280x960 gen 1 (4 slots)
hakuX-hle-back: DEVICE_CREATE 640x480 surfaces=0 present=0 scale=2
hakuX-hle-pb: surface 1: 01000000 format 12 640x409 pitch 2560
hakuX-hle-pb: surface 2: 01258000 format 2e 640x268 pitch 2560
hakuX-native: av: display mode 080f0d12 format 00000012 pitch 2560 fb 01000000
hakuX-hle-pb: surface 7: 0112c000 format 12 640x339 pitch 2560
...
hakuX-hle-drawlog: rt-tex id=1 surf=1 img=1 layout=5 slot=288 fmt=44 640x409 rt=291
hakuX-hle-drawlog: rt-tex id=7 surf=1 img=1 layout=5 slot=298 fmt=44 640x339 rt=301
```

## Expected

The picture fills the 640x480 frame.

## Notes

- Thrillville (`thrillville-u`, also in this run) logs the same three surfaces at the same addresses with the same sizes (640x409, 640x268, 640x339), and its picture is also cut off at the bottom.
- From about 210 s to Quit at 300 s, Wallace's dialog ("Righto, Gromit...", with an A prompt) stays up; the A presses don't dismiss it. It is not known whether this is related.
- Seen in one run; there is no result from an earlier version.

- Related (the same colour-surface heights (640x409, 640x339) at the same addresses): #153
