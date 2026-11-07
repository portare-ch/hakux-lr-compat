## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Reign of Fire (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `424d0002`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/reign-of-fire-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The intro movie plays with sound from 10.5 s, and the presses reach the Basic Training mission screen (30 s), which renders correctly. From about 32 s the game loads the level: `DATA\LEVEL\TEST\HUM_1_0\HUM1_0.LVL`, the Norfolk map files, then `HUM1_0.BTF` and `HUM1_0.OBJ`. At about 35 s, right after `HUM1_0.OBJ`, the title writes to 00000000 and the core stops with an unhandled access violation. The screen is black and silent from then on; RetroArch reports no content from 35.7 s.

```
hakuX-native-io: open \Device\CdRom0\DATA\LEVEL\TEST\HUM_1_0\HUM1_0.LVL -> 
hakuX-native-io: open \Device\CdRom0\DATA\LEVEL\TEST\HUM_1_0\HUM1_0.BTF -> 
hakuX-native-io: open \Device\CdRom0\DATA\LEVEL\TEST\HUM_1_0\HUM1_0.OBJ -> 
hakuX-ktrace: t12 NtReleaseSemaphore from 000a4f99 [0000000c 00000001 00000000 00000000 00000000 00000000] -> c0000047 | frames 80010f08
[the same NtReleaseSemaphore line 79 more times]
hakuX-native: seh: t8 access violation at 000ab080, writing 00000000: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 000ab080 (no handler took it), writing 00000000
hakuX-native-frontier: summary stage=S2 kernel_calls=107239 first_call=PsCreateSystemThreadEx threads=6
```

## Expected

The Basic Training mission starts.

## Notes

- Thread t12's `NtReleaseSemaphore` on handle 0000000c returns c0000047 (STATUS_SEMAPHORE_LIMIT_EXCEEDED) about 290 times, in three bursts, each after the game opens map or level files: 23 at about 13 s, 186 at about 32 s and 80 right before the crash.
- 30–55 new frames/s before the crash (`hakuX-hle-disp` 55.3, 40.8 and 29.9).
- Seen in the only run; no earlier results for this title.
