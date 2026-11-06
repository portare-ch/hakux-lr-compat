## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Tom Clancy's Splinter Cell - Pandora Tomorrow (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `55530019`
- **Run:** isolated RetroArch profile and console disk; alternating Start/A every 2.5 s from 10.5–33 s; screenshots at 10, 22 and 45 s; Quit at about 46 s. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.

Observed once in a scripted 45 s pass over 77 titles; no retest or ARM64 comparison.

## What happens

- **10 s:** the title screen ("Press Start to begin").
- **About 11–21 s after launch:** a 10 s stall, where nothing is drawn from frame 636.
- **22 s and 45 s:** both screenshots show the same still image, a harbour at sunset with no menu text. Sound plays for the whole run, apart from a gap at about 6–10 s.

```
hakuX-hle-hitch: HANG started 0.50 s since frame 636: JIT compiling: 55% of the vCPU in FEX | render idle for 501 ms | vCPU cpu 354 ms ...
hakuX-hle-hitch: HANG ongoing 9.51 s since frame 636: ...
```

## Question

A longer run is needed to identify the still image and determine whether the 10 s first-boot stall is expected (for example, save-data creation).

## Expected

The main menu after Start.
