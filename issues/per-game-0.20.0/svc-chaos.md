## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Images:** `SNK vs Capcom - SVC Chaos (USA).chd` (NTSC-U) and `SNK vs Capcom - SVC Chaos (Europe) (En,Fr,De,Es,It).chd` (PAL), CHD (`chdman createdvd` from an XISO); XBE title ID `534e0001` on both
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Results:** [USA result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/snk-vs-capcom-svc-chaos-usa/result.json), [Europe result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/snk-vs-capcom-svc-chaos-europe-en-fr-de-es-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

**USA disc:** at about 3 s, calls to `MmAllocateContiguousMemoryEx` from 00158858 (0x555 bytes, alignment 0x80) start to fail, although the core reports 10424 KiB free in one run at 00050000. Each failing call holds the CPU for about 9 ms, and the log counts at least 256 failures. The game then opens `data\SKILL.DAT`, `US_SKILL.DAT`, `BASE\FIRST.GRC` and `SK_PVX.DAT`, and at 4.9 s RetroArch exits by itself with code 0. The core logs no stop line, no exception and no shutdown; RetroArch's own log ends after loading the content. Nothing was captured (the first screenshot is due at 10 s) and the recording is empty.

**Europe disc:** the same, later. The Ignition Entertainment logo plays with sound (10 s screenshot, correct). At about 14 s the same allocations, from 0015ab79, fail with 9996 KiB free in one run; the game opens the same four files, and RetroArch exits by itself at 15.2 s with code 0.

USA disc, the end of the core log:

```
hakuX-native: mm: contiguous allocation of 4 KiB failed (#1; from 00158858, 00000000-04000000, align 80; free 10424 KiB: 50000+10424K | 1 runs, largest 10424 KiB)
hakuX-native-mm: contiguous allocation failed: contiguous by caller: 00158858 22028K/4094 00200096 20K/1 00245a07 12K/1
hakuX-native-mm: contiguous allocation failed: regions by committed (of 2): 00010000+1f62000:32052K(image) 01f80000+100000:336K
hakuX-native-slow: MmAllocateContiguousMemoryEx from 00158858 held the CPU 9.0 ms [00000555 00000000 ffffffff 00000080 00000404 00000000]
...
hakuX-native: mm: contiguous allocation of 4 KiB failed (#256; from 00158858, 00000000-04000000, align 80; free 9404 KiB: 50000+9404K | 1 runs, largest 9404 KiB)
hakuX-native-slow: MmAllocateContiguousMemoryEx from 00158858 held the CPU 9.1 ms [00000555 00000000 ffffffff 00000080 00000404 00000000]
hakuX-native-io: open \Device\CdRom0\data\SKILL.DAT -> 
hakuX-native-io: open \Device\CdRom0\data\US_SKILL.DAT -> 
hakuX-native-io: open \Device\CdRom0\data\BASE\FIRST.GRC -> 
hakuX-native-io: open \Device\CdRom0\data\SK_PVX.DAT -> 
```

Europe disc:

```
hakuX-native-mm: contiguous allocation failed: contiguous by caller: 0015ab79 21364K/4094 00202436 20K/1 00270107 12K/1
```

## Expected

The intro and the title screen.

## Notes

- On both discs the `contiguous by caller` counts add up to 4,096 allocations (4094 + 1 + 1) when the first request fails. Shrek Super Party (4071 + 1 + 1 + 1 + 1 + 19 + 1 + 1) and Wings of War (4077 + 18 + 1) also fail at a total of 4,096, with 10,624 and 24,504 KiB free in one run.
- RetroArch exits with code 0 and no message from the core; SX Superstar ends the same way after a guest fault.
- Seen in the only run of each disc; no earlier results for this title.

- Related (contiguous allocations fail with the game's live contiguous total at 4,096): #118, #161
