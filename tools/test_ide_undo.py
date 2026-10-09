#!/usr/bin/env python3
"""Undo (Ctrl-Z) regression test for the Sutram IDE.

Drives the real binary through a PTY, then saves and reads the file back. The
file is the source of truth: an earlier version of this test read the
reconstructed screen and reported false failures, because the screen parser did
not reflect the final render. Save-then-read has no such ambiguity.

Run: python3 tools/test_ide_undo.py
"""
import os, sys, tempfile, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ide_test import run                      # noqa: E402

CTRL_Z = b"\x1a"
CTRL_S = b"\x13"
CTRL_Q = b"\x11"
BACKSPACE = b"\x7f"

# (typed, number of undos, extra keys after the undos, expected file contents)
CASES = [
    ("c",    1, b"",  "AB"),
    ("cd",   1, b"",  "cAB"),
    ("cd",   2, b"",  "AB"),
    ("cde",  1, b"",  "cdAB"),
    ("cde",  2, b"",  "cAB"),
    ("cde",  3, b"",  "AB"),
    ("cdef", 2, b"",  "cdAB"),
    ("",     1, b"",  "AB"),          # undo with empty history is a no-op
    ("",     3, b"",  "AB"),
    ("c",    1, b"X", "XAB"),         # typing still works after an undo
    ("cd",   0, b"X", "cdXAB"),       # control: typing without undo
    ("",     1, b"X", "XAB"),         # Ctrl-Z must not suspend the process
]

if __name__ == "__main__":
    fails = 0
    for typed, undos, extra, want in CASES:
        fd, path = tempfile.mkstemp(suffix=".sm")
        os.close(fd)
        with open(path, "w") as f:
            f.write("AB\n")
        keys = [t.encode() for t in typed] + [CTRL_Z] * undos
        if extra:
            keys.append(extra)
        keys += [CTRL_S, CTRL_Q]
        run(keys, path)
        time.sleep(0.15)
        got = open(path).read().rstrip("\n")
        os.unlink(path)
        ok = got == want
        if not ok:
            fails += 1
        label = f"type {typed!r} x{undos}" + (f" then {extra!r}" if extra else "")
        print(f"  {'PASS' if ok else 'FAIL'}  {label:26s} -> {got!r}"
              + ("" if ok else f"  (expected {want!r})"))
    print(f"\n  {len(CASES) - fails}/{len(CASES)} undo cases pass")
    sys.exit(1 if fails else 0)
