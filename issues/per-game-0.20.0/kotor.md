## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Images:** `Star Wars - Knights of the Old Republic (U).chd` and `Star Wars - Knights of the Old Republic (U) (Rev 1).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4c410003` in both
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s; from 232 s only A every 6 s until 250 s, for Trask's dialogue later in the run ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Results:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/star-wars-knights-of-the-old-republic-u/result.json) and [Rev 1 result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/star-wars-knights-of-the-old-republic-u-rev-1/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

Both discs behave the same. The menus before the movie run at 57-59 fps. At about 35 s the game opens `movies\01A.xmv`: the opening crawl and the intro cutscene over Taris, shown through the video overlay (0 draws a second; the overlay counter rises with each displayed frame). The movie starts at 30 fps, then the displayed rate drops in steps. The music plays on without gaps.

| Time | Displayed fps (`hakuX-hle-fps`, 5 s windows) |
| --- | --- |
| 35-75 s | 29.7-30.0 |
| 80-105 s | 15.0 |
| 110-145 s | 9.8-10.0 (Rev 1: 7.6-10.0) |
| 150-155 s | 7.5-8.8 |
| from 158 s (the Endar Spire bunk room, drawn by the game) | 51-58 |

During the slow part the hitch reports say "vCPU starved". The vCPU thread gets only 15-21 ms of CPU per 90-134 ms frame, and the render thread is idle. The kernel call rate is the same at 30 fps and at 10 fps (about 8,800 a second: `MmLockUnlockBufferPages` 4,780, `MmGetPhysicalAddress` 2,400, `KeDelayExecutionThread` 720).

```
hakuX-native-io: open \Device\CdRom0\movies\01A.xmv -> 
...
hakuX-hle-fps: 15.0 fps (75 frames in 5.00 s)
...
hakuX-hle-hitch: stutter #84 frame 2979: front 100.6 ms after the last (expected 66.7), 0 dropped: guest 101 ms: vCPU starved: 16 ms CPU of 101 (host) | ... | guest: vCPU cpu 16 ms halted -1% | render cpu 0 run 0 idle 101 compile 0 (0) submit 0 (1) gpu 0 display 0 | GPU 4495/4495, last done 101 ms ago | swaps 1 vblanks 6 draws 0 | dvd 0 ops 0.0 MB 0 ms | ...
hakuX-hle-pb: kicks 70 words 0 headers 0 methods 0 faults 0 ... swaps 1139 draws 101920 ... overlays 2041 ...
hakuX-native-stats: per s: kcalls 8788 sysops 11658 (int 1262, of them ticks 1; hook 0) schedules 3169 switches 2391 idle 1442 ... mmio 7710 ... | MmLockUnlockBufferPages:4759 MmGetPhysicalAddress:2391 KeInsertQueueDpc:804 KeDelayExecutionThread:718 KeSetEvent:60 NtWaitForSingleObjectEx:30
hakuX-hle-fps: 10.0 fps (50 frames in 5.02 s)
...
hakuX-hle-fps: 7.5 fps (38 frames in 5.07 s)
```

## Expected

The crawl and the intro cutscene play at their full rate.

## Notes

- The rate steps through 30, 15, 10 and 7.5 fps: 2, 4, 6 and 8 vblanks a frame.
- The Rev 1 run logged 213 "vCPU starved" reports, the original 16.
