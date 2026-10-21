#!/usr/bin/env python3
"""ROUND-33: a fuzzer for the FFI. Random Sutram programs call the C functions in
tests/r32/foreign.o and tests/r33/kinds.o - integers and dasham, nested inside each other
and inside Sutram arithmetic, from mukhya and from a prakriya that keeps locals live across
the foreign calls - and every printed value is compared with a Python model.

It is the FFI's second net, beside tests/r32 and tests/r33: those check each rule once;
this checks the calling convention (which register, which kind, the stack, the result)
in combinations nobody wrote by hand.

usage: python3 -B tools/fuzz_ffi.py [--seed N] [--count N] [--compiler C] [--linker L]
                                    [--elf2smo E] [--out DIR]
Linux only. No network. Exit 0 when every program agrees.
"""
from __future__ import annotations

import argparse
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]

SIDECAR = """sutram-ffi-v1|linux-x86_64-sysv
s_add|2|i64,i64|i64|sutram_ffi_add
s_neg|1|i64|i64|sutram_ffi_neg
s_mix|6|i64,i64,i64,i64,i64,i64|i64|sutram_ffi_mix
k_half|1|f64|f64|sutram_k_half
k_scale|2|f64,i64|f64|sutram_k_scale
k_mix|6|i64,f64,i64,f64,i64,f64|f64|sutram_k_mix
k_trunc|1|f64|i64|sutram_k_trunc
"""
# the Sutram helper: locals live across two foreign calls
HELPER = """prakriya sf(a) {
    vitti t = a * 3
    vitti u = s_add(t, 1)
    vitti w = s_neg(u)
    prati t + u + w + a
}
"""


def sf(a):
    t = a * 3
    u = t + 1
    return t + u - u + a


