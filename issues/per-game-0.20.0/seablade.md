## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `SeaBlade (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `56550017`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/seablade-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The SeaBlade loading screen (10 s) and a hangar cutscene (50 s) render correctly. The front-end screens at 30 s, 45 s and 70 s show only an animated background: a blue frame, rotating rings, scrolling green figures and faint ship labels. No menu items or selection are drawn on them.

From about 11 s the guest swaps far more often than the display shows: 1,445–5,274 swaps a second for 12 s, then bursts of about 1,650–2,970 a second between stalls of about 5 s (at about 22, 28, 35, 43, 50, 58 and 65 s). 10–57 new frames a second reach the screen.

From about 70 s (frame 72599) nothing is drawn; the picture stays on a front-end background to the end. In the final hang report the vCPU got 18 s of CPU in 244 s. RetroArch doesn't respond to Quit at 300 s and is killed at the hard limit (315 s); the core logs no stop line, and the audio recording holds only the first 7.5 s.

```
hakuX-hle-fps: 58.4 fps (292 frames in 5.00 s)
hakuX-hle-fps: 3989.5 fps (20153 frames in 5.05 s)
hakuX-apu: dsp_dma_run: a guest value fails !"a known DMA format"; dropped
hakuX-apu: dsp_dma_run: a guest value fails !"a DMA transfer in DSP memory"; dropped
hakuX-hle-fps: 3718.6 fps (18593 frames in 5.00 s)
hakuX-hle-hitch: HANG #2 frame 43704: 5082.1 ms (expected 16.7, reported live): JIT compiling: 99% of the vCPU in FEX | vCPU cpu 4898 ms halted 0% | ...
hakuX-hle-fps: 667.0 fps (4427 frames in 6.64 s)
...
hakuX-hle-fps: 783.0 fps (5825 frames in 7.44 s)
hakuX-hle-hitch: HANG ongoing 243.63 s since frame 72599: vCPU starved: 18271 ms CPU of 243633 (host) | render idle for 243633 ms | vCPU cpu 18271 ms halted 0% | ... | eip 081464e0(host JIT) 16847, 081464e0 17, 080abbe0 15 of 220858, host: FEX 220743 kernel 115 | ...
hakuX-native-stats: per s: kcalls 2371 ... | MmLockUnlockBufferPages:1001 KeInsertQueueDpc:559 MmGetPhysicalAddress:500 KfLowerIrql:125 KeStallExecutionProcessor:118 KeSetEvent:60
```

## Expected

The front-end menus with their text and items, swapping at the display rate, and no hang.

## Notes

- Far Cry Instincts (#99) and Far Cry Instincts – Evolution (#100) also swap over 1,000 times a second.
- During the final hang the guest makes about 2,370 kernel calls a second, mostly background, plus 118–236 `KeStallExecutionProcessor`.
- The `hang vCPU` sample gives the XBE entry point (0007f7b3) with all general registers zero.
- Seen in the only run; no earlier results for this title.

- Related (RetroArch doesn't exit after Quit): #144, #123, #131
