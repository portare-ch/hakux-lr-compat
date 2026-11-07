## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Test Drive (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `49470007`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/test-drive-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The PSL logo, the garage intro, Create Player and Quick Race work. From about 20 s the game stalls eight times for about 5 s each (JIT compiling, 99% of the vCPU in FEX). The Loading screen shows from about 70 s; from about 85 s the guest draws nothing for 26.5 s, still JIT compiling. At about 111 s the menu program saves the display for the next title and relaunches into `TDGame.xbe`. The core does not stop within 10 s for the relaunch and ends the process at 121 s; `TDGame.xbe` never starts.

```
hakuX-hle-hitch: HANG ongoing 24.51 s since frame 1921: JIT compiling: 99% of the vCPU in FEX | render idle for 24510 ms | vCPU cpu 23546 ms halted 0% | ...
hakuX-native-mm: MmPersistContiguousMemory 8362f000+1232896: kept
hakuX-native: AvSetSavedDataAddress 8362f000
hakuX-native: ps: thread 28 exits (00000000)
hakuX-hle-pb: kept memory: the decoder did not get to it in 2000 ms
hakuX-native-mm: kept memory: the GPU's copies did not come back; saved as it is
hakuX-native-mm: kept memory: 1 range(s), 1204 KiB, saved display 8362f000 for the next title
hakuX-native-slow: HalReturnToFirmware from 0002fb96 held the CPU 2000.7 ms [00000002 00000000 00000000 00000000 00000000 00000000]
hakuX-native-frontier: stop: relaunch into \Device\CdRom0\TDGame.xbe (launch type 0)
hakuX-native-frontier: summary stage=S2 kernel_calls=286785 first_call=PsCreateSystemThreadEx threads=4
hakuX-libretro: core: stopped
hakuX-libretro: relaunch: the game boots again in RetroArch's process
hakuX-native: nv2a: push-buffer mode off
hakuX-hle-pipe: pipeline cache saved: 20608 bytes (merged in 0.0 ms, serialized in 0.0 ms, written in 0.1 ms), spirv hits=4 misses=10
hakuX-native-usb: ohci: 0 TDs in 10 s, ctl 000000be (lists PCB), hcca 03a12000, intr 00000006/80000073
hakuX-libretro: relaunch: the core did not stop in 10000 ms (the devices and the renderer): ending the process
```

## Expected

The core stops, boots `TDGame.xbe`, and the race loads.

## Notes

- Other relaunches in the same run work; Totaled!'s relaunch into `default.xbe` logs `relaunch: the core stopped in 51 ms`.
- 5.4-60 frames shown per second; 20 fps median.
- Seen in the only run; no earlier results for this title. The audio recording is empty.
