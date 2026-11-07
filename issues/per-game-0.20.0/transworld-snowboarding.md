## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `TransWorld Snowboarding (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `49470004`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/transworld-snowboarding-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Atari logo plays, and at about 10 s the game relaunches into `UPP_Structure.xbe` (the core stops and boots it in 28 ms). The main menu draws at about 59 frames per second, then freezes after frame 91, about 20 s after launch. Every screenshot from 32.6 s to 292.7 s shows the same main menu (TRANSWORLD TOUR highlighted). The menu music keeps playing, -26 to -31 dBFS RMS, to the end of the run.

During the freeze the vCPU is busy (halted 24%) and the guest makes about 110,000 `NtWaitForMultipleObjectsEx` calls a second; nothing is drawn.

```
hakuX-native-frontier: stop: relaunch into \Device\CdRom0\UPP_Structure.xbe (launch type 4294967295)
hakuX-libretro: relaunch: the core stopped in 28 ms
hakuX-native-frontier: relaunch: \Device\CdRom0\UPP_Structure.xbe (launch type 4294967295)
...
hakuX-hle-hitch: stutter #9 frame 91: front 100.0 ms after the last (expected 16.7), 0 dropped: guest 115 ms: JIT compiling: 62% of the vCPU in FEX | ...
hakuX-hle-hitch: HANG started 0.50 s since frame 91: JIT compiling: 62% of the vCPU in FEX | render idle for 500 ms | vCPU cpu 389 ms halted 27% | ...
hakuX-hle-hitch: HANG ongoing 206.62 s since frame 91: JIT compiling: 62% of the vCPU in FEX | render idle for 206624 ms | vCPU cpu 155991 ms halted 24% | render cpu 0 run 0 idle 206624 compile 0 (0) submit 0 (1) gpu 0 display 0 | GPU 97/97, last done 206624 ms ago | swaps 0 vblanks 12397 draws 0 | ... | eip 083464e0(host JIT) 111245, 083464e0 811, 082b4610 768 of 180188, host: FEX 113148 kernel 23886 | ...
hakuX-native-stats: per s: kcalls 114147 sysops 116307 (int 1031, of them ticks 1; hook 0) schedules 3294 switches 2797 idle 0 slices 0 ... | NtWaitForMultipleObjectsEx:111365 MmLockUnlockBufferPages:1041 KeInsertQueueDpc:562 NtWaitForSingleObjectEx:554 MmGetPhysicalAddress:538 KeSetEvent:60
```

The last `HANG ongoing` line is at 206.62 s; the stats lines show the same pattern up to the stop at 303 s.

## Expected

The main menu stays live and answers the pad.

## Notes

- Tom Clancy's Rainbow Six: Critical Hour freezes the same way on its ESRB notice: no new frame, vCPU about 25% halted with 61% in FEX, about 105,000 `NtWaitForSingleObjectEx` calls a second, sound still playing.
- The first stats line after the relaunch has wrapped counters: `int 96, of them ticks 3113246888289482752 ... mmio 3113246888289473024`.
- Seen in the only run; no earlier results for this title.

- Related (freezes with ~100k wait calls a second, sound still playing): #150, #148
