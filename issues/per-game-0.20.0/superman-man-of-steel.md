## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Superman - The Man of Steel (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `49470016`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, then from 42 s only A every 4 s, so that Start doesn't pause play ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/superman-the-man-of-steel-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Atari logo, the Fortress cutscene and the mission loading screen run at a steady 30 fps. From about 50 s Superman is in play on a Metropolis rooftop and draws correctly, but at 14.8-20.6 frames shown per second (guest presents 12.7-17.4 per second) until the stop at 80 s.

In play the guest's GPU interrupts rise from 90 a second (menus) to 1,500-3,100 a second, and the push-buffer decoder waits 30-52 ms of a frame on the guest's GPU interrupt handler. Each frame has about 4,900 draws.

```
hakuX-hle-disp: stats: 20.6 new frames/s, age front to taken 8.34 ms (max 31.21), gap 48.63 ms (max 252.64, 206 over 25 ms)
hakuX-hle-disp: stats: 14.8 new frames/s, age front to taken 7.33 ms (max 16.36), gap 67.34 ms (max 116.86, 149 over 25 ms)
hakuX-hle-disp: stats: 17.2 new frames/s, age front to taken 8.52 ms (max 40.01), gap 58.23 ms (max 87.32, 172 over 25 ms)
hakuX-hle-hitch: stutter #27 frame 1388: front 113.9 ms after the last (expected 66.7), 0 dropped: guest flipped 47 ms late (guest 97 ms: decoder waited 51 ms on the guest's GPU interrupt handle | swap +0.7 write +1.0 ready +1.1 flip +113.9 front +113.9 shown +124.7 ms (vs the last front) | guest: vCPU cpu 51 ms halted -1% | render cpu 5 run 4 idle 93 compile 0 (0) submit 0 (10) gpu 0 display 0 | GPU 2265/2265, last done 1 ms ago | swaps 1 vblanks 6 draws 4926 | ... | decoder cpu 17 idle 18 flip 0 trap 51 ring 0 arena 0 gpu 0
hakuX-native-stats: per s: kcalls 5174 sysops 14289 (int 2992, of them ticks 25; hook 0) schedules 9071 switches 6592 idle 1307 slices 0 page faults 0 mmio 94302 apu waits 0 vm pages +0 -0 isr irq1:506 (max 1.3 ms) irq3:2512 (max 1.5 ms) irq5:30 (max 0.6 ms) | dpc max wait 3.4 run 4.2 ms, 0 over 8 ms | holds 252 (longest 1.6 ms), 0.0 ms left out | KeInsertQueueDpc:3039 MmLockUnlockBufferPages:1174 MmGetPhysicalAddress:630 KeSetEvent:119 KeWaitForSingleObject:59 KeDelayExecutionThread:56
hakuX-hle-emit: per s: draws=83738 verts=8057080 mergeable=0 (not: strip 42615 idx 41123 state 0 work 0 gap 0) ...
```

## Expected

Play at the game's normal frame rate (the menus and cutscenes hold 30 fps).

## Notes

- The first run, without the override, is the same: 13.8-19.9 frames shown per second in play, 14 `decoder waited` stutters.
- No earlier results for this title.
