## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `WWE WrestleMania 21 (U) (Rev 1).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `54510024`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/wwe-wrestlemania-21-u-rev-1/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The screen is black and the recording is silent for the whole 5 min run. The game loads the `LEGAL` XBE section, creates the 640x480 device and clears the first surface twice. The next push-buffer command is invalid (word ff000000 at GET 03e00b34); hakuX skips to PUT. After that the guest submits nothing more: the push-buffer counters stay at 0 kicks, 0 draws and 0 swaps to the end. The guest makes 120 kernel calls a second, only `KeInsertQueueDpc` and `KeSetEvent` (60 each). It never opens the gamepad, so the inputs reach nothing. RetroArch keeps running at 60 frames/s until Quit.

```
hakuX-native: ex: load section LEGAL 00642ec0+18002c (refs 1)
hakuX-native: nv2a: channel PUT <- 03e00b54 (GET 03e00280 PUT 03e00280)
hakuX-native: nv2a: channel PUT <- 03e01304 (GET 03e008a0 PUT 03e00b54)
hakuX-native: nv2a: channel PUT <- 03e01324 (GET 03e008a0 PUT 03e01304)
hakuX-hle-pb: device 640x480
hakuX-hle-pb: surface 1: 03cd4000 format 12 640x480 pitch 2560
hakuX-hle-pb: surface 2: 03a7c000 format 2e 640x480 pitch 2560
hakuX-hle-back: clear #1 flags=0x3 color=00000000 z=1.000 rects=0 rt=1
hakuX-hle-back: clear #2 flags=0xf0 color=00000000 z=0.000 rects=0 rt=1
hakuX-hle-pb: push buffer fault: invalid command at GET 03e00b34 (word ff000000), PUT 03e01324, object 111c0 base 00000000 limit 07ffafff: skipped to PUT (subroutine 00000000, register 00000000, guest writes 1)
...
hakuX-native-stats: per s: kcalls 120 sysops 796 (int 557, of them ticks 469; hook 0) schedules 180 switches 180 idle 0 ... | KeInsertQueueDpc:60 KeSetEvent:60
hakuX-hle-pb: kicks 0 words 0 headers 0 methods 0 faults 1 GET 03e01324 PUT 03e01324 binds 5 semaphores 1 flips 0 traps 7 (9=6 28=1) runs 0 surfaces 2 clears 2 swaps 0 draws 0 ...
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=36461 first_call=PsCreateSystemThreadEx threads=3
```

## Expected

The game presents frames: the opening screens, the intro and the title screen.

## Notes

- The core logs no exception and no hang report; the run ends at Quit after 300 s.
- Seen in one run; there is no result from an earlier version.
