## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `WWE Raw 2 (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `5451000d`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/wwe-raw-2-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The game itself works: Quick Start at 70 s, and The Rock vs The Undertaker from 110 s to the end of the run, at 60 fps. The harness sends Quit at 137.8 s.

The core logs `core: stopped`, but the process does not exit. RetroArch stops answering status requests from 138.9 s, and the log never reaches the `RetroArch destroyed the context` line. The harness kills the process 10 s after Quit, at 147.9 s.

```
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=711739 first_call=PsCreateSystemThreadEx threads=5
hakuX-libretro: core: stopped
hakuX-native: nv2a: push-buffer mode off
hakuX-native-usb: ohci: 9076 TDs in 10 s, ctl 000000be (lists PCB), hcca 03fde000, intr 00000006/80000073
```

A clean quit of another title in the same run (UFC: Tapout) logs, after `nv2a: push-buffer mode off`:

```
hakuX-libretro: vulkan: RetroArch destroyed the context: the core stopped in 48 ms
```

## Expected

RetroArch closes within a second or two of Quit.

## Notes

- Four more runs on 0.20.0 end the same way (`core: stopped`, then no `destroyed the context` line before the kill 10 s after Quit): RollerCoaster Tycoon, The Simpsons: Road Rage, Sneakers and The Thing.
- Seen in the only run of this title.

- Related (RetroArch doesn't exit after Quit): #123, #131, #127
