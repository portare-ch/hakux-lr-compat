## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Images:** `Unreal Championship (U) (En,Fr,De,Es,It).chd` and `Unreal Championship (Japan, Asia).chd`, CHD (`chdman createdvd` from an XISO); XBE title ID `49470024` in both
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Results:** [USA result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/unreal-championship-u-en-fr-de-es-it/result.json) and [Japan/Asia result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/unreal-championship-japan-asia/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

Both discs behave the same. The game copies `atari.wmv` from the disc to `Partition5` and plays it from there; at about 43 s it opens `ucintro.wmv` from the disc. The movies play through the video overlay with sound from launch, but the screen stays black from launch to about 45 s (screenshots at 10, 30 and 45 s).

During the movies the push-buffer counters show the overlay updated 30 times a second, 1,278 updates in all, while swaps and draws stay at 2. From about 47 s the game draws its menus itself, and the "You must create a profile" notice, Game Setup and Pick Your Teammates render correctly at 60 fps.

```
hakuX-native-io: open \Device\CdRom0\atari.wmv -> 
hakuX-native-io: open \Device\Harddisk0\Partition5\atari.wmv -> (created)
hakuX-native-io: open \Device\Harddisk0\Partition5\Atari.wmv -> 
hakuX-hle-drawlog: rt-tex id=1 surf=1 img=1 layout=5 slot=2 fmt=44 1280x480 rt=3
hakuX-hle-pb: overlay on: 640x480 -> 0,0-640,480
hakuX-hle-back: overlay: 640x480 drawn at 0,0-1280,960
hakuX-hle-pb: scanout: the GPU wrote the frame on screen (3) and the title doesn't flip: shown again (first 4 logged)
hakuX-hle-pb: kicks 90 words 0 headers 0 methods 0 faults 0 GET 03f5e72c PUT 03f5e72c binds 4 semaphores 6 flips 2 traps 9 (9=6 21=2 28=1) runs 0 surfaces 3 clears 2 swaps 2 draws 2 ff 0 skipped 0 () textures 1 (1 held, 2 MiB) ... overlays 248 ...
hakuX-hle-fps: 30.0 fps (150 frames in 5.01 s)
...
hakuX-native-io: open \Device\CdRom0\ucintro.wmv -> 
```

## Expected

The Atari logo and the intro movie are visible.

## Notes

- Other titles in this run show their overlay movies with the same `overlay on: 640x480 -> 0,0-640,480` and `overlay: 640x480 drawn at 0,0-1280,960` lines, for example the Crave logo in World Championship Poker 2.
- Unreal Championship 2 - The Liandri Conflict (title ID `4d570021`) doesn't use the overlay, and its XMV cutscene renders correctly in the same run.
