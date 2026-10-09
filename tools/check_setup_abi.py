#!/usr/bin/env python3
"""Static Win64 ABI check for sutram_setup.asm.

Verifies, per function, that every stack slot written for a Windows call
argument ([rsp+K], K >= 32) lies inside the frame the PROLOG reserved, and
that the frame is at least 32 bytes of shadow space.  A frame smaller than
the largest K+8 silently corrupts the saved RBP / return address.
"""
import re, sys

PATH = "/scratch/work/windows/native-installer/sutram_setup.asm"

def main():
    lines = open(PATH, encoding="utf-8").read().splitlines()
    # Split into functions on top-level labels.
    funcs = []
    cur = None
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*$", ln)
        if m:
            cur = {"name": m.group(1), "line": i, "frame": None, "slots": []}
            funcs.append(cur)
            continue
        if cur is None:
            continue
        mp = re.match(r"\s*PROLOG\s+(\d+)", ln)
        if mp:
            cur["frame"] = int(mp.group(1))
        ms = re.search(r"\[\s*rsp\s*\+\s*(\d+)\s*\]", ln)
        if ms:
            cur["slots"] = cur["slots"] + [(int(ms.group(1)), i)]

    bad = 0
    print(f"{'function':22} {'frame':>6} {'max slot':>9}  verdict")
    print("-" * 56)
    for f in funcs:
        if f["frame"] is None:
            continue
        maxk = max((k for k, _ in f["slots"]), default=-1)
        if f["frame"] < 32:
            verdict = "FAIL: no 32-byte shadow space"
            bad += 1
        elif maxk >= 0 and (maxk + 8) > f["frame"]:
            verdict = f"FAIL: writes [rsp+{maxk}] but frame is only {f['frame']}"
            bad += 1
        else:
            verdict = "ok"
        print(f"{f['name']:22} {f['frame']:>6} {maxk:>9}  {verdict}")

    # Entry-point alignment: a PE entry arrives 16-byte aligned with no return
    # address, so _start must normalise RSP before any PROLOG or call.
    print()
    entry = next((f for f in funcs if f["name"] == "_start"), None)
    if entry is not None:
        head = "\n".join(lines[entry["line"] - 1: entry["line"] + 8])
        normalised = re.search(r"and\s+rsp\s*,\s*-?16", head) is not None
        if not normalised:
            print("FAIL: _start does not normalise RSP (needs `and rsp,-16` "
                  "before the frame) -> every API call is misaligned.")
            bad += 1
        else:
            print("Entry point normalises RSP before its frame: ok")

    print()
    if bad:
        print(f"{bad} ABI problem(s) found.")
        return 1
    print("All frames cover their stack arguments; shadow space present.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
