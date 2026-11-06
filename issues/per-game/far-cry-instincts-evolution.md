## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, the release's default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Far Cry Instincts - Evolution (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `55530060`
- **Run:** a fresh RetroArch with an empty profile and a new console disk. Start and A are pressed in turn every 2.5 s from 10.5 s to 33 s; screenshots are taken at 10, 22 and 45 s; Quit is sent at about 46 s. `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1` are set.

Found in a scripted 45 s first pass over 77 titles. Seen once, not yet retried, and not tried on ARM64.

## What happens

The game starts a new game and plays its in-engine opening, and the screenshots look right. The core counts far more swaps than it shows:

- **Swaps, `hakuX-hle-fps`, per 5 s window:** 1187.6, 995.0, 418.2, 740.0, 1639.1, 1086.8, 1253.9, 1370.1, 1321.2
- **Shown, `hakuX-hle-disp` new frames per 10 s:** 50.3, 40.8, 57.5, 56.3

## Question

Does the game present without waiting for vblank (immediate presentation)? If so, does the Xbox pace those presents, and should hakuX? Unpaced presents could cost CPU time or change game speed. Neither has been checked in gameplay.

## Notes

- Far Cry Instincts does the same (#99).
