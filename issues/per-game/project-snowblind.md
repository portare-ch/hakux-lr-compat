## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Project - Snowblind (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `45530019`
- **Run:** isolated RetroArch profile and console disk; alternating Start/A every 2.5 s from 10.5–33 s; screenshots at 10, 22 and 45 s; Quit at about 46 s. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.

Observed once in a scripted 45 s pass over 77 titles; no retest or ARM64 comparison.

## What happens

Nothing new is drawn after the 19th frame, about 2 s after launch. All three screenshots show the same frame: a grey gradient, like a sky over a flat grey plane, with no geometry or text. The run is silent. The core reports the guest CPU busy and the renderer idle until Quit. Quit fails to stop the core; it terminates the process after 10 s.

```
hakuX-hle-hitch: HANG started 0.50 s since frame 19: JIT compiling: 99% of the vCPU in FEX | render idle for 501 ms | vCPU cpu 499 ms halted 0% | ... | GPU 19/19, last done 500 ms ago | ...
hakuX-hle-hitch: HANG ongoing 43.52 s since frame 19: JIT compiling: 99% of the vCPU in FEX | render idle for 43524 ms | vCPU cpu 43411 ms halted 0% | ...
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=98562 first_call=PsCreateSystemThreadEx threads=3
hakuX-libretro: vulkan: RetroArch destroyed the context: the core did not stop in 10000 ms (the devices and the renderer): ending the process
```

During the hang the guest makes about 2,200 kernel calls a second, all background: `MmLockUnlockBufferPages` 1000, `KeInsertQueueDpc` 560, `MmGetPhysicalAddress` 500, `KeSetEvent` 60, `KfLowerIrql` 53.

## Expected

The publisher logos and the title screen.

## Notes

- All 66 KVM hang samples across 33 titles report zero general registers, so `hang vCPU` cannot locate the spinning code.
- Oddworld: Munch's Oddysee (#93) and Project Gotham Racing (#95) hang the same way.
