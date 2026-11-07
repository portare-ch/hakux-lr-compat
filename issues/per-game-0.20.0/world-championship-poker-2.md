## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `World Championship Poker 2 featuring Howard Lederer (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `43560010`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/world-championship-poker-2-featuring-howard-lederer-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

Sound starts at 4 s and the Crave logo movie (`DATA\CRAVE.xmv`) plays at 60 fps; it is on screen at 10 s. Right after the Start press at 10.5 s the game opens `DATA\POVLOGO.xmv`. It then loads the `MssgeBox`, `Progress`, `OnlMesag` and `Loading` `.sfp`/`.sfc` files. Right after `Loading.sfc` opens, about 13 s after launch, the guest reads address 0 at 0006f109, no handler takes the exception, and the core stops. RetroArch reports no content from 14.3 s; the rest of the run is black and silent.

```
hakuX-native-usb: gamepad 0: buttons 0000 -> 0010 (A 00)
hakuX-native-io: open \Device\CdRom0\DATA\POVLOGO.xmv -> 
...
hakuX-native-io: open \Device\CdRom0\DATA\OnlMesag.sfp -> 
hakuX-native-io: open \Device\CdRom0\DATA\OnlMesag.sfc -> 
hakuX-native-io: open \Device\CdRom0\DATA\Loading.sfp -> 
hakuX-native-io: open \Device\CdRom0\DATA\Loading.sfc -> 
hakuX-native: seh: t8 access violation at 0006f109, reading 00000000: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 0006f109 (no handler took it), reading 00000000
hakuX-native-frontier: summary stage=S2 kernel_calls=438330 first_call=PsCreateSystemThreadEx threads=12
```

## Expected

The remaining intro movies, then the title screen.

## Notes

- Seen in one run; there is no result from an earlier version. The run didn't test whether the crash also happens when the logo isn't skipped.
