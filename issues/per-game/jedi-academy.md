## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, the release's default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Star Wars - Jedi Knight - Jedi Academy (U) (En,Fr,De).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4c41000b`
- **Run:** a fresh RetroArch with an empty profile and a new console disk. Start and A are pressed in turn every 2.5 s from 10.5 s to 33 s; screenshots are taken at 10, 22 and 45 s; Quit is sent at about 46 s. `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1` are set.

Found in a scripted 45 s first pass over 77 titles. Seen once, not yet retried, and not tried on ARM64.

## What happens

The LucasArts logo and the menus work. After the Difficulty menu (Jedi highlighted), the game opens its first movie. About 26 s after launch hakuX runs out of guest physical memory, an access violation follows, and the core stops. RetroArch returns to its menu.

```
hakuX-native-io: open \Device\CdRom0\base\video\ja01_e.bik -> 
hakuX-native: vm: out of physical memory for 16 KiB at d0110000 (0 KiB free)
hakuX-native: vm: out of physical memory for 16 KiB at d0050000 (0 KiB free)
hakuX-native: vm: out of physical memory for 16 KiB at d0130000 (0 KiB free)
hakuX-native: seh: t8 access violation at 0029c694, reading 00000000: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 0029c694 (no handler took it), reading 00000000
hakuX-native-frontier: summary stage=S2 kernel_calls=929427 first_call=PsCreateSystemThreadEx threads=5
```

## Expected

The movie plays and the first level loads.

## Notes

- 0.19.0 already includes #69, the fix for Halo's level-load crash, so this is another case of guest RAM running out.
- No other title in the pass logged `out of physical memory`.
