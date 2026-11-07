## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Tony Hawk's American Wasteland (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `41560049`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/tony-hawk-s-american-wasteland-u-en-fr-de-es-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Activision logo shows at 10.8 s, at 29.5 fps. At about 15 s, while the game opens the zone packs under `data\Worlds\WorldZones\`, `default_sky.pak.xbx` and `cas_01.img.xbx`, the title reads from 7f93ca71 and the core stops with an unhandled access violation. RetroArch has no content for the rest of the run; every later screenshot is black.

```
hakuX-native-io: open \Device\CdRom0\data\Worlds\WorldZones\z_test_nn\z_test_nn.pak.Xbx -> 
hakuX-native-io: open \Device\CdRom0\data\Map: not on the disc
hakuX-ktrace: t8 NtOpenFile from 0025f77c [d0080438 00100001 d0080414 d008040c 00000003 00004021] -> c0000034 | frames 0025a9f1
hakuX-native-io: open \Device\CdRom0\data\skies\default_sky\default_sky.pak.xbx -> 
hakuX-native-io: open \Device\CdRom0\data\images\tags\cas_01.img.xbx -> 
hakuX-native: seh: t8 access violation at 00011985, reading 7f93ca71: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 00011985 (no handler took it), reading 7f93ca71
hakuX-native-frontier: summary stage=S2 kernel_calls=1573660 first_call=PsCreateSystemThreadEx threads=6
```

## Expected

The intro plays and the title screen shows.

## Notes

- Seen in the only run; no earlier results for this title.
- Tony Hawk's Pro Skater 2x, 3 and 4 are playable on 0.20.0, and Underground and Underground 2 on 0.19.1.
