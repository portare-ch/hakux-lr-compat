## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Tim Burton's The Nightmare Before Christmas - Oogie's Revenge (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `42560004`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/tim-burton-s-the-nightmare-before-christmas-oogie-s-revenge-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The first "Now Loading..." screen (pumpkin scarecrow, bottom left) shows from 10.3 s and never changes; every screenshot to 300 s is the same. The run is silent from launch to the end.

In the first seconds the game opens its XACT banks (`effect.bin`, `bgm_21`, `jaksys`, `combo_u`) and `data.inf`, starts and ends thread 28, and presents 25 frames. After that it presents nothing, reads nothing more from the disc, and makes 120 kernel calls a second, all `KeInsertQueueDpc` and `KeSetEvent` (60 each). The push buffer stays empty (GET = PUT). The hang monitor reports no hang.

```
hakuX-native-io: open \Device\CdRom0\data.inf -> 
hakuX-native: ps: thread 28 created: start 001a83a0 (via system routine), stack d00a0000-d00b1000, tls 148
hakuX-native: ps: thread 28 exits (00000000)
hakuX-native: nv2a: flip read -> 2 (write 1, display 03cd4000)
hakuX-native: nv2a: flip read -> 0 (write 2, display 03ba8000)
hakuX-native: nv2a: flip read -> 1 (write 2, display 03a7c000)
hakuX-hle-pb: kicks 230 words 14239 headers 3471 methods 10752 faults 0 GET 03e0de78 PUT 03e0de78 binds 5 semaphores 54 flips 25 traps 34 (21=25 9=8 28=1) runs 0 surfaces 4 clears 4 swaps 25 draws 154 ...
hakuX-hle-pb: kicks 59 words 0 headers 0 methods 0 faults 0 GET 03e0de78 PUT 03e0de78 binds 5 semaphores 54 flips 25 traps 34 ...
hakuX-native-stats: per s: kcalls 120 sysops 800 (int 560, of them ticks 459; hook 0) schedules 180 switches 180 idle 0 slices 0 page faults 0 mmio 480 apu waits 0 vm pages +0 -0 isr irq3:60 (max 0.0 ms) | dpc max wait 0.0 run 0.1 ms, 0 over 8 ms | holds 0 (longest 0.0 ms), 0.0 ms left out | KeInsertQueueDpc:60 KeSetEvent:60
...
hakuX-native-frontier: summary stage=S2 kernel_calls=42379 first_call=PsCreateSystemThreadEx threads=3
```

## Expected

The loading finishes and the intro or title screen shows, with sound.

## Notes

- The same 120 calls a second (`KeInsertQueueDpc` 60, `KeSetEvent` 60) repeat unchanged from about 10 s to the stop at 300 s.
- Seen in the only run; no earlier results for this title.
