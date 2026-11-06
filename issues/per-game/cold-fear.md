## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Cold Fear (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `5553004b`
- **Run:** isolated RetroArch profile and console disk; alternating Start/A every 2.5 s from 10.5–33 s; screenshots at 10, 22 and 45 s; Quit at about 46 s. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.

Observed once in a scripted 45 s pass over 77 titles; no retest or ARM64 comparison.

## What happens

After the Ubisoft logo (10 s), the screen is black with only a spinning red radar icon in the top-left corner. That screen lasts from 22 s to the end of the run at 45 s. Frames keep coming (`hakuX-hle-disp`: 56.2, 44.1, 30.0, 30.0 per 10 s), and no hang is reported. Sound plays for about the first 14 s, then stops.

## Question

A longer run is needed to distinguish loading from a stall.

## Expected

The intro and the title screen.