class Gen:
    def __init__(self, rng):
        self.r = rng

    def ilit(self):
        v = self.r.randint(-40, 40)
        return (str(v) if v >= 0 else f'(0 - {-v})'), v

    def flit(self):
        v = self.r.randint(-64, 64) / 4.0
        s = f'{abs(v):.2f}'
        return (s if v >= 0 else f'(0.0 - {s})'), v

    def i(self, d):
        r = self.r
        if d <= 0:
            return self.ilit()
        k = r.randrange(9)
        if k == 0:
            return self.ilit()
        if k == 1:
            (a, x), (b, y) = self.i(d - 1), self.i(d - 1)
            return f'({a} + {b})', x + y
        if k == 2:
            (a, x), (b, y) = self.i(d - 1), self.i(d - 1)
            return f'({a} - {b})', x - y
        if k == 3:
            (a, x), (b, y) = self.i(d - 1), self.ilit()
            return f'({a} * {b})', x * y
        if k == 4:
            (a, x), (b, y) = self.i(d - 1), self.i(d - 1)
            return f's_add({a}, {b})', x + y
        if k == 5:
            a, x = self.i(d - 1)
            return f's_neg({a})', -x
        if k == 6:
            args = [self.i(d - 2) for _ in range(6)]
            return ('s_mix(' + ', '.join(a for a, _ in args) + ')',
                    sum((n + 1) * v for n, (_, v) in enumerate(args)))
        if k == 7:
            a, x = self.f(d - 1)
            return f'k_trunc({a})', int(x)
        a, x = self.i(d - 1)
        return f'sf({a})', sf(x)

    def f(self, d):
        r = self.r
        if d <= 0:
            return self.flit()
        k = r.randrange(7)
        if k == 0:
            return self.flit()
        if k == 1:
            a, x = self.f(d - 1) if r.randrange(2) else self.i(d - 1)
            return f'k_half({a})', x / 2.0
        if k == 2:
            (a, x), (b, y) = self.f(d - 1), self.ilit()
            return f'k_scale({a}, {b})', x * y
        if k == 3:
            args = [self.i(d - 2), self.f(d - 2), self.i(d - 2), self.f(d - 2), self.i(d - 2), self.f(d - 2)]
            v = [x for _, x in args]
            return ('k_mix(' + ', '.join(a for a, _ in args) + ')',
                    v[0] + v[1] * 10.0 + v[2] * 100.0 + v[3] * 1000.0 + v[4] * 10000.0 + v[5] * 100000.0)
        if k == 4:
            (a, x), (b, y) = self.f(d - 1), self.f(d - 1)
            return f'({a} + {b})', x + y
        if k == 5:
            (a, x), (b, y) = self.f(d - 1), self.f(d - 1)
            return f'({a} - {b})', x - y
        a, x = self.f(d - 1)
        return f'k_half({a})', x / 2.0

    def program(self):
        lines, want = [], []
        for _ in range(self.r.randint(3, 8)):
            d = self.r.randint(1, 4)
            if self.r.randrange(2):
                e, v = self.i(d)
                want.append(f'{v}\n')
            else:
                e, v = self.f(d)
                while abs(v) >= 1e8:          # likha prints a dasham this large inexactly (R33-01)
                    e, v = self.f(d)
                want.append(f'{v + 0.0:.6f}\n' if v != 0 else '0.000000\n')   # Sutram prints -0.0 as 0.000000
            lines.append(f'    likha({e})')
        return HELPER + 'mukhya() {\n' + '\n'.join(lines) + '\n}\n', ''.join(want)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=33)
    ap.add_argument('--count', type=int, default=200)
    ap.add_argument('--compiler', default=str(ROOT / 'sutram_compiler'))
    ap.add_argument('--linker', default=str(ROOT / 'sutram-link'))
    ap.add_argument('--elf2smo', default=str(ROOT / 'sutram-elf2smo'))
    ap.add_argument('--out', default=None)
    a = ap.parse_args(argv)
    out = Path(a.out or tempfile.mkdtemp(prefix='fuzz-ffi-'))
    out.mkdir(parents=True, exist_ok=True)
    (out / 'f.sffi').write_text(SIDECAR)
    objs = []
    for k, o in enumerate(('tests/r32/foreign.o', 'tests/r33/kinds.o')):
        dst = out / f'foreign{k}.smo'
        r = subprocess.run([a.elf2smo, str(ROOT / o), str(dst)], capture_output=True)
        if r.returncode:
            print(f'fuzz_ffi: {o}: {r.stdout!r}')
            return 1
        objs.append(str(dst))
    rng = random.Random(a.seed)
    agree = fail = values = calls = 0
    for n in range(a.count):
        src, want = Gen(rng).program()
        sm, smo, exe = out / f'p{n}.sm', out / f'p{n}.smo', out / f'p{n}'
        sm.write_text(src)
        r = subprocess.run([a.compiler, '--ffi', str(out / 'f.sffi'), '--object', str(sm), str(smo)],
                           capture_output=True, timeout=60)
        ok = r.returncode == 0
        if ok:
            r = subprocess.run([a.linker, str(exe), str(smo)] + objs, capture_output=True, timeout=60)
            ok = r.returncode == 0
        got = b''
        if ok:
            p = subprocess.run([str(exe)], capture_output=True, timeout=10)
            got = p.stdout
            ok = p.returncode == 0 and got == want.encode()
        values += want.count('\n')
        calls += sum(src.count(f) for f in ('s_add(', 's_neg(', 's_mix(', 'k_half(', 'k_scale(', 'k_mix(', 'k_trunc('))
        if ok:
            agree += 1
            for f in (sm, smo, exe):
                f.unlink(missing_ok=True)
        else:
            fail += 1
            if fail <= 3:
                print(f'DIFFER p{n}.sm: want {want!r}\n               got  {got!r} {r.stdout[-200:]!r}')
    print(f'fuzz_ffi: seed {a.seed}, {a.count} programs, {calls} foreign calls, {values} printed values: '
          f'{agree} agree, {fail} differ')
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
