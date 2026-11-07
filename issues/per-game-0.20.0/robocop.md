## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `RoboCop (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `54530005`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/robocop-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The MGM logo plays with sound from 7 s. The presses reach the Game Menu (New Game, 30 s), the briefing cutscene ("Good evening, Robocop...", 45 s) and the city overview (50 s); all render correctly.

While the menus and the briefing run, the title prints `FATAL error : [ Akoya Xbox ] Win32 Error 997!` and a `DbgBreakPoint` three times (at about 34, 38 and 42 s) and carries on. The first one follows four opens of the cached sound file `Partition5\flashN1.xau`.

At about 52 s the first level starts loading. The game creates `niveau01.xau` on the cache partition and opens it several times, then opens `PACKS\Robocop\Niveau1\NIV1_1.TPK`; meanwhile the picture stalls for 1.0 s. The title then prints a fatal error in `xsoundsystem.cpp`, breaks, and reads 0000000c; the core stops with an unhandled access violation at about 53 s. Black and silent from then on.

```
hakuX-native-io: open \Device\Harddisk0\Partition5\flashN1.xau -> 
hakuX-native-dbg: [ Akoya Xbox ] FATAL error :  [ Akoya Xbox ] Win32 Error 997! 
hakuX-native-dbg: DbgBreakPoint from 00095817
...
hakuX-native-io: open \Device\CdRom0\Audio\SfxFiles\Niveau01\niveau01.xau -> 
hakuX-native-io: open \Device\Harddisk0\Partition5\niveau01.xau -> (created)
hakuX-native-io: open \Device\CdRom0\PACKS\Robocop\Niveau1\NIV1_1.TPK -> 
hakuX-hle-hitch: HANG #1 frame 2311: 1029.5 ms (expected 16.7, reported live): guest idle: vCPU halted 90% | ...
hakuX-native-dbg: [ Akoya Xbox ] FATAL error on line 893 of D:\Projects\Akoya\AKOYAXBOX\Src\xsoundsystem.cpp! 
hakuX-native-dbg: DbgBreakPoint from 0009640a
hakuX-native: seh: t8 access violation at 0009644b, reading 0000000c: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 0009644b (no handler took it), reading 0000000c
hakuX-native-frontier: summary stage=S2 kernel_calls=146429 first_call=PsCreateSystemThreadEx threads=4
```

## Expected

The first level starts, with no fatal errors from the sound system.

## Notes

- Win32 error 997 is ERROR_IO_PENDING. The three breaks after it come from 00095817, 0009524d and 00095817.
- 24–58 new frames/s before the crash.
- Seen in the only run; no earlier results for this title.
