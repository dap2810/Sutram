#!/usr/bin/env python3
"""ROUND-35: a malformed-input fuzzer for sutram-coff2smo, the Windows FFI's COFF reader.

The same contract as tools/fuzz_elf2smo.py, for COFF. A foreign object is untrusted input
to a NASM program that does pointer arithmetic on it. Starting from good objects
(tests/r35/winffi.obj, and the refused ones beside it), this writes mutated copies - random
byte flips, targeted corruption of the fields the reader trusts (the file header; every
section header's sizes, pointers, relocation count and characteristics; every symbol's
name, value, section, class and aux count; every relocation's offset, symbol and type;
the string table's size; huge, off-by-one and zero values), and truncations - and runs the
reader on each, with a timeout.

The contract, for every input:
  * it ends by itself: no crash (a signal on Linux, an exception status on Windows), no hang;
  * exit 0 or 1, nothing else;
  * exit 1 (a refusal): NO output file is written;
  * exit 0: the output is a well-formed SUTRAMO2 object whose code, symbols and (zero)
    relocations fit exactly in the file, and every symbol lies inside the code.

usage: python -B tools/fuzz_coff2smo.py [--seed N] [--count N] [--coff2smo C] [--out DIR]
Linux or Windows (the reader builds for both). No network. Exit 0 when every input met the contract.
"""
from __future__ import annotations

import argparse
import os
import random
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SEEDS = ['tests/r35/winffi.obj', 'tests/r35/callout.obj', 'tests/r35/writable.obj',
         'tests/r35/dataptr.obj', 'tests/r35/winffi-unwind.obj']
NASTY32 = [0, 1, 2, 3, 4, 5, 9, 10, 17, 18, 39, 40, 0x7F, 0x80, 0xFF, 0x100, 0x7FFF, 0x8000,
           0xFFFF, 0x10000, 0x7FFFFFFF, 0x80000000, 0xFFFFFFF0, 0xFFFFFFFF]


def smo_ok(data):
    """A well-formed SUTRAMO2 object: every table fits, the file ends after the last."""
    if len(data) < 32 or data[:8] != b'SUTRAMO2':
        return False
    code, nsym, nrel = struct.unpack_from('<3Q', data, 8)
    pos = 32 + code
    if pos > len(data):
        return False
    for n in (nsym, nrel):
        for _ in range(n):
            if pos + 16 > len(data):
                return False
            off, ln = struct.unpack_from('<2Q', data, pos)
            pos += 16 + ln
            if pos > len(data) or off > code:
                return False
    return pos == len(data)


def fields(coff):
    """(offset, width) of the fields worth corrupting in this COFF object."""
    out = [(0, 2), (2, 2), (8, 4), (12, 4), (16, 2), (18, 2)]
    nsec, = struct.unpack_from('<H', coff, 2)
    symptr, nsym = struct.unpack_from('<II', coff, 8)
    for i in range(nsec):
        h = 20 + 40 * i
        if h + 40 > len(coff):
            break
        out += [(h, 8), (h + 16, 4), (h + 20, 4), (h + 24, 4), (h + 32, 2), (h + 36, 4)]
        rel, = struct.unpack_from('<I', coff, h + 24)
        nrel, = struct.unpack_from('<H', coff, h + 32)
        for r in range(rel, rel + 10 * nrel, 10):
            out += [(r, 4), (r + 4, 4), (r + 8, 2)]
    for s in range(symptr, symptr + 18 * nsym, 18):
        out += [(s, 4), (s + 4, 4), (s + 8, 4), (s + 12, 2), (s + 16, 1), (s + 17, 1)]
    out += [(symptr + 18 * nsym, 4)]                  # the string table's size
    return [(o, w) for o, w in out if o + w <= len(coff)]


def mutate(rng, coff, fl):
    b = bytearray(coff)
    k = rng.randrange(10)
    if k < 6:                                         # a targeted field
        for _ in range(rng.randint(1, 2)):
            o, w = rng.choice(fl)
            v = rng.choice(NASTY32 + [rng.getrandbits(32), int.from_bytes(b[o:o + w], 'little') + rng.choice((-1, 1))])
            b[o:o + w] = (v % (1 << (8 * w))).to_bytes(w, 'little')
    elif k < 9:                                       # random bytes
        for _ in range(rng.randint(1, 8)):
            b[rng.randrange(len(b))] = rng.randrange(256)
    else:                                             # truncation
        del b[rng.randrange(len(b)):]
    return bytes(b)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=35)
    ap.add_argument('--count', type=int, default=2000)
    ap.add_argument('--coff2smo', default=str(ROOT / ('sutram-coff2smo.exe' if os.name == 'nt' else 'sutram-coff2smo')))
    ap.add_argument('--out', default=None)
    a = ap.parse_args(argv)
    out = Path(a.out or tempfile.mkdtemp(prefix='fuzz-coff2smo-'))
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(a.seed)
    seeds = [(ROOT / s).read_bytes() for s in SEEDS]
    fls = [fields(s) for s in seeds]
    accepted = refused = bad = 0
    for n in range(a.count):
        k = rng.randrange(len(seeds))
        data = mutate(rng, seeds[k], fls[k])
        src, dst = out / 'in.obj', out / 'out.smo'
        src.write_bytes(data)
        if dst.exists():
            dst.unlink()
        why = None
        try:
            r = subprocess.run([a.coff2smo, str(src), str(dst)], capture_output=True, timeout=5)
            if r.returncode == 1:
                refused += 1
                if dst.exists():
                    why = 'refused, but wrote an object'
            elif r.returncode == 0:
                accepted += 1
                if not dst.exists() or not smo_ok(dst.read_bytes()):
                    why = 'accepted, but the object is not well formed'
            elif r.returncode < 0:
                why = f'signal {-r.returncode}'
            else:
                why = f'exit {r.returncode:#x}' if r.returncode > 255 else f'exit {r.returncode}'
        except subprocess.TimeoutExpired:
            why = 'hang'
        if why:
            bad += 1
            keep = out / f'bad-{n}.obj'
            keep.write_bytes(data)
            if bad <= 5:
                print(f'BAD {keep.name}: {why}')
    print(f'fuzz_coff2smo: seed {a.seed}, {a.count} malformed objects: {refused} refused (no output), '
          f'{accepted} accepted (well formed), {bad} broke the contract')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
