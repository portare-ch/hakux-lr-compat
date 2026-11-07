## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Sims, The - Bustin' Out (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `45410043`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, plus Right three times and A twice at 37-40.5 s (and again at 47-50.5 s) to pick the check mark in Create-A-Sim and confirm the save ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/sims-the-bustin-out-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Maxis logo and Create-A-Sim work at 30 fps. After the Sim is confirmed, the game writes its save (`UDATA\45410043\0069006D1352\SaveMeta.xbx`, `SaveGame`, `Config`) and shows the Bustin' Out loading screen (45.5 s). At about 46 s thread 36 reads from 00008045 and the core stops with an unhandled access violation. RetroArch has no content for the rest of the run; the screen stays black.

```
hakuX-native: ps: thread 36 created: start 0015d5c0 (via system routine), stack d0120000-d0129000, tls 148, suspended
...
hakuX-native-io: open \Device\Harddisk0\partition1\UDATA\45410043\0069006D1352\Config -> (created)
hakuX-hle-hitch: stutter #23 frame 1458: front 83.6 ms after the last (expected 33.4), 0 dropped: guest 115 ms: JIT compiling: 85% of the vCPU in FEX | ...
hakuX-hle-hitch: stutter #25 frame 1461: front 217.5 ms after the last (expected 33.4), 0 dropped: guest 206 ms: JIT compiling: 78% of the vCPU in FEX | ...
hakuX-native: seh: t36 access violation at 00147c15, reading 00008045: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 00147c15 (no handler took it), reading 00008045
hakuX-native-frontier: summary stage=S2 kernel_calls=1614323 first_call=PsCreateSystemThreadEx threads=10
```

## Expected

The house loads and play starts.

## Notes

- The first run, with an earlier override that didn't get past Create-A-Sim, stayed there to the 5 min limit without a crash.
- The Sims (same run) also stops with an unhandled access violation, at 0013e596 (writing 00607992), on its Create a Sim name screen at about 41 s.
- No earlier results for this title.

- Related (access violations when Create a Sim / the house loads): #119
