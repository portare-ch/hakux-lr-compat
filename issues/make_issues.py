# Generate per-game issue drafts and titles.tsv (file, label, title).
import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "per-game")

SETUP = """## Setup

- **hakuX-lr:** 0.19.0 release (`hakux-0.19.0-x86_64.tar.gz`, 01ded7c8eb), KVM CPU backend, default core options
- **Frontend:** RetroArch 1.22.2 on KMS (Vulkan, `khr_display`, 1920x1080), PulseAudio
- **Machine:** CachyOS, Linux 7.3.1, Ryzen 7 9800X3D, Radeon RX 9070 XT (RADV, Mesa 26.2.6)
- **Image:** `{file}`, NTSC-U, CHD (`chdman createdvd` from an XISO); XBE title ID `{tid}`
- **Run:** isolated RetroArch profile and console disk; alternating Start/A every 2.5 s from 10.5–33 s; screenshots at 10, 22 and 45 s; Quit at about 46 s. Logging: `HAKUX_LR_STATS=1 HAKUX_DISP_STATS=1`.

Observed once in a scripted 45 s pass over 77 titles; no retest or ARM64 comparison.
"""

HANG_NOTE = """All 66 KVM hang samples across 33 titles report zero general registers, so `hang vCPU` cannot locate the spinning code."""

ISSUES = []

def add(slug, label, title, file, tid, body):
    ISSUES.append((slug, label, title, SETUP.format(file=file, tid=tid) + "\n" + body.strip() + "\n"))

add("jedi-academy", "bug",
    "Star Wars: Jedi Academy: out-of-memory crash after New Game",
    "Star Wars - Jedi Knight - Jedi Academy (U) (En,Fr,De).chd", "4c41000b", """
## What happens

The LucasArts logo and the menus work. After the Difficulty menu (Jedi highlighted), the game opens its first movie. About 26 s after launch hakuX runs out of guest physical memory, an access violation follows, and the core stops. RetroArch returns to its menu.

```
hakuX-native-io: open \\Device\\CdRom0\\base\\video\\ja01_e.bik -> 
hakuX-native: vm: out of physical memory for 16 KiB at d0110000 (0 KiB free)
hakuX-native: vm: out of physical memory for 16 KiB at d0050000 (0 KiB free)
hakuX-native: vm: out of physical memory for 16 KiB at d0130000 (0 KiB free)
hakuX-native: seh: t8 access violation at 0029c694, reading 00000000: to the title's handlers
hakuX-native-frontier: stop: seh: unhandled exception c0000005 at 0029c694 (no handler took it), reading 00000000
hakuX-native-frontier: summary stage=S2 kernel_calls=929427 first_call=PsCreateSystemThreadEx threads=5
```

## Expected

The movie plays and the first level loads.

## Notes

- 0.19.0 already includes #69, the fix for Halo's level-load crash, so this is another case of guest RAM running out.
- No other title in the pass logged `out of physical memory`.
""")

add("munchs-oddysee", "bug",
    "Oddworld: Munch's Oddysee: hangs at boot (black screen, no sound)",
    "Oddworld - Munch's Oddysee (U).chd", "4d530001", """
## What happens

Nothing is drawn after the 117th frame, about 6 s after launch. All three screenshots are black and the run is silent. The core reports the guest CPU busy and the renderer idle until Quit. Quit fails to stop the core; it terminates the process after 10 s.

```
hakuX-hle-hitch: HANG started 0.50 s since frame 117: JIT compiling: 100% of the vCPU in FEX | render idle for 501 ms | vCPU cpu 500 ms halted 0% | ...
hakuX-hle-hitch: HANG ongoing 39.53 s since frame 117: JIT compiling: 99% of the vCPU in FEX | render idle for 39525 ms | vCPU cpu 39431 ms halted 0% | ... | GPU 117/117, last done 39525 ms ago | ...
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=184262 first_call=PsCreateSystemThreadEx threads=4
hakuX-libretro: vulkan: RetroArch destroyed the context: the core did not stop in 10000 ms (the devices and the renderer): ending the process
```

During the hang the guest makes about 2,300 kernel calls a second, all background: USB (`MmLockUnlockBufferPages` 1000, `KeInsertQueueDpc` 560, `MmGetPhysicalAddress` 500), `KeSetEvent` 60, and `NtReleaseMutant` / `NtWaitForSingleObjectEx` 51 each. So the spinning thread doesn't call the kernel.

## Expected

The intro and the title screen.

## Notes

- """ + HANG_NOTE + """
- Project: Snowblind and Project Gotham Racing hang the same way: the guest is busy, nothing is drawn, and only the background kernel calls are made.
""")

