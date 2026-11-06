## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, the release's default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Prince of Persia - The Sands of Time (U) (En,Fr,Es).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `5553001d`
- **Run:** a fresh RetroArch with an empty profile and a new console disk. Start and A are pressed in turn every 2.5 s from 10.5 s to 33 s; screenshots are taken at 10, 22 and 45 s; Quit is sent at about 46 s. `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1` are set.

Found in a scripted 45 s first pass over 77 titles. Seen once, not yet retried, and not tried on ARM64.

## What happens

The Bink Video logo appears, and nothing new is drawn after frame 188, about 8 s after launch. All three screenshots show the Bink logo. Sound plays for about the first 8 s only. Quit works normally.

```
hakuX-hle-hitch: HANG started 0.50 s since frame 188: JIT compiling: 84% of the vCPU in FEX | render idle for 500 ms | vCPU cpu 499 ms halted 0% | ... | GPU 203/203, last done 500 ms ago | ...
hakuX-hle-hitch: HANG ongoing 37.52 s since frame 188: JIT compiling: 83% of the vCPU in FEX | render idle for 37519 ms | vCPU cpu 37406 ms halted 0% | ...
hakuX-native-frontier: summary stage=S2 kernel_calls=7497836 first_call=PsCreateSystemThreadEx threads=8
```

Unlike the other hangs in this pass, the guest keeps calling the kernel, about 167,000 times a second: `NtWaitForMultipleObjectsEx` 159,156, `NtReleaseMutant` 2,617, `NtWaitForSingleObjectEx` 2,617, `MmLockUnlockBufferPages` 1,001, `KeDelayExecutionThread` 872, `KeInsertQueueDpc` 560. That looks like a multi-object wait returning at once, again and again, perhaps on a movie or audio stream that never signals.

## Expected

The logos and the intro, then the title screen.

## Notes

- The `hang vCPU` line of the core's hang report shows every general register as zero, as all 66 hang samples on KVM in this pass did (33 titles). So it doesn't show where the guest is spinning.
