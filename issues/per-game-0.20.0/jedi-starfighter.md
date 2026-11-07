## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Star Wars - Jedi Starfighter (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4c410005`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, plus Y at 48 and 58 s to confirm the pilot name ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/star-wars-jedi-starfighter-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

Everything renders, and the first mission plays at 60 fps from about 110 s. The front end before it, from about 22 s to about 95 s (the pilot name keyboard, the profile list and the Act menu), runs at only 2.4-9.4 fps.

In the front end every draw goes out in its own push-buffer kick: the game makes about 11,000 draws a second, about 3,000 per frame, each a small non-indexed strip of about 7 vertices, and the kick count matches the draw count. In play it makes 5,400-8,700 draws a second in fewer than 1,000 kicks. Figures from the per-second `hakuX-hle-emit` and `hakuX-hle-pb` lines, grouped by 5 s window:

| | Front end (22-95 s) | In play (110-136 s) |
| --- | --- | --- |
| Displayed fps | 2.4-9.4 | 60 |
| Draws/s | 8,600-11,600 | 5,400-8,700 |
| Push-buffer kicks/s | 8,800-11,900 | 700-1,000 |
| Vertices/s | 60,000-92,000 | 1.1-1.3 M |

During the front end the hitch reports show the vCPU 100% busy (halted 0%), named either "JIT compiling" or "guest CPU-bound", while the render thread is idle most of each frame.

```
hakuX-hle-hitch: stutter #35 frame 792: front 266.6 ms after the last (expected 133.5), 0 dropped: guest 255 ms: JIT compiling: 100% of the vCPU in FEX | ... | guest: vCPU cpu 253 ms halted 0% | render cpu 26 run 16 idle 239 compile 0 (0) submit 0 (13) gpu 0 display 0 | GPU 1503/1503, last done 12 ms ago | swaps 1 vblanks 16 draws 3057 | ...
hakuX-hle-emit: per s: draws=11592 verts=79752 mergeable=0 (not: strip 11592 idx 0 state 0 work 0 gap 0) ...
hakuX-hle-pb: kicks 11878 words 915580 headers 234506 methods 681056 faults 0 ... unindexed 179158 ...
hakuX-hle-hitch: stutter #38 frame 807: front 150.0 ms after the last (expected 133.5), 0 dropped: guest 145 ms: guest CPU-bound (1451 draws) | ...
...
(in play)
hakuX-hle-fps: 60.0 fps (300 frames in 5.00 s)
hakuX-hle-pb: kicks 706 words 1332060 headers 233687 methods 1098372 faults 0 ...
hakuX-hle-emit: per s: draws=5460 verts=1114980 mergeable=0 (not: strip 0 idx 5160 state 300 work 0 gap 0) ...
```

## Expected

The front end runs at full speed, like the mission.

## Notes

- The first run of this game, without the Y override, stayed in the front end for 5 min at 3.8-9.5 fps with the same one-kick-per-draw pattern.
- Star Wars - Starfighter Special Edition and Star Wars - Obi-Wan (also LucasArts) show the same pattern in their front ends.
- The 90 s screenshot shows large hull polygons across the Act menu; it is not known whether that is a menu transition.

- Related (LucasArts front ends at one push-buffer kick per draw): #129, #130
