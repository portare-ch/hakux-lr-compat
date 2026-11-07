## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Tom Clancy's Rainbow Six - Critical Hour (U) (En,Fr).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `5553005f`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/tom-clancy-s-rainbow-six-critical-hour-u-en-fr/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The ESRB "Mature 17+" notice shows at 29.5 fps and freezes after frame 352, about 12 s after launch. Every screenshot up to 290 s shows the same notice. Sound keeps playing at a steady -31 to -38 dBFS RMS for the whole run.

Before the freeze the game copies HUD textures to `Partition5\cache`, takes 32 write faults at rising addresses from 00990000 to 009e6000 (all passed to its own handlers), starts thread 48 and creates `partition1\CACHE\LocalCache00.bin`. Then the hang monitor reports no new frame for the rest of the run (287.7 s). The vCPU is busy (halted 27%); the guest makes about 105,000 `NtWaitForSingleObjectEx` calls a second.

```
hakuX-native: seh: t8 access violation at 0024d103, writing 00990000: to the title's handlers
...
hakuX-native: seh: t8 access violation at 0024d103, writing 009e6000: to the title's handlers
hakuX-native: ps: thread 48 created: start 004f0a5e (via system routine), stack d00c0000-d00d1000, tls 148
hakuX-native-io: open \Device\Harddisk0\partition1\CACHE\LocalCache00.bin -> (created)
hakuX-native: ex: load section dspimage 0077a540+48b0 (refs 2)
hakuX-native: ex: unload section dspimage (refs 1)
hakuX-hle-hitch: HANG started 0.50 s since frame 352: JIT compiling: 67% of the vCPU in FEX | render idle for 501 ms | vCPU cpu 381 ms halted 22% | ...
hakuX-hle-hitch: HANG ongoing 287.67 s since frame 352: JIT compiling: 61% of the vCPU in FEX | render idle for 287674 ms | vCPU cpu 213602 ms halted 27% | render cpu 0 run 0 idle 287674 compile 0 (0) submit 0 (1) gpu 0 display 0 | GPU 365/365, last done 287673 ms ago | swaps 0 vblanks 17260 draws 0 | ... | eip 081464e0(host JIT) 154948, 00094ce0 920, 080b4610 756 of 254269, host: FEX 156914 kernel 28516 | ...
hakuX-native-stats: per s: kcalls 108393 sysops 110616 (int 799, of them ticks 0; hook 0) schedules 2681 switches 2567 idle 0 slices 0 ... | NtWaitForSingleObjectEx:105081 MmLockUnlockBufferPages:1399 MmGetPhysicalAddress:749 KeInsertQueueDpc:610 KeDelayExecutionThread:290 KeSetTimer:104
```

## Expected

The notice ends and the intro and the main menu show.

## Notes

- Tom Clancy's Rainbow Six: Lockdown takes a similar burst of 32 write faults (00960000 to 009be000) after copying files to `Partition5\cache` during its intro, and RetroArch then dies with SIGSEGV inside the core (separate issue).
- TransWorld Snowboarding freezes the same way on its main menu: no new frame, vCPU about 25% halted with 62% in FEX, about 110,000 `NtWaitForMultipleObjectsEx` calls a second, music still playing.
- Seen in the only run; no earlier results for this title.

- Related (freezes with ~100k wait calls a second, sound still playing): #151, #148
