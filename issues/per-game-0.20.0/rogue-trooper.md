## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Rogue Trooper (U) (En,Fr,De,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `5343000e`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/rogue-trooper-u-en-fr-de-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Rebellion logo plays with sound from 3.5 s. At about 12 s the game shows its legal screen with "Loading..." (`Graphics\frontend\legal.dds`, `Envs\Menu_Lab.xbx`), and from about 13 s (frame 318) no new frame is drawn. The legal screen stays until Quit at 300 s, silent from about 14 s. The B and Down presses the harness adds from 53 s change nothing.

During the hang the guest calls `NtWriteFile` 105,000–109,000 times a second, and the stats count no timer ticks (243–269 a second before the hang):

```
hakuX-native-io: open \Device\CdRom0\Graphics\frontend\legal.dds -> 
hakuX-native-io: open \Device\CdRom0\Envs\Menu_Lab.xbx -> 
hakuX-native-io: open \Device\CdRom0\Graphics\frontend\legal.dds -> 
hakuX-hle-hitch: HANG started 0.50 s since frame 318: JIT compiling: 54% of the vCPU in FEX | render idle for 501 ms | vCPU cpu 500 ms halted 0% | ...
hakuX-native-stats: per s: kcalls 111359 sysops 113120 (int 636, of them ticks 0; hook 0) schedules 1690 switches 1690 idle 0 ... | NtWriteFile:109232 MmLockUnlockBufferPages:1000 KeInsertQueueDpc:560 MmGetPhysicalAddress:500 KeSetEvent:60 KeSetTimer:8
hakuX-hle-hitch: HANG ongoing 235.63 s since frame 318: JIT compiling: 51% of the vCPU in FEX | render idle for 235633 ms | vCPU cpu 234618 ms halted 0% | ... | eip 081464e0(host JIT) 105981, 080b6130 75570, 000c8630 693 of 209552, host: FEX 107306 kernel 102245 | ...
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=31645674 first_call=PsCreateSystemThreadEx threads=3
```

## Expected

The front-end menu.

## Notes

- Sniper Elite, also by Rebellion, hangs the same way on its copyright screen, right after opening its front-end environment (`environments\frontend.xbx`): about 108,000 `NtWriteFile` calls a second and no timer ticks. No other title in the 0.20.0 run logs `NtWriteFile` at this rate.
- The `hang vCPU` sample gives the XBE entry point (0021f63c) with all general registers zero, so it doesn't locate the loop (as in #93).
- Seen in the only run; no earlier results for this title.

- Related (about 108,000 NtWriteFile calls a second (both Rebellion)): #124
