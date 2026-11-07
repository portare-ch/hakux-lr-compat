## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Tony Hawk's Project 8 (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4156005e`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, then from 45.5 s a fixed sequence (B, Down x4, A, B, Down x2, A) through NAME YOUR SKATER, CUSTOMIZE and START GAME, and A at 110 and 114 s on the first goal card ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/tony-hawk-s-project-8-u-en-fr-de-es-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The logos, NAME YOUR SKATER, the skater screens and the Suburbs level behind the goal cards draw correctly at 60 fps. Two loading screens are wrong:

- **First loading screen** (first run, 32.1 s): the Tony Hawk's Project 8 banner, the sky and the photo (a skater crouching by a lattice fence) are right, but a full-width band of random coloured pixels covers the screen from about half to about 85% of its height, over the photo's lower edge and the level name above LOADING. The re-run's 30.5 s screenshot shows this screen (with another photo) still fading in, without the band.
- **P8 SUBURBS LOADING** (both runs, 72.1 s): the banner, the sky and the level name are right, but the photo frame is filled with flat light grey.

The log has no error or warning around either screen.

## Expected

The loading screens show their photo and no noise.

## Notes

- The band was caught once; there is no other screenshot of that moment.
- The blank Suburbs photo is in both runs, in the only screenshot of that screen each time; it may be a frame before the photo appears.
- No earlier results for this title.
