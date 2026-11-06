## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, the release's default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Prince of Persia - The Two Thrones (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `55530058`
- **Run:** a fresh RetroArch with an empty profile and a new console disk. Start and A are pressed in turn every 2.5 s from 10.5 s to 33 s; screenshots are taken at 10, 22 and 45 s; Quit is sent at about 46 s. `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1` are set.

Found in a scripted 45 s first pass over 77 titles. Seen once, not yet retried, and not tried on ARM64.

## What happens

The game runs at 30 fps and reaches Create New Profile. Two screens look washed out:

- **Title screen** ("Please press START to begin"): a flat pale green-to-yellow gradient behind the logo.
- **Create New Profile:** a strong pale yellow-green wash over a faint city behind the letters.

They look like a full-screen bright layer drawn over the scene. Not yet compared with real hardware or xemu. Screenshots can be added.

## Expected

The menus as on the Xbox.

## Notes

- Prince of Persia: Warrior Within's Create New Profile screen looks washed out in a similar way (#98).
