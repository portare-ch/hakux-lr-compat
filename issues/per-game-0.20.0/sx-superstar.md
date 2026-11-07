## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `SX Superstar (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `41430010`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/sx-superstar-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

Sound starts at 5.5 s. The game opens the Acclaim (`Movies\AKA_Attitude_NTSC.xmv`, about 5 s) and CMX (`Movies\cmx-ntsc.xmv`, about 10 s) logo movies; the only screenshot, at 10 s, is a plain dark grey frame. At about 25 s the game opens `Movies\Mainmenu.XMV` and `SOUND\MUSIC\MENU.wav` and sets up two 1280x960 surfaces. At about 28 s it writes to 00000000 at eip 001b4e77; the core reports a guest fault the title doesn't handle, and RetroArch exits by itself at 29.8 s with code 0. The core logs no stop or summary line.

```
hakuX-native-io: open \Device\CdRom0\Movies\Mainmenu.XMV -> 
hakuX-native-io: open \Device\CdRom0\SOUND\MUSIC\MENU.wav -> 
hakuX-hle-pb: surface 39: 02c40000 format 12 1280x960 pitch 5120
hakuX-hle-pb: surface 40: 02790000 format 2e 1280x960 pitch 5120
hakuX-hle-back: clear #1360 flags=0xf3 color=002101e0 z=1.000 rects=1 rt=39 (changed)
hakuX-native-kvm: guest fault at 00000000 (write), eip 001b4e77: the title doesn't handle it
```

## Expected

The main menu.

## Notes

- Before the fault the picture stalls four times, for 3.0, 1.6, 3.0 and 0.8 s (frames 326, 327, 866 and 1115); the first two and the last report the vCPU 95–98 % in JIT compiling, the third reports the guest idle.
- Until then the surfaces are 640x480 (pitch 2560).
- RetroArch exits with code 0 and no message from the core, as with SNK vs Capcom - SVC Chaos.
- Seen in the only run; no earlier results for this title.
