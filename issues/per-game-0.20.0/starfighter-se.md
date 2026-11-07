## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Star Wars - Starfighter Special Edition (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4c410002`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, plus Y at 32 and 42 s to create a save on the empty hard disk list ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/star-wars-starfighter-special-edition-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

Everything renders, and the first mission (the canyon flight) plays at 42-60 fps from about 60 s. The front end before it, from about 22 s to about 52 s (the hard disk save list, the main menu wheel and the difficulty prompt), runs at only 4.3-13.7 fps.

In the front end almost every draw goes out in its own push-buffer kick: about 10,000 draws a second, about 1,900 per frame, mostly small non-indexed strips of about 9 vertices. In play the game makes as many draws or more in far fewer kicks. Figures from the per-second `hakuX-hle-emit` and `hakuX-hle-pb` lines, grouped by 5 s window:

| | Front end (22-52 s) | In play (60-98 s) |
| --- | --- | --- |
| Displayed fps | 4.3-13.7 | 42-60 |
| Draws/s | 9,100-10,900 | 6,600-16,400 |
| Push-buffer kicks/s | 9,300-11,300 | 1,050-2,350 |
| Vertices/s | 74,000-107,000 | 0.9-2.8 M |

During the front end the hitch reports show the vCPU 100% busy (halted 0%), named either "JIT compiling" or "guest CPU-bound", while the render thread is idle most of each frame.

```
hakuX-hle-hitch: stutter #41 frame 957: front 183.3 ms after the last (expected 83.4), 0 dropped: guest 182 ms: JIT compiling: 100% of the vCPU in FEX | ... | guest: vCPU cpu 176 ms halted 0% | render cpu 16 run 10 idle 172 compile 0 (0) submit 0 (9) gpu 0 display 0 | GPU 1584/1584, last done 9 ms ago | swaps 1 vblanks 11 draws 1932 | ...
hakuX-hle-pb: kicks 10745 words 1337984 headers 337778 methods 1000208 faults 0 ...
hakuX-hle-emit: per s: draws=10431 verts=95336 mergeable=0 (not: strip 9874 idx 557 state 0 work 0 gap 0) ...
hakuX-hle-fps: 12.2 fps (62 frames in 5.07 s)
...
(in play)
hakuX-hle-pb: kicks 1533 words 4282568 headers 554664 methods 3727862 faults 0 ...
hakuX-hle-emit: per s: draws=8817 verts=1846764 mergeable=0 (not: strip 0 idx 8817 state 0 work 0 gap 0) ...
hakuX-hle-fps: 60.0 fps (301 frames in 5.02 s)
```

## Expected

The front end runs at full speed, like the mission.

## Notes

- The first run of this game, without the Y override, stayed in the front end for 5 min at 6-15 fps with about as many kicks as draws.
- Star Wars - Jedi Starfighter and Star Wars - Obi-Wan (also LucasArts) show the same pattern in their front ends.

- Related (LucasArts front ends at one push-buffer kick per draw): #128, #129
