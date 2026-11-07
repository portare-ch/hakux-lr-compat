## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Terminator, The - Dawn of Fate (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `49470026`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/terminator-the-dawn-of-fate-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The SAVE NAME keyboard shows at 33 s, and the save is written. The game then copies the training level's files (`DATA\levels\training\TRL_00.PAK`, `TRL_00.PCK`, `TRL_A.PCK`, `TRL_B.PCK`) from the disc to the cache partition and opens Reese's skin and animations. The screen is black from then on (44.9 s).

At about 45 s the game looks for `autopistol.vk` and then `ModelError.vk` under six paths each; none of them exists. Right after the last lookup the title writes to 000000a8 and the core stops with an unhandled access violation. RetroArch reports no content for the rest of the run.

```
hakuX-native-io: open \Device\Harddisk0\Partition5\DATA\LEVELS\TRAINING\TRL_B.PCK -> 
hakuX-ktrace: t8 NtQueryInformationFile from 002395cd [ffffffff d0080a3c d0080a04 00000038 00000022 00000000] -> c0000008 | frames 001a6539 00132cce 00239d81 80010f08
hakuX-ktrace: t8 NtSetInformationFile from 00239650 [ffffffff d0080a3c d0080a44 00000008 0000000e 00000000] -> c0000008 | frames 001a6539 00132cce 00239d81 80010f08
hakuX-native-io: open \Device\CdRom0\DATA\rom_xbox\xmodels\autopistol.vk: not on the disc
hakuX-native-io: open \??\autopistol.vk: unknown device (a missing name)
hakuX-native-io: open \Device\CdRom0\DATA\D:\DATA\rom_xbox\xmodels\autopistol.vk: not on the disc
hakuX-native-io: open \Device\CdRom0\DATA\autopistol.vk: not on the disc
hakuX-native-io: open \Device\CdRom0\DATA\rom_xbox\D:\DATA\rom_xbox\xmodels\autopistol.vk: not on the disc
hakuX-native-io: open \Device\CdRom0\DATA\rom_xbox\autopistol.vk: not on the disc
hakuX-native-io: open \Device\CdRom0\DATA\rom_xbox\xmodels\ModelError.vk: not on the disc
...
hakuX-native-io: open \Device\CdRom0\DATA\rom_xbox\ModelError.vk: not on the disc
hakuX-ktrace: t8 NtCreateFile from 00238282 [d0080720 80100080 d0080704 d0080710 00000000 00000080] -> c0000034 | frames 00251f17 00252074 00256aef 0025178b 002517bc 0017a4da
hakuX-native: seh: t8 access violation at 0009e67f, writing 000000a8: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 0009e67f (no handler took it), writing 000000a8
hakuX-native-frontier: summary stage=S2 kernel_calls=146362 first_call=PsCreateSystemThreadEx threads=5
```

## Expected

The training level loads.

## Notes

- The same search over several paths finds other files (for example `load_lev0.rgb` and `MENU.PCK` under `\Device\CdRom0\DATA\`); only `autopistol.vk` and `ModelError.vk` are found nowhere.
- At boot the game asks for 25600 KiB of contiguous memory (from 0025a24b), which fails (largest free run 20496 KiB). It retries with ever smaller sizes, more than 4096 failed requests, until 21328 KiB succeeds:
  ```
  hakuX-native: mm: contiguous allocation of 25600 KiB failed (#1; from 0025a24b, 00000000-04000000, align 1000; free 21328 KiB: 50000+20496K 3f10000+832K | 2 runs, largest 20496 KiB)
  hakuX-native: mm:   map: 0+320K=K 50000+20496K=. 1454000+3760K=v 1800000+39936K=C81800000.. (2 blocks) by 0025a24b 3f00000+64K=K 3f10000+832K=. 3fe0000+128K=K
  hakuX-native: mm: contiguous allocation of 21328 KiB at 0032c000: 940 pages relocated (#3)
  ```
- Seen in the only run; no earlier results for this title.
