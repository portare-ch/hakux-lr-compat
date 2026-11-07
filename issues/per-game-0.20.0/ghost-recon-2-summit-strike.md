## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Tom Clancy's Ghost Recon 2 - Summit Strike (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `5553004d`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, then from 50 s only A every 2 s, which walks through the profile and campaign menus without opening the START menu ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/tom-clancy-s-ghost-recon-2-summit-strike-u-en-fr-de-es-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

Every text in the game's small font is drawn as blocks of scattered coloured dots, at the right place and size but unreadable. Large text is fine. Everything else draws correctly: the Ubisoft logo, the ESRB notice, the menus at 60 fps, and the snowy mountain mission with radar and ammo HUD at 30-31 fps from about 90 s.

- NAME PROFILE wheel (`mid.png`, 46.0 s): the title, the letters, ACCEPT and PROFILE are clean; the help text under L and R and the labels next to the Start, B, A and Y button icons are dots.
- EQUIPMENT SETUP (`w070.jpg`, 72.2 s): the heading is clean; the description line, the weapon names and the button labels are dots.
- In the mission (`w090.jpg`, 92.6 s): the message box at the top holds two lines of dots; the ammo counter (030) is clean.

The log has no error or warning about textures or draws.

## Expected

The small-font text is readable.

## Notes

- Tom Clancy's Ghost Recon 2 (title ID `55530005`) shows the same on 0.19.1: the help text under L and R and the button labels on its NAME PROFILE screen are dots ([its 0.19.1 result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261105-0.19.1-ingame/tom-clancy-s-ghost-recon-2-u-en-fr-de-es-it/result.json)).
- The first run on 0.20.0 (without the override) shows the same dots on the menus.
