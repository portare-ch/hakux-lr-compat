#!/usr/bin/env python3
"""Drive a virtual gamepad through /dev/uinput using stdin commands.
Requires write access to /dev/uinput.

  down <buttons...>   press and hold
  up <buttons...>     release
  tap <button> [ms]   press for 150 ms by default, then release
  release            release all buttons and centre sticks and triggers
  quit               remove the device and exit

Replies: "ok" or "err <reason>". Unknown lines are ignored, including a
password left on stdin by sudo -S.
Buttons: a b x y lb rb back start guide ls rs up down left right lt rt.
Gamepad events avoid sending keyboard input to the active KMS console."""
import fcntl
import os
import struct
import sys
import time

NAME = b"hakuX compat pad"
VENDOR, PRODUCT = 0x1209, 0x7778  # pid.codes test range

EV_SYN, EV_KEY, EV_ABS = 0, 1, 3
BTN = {
    "a": 0x130, "b": 0x131, "x": 0x133, "y": 0x134,
    "lb": 0x136, "rb": 0x137, "back": 0x13A, "start": 0x13B,
    "guide": 0x13C, "ls": 0x13D, "rs": 0x13E,
}
# axis code: (min, max, resting value)
ABS = {
    0x00: (-32768, 32767, 0), 0x01: (-32768, 32767, 0),  # left stick
    0x02: (0, 255, 0),                                   # left trigger
    0x03: (-32768, 32767, 0), 0x04: (-32768, 32767, 0),  # right stick
    0x05: (0, 255, 0),                                   # right trigger
    0x10: (-1, 1, 0), 0x11: (-1, 1, 0),                  # d-pad hat
}
HAT = {"up": (0x11, -1), "down": (0x11, 1), "left": (0x10, -1), "right": (0x10, 1)}
TRIGGER = {"lt": 0x02, "rt": 0x05}

UI_SET_EVBIT, UI_SET_KEYBIT, UI_SET_ABSBIT = 0x40045564, 0x40045565, 0x40045567
UI_DEV_CREATE, UI_DEV_DESTROY = 0x5501, 0x5502


def open_device():
    fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
    for ev in (EV_KEY, EV_ABS):
        fcntl.ioctl(fd, UI_SET_EVBIT, ev)
    for code in BTN.values():
        fcntl.ioctl(fd, UI_SET_KEYBIT, code)
    absmax, absmin = [0] * 64, [0] * 64
    for code, (lo, hi, _) in ABS.items():
        fcntl.ioctl(fd, UI_SET_ABSBIT, code)
        absmin[code], absmax[code] = lo, hi
    dev = struct.pack("80sHHHHI", NAME, 0x03, VENDOR, PRODUCT, 1, 0)
    dev += struct.pack("64i", *absmax) + struct.pack("64i", *absmin)
    dev += struct.pack("64i", *([0] * 64)) * 2  # fuzz, flat
    os.write(fd, dev)
    fcntl.ioctl(fd, UI_DEV_CREATE)
    return fd


def main():
    fd = open_device()
    held = set()

    def emit(t, c, v):
        os.write(fd, struct.pack("llHHi", 0, 0, t, c, v))

    def sync():
        emit(EV_SYN, 0, 0)

    def set_btn(name, on):
        if name in BTN:
            emit(EV_KEY, BTN[name], 1 if on else 0)
        elif name in HAT:
            code, v = HAT[name]
            emit(EV_ABS, code, v if on else 0)
        elif name in TRIGGER:
            emit(EV_ABS, TRIGGER[name], 255 if on else 0)
        else:
            raise KeyError(name)
        (held.add if on else held.discard)(name)

    def release_all():
        for code in BTN.values():
            emit(EV_KEY, code, 0)
        for code, (_, _, rest) in ABS.items():
            emit(EV_ABS, code, rest)
        held.clear()
        sync()

    release_all()
    print("ready", flush=True)
    for line in sys.stdin:
        words = line.split()
        if not words:
            continue
        cmd, args = words[0], words[1:]
        try:
            if cmd == "down":
                for b in args:
                    set_btn(b, True)
                sync()
            elif cmd == "up":
                for b in args:
                    set_btn(b, False)
                sync()
            elif cmd == "tap":
                ms = int(args[1]) if len(args) > 1 else 150
                set_btn(args[0], True)
                sync()
                time.sleep(ms / 1000)
                set_btn(args[0], False)
                sync()
            elif cmd == "release":
                release_all()
            elif cmd == "quit":
                release_all()
                break
            else:
                continue
            print("ok", flush=True)
        except (KeyError, IndexError, ValueError) as e:
            print(f"err {cmd} {e}", flush=True)
    time.sleep(0.05)
    fcntl.ioctl(fd, UI_DEV_DESTROY)
    os.close(fd)


if __name__ == "__main__":
    main()
