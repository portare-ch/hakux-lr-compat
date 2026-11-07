## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Shin Sangoku Musou 3 (Japan, Asia).chd`, NTSC-J, CHD (`chdman createdvd` from an XISO); XBE title ID `4b4f0004`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s; an override in [overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json) replaces them from 50 to 58 s with B, Down ×4 and A, which picks 戦闘開始 (start battle) on the battle preparation menu. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/shin-sangoku-musou-3-japan-asia/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Omega Force logo, the story overview, the stage select and the battle preparation screen (戦闘準備, 50 s) render correctly at about 60 fps, with sound. The override's A at 55.3 s starts the battle: the game starts thread 28 and, within about 2 s, opens 186 cache files (`Partition5\DATAnnnn`), 153 of them new. At about 57 s thread 28 exits, and right after it thread 8 reads d0083028; the core stops with an unhandled access violation. RetroArch reports no content from 58.1 s; black and silent from then on.

```
hakuX-native: ps: thread 28 created: start 000d9340 (via system routine), stack d0100000-d0111000, tls 148
hakuX-native-io: open \Device\Harddisk0\Partition5\DATA0608 -> (created)
[184 more opens of Partition5\DATAnnnn]
hakuX-native-io: open \Device\Harddisk0\Partition5\DATA0531 -> (created)
hakuX-native: ps: thread 28 exits (00000000)
hakuX-native: seh: t8 access violation at 00174091, reading d0083028: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 00174091 (no handler took it), reading d0083028
hakuX-native-frontier: summary stage=S2 kernel_calls=157679 first_call=PsCreateSystemThreadEx threads=5
```

## Expected

The first battle loads.

## Notes

- d0083028 is 0x2028 bytes above the end of thread 8's stack as logged at its creation: `ps: thread 8 created: start 001b7210 (via system routine), stack d0070000-d0081000, tls 148`.
- The first run, without the override, sat on the weapon info page (武器情報) for the whole 5 min with no crash.
- The core reports 2776 KiB of RAM free in the last stats before the crash.
- Seen in the only run that started a battle; no earlier results for this title.
