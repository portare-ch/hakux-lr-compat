## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, the release's default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Far Cry Instincts (U) (En,Fr,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `55530008`
- **Run:** a fresh RetroArch with an empty profile and a new console disk. Start and A are pressed in turn every 2.5 s from 10.5 s to 33 s; screenshots are taken at 10, 22 and 45 s; Quit is sent at about 46 s. `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1` are set.

Found in a scripted 45 s first pass over 77 titles. Seen once, not yet retried, and not tried on ARM64.

## What happens

The game reaches first-person gameplay on the beach, and the screenshots look right. The core counts far more swaps than it shows:

- **Swaps, `hakuX-hle-fps`, per 5 s window:** 1105.6, 1012.9, 739.3, 52.4, 1088.9, 1115.8, 1330.7, 1440.4, 1092.6
- **Shown, `hakuX-hle-disp` new frames per 10 s:** 51.2, 37.2, 56.7, 56.6

## Question

Does the game present without waiting for vblank (immediate presentation)? If so, does the Xbox pace those presents, and should hakuX? Unpaced presents could cost CPU time or change game speed. Neither has been checked in gameplay.

## Notes

- Far Cry Instincts – Evolution does the same (#100).
