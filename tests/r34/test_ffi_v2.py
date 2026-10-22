#!/usr/bin/env python3
"""ROUND-34 (cloud): the FFI's version header, and the test-net gaps ChatGPT's R99 named.

  1. THE VERSION: `sutram-ffi-v1` is R32's form exactly (i64 only; tests/r32 checks that
     f64, ptr and void are refused under it). `sutram-ffi-v2` adds the R33 kinds. The same
     i64 declarations under v1 and v2 give the same object, byte for byte.
  2. A DASHAM WORKS, not only "is no longer truncated": a double goes Sutram -> C -> Sutram
     -> C bit for bit, for -0.0, both infinities, a quiet NaN, a NaN with a payload, the
     smallest subnormal, the largest finite and 1.0; both through an expression and through
     a dasham variable. (tests/r33 checks values; tools/fuzz_ffi.py checks 10,000 more.)
  3. THE ARITY EDGES: a 0-argument declaration called with 1, a 6-argument one with 5,
     and a call with 7 arguments: refused at compile time, exit 1, no object.
  4. HOSTILE SIDECAR BYTES: a NUL, an invalid UTF-8 sequence, a DEL, a tab - each refused
     with its line, no object.
  5. THE PACKS: E_FFI_KIND in the Sanskrit and Gujarati packs (tests/r32 checks Hindi).
Linux only. No network. No C compiler needed (tests/r34/ffi_bits.o is committed).
usage: python3 -B tests/r34/test_ffi_v2.py [--compiler PATH] [--linker PATH] [--elf2smo PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests' / 'r34'
V1 = 'sutram-ffi-v1|linux-x86_64-sysv\n'
V2 = 'sutram-ffi-v2|linux-x86_64-sysv\n'


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def main(argv) -> int:
    comp = arg(argv, '--compiler', str(ROOT / 'sutram_compiler'))
    link = arg(argv, '--linker', str(ROOT / 'sutram-link'))
    e2s = arg(argv, '--elf2smo', str(ROOT / 'sutram-elf2smo'))
    fails = checks = 0

    def check(ok, what):
        nonlocal fails, checks
        checks += 1
        if not ok:
            fails += 1
            print('FAIL', what)

    def run(cmd, **kw):
        return subprocess.run(cmd, capture_output=True, timeout=60, **kw)

    os.chdir(ROOT)
    t = Path(tempfile.mkdtemp(prefix='r34-ffi-'))
    main_sm = str(ROOT / 'tests/r32/main.sm')
    decls = (ROOT / 'tests/r32/ffi.sffi').read_text().split('\n', 1)[1]

    # 1. the version
    objs = []
    for v, hdr in (('v1', V1), ('v2', V2)):
        f = t / f'{v}.sffi'
        f.write_text(hdr + decls)
        o = t / f'{v}.smo'
        r = run([comp, '--ffi', str(f), '--object', main_sm, str(o)])
        check(r.returncode == 0, f'{v}: {r.stdout!r}')
        objs.append(o.read_bytes() if o.exists() else b'')
    check(objs[0] == objs[1] and objs[0], 'the same i64 declarations: the same object under v1 and v2')
    f = t / 'k1.sffi'
    f.write_text(V1 + 'k_half|1|f64|f64|sutram_k_half\n')
    r = run([comp, '--ffi', str(f), '--object', str(ROOT / 'tests/r33/modmain.sm'), str(t / 'k1.smo')])
    check(r.returncode == 1 and b'pankti 2' in r.stdout and not (t / 'k1.smo').exists(), f'f64 under v1: {r.stdout!r}')
    print('the version: v1 is i64 only, as R32 promised; v2 adds the kinds; i64 declarations give the same object')

    # 2. a dasham works, bit for bit
    b = run([sys.executable, '-B', 'tools/sutram_build.py', '--compiler', comp, '--linker', link, '--elf2smo', e2s,
             '--ffi', str(HERE / 'ffi_bits.sffi'), '--foreign', str(HERE / 'ffi_bits.o'),
             str(HERE / 'ffi_bits.sm'), '-o', str(t / 'bits')])
    out = run([str(t / 'bits')]).stdout if b.returncode == 0 else b.stdout + b.stderr
    check(out == (HERE / 'ffi_bits.expect').read_bytes(), f'bits: {out[:200]!r}')
    print('a dasham works: 8 special doubles, Sutram -> C -> Sutram -> C, bit for bit, by expression and by variable')

    # 3. the arity edges
    f = t / 'a.sffi'
    f.write_text(V2 + 'z0|0||i64|sutram_z0\ns6|6|i64,i64,i64,i64,i64,i64|i64|sutram_ffi_mix\n')
    for body, want in (('likha(z0(1))', b"'z0' ityasmai 1 tarkah dattah; hastakshare 0"),
                       ('likha(s6(1, 2, 3, 4, 5))', b"'s6' ityasmai 5 tarkah dattah; hastakshare 6"),
                       ('likha(s6(1, 2, 3, 4, 5, 6, 7))', b'Sutram Error')):
        src = t / 'e.sm'
        src.write_text(f'mukhya() {{\n    {body}\n}}\n')
        o = t / 'e.smo'
        o.unlink(missing_ok=True)
        r = run([comp, '--ffi', str(f), '--object', str(src), str(o)])
        check(r.returncode == 1 and want in r.stdout and not o.exists(), f'{body}: {r.stdout!r}')
    print('the arity edges: 0 called with 1, 6 with 5, and 7 arguments: refused, no object')

    # 4. hostile sidecar bytes
    for what, raw in (('a NUL', b's_add|2|i64,i64|i64|sutram_ffi_add\x00\n'),
                      ('invalid UTF-8', b's_\xc3\x28dd|2|i64,i64|i64|sutram_ffi_add\n'),
                      ('a DEL', b's_add|2|i64,i64|i64|sutram\x7fffi_add\n'),
                      ('a tab', b's_add|2|i64,\ti64|i64|sutram_ffi_add\n')):
        f = t / 'h.sffi'
        f.write_bytes(V2.encode() + raw)
        o = t / 'h.smo'
        o.unlink(missing_ok=True)
        r = run([comp, '--ffi', str(f), '--object', main_sm, str(o)])
        check(r.returncode == 1 and b'dushtam, pankti 2' in r.stdout and not o.exists(), f'{what}: {r.stdout!r}')
    print('hostile sidecar bytes: a NUL, invalid UTF-8, a DEL, a tab: refused with the line, no object')

    # 5. the packs
    src = t / 'p.sm'
    src.write_text('mukhya() {\n    likha(k_scale(1.5, 2.5))\n}\n')
    for lang, want in (('sanskrit', 'घोषितात् प्रकारात् भिन्नः तर्कः 2'), ('gujarati', 'જાહેર પ્રકારથી અલગ દલીલ 2')):
        r = run([comp, '--ffi', str(ROOT / 'tests/r33/kinds.sffi'), '--object', str(src), str(t / 'p.smo')],
                env=dict(os.environ, SUTRAM_LANG=lang))
        check(r.returncode == 1 and want.encode() in r.stdout and b'[E_FFI_KIND]' in r.stdout, f'{lang}: {r.stdout!r}')
    print('the packs: E_FFI_KIND in Sanskrit and Gujarati')
    print(f'r34 ffi v2: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
