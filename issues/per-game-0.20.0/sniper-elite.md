## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Sniper Elite (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4d49000d`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/sniper-elite-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The copyright screen ("Sniper Elite contents and technology ©Rebellion 2005...", `Graphics\splash\legal.dds`) appears at about 1 s. The game opens `environments\frontend.xbx` at about 2 s, and from then on (frame 31) no new frame is drawn, before the first input at 10.5 s. The copyright screen stays until Quit at 300 s; the run is silent throughout, and the B and Down presses the harness adds from 53 s change nothing.

During the hang the guest calls `NtWriteFile` 105,000–109,000 times a second, and the stats count no timer ticks:

```
hakuX-native-io: open \Device\CdRom0\Graphics\splash\legal.dds -> 
hakuX-native-io: open \Device\CdRom0\environments\frontend.xbx -> 
hakuX-hle-hitch: HANG started 0.50 s since frame 31: guest idle: vCPU halted 87% | render idle for 501 ms | vCPU cpu 70 ms halted 87% | ...
hakuX-native-stats: per s: kcalls 111172 sysops 112915 (int 622, of them ticks 0; hook 0) schedules 1670 switches 1651 idle 0 ... | NtWriteFile:109052 MmLockUnlockBufferPages:1000 KeInsertQueueDpc:560 MmGetPhysicalAddress:500 KeSetEvent:60
hakuX-hle-hitch: HANG ongoing 206.63 s since frame 31: JIT compiling: 52% of the vCPU in FEX | render idle for 206629 ms | vCPU cpu 205485 ms halted 0% | ... | eip 083464e0(host JIT) 95238, 082b6130 65053, 00095810 630 of 183665, host: FEX 96306 kernel 86991 | ...
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=32662827 first_call=PsCreateSystemThreadEx threads=4
```

## Expected

The intro and the title screen.

## Notes

- Rogue Trooper, also by Rebellion, hangs the same way on its "Loading..." legal screen, right after opening `Envs\Menu_Lab.xbx`: about 108,000 `NtWriteFile` calls a second and no timer ticks. No other title in the 0.20.0 run logs `NtWriteFile` at this rate.
- The `hang vCPU` sample gives the XBE entry point (00181521) with all general registers zero, so it doesn't locate the loop (as in #93).
- Seen in the only run; no earlier results for this title.

- Related (about 108,000 NtWriteFile calls a second (both Rebellion)): #115
