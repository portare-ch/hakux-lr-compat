## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Tom Clancy's Rainbow Six - Lockdown (U) (En,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `55530048`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/tom-clancy-s-rainbow-six-lockdown-u-en-fr-de-es-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The Ubisoft logo and the intro movie play at 29.7 fps; the 11.8 s screenshot shows the movie correctly. Meanwhile the game copies models and textures to `Partition5\cache`. At the end of the log the title takes 32 write faults at rising addresses from 00960000 to 009be000, all passed to its own handlers. At 15 s RetroArch dies with SIGSEGV. The core log just ends, with no stop line.

```
hakuX-native-io: open \Device\Harddisk0\Partition5\cache\textures\3p_r_sa58_128.dds -> (created)
hakuX-native: seh: t8 access violation at 0023ee13, writing 00960000: to the title's handlers
hakuX-native: seh: t8 access violation at 000490c2, writing 00967010: to the title's handlers
hakuX-native: seh: t8 access violation at 000e78f9, writing 0096a000: to the title's handlers
...
hakuX-native: seh: t8 access violation at 00043ee0, writing 009b6004: to the title's handlers
hakuX-native: seh: t8 access violation at 0023ee13, writing 009b8000: to the title's handlers
hakuX-native: seh: t8 access violation at 000e78f9, writing 009bb000: to the title's handlers
hakuX-native: seh: t8 access violation at 0023ee13, writing 009be000: to the title's handlers
```

The host core dump (systemd-coredump) shows the fault in a thread the core started, writing to `rcx + rax` with `rax` = 0xa07000:

```
Signal: 11 (SEGV) si_code: SEGV_ACCERR
#0  hakux_libretro.so + 0x97c78    movl $0x40001,(%rcx,%rax,1)
#1  hakux_libretro.so + 0x91562
#2  hakux_libretro.so + 0x8f811
#3  hakux_libretro.so + 0xc4fee
#4  hakux_libretro.so + 0x7c1c6
#5  hakux_libretro.so + 0x7469d
#6  libc.so.6 + 0xacef1 (thread start)
rax 0xa07000  rcx 0x7f602bff0000  si_addr 0x7f602c9f7000
```

At that moment the main thread was in `retro_run` → `video_driver_frame` → `vulkan_acquire_next_image`.

## Expected

The intro ends and the main menu shows.

## Notes

- Seen in the only run; no earlier results for this title.

- Related (freezes with ~100k wait calls a second, sound still playing): #150, #151
