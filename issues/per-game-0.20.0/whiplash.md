## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Whiplash (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `45530011`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, plus B at 91 and 101 s to accept the save prompt, where B is OK and A is Cancel ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/whiplash-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Eidos logo, the player icon picker, the save prompt and the Player list work. The intro cutscene starts at about 110 s and is still playing at 233 s. At about 233 s, about 2.5 s after a Start press, the title writes to 00000030 and the core stops with an unhandled access violation. RetroArch then waits 10 s for the core to stop, and the core ends the process at 243 s.

```
hakuX-native: seh: t8 access violation at 002c66a9, writing 00000030: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 002c66a9 (no handler took it), writing 00000030
hakuX-native-frontier: summary stage=S2 kernel_calls=573925 first_call=PsCreateSystemThreadEx threads=3
hakuX-libretro: core: stopped
hakuX-libretro: shutting down: the core stopped
hakuX-hle-hitch: HANG started 0.50 s since frame 13777: decoder waited 501 ms on the guest's GPU interrupt handler | render idle for 501 ms | vCPU cpu 0 ms halted 0% | ...
hakuX-hle-hitch: HANG ongoing 1.50 s since frame 13777: decoder waited 1501 ms on the guest's GPU interrupt handler | render idle for 1501 ms | ...
hakuX-native: nv2a: push-buffer mode off
hakuX-libretro: vulkan: RetroArch destroyed the context: the core did not stop in 10000 ms (the devices and the renderer): ending the process
```

## Expected

The intro ends and the game reaches its menus; after a stop, the core shuts down within the 10 s limit.

## Notes

- Seen once. The first run, without the override, stayed on the save prompt (A cancels it) and ran to the 5 min limit without a crash.
- 55.7-60.0 frames shown per second for the whole run.
- The audio recording is empty, so sound can't be judged.
