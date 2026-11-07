## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Spikeout - Battle Street (U) (En,Ja,Fr,De,Es,It).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO; data SHA-1 `3d4820336b4d06fa2f5d9329975b90c4c48dc794`); XBE title ID `53450029` (read from the disc's `default.xbe` certificate; the core doesn't get that far)
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/spikeout-battle-street-u-en-ja-fr-de-es-it/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The game doesn't start. Right after reading the disc's file system the core fails to parse the XBE and reports a boot failure. Nothing is drawn or heard, and RetroArch runs without content for the rest of the run.

```
hakuX-native: disc: CHD v5, 1168834560 bytes in 285360 hunks of 4096 (lzma, zlib, huff, flac)
hakuX-native: disc: XDVDFS at +0x0, root sector 264 (100 bytes)
hakuX-native: xbe: parse failed (-3)
hakuX-libretro: core: boot failed
```

## Expected

The game boots.

## Notes

- The disc's `default.xbe` (sector 265, 6,246,400 bytes) has a plausible header: magic `XBEH`, base address 00010000, size of headers 0x6d6c, certificate title ID `53450029`, title name "SPIKEOUT Battle Street". It declares 398 sections (`.text`, `D3D`, `DSOUND`, ..., many named `wnDraw_D`, ..., `.XTLID`); the 398 section headers end at file offset 0x5a80, inside the headers.
- The most sections of any XBE the core loaded in this run is 78.
- No other title in the run logs `xbe: parse failed`.
- Seen in the only run; no earlier results for this title.
