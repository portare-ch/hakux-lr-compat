## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `XIII (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `55530009`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/xiii-u-en-fr-de-es-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The core stops about 4 s after launch, before any input is sent. RetroArch reports no content from 5.2 s; every screenshot is black and the recording is silent.

In those 4 s the game opens `System\common.lin`, `ubilogo480.raw`, `southend480.raw` and `splash480USA.raw` from the disc and copies `common.lin` to `Partition5`. It then throws three rounds of four C++ exceptions, all "Can't resolve package name". The game goes on after the first round (it opens `Sounds\fix.hxx` and `dsstdfx.bin`) and after the second (it opens `System\mapmenu.lin` and copies it to `Partition5`). The third round ends the run with "exceptions nested too deep". The first and third rounds come right after an `NtCreateFile` from 001da61b that returns c0000034 (not found) and has no `open` line, so the log doesn't name the file. The third object of each round holds the ASCII text `Failed to load 'NULL': Can't`.

```
hakuX-ktrace: t8 NtCreateFile from 001da61b [d012a24c 80100080 d012a230 d012a23c 00000000 00000000] -> c0000034 | frames 00018b65
hakuX-native: seh: t8 raises e06d7363 at 001dc840, C++ .PAD | frames 0025deb4 00049c7f 00060156 00040568
hakuX-native: seh:   thrown object d0127d9c: 004415d8 0005fc7a 004425e0 00000000 00000000 00000002 00a4e0a0 010bbb80 [0]"Can't resolve package name" [2]"Can't resolve package name"
hakuX-native: seh: t8 raises e06d7363 at 001dc840, C++ .PAD | frames 0025deb4 00049c7f 0006001f 00060156 00040568
hakuX-native: seh:   thrown object d0126838: 004415d8 00051d46 00377a94 004415d8 d0127fcc 00380360 0005ffd5 d012688c [0]"Can't resolve package name" [3]"Can't resolve package name" [5]"NULL"
hakuX-native: seh: t8 raises e06d7363 at 001dc840, C++ .PAD | frames 0025deb4 00051d9f 0006001f 00060156 00040568
hakuX-native: seh:   thrown object d0126858: 004415d8 6c696146 74206465 6f6c206f 27206461 4c4c554e 43203a27 74276e61 [0]"Can't resolve package name"
...
hakuX-native-io: open \Device\CdRom0\System\mapmenu.lin -> 
hakuX-native-io: open \Device\Harddisk0\Partition5\System\mapmenu.lin -> (created)
hakuX-ktrace: t8 NtCreateFile from 001da61b [d012a004 80100080 d0129fe8 d0129ff4 00000000 00000000] -> c0000034 | frames 00018b65
...
hakuX-native: seh: t8 raises e06d7363 at 001dc840, C++ .PAD | frames 0025deb4 00060045 00060156 00040568
hakuX-native: seh:   thrown object d0126914: 004415d8 00000000 d0126a88 0005c336 d0127470 d0127898 00000001 00000000 [0]"Can't resolve package name"
hakuX-native-frontier: stop: seh: exceptions nested too deep
hakuX-native-frontier: summary stage=S2 kernel_calls=30794 first_call=PsCreateSystemThreadEx threads=7
```

## Expected

The Ubisoft logo, the intro and the title screen.

## Notes

- 12 throws in all, all from 001dc840 on thread t8. Seen in one run; there is no result from an earlier version.
