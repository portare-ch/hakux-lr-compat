## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Thrillville (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4c410022`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/thrillville-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The game plays at 44-60 fps, but the lower part of every picture is black:

- 31.2 s, "Visit Thrillville" title: the picture ends at about 67% of the height.
- 51.8 s, walking in the park (HUD 0/25, $2,000, NEXT PARK): it ends at about 81%.
- 71.5 s, pause menu: it ends at about 67%, cutting the menu off just below SAVE.

The display mode has a 2560-byte pitch and the framebuffer at 01000000. The three buffers at 01000000, 0112c000 and 01258000 are 0x12c000 bytes apart, the size of a 640 x 480 x 4-byte buffer, but the push-buffer decoder logs them as 640x409, 640x339 and 640x268 surfaces:

```
hakuX-native: av: display mode 080f0d12 format 00000012 pitch 2560 fb 01000000
hakuX-hle-pb: surface 1: 01000000 format 12 640x409 pitch 2560
hakuX-hle-pb: surface 2: 01258000 format 2e 640x268 pitch 2560
hakuX-hle-pb: surface 3: 0112c000 format 12 640x339 pitch 2560
```

## Expected

The full 640x480 picture, with the HUD and the whole pause menu visible.

## Notes

- Wallace & Gromit: The Curse of the Were-Rabbit (same run) shows the same black bottom (the picture ends at about 80%, then 67%) and logs the same display mode and the same three surfaces (01000000 640x409, 01258000 640x268, 0112c000 640x339).
- Sound comes in bursts with 2-6 s silent gaps, audible in 34% of the run.
- Seen in the only run; no earlier results for this title.

- Related (the same colour-surface heights (640x409, 640x339) at the same addresses): #140
