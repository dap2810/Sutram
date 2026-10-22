#!/usr/bin/env python3
"""ROUND-35: sutram-coff2smo, the Windows FFI's COFF reader - on either host.

The reader builds for Linux (sutram-coff2smo) and Windows (sutram-coff2smo.exe) from one
source, like sutram-link. This test runs whichever one this host has:

  1. THE SAME BYTES ON BOTH HOSTS: tests/r35/winffi.obj (C compiled for Windows, committed)
     converts to exactly the SUTRAMO2 object below - the hash the Windows build gave. On
     Linux this is the cross-host check.
  2. WHAT IS IN IT: SUTRAMO2, 22 functions, no relocation left (all resolved in the reader).
  3. THE REFUSALS: a C function that calls out, writable data, a pointer table (a relocation
     in data), unwind tables, a file that is not COFF, a truncated object, a missing file:
     exit 1, no output; and its usage: exit 2.

No network, no C compiler. The Windows gate that runs the program is tests/r35/test_ffi_windows.py.
usage: python -B tests/r35/test_coff2smo.py [--coff2smo PATH]
"""
from __future__ import annotations

import hashlib
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WINFFI_SMO_SHA256 = 'cc0be81e75b107e1b27576a928f81c53d375deb36f123a11ae36cb960d01bf12'
NAMES = ['w_zero', 'w_one', 'w_four', 'w_five', 'w_six', 'w_mixed', 'w_fmix', 'w_i3f', 'w_mix6', 'w_f4',
         'w_f6', 'w_neg', 'w_abs', 'w_trunc', 'w_strlen', 'w_sum', 'w_fsum', 'w_set', 'w_nothing',
         'w_align', 'w_shadow', 'w_clobber']


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def main(argv) -> int:
    c2s = arg(argv, '--coff2smo', str(ROOT / ('sutram-coff2smo.exe' if os.name == 'nt' else 'sutram-coff2smo')))
    fails = checks = 0

    def check(ok, what):
        nonlocal fails, checks
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    def run(cmd):
        return subprocess.run([str(c) for c in cmd], capture_output=True, timeout=60)

    with tempfile.TemporaryDirectory(prefix='r35c-') as td:
        t = Path(td)
        r = run([c2s, HERE / 'winffi.obj', t / 'w.smo'])
        data = (t / 'w.smo').read_bytes() if (t / 'w.smo').exists() else b''
        digest = hashlib.sha256(data).hexdigest()
        check(r.returncode == 0 and digest == WINFFI_SMO_SHA256,
              'winffi.obj -> SUTRAMO2, the same bytes as the Windows build (%s) %r' % (digest[:16], r.stdout[-60:]))
        names = []
        if data[:8] == b'SUTRAMO2':
            code, nsym, nrel = struct.unpack_from('<3Q', data, 8)
            pos = 32 + code
            for _ in range(nsym):
                _off, ln = struct.unpack_from('<2Q', data, pos)
                names.append(data[pos + 16:pos + 16 + ln].decode())
                pos += 16 + ln
            check(nrel == 0 and pos == len(data), 'no relocation left, and the file ends after the last symbol')
        check(names == NAMES, '22 functions, in order: %r' % names[:4])
        for name, src, want in [('calls out', 'callout.obj', b'agyat sanket: elsewhere'),
                                ('writable data', 'writable.obj', b'bhara-khandam asamarthitam'),
                                ('a pointer table (relocation in data)', 'dataptr.obj', b'punahsthapanam asamarthitam'),
                                ('unwind tables', 'winffi-unwind.obj', b'.pdata/.xdata'),
                                ('not COFF', 'winffi.sm', b'COFF x64 vastu-patram na')]:
            out = t / 'c.smo'
            if out.exists():
                out.unlink()
            r = run([c2s, HERE / src, out])
            check(r.returncode == 1 and not out.exists() and want in r.stdout, 'refuses %s %r' % (name, r.stdout[-70:]))
        (t / 'trunc.obj').write_bytes((HERE / 'winffi.obj').read_bytes()[:300])
        r = run([c2s, t / 'trunc.obj', t / 'c.smo'])
        check(r.returncode == 1 and not (t / 'c.smo').exists() and b'khanditam' in r.stdout, 'refuses a truncated object')
        r = run([c2s, t / 'nope.obj', t / 'c.smo'])
        check(r.returncode == 1 and b'patram na udghatitam' in r.stdout, 'a missing file')
        r = run([c2s])
        check(r.returncode == 2 and b'Prayog' in r.stdout, 'usage')
    print('r35 coff2smo: %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
