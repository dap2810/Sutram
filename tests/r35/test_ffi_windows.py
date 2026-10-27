#!/usr/bin/env python3
"""ROUND-35: the FFI on Windows - the Microsoft x64 ABI (ChatGPT ROUND-100-WS3). Run on Windows.

  1. IT WORKS: tests/r35/winffi.sm calls 22 C functions in tests/r35/winffi.obj (C compiled
     for Windows, read by sutram-coff2smo) and prints exactly tests/r35/winffi.expect: 0, 1,
     4, 5 and 6 integer arguments (5 and 6 on the stack above the shadow space); doubles and
     integers MIXED, which go by overall POSITION (f(i64, f64, i64, f64): rcx, xmm1, r8, xmm3
     - the case a port keeping System V's rule gets wrong without crashing); six mixed (two on
     the stack); four and six doubles; 16-byte constants (xorpd: the object must be aligned);
     a string and a kosh as ptr; a void statement; rsp = 8 mod 16 at the callee's entry; a
     callee that writes over all 32 bytes of its shadow space; a callee that destroys every
     volatile register; foreign calls nested in expressions and inside a prakriya's live locals.
  2. THROUGH THE BUILDER: tools/sutram_build.py --ffi --foreign winffi.obj gives the same output.
  3. THE SIDECAR: windows-x86_64-msabi only under v2, and only for a PE target; sysv on the
     Windows compiler, msabi under v1, a near-miss ABI name, v3, arity 7: each refused at its
     line, exit 1, no object. --ffi without --object is a usage error (the usage text, no
     output - the compiler's usage path exits 0, as on Linux), and the ordinary compile of
     winffi.sm reads no sidecar (agyat prakriya).
  4. THE READER: sutram-coff2smo refuses a C function that calls out, writable data, a pointer
     table (a relocation in data), unwind tables, a file that is not COFF, a truncated object,
     a missing file (exit 1, no output) and its usage (exit 2).
  5. OPT-IN: a program that uses no FFI compiles to the same bytes with and without the FFI
     existing - see the ordinary-path guard in the delivery (562 programs, 0 differ).

Windows only. No network, no C compiler (the .obj files are committed: tests/r35/OBJECTS.md).
usage: python -B tests/r35/test_ffi_windows.py [--compiler C] [--linker L] [--coff2smo R]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def main(argv) -> int:
    if os.name != 'nt':
        print('r35 ffi (Windows): NOT-RUN - this gate runs on Windows')
        return 0
    comp = arg(argv, '--compiler', str(ROOT / 'sutram.exe'))
    link = arg(argv, '--linker', str(ROOT / 'sutram-link.exe'))
    c2s = arg(argv, '--coff2smo', str(ROOT / 'sutram-coff2smo.exe'))
    fails = checks = 0

    def check(ok, what):
        nonlocal fails, checks
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)
        return ok

    def run(cmd, **kw):
        return subprocess.run([str(c) for c in cmd], capture_output=True, timeout=120, **kw)

    want = (HERE / 'winffi.expect').read_bytes().replace(b'\r\n', b'\n')
    with tempfile.TemporaryDirectory(prefix='r35-') as td:
        t = Path(td)
        # 1. it works
        r1 = run([c2s, HERE / 'winffi.obj', t / 'w.smo'])
        r2 = run([comp, '--ffi', HERE / 'winffi.sffi', '--object', HERE / 'winffi.sm', t / 'm.smo'])
        r3 = run([link, t / 'm.exe', t / 'm.smo', t / 'w.smo'])
        ok = check(r1.returncode == 0 and r2.returncode == 0 and r3.returncode == 0,
                   'build: coff2smo %d, compile %d, link %d %r' % (r1.returncode, r2.returncode, r3.returncode,
                                                                  (r1.stdout + r2.stdout + r3.stdout)[-160:]))
        if ok:
            p = run([t / 'm.exe'])
            got = p.stdout.replace(b'\r\n', b'\n')
            check(p.returncode == 0 and got == want, 'winffi.sm prints winffi.expect exactly (%d lines), exit %d'
                  % (want.count(b'\n'), p.returncode))
            if got != want:
                for i, (a, b) in enumerate(zip(want.split(b'\n'), got.split(b'\n'))):
                    if a != b:
                        print('      line %d: expected %r, got %r' % (i + 1, a, b))
                        break
        # 2. the builder
        r = run([sys.executable, '-B', ROOT / 'tools' / 'sutram_build.py', '--compiler', comp, '--linker', link,
                 '--coff2smo', c2s, '--ffi', HERE / 'winffi.sffi', '--foreign', HERE / 'winffi.obj',
                 HERE / 'winffi.sm', '-o', t / 'b.exe'])
        if check(r.returncode == 0, 'sutram_build.py --ffi --foreign winffi.obj: %r' % (r.stdout + r.stderr)[-160:]):
            p = run([t / 'b.exe'])
            check(p.returncode == 0 and p.stdout.replace(b'\r\n', b'\n') == want, 'the builder\'s program prints the same')
        # 3. the sidecar
        (t / 'one.sm').write_text('mukhya() {\n    likha(w_one(2))\n}\n', newline='\n')
        decl = 'w_one|1|i64|i64|w_one\n'
        cases = [
            ('sysv on the Windows compiler', 'sutram-ffi-v2|linux-x86_64-sysv\n' + decl, 1),
            ('msabi under v1', 'sutram-ffi-v1|windows-x86_64-msabi\n' + decl, 1),
            ('a near-miss ABI name', 'sutram-ffi-v2|windows-x86_64-ms\n' + decl, 1),
            ('a longer ABI name', 'sutram-ffi-v2|windows-x86_64-msabiX\n' + decl, 1),
            ('v3', 'sutram-ffi-v3|windows-x86_64-msabi\n' + decl, 1),
            ('arity 7', 'sutram-ffi-v2|windows-x86_64-msabi\nw_one|7|i64,i64,i64,i64,i64,i64,i64|i64|w_one\n', 2),
        ]
        for name, text, line in cases:
            (t / 's.sffi').write_text(text, newline='\n')
            out = t / 'o.smo'
            if out.exists():
                out.unlink()
            r = run([comp, '--ffi', t / 's.sffi', '--object', t / 'one.sm', out])
            check(r.returncode == 1 and not out.exists() and (b'pankti %d' % line) in r.stdout,
                  'sidecar refused: %s (line %d, no object) %r' % (name, line, r.stdout[-90:]))
        (t / 's.sffi').write_text('sutram-ffi-v2|windows-x86_64-msabi\n' + decl, newline='\n')
        r = run([comp, '--ffi', t / 's.sffi', '--object', t / 'one.sm', t / 'ok.smo'])
        check(r.returncode == 0 and (t / 'ok.smo').read_bytes()[:8] == b'SUTRAMO2', 'the same, msabi under v2: accepted')
        # opt-in, as tests/r32/test_ffi.py checks it on Linux: the usage text and no output
        r = run([comp, '--ffi', t / 's.sffi', t / 'one.sm', t / 'x.exe', 'x', 'y'])
        check(b'Prayog' in r.stdout and not (t / 'x.exe').exists(), '--ffi without --object or --separate: the usage, no output')
        r = run([comp, HERE / 'winffi.sm', t / 'plain.exe'])
        check(r.returncode == 1 and b'agyat prakriya' in r.stdout, 'the ordinary compile reads no sidecar: %r' % r.stdout[-80:])
        # 4. the reader
        for name, src, want_msg in [('calls out', 'callout.obj', b'agyat sanket: elsewhere'),
                                    ('writable data', 'writable.obj', b'bhara-khandam asamarthitam'),
                                    ('a pointer table (relocation in data)', 'dataptr.obj', b'punahsthapanam asamarthitam'),
                                    ('unwind tables', 'winffi-unwind.obj', b'.pdata/.xdata'),
                                    ('not COFF', 'winffi.sm', b'COFF x64 vastu-patram na')]:
            out = t / 'c.smo'
            if out.exists():
                out.unlink()
            r = run([c2s, HERE / src, out])
            check(r.returncode == 1 and not out.exists() and want_msg in r.stdout,
                  'coff2smo refuses %s %r' % (name, r.stdout[-80:]))
        (t / 'trunc.obj').write_bytes((HERE / 'winffi.obj').read_bytes()[:300])
        r = run([c2s, t / 'trunc.obj', t / 'c.smo'])
        check(r.returncode == 1 and not (t / 'c.smo').exists() and b'khanditam' in r.stdout, 'coff2smo refuses a truncated object')
        r = run([c2s, t / 'nope.obj', t / 'c.smo'])
        check(r.returncode == 1 and b'patram na udghatitam' in r.stdout, 'coff2smo: a missing file')
        r = run([c2s])
        check(r.returncode == 2 and b'Prayog' in r.stdout, 'coff2smo: usage')
    print('r35 ffi (Windows): %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