add("project-snowblind", "bug",
    "Project: Snowblind: hangs at boot on a grey frame",
    "Project - Snowblind (U).chd", "45530019", """
## What happens

Nothing new is drawn after the 19th frame, about 2 s after launch. All three screenshots show the same frame: a grey gradient, like a sky over a flat grey plane, with no geometry or text. The run is silent. The core reports the guest CPU busy and the renderer idle until Quit. Quit fails to stop the core; it terminates the process after 10 s.

```
hakuX-hle-hitch: HANG started 0.50 s since frame 19: JIT compiling: 99% of the vCPU in FEX | render idle for 501 ms | vCPU cpu 499 ms halted 0% | ... | GPU 19/19, last done 500 ms ago | ...
hakuX-hle-hitch: HANG ongoing 43.52 s since frame 19: JIT compiling: 99% of the vCPU in FEX | render idle for 43524 ms | vCPU cpu 43411 ms halted 0% | ...
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=98562 first_call=PsCreateSystemThreadEx threads=3
hakuX-libretro: vulkan: RetroArch destroyed the context: the core did not stop in 10000 ms (the devices and the renderer): ending the process
```

During the hang the guest makes about 2,200 kernel calls a second, all background: `MmLockUnlockBufferPages` 1000, `KeInsertQueueDpc` 560, `MmGetPhysicalAddress` 500, `KeSetEvent` 60, `KfLowerIrql` 53.

## Expected

The publisher logos and the title screen.

## Notes

- """ + HANG_NOTE + """
- Oddworld: Munch's Oddysee and Project Gotham Racing hang the same way.
""")

add("project-gotham-racing", "bug",
    "Project Gotham Racing: hangs during the intro",
    "Project Gotham Racing (U).chd", "4d530003", """
## What happens

The intro movie and the Bizarre Creations logo play. About 31 s after launch (frame 1386), on a garage shot from the intro, the game stops drawing until Quit. Sound stops earlier, about 12 s after launch. The core reports the guest CPU busy and the renderer idle. Quit fails to stop the core; it terminates the process after 10 s.

```
hakuX-hle-hitch: HANG started 0.50 s since frame 1386: JIT compiling: 100% of the vCPU in FEX | render idle for 500 ms | vCPU cpu 468 ms halted 0% | ... | GPU 1826/1826, last done 500 ms ago | ...
hakuX-hle-hitch: HANG ongoing 14.51 s since frame 1386: JIT compiling: 99% of the vCPU in FEX | render idle for 14508 ms | vCPU cpu 14442 ms halted 0% | ...
hakuX-native-frontier: stop: the front end stopped the console
hakuX-native-frontier: summary stage=S2 kernel_calls=709635 first_call=PsCreateSystemThreadEx threads=4
hakuX-libretro: vulkan: RetroArch destroyed the context: the core did not stop in 10000 ms (the devices and the renderer): ending the process
```

During the hang only background kernel calls are made (about 2,100 a second): `MmLockUnlockBufferPages` 1000, `KeInsertQueueDpc` 560, `MmGetPhysicalAddress` 500, `KeSetEvent` 60.

## Expected

The intro continues to the title screen. Project Gotham Racing 2 reached its menus in the same pass.

## Notes

- """ + HANG_NOTE + """
- Oddworld: Munch's Oddysee and Project: Snowblind hang the same way, but earlier.
""")

add("pop-sands-of-time", "bug",
    "Prince of Persia: The Sands of Time: hangs on the Bink logo",
    "Prince of Persia - The Sands of Time (U) (En,Fr,Es).chd", "5553001d", """
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

- """ + HANG_NOTE + """
""")

add("pop-two-thrones", "question",
    "Prince of Persia: The Two Thrones: title and profile screens look washed out",
    "Prince of Persia - The Two Thrones (U) (En,Fr,De,Es,It).chd", "55530058", """
## What happens

The game runs at 30 fps and reaches Create New Profile. Two screens look washed out:

- **Title screen** ("Please press START to begin"): a flat pale green-to-yellow gradient behind the logo.
- **Create New Profile:** a strong pale yellow-green wash over a faint city behind the letters.

A bright full-screen layer appears to cover the scene. Hardware or xemu comparison is pending.

## Expected

The menus as on the Xbox.

## Notes

- Prince of Persia: Warrior Within's Create New Profile screen looks washed out in a similar way.
""")

add("pop-warrior-within", "question",
    "Prince of Persia: Warrior Within: Create New Profile screen looks washed out",
    "Prince of Persia - Warrior Within (U) (En,Fr,De,Es,It).chd", "5553003b", """
## What happens

The title screen (the red logo on black) looks right. The Create New Profile screen is mostly white and light grey behind a faint red emblem, and its letters are pale grey on that light background. They are hard to read.

Not yet compared with real hardware or xemu. Screenshots can be added.

## Expected

The profile screen as on the Xbox.

## Notes

- Prince of Persia: The Two Thrones' title and profile screens look washed out in a similar way.
""")

