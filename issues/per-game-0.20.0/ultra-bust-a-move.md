## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Ultra Bust-A-Move (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4d4a000c`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/ultra-bust-a-move-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

Music starts at 3 s and plays for the whole run. From 10 s to Quit at 300 s the screen shows only the animated "Now Loading" bubbles on white, at 60 fps. No logo or title screen appears. The game reads the pad (57 Start presses are logged), but the presses change nothing.

The game reads `SBM3.UAS` and the `bgm\*.sgt` files in the first seconds, opens `SBM3.UAS` 57 more times between about 32 and 40 s, and once more at about 240 s. Meanwhile the draw rate rises and then stays high. These are the `hakuX-hle-emit` per-second lines, counted in seconds from the first frame:

| Time | Draws/s | Vertices/s |
| --- | --- | --- |
| 1-15 s | 110-640 | 440-2,500 |
| 17-42 s | 2,100-3,000 | 1.30-1.54 M |
| 43-300 s | mostly 4,000-4,850 (2,900 for a few seconds at 237-242 s; one-second peaks up to 16,600) | 1.54-1.66 M |

So from about 45 s the guest draws about 75 draws and 26,000 vertices a frame while the screen shows the loading animation.

```
hakuX-hle-emit: per s: draws=4252 verts=1564156 mergeable=0 (not: strip 1408 idx 2844 state 0 work 0 gap 0) ...
hakuX-hle-pb: kicks 733 words 1299523 headers 95939 methods 1203569 faults 0 ... surfaces 3 clears 9024 swaps 9022 draws 578668 ff 368537 skipped 0 () textures 153 (153 held, 18 MiB) ... | top 0:1800=780945 0:0b00=52560 0:1818=38000 0:0b80=23680 ...
hakuX-hle-fps: 60.0 fps (301 frames in 5.02 s)
hakuX-native-stats: per s: kcalls 3123 ... | MmLockUnlockBufferPages:1019 KeInsertQueueDpc:678 MmGetPhysicalAddress:568 ExQueryPoolBlockSize:199 KeSetTimer:121 KeSynchronizeExecution:114
```

The core logs no exception, no hang report and no push-buffer fault.

## Expected

Loading ends and the logos and title screen follow.

## Notes

- Seen in one run; there is no result from an earlier version.
