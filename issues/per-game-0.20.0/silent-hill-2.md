## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Silent Hill 2 - Restless Dreams (U) (En,Ja).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4b4e0004`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min, ending early once in game. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/silent-hill-2-restless-dreams-u-en-ja/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The title and the restroom scene render correctly, and James is in control from about 30 s, with sound. The Start presses pause the game, and the Paused screen is broken each time:

- At 45 s the frozen picture is cut into blocks at the middle of the screen that don't line up, and the right sixth and the bottom quarter are smeared lines.
- At 70 s and in the final shot (75 s) only the top-left quarter of the screen shows the frozen picture, at its normal size. To its right are horizontal streaks, below it vertical streaks, and the bottom-right quarter is one flat dark colour.

The "Paused" text itself draws correctly. Unpaused gameplay (30 s, 50 s) is correct. The run stopped at 75 s once it was in game.

The core logs no errors around the pauses. After the Start presses it logs a 640x480 render target that is then sampled as a texture:

```
hakuX-native-usb: gamepad 0: buttons 0000 -> 0010 (A 00)
hakuX-hle-back: clear #1383 flags=0xf3 color=40464646 z=1.000 rects=0 rt=3 (changed)
hakuX-hle-pb: surface 34: 03032000 format 12 640x480 pitch 2560
hakuX-hle-drawlog: rt-tex id=34 surf=1 img=1 layout=5 slot=32 fmt=44 640x480 rt=10
...
hakuX-native-usb: gamepad 0: buttons 0000 -> 0010 (A 00)
hakuX-hle-drawlog: rt-tex id=1 surf=1 img=1 layout=5 slot=33 fmt=44 640x480 rt=3
```

## Expected

The Paused screen shows the whole frozen picture behind the "Paused" text.

## Notes

- The core option render scale is the default 2x. In the 70 s and 75 s shots the intact part is exactly half the output's width and half its height.
- 38–60 new frames/s (`hakuX-hle-disp`).
- Seen in the only run; no earlier results for this title.
