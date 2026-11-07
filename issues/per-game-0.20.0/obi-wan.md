## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Star Wars - Obi-Wan (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4c410001`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, replaced at 31-43 s by 400 ms presses 2 s apart (Down, Down, Right, Right, A) meant to reach PROCEED on the name keyboard ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/star-wars-obi-wan-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The LucasArts logo plays with sound. From about 30 s to Quit at 300 s the game stays in its front end: the ENTER NAME keyboard, and the main menu after the B presses the harness sends when the screen doesn't change (73, 171 and 271 s). Both render correctly but run at only 6.3-11 fps for the whole time.

The game draws about 11,000 times a second, about 1,700 draws per frame, nearly all small non-indexed strips of about 10 vertices, and sends almost every draw in its own push-buffer kick (about 10,500 kicks a second). The hitch reports show the vCPU busy for the whole frame ("guest CPU-bound (1701 draws)", or "JIT compiling") while the render thread is idle most of it.

```
hakuX-hle-hitch: stutter #62 frame 565: front 166.6 ms after the last (expected 133.5), 0 dropped: guest 159 ms: guest CPU-bound (1701 draws) | ... | guest: vCPU cpu 158 ms halted -1% | render cpu 14 run 9 idle 150 compile 0 (0) submit 0 (8) gpu 0 display 0 | GPU 2594/2594, last done 0 ms ago | swaps 1 vblanks 10 draws 1701 | ...
hakuX-hle-pb: kicks 10840 words 1355001 headers 338025 methods 1016960 faults 0 ...
hakuX-hle-emit: per s: draws=11314 verts=107428 mergeable=0 (not: strip 10985 idx 329 state 0 work 0 gap 0) ...
hakuX-hle-fps: 6.6 fps (34 frames in 5.13 s)
```

The keyboard also doesn't follow the d-pad. At 30 s the name reads `JEDI 1YYY` with the cursor on Y. The log shows the override's presses reaching the pad (`buttons 0000 -> 0002` twice for Down, `0000 -> 0008` twice for Right). At 45 s the cursor is on R, one row up and three columns right, and the name reads `JEDI 1YYYY`. No Up press was sent.

## Expected

The keyboard runs at full speed and moves with the d-pad, so PROCEED can be reached. With a pad by hand, PROCEED leads to the opening crawl and the first level.

## Notes

- The first run of this game, with 250 ms presses, also stayed in the front end for 5 min, at the same rate after the logo.
- Star Wars - Jedi Starfighter and Star Wars - Starfighter Special Edition (also LucasArts) show the same one-kick-per-draw pattern and low rate in their front ends; both run at 42-60 fps once a mission starts.

- Related (LucasArts front ends at one push-buffer kick per draw): #128, #130
