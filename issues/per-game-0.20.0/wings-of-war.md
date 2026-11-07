## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Wings of War (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `54540018`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, plus Y at 32 s and A at 34.5 s to fill in a name on Create Player and accept it ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/wings-of-war-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The copyright screen, Create Player and the campaign briefing (Verdun, winter; 47.2 s) work at 30 fps. When the mission starts (A on START), the game opens `dta\verdun_z.dta` and makes thousands of 4 KiB contiguous allocations from 000a83a2. One of them fails, although 24504 KiB are free in a single run. The game then looks for `scene.4ds` in the mission's parent folders (not on the disc), opens no more files, and from 50.3 s to the end shows its own error screen: "There's a problem with the disc you're using. It may be dirty or damaged." The run is silent from then on.

```
hakuX-native-io: open \Device\CdRom0\dta\verdun_z.dta -> 
hakuX-native: mm: contiguous allocation of 4 KiB at 03213000: 1 pages relocated (#512)
hakuX-native: mm: contiguous allocation of 4 KiB at 02fdb000: 1 pages relocated (#1024)
hakuX-native: mm: contiguous allocation of 4 KiB at 02b5d000: 1 pages relocated (#2048)
hakuX-native: mm: contiguous allocation of 4 KiB failed (#1; from 000a83a2, 00000000-04000000, align 1000; free 24504 KiB: 50000+24504K | 1 runs, largest 24504 KiB)
hakuX-native: mm:   map: 0+320K=K 50000+24504K=. 183e000+10540K=v 2289000+4K=K 228a000+10212K=C8228a000.. (2308 blocks) by 000a83a2 2c83000+48K=P va 0078a000 2c8f000+1652K=C82c8f000.. (378 blocks) by 000a83a2 ...
hakuX-native-mm: contiguous allocation failed: contiguous by caller: 000a83a2 28088K/4077 00139329 340K/18 00195977 4K/1
hakuX-native-mm: contiguous allocation failed: regions by committed (of 6): 006a0000+400000:3772K 00010000+273000:2496K(image) 00490000+200000:2048K 00290000+100000:1024K 00390000+100000:1024K 00690000+10000:4K
hakuX-native-io: open \Device\CdRom0\missions\1_Verdun\FAZE_I\NEDEVASTOVANY\scene.4ds: not on the disc
hakuX-native-io: open \Device\CdRom0\missions\1_Verdun\FAZE_I\scene.4ds: not on the disc
hakuX-native-io: open \Device\CdRom0\missions\1_Verdun\scene.4ds: not on the disc
```

## Expected

The first mission loads.

## Notes

- At the failure the caller 000a83a2 holds 28088 KiB of contiguous memory in 4077 blocks.
- The first lookup of `scene.4ds` (in `...\Zima\01_kampan_zima_verdun\`) comes before the failed allocation; the walk up the parent folders comes after it.
- The first run, without the override, never left Create Player.
- No earlier results for this title.

- Related (contiguous allocations fail with the game's live contiguous total at 4,096): #113, #118
