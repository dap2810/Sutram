#!/usr/bin/env python3
"""ROUND-28: print a Sutram object file (.smo) - its header, symbols and holes.

The format is docs/OBJECT-FORMAT.md. This is a reader for people; the linker
(linker/sutram_link.asm) is the reader the build uses.

usage: python3 -B tools/smo_dump.py file.smo
"""
import struct
import sys


def read(path):
    d = open(path, 'rb').read()
    if len(d) < 32 or d[:8] != b'SUTRAMO1':
        raise SystemExit('%s: not a Sutram object (no SUTRAMO1 magic)' % path)
    code_size, nsym, nrel = struct.unpack_from('<3Q', d, 8)
    p = 32 + code_size

    def entries(n):
        nonlocal p
        out = []
        for _ in range(n):
            off, ln = struct.unpack_from('<2Q', d, p)
            out.append((off, d[p + 16:p + 16 + ln].decode('utf-8', 'replace')))
            p += 16 + ln
        return out
    syms, rels = entries(nsym), entries(nrel)
    if p != len(d):
        raise SystemExit('%s: %d bytes left over after the tables' % (path, len(d) - p))
    return code_size, syms, rels


def main(argv):
    code_size, syms, rels = read(argv[0])
    print('SUTRAMO1  code %d bytes, %d symbols, %d relocations' % (code_size, len(syms), len(rels)))
    for off, name in syms:
        print('  defines  %-28s at code+%d' % (name, off))
    for off, name in rels:
        print('  needs    %-28s rel32 at code+%d' % (name, off))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
