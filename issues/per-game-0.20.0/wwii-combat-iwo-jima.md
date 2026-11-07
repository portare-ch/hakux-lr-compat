## Setup

- **hakuX-lr:** 0.20.0 release (`linux-v0.20.0`, 16440f4dba), x86_64 core, KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 in headless gamescope (Vulkan, 1920x1080); audio to a PulseAudio null sink, recorded
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `World War II Combat - Iwo Jima (U).chd`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `4756000b`
- **Run:** isolated RetroArch profile and console disk; pad input through RetroArch's network RetroPad: Start and A alternately every 2.5 s from 10.5 s. A screenshot every 20 s from 30 s; a run lasts up to 5 min. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.
- **Result:** [result.json](https://github.com/portare-ch/hakux-lr-compat/blob/main/runs/amd64-linux-20261106-0.20.0/world-war-ii-combat-iwo-jima-u/result.json) in the [compatibility list](https://hakuxlr.portareos.org)

## What happens

After the ESRB notice, from 30 s to Quit at 300 s, the game shows its name keyboard over the battleship movie at 60 fps, with sound. The name reads `Player1` and the cursor is on the `1` key. The on-screen hints say A Select, B Back, X Caps Lock, START Done. The game takes no input on this screen: after 57 Start and 57 A presses the name, the cursor and the screen are unchanged in every screenshot up to 290 s.

The Start presses reach the emulated pad on port 1 (the log shows each one; it doesn't log the analog A button). The game polled all four ports at boot. Its last file access is opening its `UDATA\4756000b` save folder at about 15 s. After that, the log shows only the steady per-second stats: about 2,650 kernel calls a second, mostly `MmLockUnlockBufferPages`, `KeInsertQueueDpc` and `MmGetPhysicalAddress`, and 500 USB transfers a second.

```
hakuX-native-usb: gamepad 0: polled
hakuX-native-usb: gamepad 1: polled
hakuX-native-usb: gamepad 2: polled
hakuX-native-usb: gamepad 3: polled
...
hakuX-native-io: open \Device\Harddisk0\partition1\UDATA\4756000b -> dir 
hakuX-native-usb: ohci: 5000 TDs in 10 s, ctl 000000be (lists PCB), hcca 03fe8000, intr 00000004/80000073
hakuX-native-usb: gamepad 0: buttons 0000 -> 0010 (A 00)
hakuX-native-usb: gamepad 0: buttons 0010 -> 0000 (A 00)
hakuX-native-stats: per s: kcalls 2653 ... | MmLockUnlockBufferPages:1006 KeInsertQueueDpc:625 MmGetPhysicalAddress:516 RtlNtStatusToDosError:123 ExQueryNonVolatileSetting:120 RtlTimeToTimeFields:120
```

## Expected

A types the highlighted character and Start confirms the name, leading to the main menu.

## Notes

- World War II Combat - Road to Berlin (`47560009`, same publisher and engine) stops on the same keyboard the same way.
- Start and A work in other titles in this run.
- The d-pad and the other buttons weren't tried.
- Seen in one run; there is no result from an earlier version.
