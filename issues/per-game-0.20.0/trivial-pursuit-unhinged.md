## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Trivial Pursuit - Unhinged (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4947003d`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/trivial-pursuit-unhinged-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

By the first screenshot at 10 s the game shows its animated error screen, "There's a problem with the disc you're using. It may be dirty or damaged.", and stays on it at 30 fps until Quit at 300 s. The run is silent, and no movie, logo or menu appears.

Before that, the game finds its intro movies in `DataXbox\English\Video` (`Blank`, `Atari`, `Artech`, `Horn`, `TP_Unhinged.xmv`) and copies them to `Partition5`. It then looks for the same movies in `DataXbox\Video`, which isn't on the disc. It goes on to copy its `.dpk`, font and sound files to `Partition5`. The last lookup before the error screen is `Data\HelpDisplay.txt`, also not on the disc. A listing of the image shows that file only inside language folders: `Data\English\HelpDisplay.txt` (2264 bytes), plus `English - UK`, `French`, `German`, `Italian` and `Spanish` copies. Both failed paths are the disc's paths without the language folder.

```
hakuX-native: ex: video flags 00400000, AV pack 0, AV region 00400100, language 1, time zone bias 0 min
...
hakuX-native-io: open \Device\CdRom0\DataXbox\English\Video\TP_Unhinged.xmv -> 
hakuX-native-io: open \Device\Harddisk0\Partition5\DataXbox\English\Video\TP_Unhinged.xmv -> (created)
...
hakuX-native-io: open \Device\CdRom0\DataXbox\Video: not on the disc
hakuX-ktrace: t8 NtOpenFile from 000681c2 [d007fb9c 00100001 d007fb78 d007fb70 00000003 00004021] -> c0000034 | frames 00066b05 0001e8e4
hakuX-native-io: open \Device\CdRom0\DataXbox\Video\Blank.xmv: not on the disc
hakuX-ktrace: t8 NtCreateFile from 00068fdf [d007fdc4 80100080 d007fda8 d007fdb4 00000000 00000080] -> c0000034 | frames 001fbac3 000cd67a 0001e8e4
... (the same for Atari, Artech, Horn, TP_Unhinged and Blank again)
hakuX-native-io: open \Device\CdRom0\Data\Common\Particles.dpk -> 
hakuX-native-io: open \Device\Harddisk0\Partition5\Data\Common\Particles.dpk -> (created)
...
hakuX-native-io: open \Device\CdRom0\dataXbox\common\font\arialuni.ttf -> 
hakuX-native-io: open \Device\CdRom0\Data\HelpDisplay.txt: not on the disc
hakuX-ktrace: t8 NtCreateFile from 00068fdf [d007f9c4 80100080 d007f9a8 d007f9b4 00000000 00000080] -> c0000034 | frames 000aa490
hakuX-hle-fps: 25.0 fps (126 frames in 5.03 s)
```

After `HelpDisplay.txt` the game opens no more files, and from then on the USB host controller reports 0 transfers per 10 s.

## Expected

The intro movies, then the title screen.

## Notes

- The language core option is `1 (auto)`; the new console EEPROM has language 1.
- Seen in one run; there is no result from an earlier version.
