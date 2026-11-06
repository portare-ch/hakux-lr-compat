## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, the release's default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Call of Cthulhu - Dark Corners of the Earth (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `42530007`
- **Run:** a fresh RetroArch with an empty profile and a new console disk. Start and A are pressed in turn every 2.5 s from 10.5 s to 33 s; screenshots are taken at 10, 22 and 45 s; Quit is sent at about 46 s. `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1` are set.

Found in a scripted 45 s first pass over 77 titles. Seen once, not yet retried, and not tried on ARM64.

## What happens

The game reaches the main menu (New Game / Options), and the screenshots look right. The frame rate drops to a third of the refresh rate on the menu:

- **Shown, `hakuX-hle-disp` new frames per 10 s:** 32.5 and 29.5 (logo and first-run loading screen), then 19.9 and 19.9 (main menu)
- **Swaps, `hakuX-hle-fps`, per 5 s window:** 32.8, 32.7, 32.7, 25.9, then 19.9 four times

## Question

Does the menu run at 20 fps on the Xbox too, or is hakuX slow here? Not yet compared with hardware, and gameplay wasn't reached.
