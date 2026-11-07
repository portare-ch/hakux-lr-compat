## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Spartan - Total Warrior (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `5345008b`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/spartan-total-warrior-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The logos and the "Loading" title screen (30 s) render correctly. From about 45 s to the end of the run the in-engine intro plays (the speech in Sparta, the army, the Roman attack) with sound and subtitles, at 60 fps. Its 3D scenes have wrong colours in every screenshot: skin, faces, sky, stone, banners and armour show in false green, cyan, yellow and purple tones, with purple and orange patches in the sky. The subtitle text is white. Start and A don't skip the intro, so gameplay isn't reached.

The core logs no errors or warnings for the run.

## Expected

The intro in its normal colours.

## Notes

- At about 3 s, during the logos, the title sets up a chain of render targets in format 1e (640x480, 320x240, 160x120, 80x60) and samples each one as a texture for the next:
  ```
  hakuX-hle-pb: surface 6: 0384c000 format 1e 320x240 pitch 1280
  hakuX-hle-drawlog: rt-tex id=3 surf=1 img=1 layout=5 slot=3 fmt=44 640x480 rt=6
  hakuX-hle-pb: surface 10: 038e2000 format 1e 160x120 pitch 640
  hakuX-hle-pb: surface 12: 038f4c00 format 1e 80x60 pitch 320
  hakuX-hle-drawlog: rt-tex id=12 surf=1 img=1 layout=5 slot=11 fmt=44 80x60 rt=13
  hakuX-hle-drawlog: rt-tex id=13 surf=1 img=1 layout=5 slot=12 fmt=44 80x60 rt=3
  ```
  The display mode is `av: display mode 0801010d format 0000001e`.
- 49–60 new frames/s.
- Seen in the only run; no earlier results for this title.
