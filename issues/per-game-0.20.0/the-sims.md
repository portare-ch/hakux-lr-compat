## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Sims, The (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4541002f`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/sims-the-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Sims logo and the menus render with sound from 1 s. At 30 s the Create a Sim name keyboard is up, with the name "PAT" entered and Done highlighted; it renders correctly. Right after the Start press at 40.5 s, thread t36 writes to 00607992 and the core stops with an unhandled access violation; RetroArch reports no content from 41.7 s. Black and silent from then on.

```
hakuX-native-usb: gamepad 0: buttons 0000 -> 0010 (A 00)
hakuX-hle-fps: 30.0 fps (150 frames in 5.00 s)
hakuX-hle-disp: stats: 27.1 new frames/s, age front to taken 8.21 ms (max 10.75), gap 36.88 ms (max 816.32, 272 over 25 ms)
hakuX-native-usb: gamepad 0: buttons 0010 -> 0000 (A 00)
hakuX-native: seh: t36 access violation at 0013e596, writing 00607992: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 0013e596 (no handler took it), writing 00607992
hakuX-native-frontier: summary stage=S2 kernel_calls=1220648 first_call=PsCreateSystemThreadEx threads=9
```

## Expected

The name is accepted and Create a Sim continues.

## Notes

- Thread t36 was created at boot: `ps: thread 36 created: start 0014b5a0 (via system routine), stack d0110000-d0115000, tls 20, suspended`.
- In the last seconds before the crash the guest makes 13,000–33,000 `NtReleaseSemaphore` and as many `NtWaitForSingleObjectEx` calls a second; the core reports 3668 KiB of RAM free.
- 27–59 new frames/s before the crash (`hakuX-hle-disp` 43.4, 59.0, 31.4 and 27.1).
- Seen in the only run; no earlier results for this title.

- Related (access violations when Create a Sim / the house loads): #160
