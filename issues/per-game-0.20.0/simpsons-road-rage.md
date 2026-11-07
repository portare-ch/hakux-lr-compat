## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Simpsons, The - Road Rage (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `45410013`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/simpsons-the-road-rage-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Fox Interactive logo plays (10 s screenshot), then the Radical Entertainment logo. At about 14 s two guest threads exit, and from about 15 s (frame 855) no new frame is drawn. The Radical logo stays on screen until Quit at 300 s; the B and Down presses the harness adds from 50 s change nothing. The guest swap count stays at 853 from the start of the hang to the stop.

During the hang the guest makes about 2,120 kernel calls a second, all background (`MmLockUnlockBufferPages` 1000, `KeInsertQueueDpc` 560, `MmGetPhysicalAddress` 500, `KeSetEvent` 60), so the busy thread doesn't call the kernel.

```
hakuX-native: ps: thread 36 exits (00000000)
hakuX-native: ps: thread 32 exits (00000000)
hakuX-hle-pb: scanout: the GPU wrote the frame on screen (4) and the title doesn't flip: shown again (first 4 logged)
hakuX-hle-hitch: HANG started 0.50 s since frame 855: JIT compiling: 99% of the vCPU in FEX | render idle for 500 ms | vCPU cpu 487 ms halted 0% | ...
hakuX-hle-hitch: HANG ongoing 94.55 s since frame 855: JIT compiling: 99% of the vCPU in FEX | render idle for 94555 ms | vCPU cpu 91764 ms halted 0% | ... | eip 083464e0(host JIT) 83146, 000c3870 62, 083464e0 45 of 83738, host: FEX 83466 kernel 272 | ...
hakuX-native-stats: per s: kcalls 2121 sysops 4109 (int 868, of them ticks 245; hook 0) ... | MmLockUnlockBufferPages:1000 KeInsertQueueDpc:560 MmGetPhysicalAddress:500 KeSetEvent:60
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=692314 first_call=PsCreateSystemThreadEx threads=6
hakuX-libretro: core: stopped
```

## Expected

The intro and the title screen.

## Notes

- Munch's Oddysee (#93), Project: Snowblind (#94) and Project Gotham Racing (#95) hang the same way: the guest is busy, nothing is drawn, and only the background kernel calls are made.
- The `hang vCPU` sample gives the XBE entry point (0009836f) with all general registers zero, so it doesn't locate the loop. The hang reports stop after 94.55 s, at a short pause and resume of the core; nothing is drawn after that either.
- After Quit the core stops, but the RetroArch process doesn't exit; the harness kills it at 310.6 s. The audio recording is empty, so the sound before the hang can't be judged.
- Seen in the only run; no earlier results for this title.

- Related (RetroArch doesn't exit after Quit): #144, #131, #127
