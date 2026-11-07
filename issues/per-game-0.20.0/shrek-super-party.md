## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Shrek Super Party (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `544d0004`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/shrek-super-party-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The TDK Mediactive logo shows at 10 s, with sound from 3 s. At about 18 s a 12 KiB contiguous allocation from 000d7caf fails, although the core reports 10624 KiB free in one run at 00050000. Right after it the title writes to 00000000 and the core stops with an unhandled access violation; RetroArch reports no content from 19.4 s. Black and silent from then on.

```
hakuX-native: mm: contiguous allocation of 4 KiB at 02041000: 1 pages relocated (#4096)
hakuX-native: mm: contiguous allocation of 12 KiB failed (#1; from 000d7caf, 00000000-04000000, align 1000; free 10624 KiB: 50000+10624K | 1 runs, largest 10624 KiB)
hakuX-native-mm: contiguous allocation failed: contiguous by caller: 000d7caf 30556K/4071 000e1da6 2400K/1 000e1f72 2400K/1 000e1e95 1200K/1 000e27fd 512K/1 000f2173 344K/19 00121fea 8K/1 000e209d 4K/1
hakuX-native-mm: contiguous allocation failed: regions by committed (of 7): 01030000+800000:4948K 00c30000+400000:4068K 00010000+29d000:2656K(image) 004b0000+200000:2048K 002b0000+100000:1024K 003b0000+100000:1024K 006b0000+10000:4K
hakuX-native: seh: t8 access violation at 000ba334, writing 00000000: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 000ba334 (no handler took it), writing 00000000
hakuX-native-frontier: summary stage=S2 kernel_calls=56758 first_call=PsCreateSystemThreadEx threads=4
```

## Expected

The allocation succeeds, and the intro and title screen follow.

## Notes

- The `contiguous by caller` counts add up to 4,096 allocations (4071 from 000d7caf). SNK vs Capcom - SVC Chaos (both discs, 4094 + 1 + 1) and Wings of War (4077 + 18 + 1) fail at the same total, also with most of the free memory in one run at 00050000.
- 35 new frames/s before the crash.
- Seen in the only run; no earlier results for this title.

- Related (contiguous allocations fail with the game's live contiguous total at 4,096): #113, #161
