#!/usr/bin/env python3
"""ROUND-33: the FFI's second-smallest version - f64, ptr and void, and the stage-2 reader.

  1. THE KINDS WORK: tests/r33/kinds.sm calls nine C functions in tests/r33/kinds.o:
     f64 in and out, integers and doubles interleaved across rdi.. and xmm0.. (the System V
     rule), a string and a kosh passed as pointers, a C function writing into a kosh,
     void results as statements, and a dasham result used in Sutram
     arithmetic. tests/r33/modmain.sm does it from a separately compiled module.
  2. THE KINDS ARE CHECKED: a dasham for an i64 or a ptr, a string or a kosh for an i64 or
     an f64 - each is E_FFI_KIND at the call, exit 1, no object; also in a statement call.
     A void function's value, used anywhere, is E_FFI_KIND too: there is no made-up 0.
  3. STATEMENT CALLS: k_set(...) and k_nothing() as statements are foreign calls. (In R32 a
     statement call to a declared function was sent to the Sutram call, by its local name,
     and failed at the link: the defect this round found.)
  4. THE STAGE-2 READER: kinds.o has read-only data (its double constants) and six PC32
     relocations into it - read and resolved, nothing left for the linker; a C function that
     calls out (undefined symbol), unwind tables (relocations outside the code), and a
     16-byte constant (alignment the linker cannot keep) are refused.
  5. THE EDGES (ChatGPT R99's list): a failed compile leaves an existing object untouched; 64
     declarations and an 8192-byte sidecar are accepted, 65 and 8193 refused; a 3-, 4- and
     5-argument call; a foreign symbol in two objects, or declared and in none, is refused by
     the link with no executable; a changed foreign object under a warm cache is used.
Linux only. No network. No C compiler needed (the .o files are committed).
usage: python3 -B tests/r33/test_ffi_kinds.py [--compiler PATH] [--linker PATH] [--elf2smo PATH]
"""
from __future__ import annotations

import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests' / 'r33'

