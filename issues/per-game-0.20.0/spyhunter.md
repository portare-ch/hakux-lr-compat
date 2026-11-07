## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `SpyHunter (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4d570004`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/spyhunter-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The logos and the Mission Data screen run at 60 fps. Once the mission starts (about 42 s; the car on the start line with the HUD, mission timer 7:57 to 7:45, with sound), the rate drops to 13-23 fps and stays there until the run stops at 77 s. Everything renders correctly.

In the mission the game makes about 29,000 draws a frame (24 hitch reports: median 29,209, up to 37,656), nearly all small non-indexed strips of about 4.6 vertices, so 300,000-675,000 draws a second. The push buffer carries about 7 million words a second in 3,600-6,700 kicks. The hitch reports name "guest CPU-bound (29xxx draws)" or "vCPU starved". The vCPU thread gets 60-65 ms of CPU in a 100-110 ms frame, and the render thread is idle about 95 of those ms.

```
hakuX-hle-hitch: stutter #99 frame 2151: front 100.3 ms after the last (expected 83.4), 0 dropped: guest 114 ms: guest CPU-bound (29351 draws) | ... | guest: vCPU cpu 64 ms halted -1% | render cpu 17 run 15 idle 99 compile 0 (0) submit 0 (15) gpu 0 display 0 | GPU 3724/3724, last done 4 ms ago | swaps 1 vblanks 7 draws 29351 | ...
hakuX-hle-hitch: stutter #85 frame 2040: front 66.1 ms after the last (expected 50.0), 0 dropped: guest 74 ms: vCPU starved: 30 ms CPU of 74 (host) | ... | guest: vCPU cpu 30 ms halted -1% | render cpu 15 run 15 idle 58 ... | swaps 1 vblanks 4 draws 28558 | ...
hakuX-hle-pb: kicks 7099 words 7244782 headers 2301903 methods 4942824 faults 0 ...
hakuX-hle-emit: per s: draws=428024 verts=1983776 mergeable=0 (not: strip 427068 idx 74 state 885 work 0 gap 0) batches=4082 of 61319 draws indexed: ...
hakuX-hle-fps: 12.7 fps (64 frames in 5.03 s)
```

## Expected

The mission runs at the game's full rate.

## Notes

- SpyHunter 2 (`4d57001b`) and SpyHunter - Nowhere to Run (`4d570037`) run at 49-60 fps and 30 fps in this run.
- Seen in one run; there is no result from an earlier version.
