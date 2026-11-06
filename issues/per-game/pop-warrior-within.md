## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Prince of Persia - Warrior Within (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `5553003b`
- **Run:** isolated RetroArch profile and console disk; alternating Start/A every 2.5 s from 10.5–33 s; screenshots at 10, 22 and 45 s; Quit at about 46 s. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.

Observed once in a scripted 45 s pass over 77 titles; no retest or ARM64 comparison.

## What happens

The title screen (the red logo on black) looks right. The Create New Profile screen is mostly white and light grey behind a faint red emblem, and its letters are pale grey on that light background. They are hard to read.

Not yet compared with real hardware or xemu. Screenshots can be added.

## Expected

The profile screen as on the Xbox.

## Notes

- Prince of Persia: The Two Thrones' title and profile screens look washed out in a similar way (#97).
