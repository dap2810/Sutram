#!/usr/bin/env python3
"""ROUND-33: a malformed-input fuzzer for sutram-elf2smo, the FFI's ELF reader.

A foreign object is untrusted input to a NASM program that does pointer arithmetic on
it. Starting from good objects (tests/r32/foreign.o, tests/r33/kinds.o), this writes
mutated copies - random byte flips, targeted corruption of the fields the reader trusts
least (the ELF header, every section header's offset, size, link and info, every symbol's
name, section, value and size, every relocation's offset, info and addend; huge values,
off-by-one values, zero), and truncations - and runs the reader on each, with a timeout.

The contract, for every input:
  * it ends by itself: no signal (no crash), no hang;
  * exit 0 or 1, nothing else;
  * exit 1 (a refusal): NO output file is written;
  * exit 0: the output is a well-formed SUTRAMO1 object whose code, symbols and (zero)
    relocations fit exactly in the file, and every symbol lies inside the code.

usage: python3 -B tools/fuzz_elf2smo.py [--seed N] [--count N] [--elf2smo E] [--out DIR]
Linux only. No network. Exit 0 when every input met the contract.
"""
from __future__ import annotations

import argparse
import random
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SEEDS = ['tests/r32/foreign.o', 'tests/r33/kinds.o']
NASTY64 = [0, 1, 7, 8, 63, 64, 65, 0xFFFF, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 1 << 32,
           (1 << 63) - 1, 1 << 63, (1 << 64) - 64, (1 << 64) - 1]


def smo_ok(data):
    """A well-formed SUTRAMO1 object: every table fits, the file ends after the last."""
    if len(data) < 32 or data[:8] != b'SUTRAMO1':
        return False
    code, nsym, nrel = struct.unpack_from('<3Q', data, 8)
    pos = 32 + code
    if pos > len(data):
        return False
    for n, need_in_code in ((nsym, True), (nrel, True)):
        for _ in range(n):
            if pos + 16 > len(data):
                return False
            off, ln = struct.unpack_from('<2Q', data, pos)
            pos += 16 + ln
            if pos > len(data) or (need_in_code and off > code):
                return False
    return pos == len(data)


def fields(elf):
    """(offset, width) of the fields worth corrupting in this ELF."""
    out = [(4, 1), (5, 1), (6, 1), (16, 2), (18, 2), (40, 8), (56, 2), (58, 2), (60, 2), (62, 2)]
    shoff, = struct.unpack_from('<Q', elf, 40)
    shnum, = struct.unpack_from('<H', elf, 60)
    for i in range(shnum):
        h = shoff + 64 * i
        if h + 64 > len(elf):
            break
        out += [(h + 4, 4), (h + 8, 8), (h + 24, 8), (h + 32, 8), (h + 40, 4), (h + 44, 4), (h + 48, 8), (h + 56, 8)]
        typ, = struct.unpack_from('<I', elf, h + 4)
        off, size = struct.unpack_from('<QQ', elf, h + 24)
        if typ == 2:                                  # symbols
            for s in range(off, off + size, 24):
                out += [(s, 4), (s + 4, 1), (s + 5, 1), (s + 6, 2), (s + 8, 8), (s + 16, 8)]
        if typ == 4:                                  # relocations
            for r in range(off, off + size, 24):
                out += [(r, 8), (r + 8, 4), (r + 12, 4), (r + 16, 8)]
    return [(o, w) for o, w in out if o + w <= len(elf)]


def mutate(rng, elf, fl):
    b = bytearray(elf)
    k = rng.randrange(10)
    if k < 6:                                         # a targeted field
        for _ in range(rng.randint(1, 2)):
            o, w = rng.choice(fl)
            v = rng.choice(NASTY64 + [rng.getrandbits(64), int.from_bytes(b[o:o + w], 'little') + rng.choice((-1, 1))])
            b[o:o + w] = (v % (1 << (8 * w))).to_bytes(w, 'little')
    elif k < 9:                                       # random bytes
        for _ in range(rng.randint(1, 8)):
            b[rng.randrange(len(b))] = rng.randrange(256)
    else:                                             # truncation
        del b[rng.randrange(len(b)):]
    return bytes(b)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=33)
    ap.add_argument('--count', type=int, default=2000)
    ap.add_argument('--elf2smo', default=str(ROOT / 'sutram-elf2smo'))
    ap.add_argument('--out', default=None)
    a = ap.parse_args(argv)
    out = Path(a.out or tempfile.mkdtemp(prefix='fuzz-elf2smo-'))
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(a.seed)
    seeds = [(ROOT / s).read_bytes() for s in SEEDS]
    fls = [fields(s) for s in seeds]
    accepted = refused = bad = 0
    for n in range(a.count):
        k = rng.randrange(len(seeds))
        data = mutate(rng, seeds[k], fls[k])
        src, dst = out / 'in.o', out / 'out.smo'
        src.write_bytes(data)
        dst.unlink(missing_ok=True)
        why = None
        try:
            r = subprocess.run([a.elf2smo, str(src), str(dst)], capture_output=True, timeout=5)
            if r.returncode < 0:
                why = f'signal {-r.returncode}'
            elif r.returncode == 1:
                refused += 1
                if dst.exists():
                    why = 'refused, but wrote an object'
            elif r.returncode == 0:
                accepted += 1
                if not dst.exists() or not smo_ok(dst.read_bytes()):
                    why = 'accepted, but the object is not well formed'
            else:
                why = f'exit {r.returncode}'
        except subprocess.TimeoutExpired:
            why = 'hang'
        if why:
            bad += 1
            keep = out / f'bad-{n}.o'
            keep.write_bytes(data)
            if bad <= 5:
                print(f'BAD {keep.name}: {why}')
    print(f'fuzz_elf2smo: seed {a.seed}, {a.count} malformed objects: {refused} refused (no output), '
          f'{accepted} accepted (well formed), {bad} broke the contract')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
