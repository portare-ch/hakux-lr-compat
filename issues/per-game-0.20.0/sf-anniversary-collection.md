## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Street Fighter Anniversary Collection (Japan, Europe) (En,Ja).chd`, CHD (`chdman createdvd` from an XISO); XBE title ID `4343000f`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, then from 62 s only A every 4 s, so that Start doesn't pause the fight ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/street-fighter-anniversary-collection-japan-europe-en-ja/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The menu program relaunches into `sf33rd.xbe` (Street Fighter III: 3rd Strike; the core stops in 43 ms and boots it). The ESRB notice and the save message are fine, and so is the Alex vs Necro fight from about 70 s, with its HUD, at 60 fps. Two screens in between are corrupted:

- **Super Arts select** (`mid.png`, 46.0 s): Alex's portrait and the SUPER ARTS SELECT banner are right, but the selected Super Art (the icon panel between the blue arrows) is a jumble of white, dark-red and green fragments; its name reads "3RIBOMO". The TIME counter in the bottom right corner is garbled too.
- **VS screen** (`w050.jpg`, 51.2 s): the left half (Russia / Brazil cards with place and time text) is fine; the right half is covered by white and yellow blocks and letter fragments ("STAGE", parts of large red letters), and the Super Art name left of Alex's name is broken the same way.

The log has no error or warning after the relaunch apart from one `draw dropped (pipeline being built)`.

## Expected

The Super Art icon and name, the TIME counter and the VS screen's right half are drawn cleanly, as in the fight.

## Notes

- The first run, without the override, shows the same corruption on both screens at the same times.
- Shown frames per second: 53.7-60.0.
- No earlier results for this title.
