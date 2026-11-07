## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Sneakers (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4d530023`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/sneakers-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The intro (`Stream\microsoft.wmv`, then the in-engine intro), the Loading screen and the first level (the rat chase, from about 50 s) render correctly. Between about 10 s and 55 s the picture freezes six times for 1.9-4.6 s. Each hang report names JIT compiling, with the vCPU 80-99% in FEX and the render thread idle. The last one comes as the level starts. After it the level runs steadily at 30-31 fps, which matches the game's own 33.4 ms frame interval, until the run stops at 80 s. The displayed rate over 10 s windows swings between 7.4 and 31 fps because of the freezes.

```
hakuX-hle-hitch: HANG #1 frame 166: 2398.5 ms (expected 33.4, reported live): JIT compiling: 80% of the vCPU in FEX | vCPU cpu 1836 ms halted 18% | render cpu 0 run 0 idle 2398 ... | swaps 1 vblanks 143 draws 1 | ...
hakuX-hle-hitch: HANG #2 frame 185: 2386.7 ms (expected 33.4, reported live): JIT compiling: 98% of the vCPU in FEX | vCPU cpu 2288 ms halted 0% | ...
hakuX-hle-hitch: HANG #3 frame 449: 1856.8 ms (expected 33.4, reported live): JIT compiling: 98% of the vCPU in FEX | vCPU cpu 1776 ms halted 0% | ...
hakuX-hle-hitch: HANG #4 frame 540: 4574.2 ms (expected 33.4, reported live): JIT compiling: 99% of the vCPU in FEX | vCPU cpu 4394 ms halted 0% | ...
hakuX-hle-hitch: HANG #5 frame 702: 2392.6 ms (expected 66.7, reported live): JIT compiling: 99% of the vCPU in FEX | vCPU cpu 2289 ms halted 0% | ...
hakuX-hle-hitch: HANG #6 frame 978: 2516.7 ms (expected 33.4, reported live): JIT compiling: 99% of the vCPU in FEX | vCPU cpu 2424 ms halted 0% | ...
```

Quit doesn't end the process. The core logs its stop, then nothing after `push-buffer mode off`: no pipeline-cache save and no context teardown, unlike a normal quit. The harness kills the process at 90 s.

```
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=196727 first_call=PsCreateSystemThreadEx threads=3
hakuX-libretro: core: stopped
hakuX-native: nv2a: push-buffer mode off
hakuX-native-usb: ohci: 6571 TDs in 10 s, ctl 000000be (lists PCB), hcca 03fe9000, intr 00000006/80000073
```

## Expected

No multi-second freezes, and Quit ends the process.

## Notes

- The audio recording is empty (0 s), so sound can't be judged. At boot the APU logs two dropped DSP DMA transfers: `dsp_dma_run: a guest value fails !"a known DMA format"; dropped` and `... !"a DMA transfer in DSP memory"; dropped`.
- Seen in one run; there is no result from an earlier version.

- Related (RetroArch doesn't exit after Quit): #144, #123, #127