KINDS_OUT = (b'2.500000\n3.500000\n6.000000\n654321.000000\n7\n60\n200\n240\n0.750000\n'
             b'2.500000\n9\n10.000000\n')


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def header(path):
    return struct.unpack_from('<3Q', open(path, 'rb').read(), 8)


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

    def build(src, out):
        return run([sys.executable, '-B', 'tools/sutram_build.py', '--compiler', comp, '--linker', link,
                    '--elf2smo', e2s, '--ffi', str(HERE / 'kinds.sffi'), '--foreign', str(HERE / 'kinds.o'),
                    str(src), '-o', str(out)])

    os.chdir(ROOT)
    t = Path(tempfile.mkdtemp(prefix='r33-'))
    # 1 + 3. the kinds work, statement calls included
    b = build(HERE / 'kinds.sm', t / 'k')
    check(b.returncode == 0, f'build kinds: {b.stdout[-200:]!r}')
    if b.returncode == 0:
        p = run([str(t / 'k')])
        check((p.returncode, p.stdout) == (0, KINDS_OUT), f'kinds output {p.stdout!r}')
    b = build(HERE / 'modmain.sm', t / 'm')
    check(b.returncode == 0 and run([str(t / 'm')]).stdout == b'7.500000\n0.500000\n', f'module: {b.stdout!r}')
    print('the kinds work: f64 in and out, interleaved registers, a string and a kosh as pointers, a C write '
          'into a kosh, void as a statement, from mukhya and from a module')

    # 2. the kinds are checked
    sffi = str(HERE / 'kinds.sffi')
    cases = [('likha(k_scale(1.5, 2.5))', 3, 11, 'k_scale', 2),      # dasham for i64
             ('likha(k_scale("x", 2))', 3, 11, 'k_scale', 1),        # string for f64
             ('likha(k_strlen(1.5))', 3, 11, 'k_strlen', 1),         # dasham for ptr
             ('dasham d = 1.0\n    likha(k_sum(xs, d))', 4, 11, 'k_sum', 2),
             ('likha(k_scale(1.5, xs))', 3, 11, 'k_scale', 2),       # kosh for i64
             ('likha(k_trunc(xs))', 3, 11, 'k_trunc', 1),            # kosh for f64
             ('k_set(xs, 0, 2.5)', 3, 5, 'k_set', 3)]                # in a statement call
    for body, line, col, name in (('likha(k_set(xs, 0, 1))', 3, 11, 'k_set'),
                                  ('vitti v = k_nothing()', 3, 15, 'k_nothing'),
                                  ('likha(1 + k_nothing())', 3, 15, 'k_nothing')):
        src = t / 'v.sm'
        src.write_text(f'mukhya() {{\n    kosh xs[2]\n    {body}\n}}\n')
        obj = t / 'v.smo'
        obj.unlink(missing_ok=True)
        r = run([comp, '--ffi', sffi, '--object', str(src), str(obj)])
        want = f'v.sm:{line}:{col}: Sutram Error [E_FFI_KIND]: videshi prakriya {name}: mulyam na pratyarpayati'
        check(r.returncode == 1 and want.encode() in r.stdout and not obj.exists(), f'void value {body}: {r.stdout!r}')
    for body, line, col, name, n in cases:
        src = t / 'e.sm'
        src.write_text(f'mukhya() {{\n    kosh xs[2]\n    {body}\n}}\n')
        obj = t / 'e.smo'
        obj.unlink(missing_ok=True)
        r = run([comp, '--ffi', sffi, '--object', str(src), str(obj)])
        want = (f'e.sm:{line}:{col}: Sutram Error [E_FFI_KIND]: videshi prakriya {name}: '
                f'ghoshitat prakarat bhinnah tarkah {n}').encode()
        check(r.returncode == 1 and want in r.stdout and not obj.exists(), f'{body}: {r.stdout!r}')
    src = t / 'ok.sm'
    src.write_text('mukhya() {\n    kosh xs[2]\n    likha(k_strlen(xs))\n    likha(k_strlen("ab"))\n'
                   '    likha(k_sum(xs, 0))\n    likha(k_half(2))\n}\n')
    r = run([comp, '--ffi', sffi, '--object', str(src), str(t / 'ok.smo')])
    check(r.returncode == 0, f'the accepted kinds: {r.stdout!r}')
    print(f'the kinds are checked: {len(cases)} mismatches and 3 uses of a void value are E_FFI_KIND at the call, '
          f'exit 1, no object; '
          f'a kosh or string for ptr and an integer for f64 are accepted')

    # 4. the stage-2 reader
    r = run([e2s, str(HERE / 'kinds.o'), str(t / 'k.smo')])
    code, nsym, nrel = header(t / 'k.smo')
    check(r.returncode == 0 and nsym == 9 and nrel == 0, f'kinds.o: {r.stdout!r} {nsym} {nrel}')
    for name, want in (('tests/r32/negative.o', b'agyat sanket: missing_helper'),
                       ('tests/r32/foreign-unwind.o', b'punahsthapanam asamarthitam'),
                       ('tests/r33/align16.o', b'8-baait-adhika samarekhanam asamarthitam')):
        r = run([e2s, str(ROOT / name), str(t / 'n.smo')])
        check(r.returncode == 1 and want in r.stdout, f'reader refuses {name}: {r.stdout!r}')
    print('the stage-2 reader: read-only data and its PC32 relocations resolved (9 functions, 0 holes left); '
          'calling out, unwind tables, a 16-byte constant: refused')
    # 5. the edges
    sm = t / 'keep.sm'
    sm.write_text('mukhya() {\n    likha(k_half(1.0, 2.0))\n}\n')
    smo = t / 'keep.smo'
    smo.write_bytes(b'an earlier object')
    r = run([comp, '--ffi', sffi, '--object', str(sm), str(smo)])
    check(r.returncode == 1 and smo.read_bytes() == b'an earlier object', 'a failed compile left the old object alone')
    hdr = 'sutram-ffi-v1|linux-x86_64-sysv\n'
    for n, ok in ((64, True), (65, False)):
        f = t / f'n{n}.sffi'
        f.write_text(hdr + ''.join(f'n{k}|0||i64|f{k}\n' for k in range(n)))
        r = run([comp, '--ffi', str(f), '--object', str(HERE / 'kinds.sm'), str(t / 'n.smo')])
        check((r.returncode == 0) == ok or (not ok and b'pankti 66' in r.stdout), f'{n} declarations: {r.stdout[-90:]!r}')
    for size, ok in ((8192, True), (8193, False)):
        text = hdr + 'k_half|1|f64|f64|sutram_k_half\n'
        k = 0
        while len(text) < size:                       # well-formed lines up to exactly size bytes
            name = f'p{k}'
            rest = size - len(text) - len(name) - 9
            sym = 'q' * 120 + str(k) if rest > 128 else 'q' * rest
            text += f'{name}|0||i64|{sym}\n'
            k += 1
        f = t / f's{size}.sffi'
        f.write_text(text)
        check(f.stat().st_size == size, f'built a {size}-byte sidecar ({f.stat().st_size})')
        r = run([comp, '--ffi', str(f), '--object', str(HERE / 'modmain.sm'), str(t / 's.smo')])
        check((r.returncode == 0) == ok and (ok or b'pankti 0' in r.stdout), f'{size}-byte sidecar: {r.stdout[-90:]!r}')
    src = t / 'mid.sm'
    src.write_text('mukhya() {\n    likha(s3(1, 2, 3))\n    likha(s4(1, 2, 3, 4))\n    likha(s5(1, 2, 3, 4, 5))\n}\n')
    (t / 'mid.sffi').write_text(hdr + 's3|3|i64,i64,i64|i64|r33_s3\ns4|4|i64,i64,i64,i64|i64|r33_s4\n'
                                's5|5|i64,i64,i64,i64,i64|i64|r33_s5\n')
    r1 = run([comp, '--ffi', str(t / 'mid.sffi'), '--object', str(src), str(t / 'mid.smo')])
    r2 = run([e2s, str(HERE / 'mid.o'), str(t / 'midf.smo')])
    r3 = run([link, str(t / 'mid'), str(t / 'mid.smo'), str(t / 'midf.smo')])
    out = run([str(t / 'mid')]).stdout if r3.returncode == 0 else r1.stdout + r2.stdout + r3.stdout
    check(out == b'123\n1234\n12345\n', f'3, 4 and 5 arguments: {out!r}')
    run([e2s, str(ROOT / 'tests/r32/foreign.o'), str(t / 'f1.smo')])
    run([comp, '--ffi', str(ROOT / 'tests/r32/ffi.sffi'), '--object', str(ROOT / 'tests/r32/main.sm'), str(t / 'r.smo')])
    r = run([link, str(t / 'dup'), str(t / 'r.smo'), str(t / 'f1.smo'), str(t / 'f1.smo')])
    check(r.returncode == 1 and b'dvih paribhashita: sutram_ffi_' in r.stdout and not (t / 'dup').exists(),
          f'a foreign symbol twice: {r.stdout!r}')
    src = t / 'nf.sm'
    src.write_text('mukhya() {\n    likha(s_add(1, 2))\n}\n')
    run([comp, '--ffi', str(ROOT / 'tests/r32/ffi.sffi'), '--object', str(src), str(t / 'nf.smo')])
    r = run([link, str(t / 'nf'), str(t / 'nf.smo')])
    check(r.returncode == 1 and b'agyat prakriya: sutram_ffi_add' in r.stdout and not (t / 'nf').exists(),
          f'declared, in no object: {r.stdout!r}')
    cache = str(t / 'cache')
    cmd = [sys.executable, '-B', 'tools/sutram_build.py', '--compiler', comp, '--linker', link, '--elf2smo', e2s,
           '--ffi', str(t / 'mid.sffi'), '--cache', cache]
    fo = t / 'swap.o'
    fo.write_bytes((HERE / 'mid.o').read_bytes())
    a1 = run(cmd + ['--foreign', str(fo), str(src.with_name('mid.sm')), '-o', str(t / 'w1')])
    fo.write_bytes((HERE / 'mid-other.o').read_bytes())
    a2 = run(cmd + ['--foreign', str(fo), str(src.with_name('mid.sm')), '-o', str(t / 'w2')])
    o1 = run([str(t / 'w1')]).stdout
    o2 = run([str(t / 'w2')]).stdout
    check(a1.returncode == a2.returncode == 0 and b'0 compiled, 1 reused' in a2.stdout and o1 == b'123\n1234\n12345\n'
          and o2 == b'321\n4321\n54321\n', f'a changed foreign object, warm cache: {o1!r} {o2!r} {a2.stdout!r}')
    print('the edges: an old object kept on failure; 64 / 65 declarations, 8192 / 8193 bytes; 3, 4 and 5 '
          'arguments; a foreign symbol twice, or nowhere: refused by the link; a new foreign object used under a warm cache')

    print(f'r33 ffi kinds: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
