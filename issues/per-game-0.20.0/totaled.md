## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Totaled! (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4d4a0002`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/totaled-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Rage logo, Select Track and the loading screen run at 58-60 fps. After the relaunch into `default.xbe` the free-for-all derby starts at about 50 s and draws correctly, but slowly: 24.6, 22.4 and then 12.2 frames shown per second. The derby timer reads 3:30 at 54.8 s and 3:20 at 74.6 s. The run stopped at 79 s.

The hitch monitor calls the slow frames guest CPU-bound: the vCPU runs for nearly the whole frame (`vCPU cpu 124 ms halted -1%` in a 132 ms frame) and the renderer is mostly idle. During the derby the guest makes 65,000-129,000 MMIO accesses a second, against 6,000-9,000 in the menus.

```
hakuX-hle-disp: stats: 24.6 new frames/s, age front to taken 8.29 ms (max 43.38), gap 40.66 ms (max 150.01, 118 over 25 ms)
hakuX-hle-disp: stats: 22.4 new frames/s, age front to taken 8.28 ms (max 16.22), gap 44.71 ms (max 85.34, 185 over 25 ms)
hakuX-hle-disp: stats: 12.2 new frames/s, age front to taken 8.27 ms (max 26.63), gap 81.97 ms (max 151.13, 122 over 25 ms)
hakuX-hle-hitch: stutter #118 frame 1046: front 150.1 ms after the last (expected 116.8), 0 dropped: guest flipped 33 ms late (guest 132 ms: guest CPU-bound (557 draws)) | swap -2.9 write -2.9 ready -2.8 flip +150.1 front +150.1 shown +157.9 ms (vs the last front) | guest: vCPU cpu 124 ms halted -1% | render cpu 2 run 4 idle 127 compile 0 (0) submit 1 (38) gpu 0 display 0 | GPU 34363/34363, last done 52 ms ago | swaps 1 vblanks 8 draws 557 | ...
hakuX-native-stats: per s: kcalls 3563 sysops 5680 (int 876, of them ticks 219; hook 0) schedules 2265 switches 2238 idle 2 slices 1 page faults 0 mmio 129173 apu waits 0 vm pages +22 -17 ...
hakuX-native-stats: host faults per s: call-return 0 dirty pages 4011 (pages 03a8a000:320 03abd000:320 03aa2000:256 03a8d000:256 03ac0000:192 03ac3000:128) mmio 0 (eips) unaligned atomics 0
hakuX-hle-emit: per s: draws=7044 verts=1119122 mergeable=86 (not: strip 5328 idx 640 state 990 work 0 gap 0) ...
```

## Expected

The derby runs at the game's full frame rate.

## Notes

- 22 frames in the derby are flagged `guest CPU-bound`; the render thread is idle 112-127 ms of a 117-150 ms frame.
- The first stats line after the relaunch has a wrapped counter (`mmio 3376801978430567424`); TransWorld Snowboarding's log shows the same after its relaunch.
- Seen in the only run; no earlier results for this title.
