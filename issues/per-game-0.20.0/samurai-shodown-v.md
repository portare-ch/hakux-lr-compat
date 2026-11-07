## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Samurai Shodown V (U) (En,Ja,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `534e0004`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min, ending early once in game. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/samurai-shodown-v-u-en-ja-fr-de-es-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The title screen and a fight (Yoshitora vs Mina, from about 30 s) render with correct characters and HUD at 51–60 fps, with sound. The stage background is corrupted in every fight frame (30 s, 45 s, 50 s and the final shot at 55 s): strips of tiles sit in the wrong place on the building and the floor, and white, black and checkered blocks cover parts of it. The corrupted areas change from frame to frame. The run stopped at 55 s once it was in game.

From about 5 s the core reports that its texture table is full and drops textures; during the fight it does so 14–29 times a second, 496 times in the run:

```
hakuX-hle-pb: textures: table full, the 384 checked longest ago dropped (1152 kept, 17 of 24 MiB)
hakuX-hle-pb: textures: table full, the 384 checked longest ago dropped (1152 kept, 17 of 22 MiB)
...
hakuX-hle-pb: textures: table full, the 384 checked longest ago dropped (1152 kept, 15 of 21 MiB)
```

The push-buffer stats at the end of the run count `textures 452617 (1207 held, 16 MiB)`.

## Expected

The stage background is drawn whole, without misplaced tiles or blocks.

## Notes

- No other game in the 0.20.0 run logs `textures: table full`.
- Seen in the only run; no earlier results for this title.
