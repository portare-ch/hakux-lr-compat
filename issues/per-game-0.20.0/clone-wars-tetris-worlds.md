## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Star Wars - The Clone Wars + Tetris Worlds (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `584c000d`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/star-wars-the-clone-wars-tetris-worlds-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

Nothing is drawn and nothing is heard. Within the first second the disc's launcher (title 584c000d) links `B:` to the disc, opens `cdxmedia\cdx.inx`, links `Y:` to `Partition2` and relaunches into `\Device\CdRom0\dashupdate.xbe`. The core boots dashupdate.xbe in the same process. Its opens of `\??\B:\Media\Content\...` fail with "no such drive", it finds no `*.xtf` font on `Partition2`, tries `\??\HGGothicM.xtf`, and then reads 00000008; the core stops with an unhandled access violation. RetroArch reports no content for the rest of the run.

```
hakuX-native-io: link \??\B: -> \Device\CdRom0
hakuX-native-io: open \Device\CdRom0\cdxmedia\cdx.inx -> 
hakuX-ktrace: t8 IoDeleteSymbolicLink from 0001e128 [0012b8a0 00000000 00000000 00000000 00000000 00000000] -> c0000034 | frames 0001ec58 80010f08
hakuX-native-io: link \??\Y: -> \Device\Harddisk0\Partition2
hakuX-native-frontier: stop: relaunch into \Device\CdRom0\dashupdate.xbe (launch type 4294967295)
hakuX-native-frontier: relaunch: \Device\CdRom0\dashupdate.xbe (launch type 4294967295)
hakuX-native-frontier: stage S0 xbe loaded: title 584c000d base 00010000 image 53636 KiB (520 KiB in memory), 8/25 sections, entry 00018505, 103 kernel imports, tls 000134e8
hakuX-native-io: open \??\B:\Media\Content\Country\: no such drive
hakuX-native-io: open \??\B:\Media\Content\English\: no such drive
hakuX-native-io: list \Device\Harddisk0\Partition2 mask '*.xtf': nothing matches (0 entries)
hakuX-native-io: open \??\HGGothicM.xtf: unknown device (a missing name)
hakuX-native: seh: t8 access violation at 0002f1cd, reading 00000008: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 0002f1cd (no handler took it), reading 00000008
hakuX-native-frontier: summary stage=S2 kernel_calls=539 first_call=PsCreateSystemThreadEx threads=4
```

## Expected

The disc's menu to pick Star Wars: The Clone Wars or Tetris Worlds.

## Notes

- The two games on their own discs, Star Wars - The Clone Wars (U) and Tetris Worlds (U), reach gameplay in this run (Playable) and never open dashupdate.xbe. This is the only title in the run that relaunches into dashupdate.xbe.
- The test console disk has no Xbox dashboard installed.
- Seen in the only run; no earlier results for this title.
