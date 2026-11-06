## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Project Gotham Racing (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4d530003`
- **Run:** isolated RetroArch profile and console disk; alternating Start/A every 2.5 s from 10.5–33 s; screenshots at 10, 22 and 45 s; Quit at about 46 s. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.

Observed once in a scripted 45 s pass over 77 titles; no retest or ARM64 comparison.

## What happens

The intro movie and the Bizarre Creations logo play. About 31 s after launch (frame 1386), on a garage shot from the intro, the game stops drawing until Quit. Sound stops earlier, about 12 s after launch. The core reports the guest CPU busy and the renderer idle. Quit fails to stop the core; it terminates the process after 10 s.

```
hakuX-hle-hitch: HANG started 0.50 s since frame 1386: JIT compiling: 100% of the vCPU in FEX | render idle for 500 ms | vCPU cpu 468 ms halted 0% | ... | GPU 1826/1826, last done 500 ms ago | ...
hakuX-hle-hitch: HANG ongoing 14.51 s since frame 1386: JIT compiling: 99% of the vCPU in FEX | render idle for 14508 ms | vCPU cpu 14442 ms halted 0% | ...
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=709635 first_call=PsCreateSystemThreadEx threads=4
hakuX-libretro: vulkan: RetroArch destroyed the context: the core did not stop in 10000 ms (the devices and the renderer): ending the process
```

During the hang only background kernel calls are made (about 2,100 a second): `MmLockUnlockBufferPages` 1000, `KeInsertQueueDpc` 560, `MmGetPhysicalAddress` 500, `KeSetEvent` 60.

## Expected

The intro continues to the title screen. Project Gotham Racing 2 reached its menus in the same pass.

## Notes

- All 66 KVM hang samples across 33 titles report zero general registers, so `hang vCPU` cannot locate the spinning code.
- Oddworld: Munch's Oddysee (#93) and Project: Snowblind (#94) hang the same way, but earlier.
