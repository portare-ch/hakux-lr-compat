## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `Silent Hill 4 - The Room (U) (En,Ja,Ko).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4b4e001f`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s, then from 42 s only A every 4 s up to 119 s, so that Start doesn't pause the game ([overrides.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/overrides.json)). A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/silent-hill-4-the-room-u-en-ja-ko/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

The content warning, the Konami logo and the intro play with sound from 11.5 s to about 42 s. From about 45 s Henry's dark room (first person, lamp and globe on the desk) is on screen at a steady 30 fps until the stop at 304 s. From 44 s to the end the recording is digital silence (-120 dBFS in every 2 s window), 4 min 20 s in all.

Before the room shows, the game reads the room's files, among them `demo\rl.sdb` and `demo\rl.sh4`. The log has no error or warning about sound:

```
hakuX-native-io: open \Device\CdRom0\data\event_rl.bin -> 
hakuX-native-io: open \Device\CdRom0\data\message_room0_e.bin -> 
hakuX-native-io: open \Device\CdRom0\demo\rl.sdb -> 
hakuX-native-io: open \Device\CdRom0\data\event_rl01_cmn.bin -> 
hakuX-native-io: open \Device\CdRom0\data\event_rl01.bin -> 
hakuX-native-io: open \Device\CdRom0\data\snap_dial.bin -> 
hakuX-native-io: open \Device\CdRom0\data\rl01d.bin -> 
hakuX-native-io: open \Device\CdRom0\data\henhk.bin -> 
hakuX-native-io: open \Device\CdRom0\demo\rl.sh4 -> 
hakuX-native: fixups: DirectSound mailbox wait at 001b4a03 (DSOUND) waits on the APU (stub 800222f0)
hakuX-native: fixups: XMV's stream wait at 001ceccb (XMV) runs DirectSoundDoWork for a stopped stream too (stub 800222d0)
```

## Expected

The room's ambient sound plays.

## Notes

- The first run, with Start and A every 2.5 s throughout, is also silent in the room; the only sounds after 44 s are the pause screen's, each time Start opens or closes it.
- The view doesn't change in either run (no stick input), so footsteps and other action sounds were not tested.