add("far-cry-instincts", "question",
    "Far Cry Instincts: over 1,000 swaps a second, 37–57 frames shown",
    "Far Cry Instincts (U) (En,Fr,Es,It).chd", "55530008", """
## What happens

First-person gameplay on the beach renders correctly. The core counts far more swaps than it shows:

- **Swaps, `hakuX-hle-fps`, per 5 s window:** 1105.6, 1012.9, 739.3, 52.4, 1088.9, 1115.8, 1330.7, 1440.4, 1092.6
- **Shown, `hakuX-hle-disp` new frames per 10 s:** 51.2, 37.2, 56.7, 56.6

## Question

Does the game use immediate presentation, and does Xbox hardware pace it? Unpaced presents may affect CPU load or game speed; neither has been measured in gameplay.

## Notes

- Far Cry Instincts – Evolution does the same.
""")

add("far-cry-instincts-evolution", "question",
    "Far Cry Instincts – Evolution: over 1,000 swaps a second, 41–58 frames shown",
    "Far Cry Instincts - Evolution (U) (En,Fr,De,Es,It).chd", "55530060", """
## What happens

The new game and in-engine opening render correctly. The core counts far more swaps than it shows:

- **Swaps, `hakuX-hle-fps`, per 5 s window:** 1187.6, 995.0, 418.2, 740.0, 1639.1, 1086.8, 1253.9, 1370.1, 1321.2
- **Shown, `hakuX-hle-disp` new frames per 10 s:** 50.3, 40.8, 57.5, 56.3

## Question

Does the game use immediate presentation, and does Xbox hardware pace it? Unpaced presents may affect CPU load or game speed; neither has been measured in gameplay.

## Notes

- Far Cry Instincts does the same.
""")

add("call-of-cthulhu", "question",
    "Call of Cthulhu: Dark Corners of the Earth: main menu at 20 fps",
    "Call of Cthulhu - Dark Corners of the Earth (U).chd", "42530007", """
## What happens

The main menu (New Game / Options) renders correctly. The frame rate drops to a third of the refresh rate on the menu:

- **Shown, `hakuX-hle-disp` new frames per 10 s:** 32.5 and 29.5 (logo and first-run loading screen), then 19.9 and 19.9 (main menu)
- **Swaps, `hakuX-hle-fps`, per 5 s window:** 32.8, 32.7, 32.7, 25.9, then 19.9 four times

## Question

Does the Xbox menu also run at 20 fps? Hardware comparison is pending; gameplay was not reached.
""")

add("cold-fear", "question",
    "Cold Fear: black loading screen from 22 s; longer test needed",
    "Cold Fear (U) (En,Fr,De,Es,It).chd", "5553004b", """
## What happens

After the Ubisoft logo (10 s), the screen is black with only a spinning red radar icon in the top-left corner. That screen lasts from 22 s to the end of the run at 45 s. Frames keep coming (`hakuX-hle-disp`: 56.2, 44.1, 30.0, 30.0 per 10 s), and no hang is reported. Sound plays for about the first 14 s, then stops.

## Question

A longer run is needed to distinguish loading from a stall.

## Expected

The intro and the title screen.
""")

add("splinter-cell-pandora-tomorrow", "question",
    "Splinter Cell: Pandora Tomorrow: 10 s stall, then a static frame",
    "Tom Clancy's Splinter Cell - Pandora Tomorrow (U) (En,Fr,De,Es,It).chd", "55530019", """
## What happens

- **10 s:** the title screen ("Press Start to begin").
- **About 11–21 s after launch:** a 10 s stall, where nothing is drawn from frame 636.
- **22 s and 45 s:** both screenshots show the same still image, a harbour at sunset with no menu text. Sound plays for the whole run, apart from a gap at about 6–10 s.

```
hakuX-hle-hitch: HANG started 0.50 s since frame 636: JIT compiling: 55% of the vCPU in FEX | render idle for 501 ms | vCPU cpu 354 ms ...
hakuX-hle-hitch: HANG ongoing 9.51 s since frame 636: ...
```

## Question

A longer run is needed to identify the still image and determine whether the 10 s first-boot stall is expected (for example, save-data creation).

## Expected

The main menu after Start.
""")

with open(os.path.join(HERE, "titles.tsv"), "w") as t:
    for slug, label, title, body in ISSUES:
        with open(os.path.join(OUT, slug + ".md"), "w") as f:
            f.write(body)
        t.write(f"{slug}\t{label}\t{title}\n")
print(len(ISSUES))
