## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Tenchu - Return from Darkness (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `41560026`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, then from 42 s only A every 4 s up to 119 s, so that Start doesn't pause play ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/tenchu-return-from-darkness-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Activision logo, the "Now loading" screen and the letterboxed intro cutscene (70-90 s) play at 60 fps with sound. From 113 s to the stop at 158 s the screen shows a full-frame view of a dark forest by a stream, with a ninja at the right edge half hidden by bushes. The view barely changes in that time, and no HUD (health bar, ki meter) or text is drawn. A was pressed at 111, 115 and 119 s.

In the first run (Start and A every 2.5 s throughout) the same view shows at 53 s, and Start brings up a "PAUSED" text over it at 73 s, so 2D text over this view does draw.

The log has no error or warning in this part of the run; the game presents 60 frames per second with about 6,900 draws and 6.2 million vertices a second.

## Expected

If this is play, the health bar and ki meter show.

## Notes

- Not checked by hand or on a console: this may be a level-start view that waits for other input rather than play with a missing HUD.
- No earlier results for this title.
