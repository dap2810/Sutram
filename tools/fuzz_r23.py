#!/usr/bin/env python3
"""ROUND-23: a differential fuzzer for the three new capabilities.

It generates random valid programs that use function values, methods and
slices together, computes the output each must print with a model written here
in Python, compiles each with the real compiler, runs it and compares.

Every program has:
  * 2-5 two-argument functions op_i(a, b) with a random integer body;
  * a selector chuno(k) that RETURNS one of them, an applier lagu(f, x, y) that
    calls a function PASSED to it, a fold sankshep(vibhag s, f, init) that calls
    a function passed to it on every element of a SLICE, and a function value
    STORED in a local and called;
  * a rachana with 2-4 fields and 2-3 METHODS (one changes a field), called on
    two objects;
  * a mala of 4-12 elements and a chain of slices of it and of each other
    (random in-bounds lo:hi, with lo or hi sometimes omitted), read, written
    and folded; the mala is printed afterwards, so a write through a slice that
    went to the wrong element shows.

ROUND-25 adds the error type: 2-4 phal-prakriyas e_i(x), each failing with
dosh(code) on a condition of x, else calling an earlier one under prasar and
returning siddhi(...); mukhya ends by calling them under prasar, so the first
failure ends the program with its code as the exit status (checked as EXIT n).

--robust mutates these programs and the three R23 examples (with the R23
tokens `:`, `.`, `vibhag`, `[`, `]` among the insertions) and requires that the
compiler never crashes or hangs on them (tools/fuzz_robust.py's rule).

usage:
  python3 -B tools/fuzz_r23.py --seed 23 --count 300 [--compiler ./sutram_compiler]
  python3 -B tools/fuzz_r23.py --seed 23 --show 5
  python3 -B tools/fuzz_r23.py --seed 23 --robust 3000
Exit 0 when every program agreed (or nothing crashed), 1 otherwise.
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
M64 = (1 << 64) - 1


def wrap(x):
    x &= M64
    return x - (1 << 64) if x >> 63 else x


OPS = ['+', '-', '*', '&', '|', '^']


def apply(op, a, b):
    return wrap({'+': a + b, '-': a - b, '*': a * b, '&': a & b, '|': a | b, '^': a ^ b}[op])


class Gen:
    def __init__(self, seed):
        self.r = random.Random(seed)
        self.out = []          # expected output lines
        self.exit = 0          # R25: the expected exit status

    # a random expression over names, as (source, evaluator)
    def expr(self, names, depth=2):
        r = self.r
        if depth == 0 or r.random() < 0.3:
            if names and r.random() < 0.7:
                n = r.choice(names)
                return n, (lambda env, n=n: env[n])
            v = r.randint(-9, 9)
            return ('(%d)' % v if v < 0 else str(v)), (lambda env, v=v: v)
        op = r.choice(OPS)
        a, fa = self.expr(names, depth - 1)
        b, fb = self.expr(names, depth - 1)
        return '(%s %s %s)' % (a, op, b), (lambda env, op=op, fa=fa, fb=fb: apply(op, fa(env), fb(env)))

    def program(self):
        r = self.r
        src = []
        say = self.out.append
        # functions
        nf = r.randint(2, 5)
        funcs = {}
        for i in range(nf):
            body, f = self.expr(['a', 'b'], 2)
            funcs['op%d' % i] = f
            src += ['prakriya op%d(a, b) {' % i, '    prati %s' % body, '}', '']
        fnames = list(funcs)
        src += ['prakriya chuno(k) {']
        for i, n in enumerate(fnames[:-1]):
            src += ['    yadi (k == %d) {' % i, '        prati %s' % n, '    }']
        src += ['    prati %s' % fnames[-1], '}', '']

        def chuno(k):
            return fnames[k] if 0 <= k < len(fnames) - 1 else fnames[-1]
        src += ['prakriya lagu(f, x, y) {', '    prati f(x, y)', '}', '']
        src += ['prakriya sankshep(vibhag s, f, aadi) {', '    vitti t = aadi',
                '    chakra i = 0 tak pankti_len(s) - 1 {', '        t = f(t, s[i])', '    }',
                '    prati t', '}', '']
        # a rachana and methods
        nfld = r.randint(2, 4)
        flds = ['k%d' % i for i in range(nfld)]
        src += ['rachana Vastu = { %s }' % ', '.join(flds), '']
        methods = {}
        nm = r.randint(2, 3)
        for i in range(nm):
            names = ['swa_' + f for f in flds] + ['x']
            body, f = self.expr(names, 2)
            body_src = body
            for fl in flds:
                body_src = body_src.replace('swa_' + fl, 'swa.' + fl)
            if i == 0:   # this one changes a field and returns the new value
                tgt = r.choice(flds)
                src += ['prakriya Vastu.m%d(swa, x) {' % i, '    swa.%s = %s' % (tgt, body_src),
                        '    prati swa.%s' % tgt, '}', '']
                methods['m%d' % i] = ('set', tgt, f)
            else:
                src += ['prakriya Vastu.m%d(swa, x) {' % i, '    prati %s' % body_src, '}', '']
                methods['m%d' % i] = ('get', None, f)
        # mukhya
        body = []
        n = r.randint(4, 12)
        arr = [r.randint(-20, 20) for _ in range(n)]
        body.append('mala a[%d]' % n)
        for i, v in enumerate(arr):
            body.append('a[%d] = %s' % (i, v if v >= 0 else '(%d)' % v))
        # objects
        objs = {}
        for o in ('p', 'q'):
            vals = {f: r.randint(-9, 9) for f in flds}
            objs[o] = vals
            body.append('vitti %s = nirmmita(%d)' % (o, 8 * nfld))
            for f, v in vals.items():
                body.append('%s.%s = %s' % (o, f, v if v >= 0 else '(%d)' % v))
        # function values
        k = r.randint(0, nf)
        body.append('vitti g = chuno(%d)' % k)
        g = chuno(k)
        x, y = r.randint(-9, 9), r.randint(-9, 9)
        body.append('likha(g(%d, %d))' % (x, y)); say(funcs[g]({'a': x, 'b': y}))
        h = r.choice(fnames)
        body.append('likha(lagu(%s, %d, %d))' % (h, x, y)); say(funcs[h]({'a': x, 'b': y}))
        body.append('likha(lagu(g, %d, %d))' % (y, x)); say(funcs[g]({'a': y, 'b': x}))
        # slices: s0 = a[...], later ones of the earlier
        views = {}   # name -> (start offset in a, length)

        def fold(off, ln, fname, init):
            t = init
            for i in range(ln):
                t = funcs[fname]({'a': t, 'b': arr[off + i]})
            return t
        names = ['a']
        for si in range(r.randint(2, 5)):
            base = r.choice(names)
            boff, blen = (0, n) if base == 'a' else views[base]
            lo = r.randint(0, blen)
            hi = r.randint(lo, blen)
            form = r.randrange(4)
            if form == 1 and lo == 0:
                text = '%s[:%d]' % (base, hi)
            elif form == 2 and hi == blen:
                text = '%s[%d:]' % (base, lo)
            elif form == 3 and lo == 0 and hi == blen:
                text = '%s[:]' % base
            else:
                text = '%s[%d:%d]' % (base, lo, hi)
            sname = 's%d' % si
            body.append('vitti %s = %s' % (sname, text))
            views[sname] = (boff + lo, hi - lo)
            names.append(sname)
            off, ln = views[sname]
            body.append('likha(pankti_len(%s))' % sname); say(ln)
            if ln:
                j = r.randrange(ln)
                v = r.randint(-30, 30)
                body.append('%s[%d] = %s' % (sname, j, v if v >= 0 else '(%d)' % v))
                arr[off + j] = v
                j2 = r.randrange(ln)
                body.append('likha(%s[%d])' % (sname, j2)); say(arr[off + j2])
            fn = r.choice(fnames)
            init = r.randint(-5, 5)
            body.append('likha(sankshep(%s, %s, %d))' % (sname, fn, init)); say(fold(off, ln, fn, init))
        # a fold over a fresh slice expression passed straight to the call
        lo = r.randint(0, n); hi = r.randint(lo, n)
        fn = r.choice(fnames)
        body.append('likha(sankshep(a[%d:%d], g, 1))' % (lo, hi))
        say(fold(lo, hi - lo, g, 1))
        body.append('likha(sankshep(a, %s, 0))' % fn); say(fold(0, n, fn, 0))
        # methods
        for _ in range(r.randint(2, 5)):
            o = r.choice(['p', 'q'])
            m = r.choice(list(methods))
            x = r.randint(-9, 9)
            kind, tgt, f = methods[m]
            env = {'swa_' + fl: objs[o][fl] for fl in flds}
            env['x'] = x
            v = f(env)
            if kind == 'set':
                objs[o][tgt] = v
            body.append('likha(%s.%s(%d))' % (o, m, x)); say(v)
        for o in ('p', 'q'):
            for fl in flds:
                body.append('likha(%s.%s)' % (o, fl)); say(objs[o][fl])
        for i in range(n):
            body.append('likha(a[%d])' % i); say(arr[i])
        # R25: the error type
        ne = r.randint(2, 4)
        efuncs = []
        for i in range(ne):
            m = r.choice([1, 3, 7])
            v = r.randint(0, m)
            code = r.randint(1, 120)
            callee = r.randrange(i) if i and r.random() < 0.7 else None
            lines = ['prakriya e%d(x) {' % i, '    yadi ((x & %d) == %d) {' % (m, v),
                     '        prati dosh(%d)' % code, '    }']
            if callee is not None:
                arg, fa = self.expr(['x'], 1)
                lines.append('    vitti y = prasar e%d(%s)' % (callee, arg))
                res, fr = self.expr(['x', 'y'], 2)
            else:
                fa = None
                res, fr = self.expr(['x'], 2)
            lines += ['    prati siddhi(%s)' % res, '}', '']
            # functions go before mukhya: insert them ahead of the rachana
            src[0:0] = lines
            efuncs.append((m, v, code, callee, fa, fr))

        def ecall(i, x):
            m, v, code, callee, fa, fr = efuncs[i]
            if (x & m) == v:
                return ('dosh', code)
            env = {'x': x}
            if callee is not None:
                st, y = ecall(callee, fa(env))
                if st == 'dosh':
                    return (st, y)
                env['y'] = y
            return ('siddhi', fr(env))
        for _ in range(r.randint(2, 6)):
            i = r.randrange(ne)
            x = r.randint(-20, 20)
            body.append('likha(prasar e%d(%s))' % (i, x if x >= 0 else '(%d)' % x))
            st, val = ecall(i, x)
            if st == 'dosh':
                self.exit = val & 255
                break
            say(val)
        src += ['mukhya() {'] + ['    ' + b for b in body] + ['}']
        return '\n'.join(src) + '\n'


def make(seed):
    g = Gen(seed)
    s = g.program()
    return s, [str(v) for v in g.out] + (['EXIT %d' % g.exit] if g.exit else [])


def robust(a, comp):
    import fuzz_robust as fr
    rng = random.Random(a.seed)
    base = [p.read_bytes() for p in sorted((ROOT / 'examples').glob('24[6-8]_r23_*.sm'))]
    for i in range(40):
        base.append(make(rng.randrange(1 << 30))[0].encode())
    extra = [b':', b'[', b']', b'.', b'vibhag ', b'[:', b':]', b'.m0(', b'prakriya Vastu.', b'chuno',
             b'prasar ', b'siddhi(', b'dosh(', b'prati dosh(1)', b'prasar e0(1)']
    bad = 0
    counts = {}
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        sp, bp = Path(td, 'in.sm'), Path(td, 'out.bin')
        for i in range(a.robust):
            m = fr.mutate(rng, rng.choice(base))
            if rng.random() < 0.5:
                b = bytearray(m)
                j = rng.randrange(len(b) + 1)
                b[j:j] = rng.choice(extra)
                m = bytes(b)
            sp.write_bytes(m)
            if bp.exists():
                bp.unlink()
            v, first = fr.run(comp, sp, bp, a.timeout)
            key = v.split()[0]
            counts[key] = counts.get(key, 0) + 1
            if key in ('CRASH', 'HANG'):
                bad += 1
                dst = out / ('r23-mutation-%d-%d.sm' % (a.seed, i))
                dst.write_bytes(m)
                print('%s  %s' % (v, dst), flush=True)
    print('mutations: ' + '  '.join('%s %d' % kv for kv in sorted(counts.items())))
    print('CRASH or HANG: %d' % bad)
    return 1 if bad else 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=23)
    ap.add_argument('--count', type=int, default=200)
    ap.add_argument('--compiler', default=str(ROOT / 'sutram_compiler'))
    ap.add_argument('--show', type=int)
    ap.add_argument('--robust', type=int, default=0, metavar='N')
    ap.add_argument('--out', default='fuzz-r23-out')
    ap.add_argument('--timeout', type=float, default=20)
    a = ap.parse_args(argv)
    comp = os.path.abspath(a.compiler)
    sys.path.insert(0, str(ROOT / 'tools'))
    if a.robust:
        return robust(a, comp)
    rng = random.Random(a.seed)
    seeds = [rng.randrange(1 << 30) for _ in range(max(a.count, (a.show or 0) + 1))]
    if a.show is not None:
        s, exp = make(seeds[a.show])
        print(s); print('--- expected ---'); print('\n'.join(exp)); return 0
    bad = 0
    lines = 0
    out = Path(a.out)
    with tempfile.TemporaryDirectory() as td:
        sp, bp = Path(td, 'p.sm'), Path(td, 'p.bin')
        for i in range(a.count):
            s, exp = make(seeds[i])
            sp.write_text(s, encoding='utf-8')
            c = subprocess.run([comp, str(sp), str(bp)], capture_output=True, timeout=60)
            if c.returncode != 0:
                got = ['COMPILE %d: %s' % (c.returncode, c.stdout.decode('utf-8', 'replace').strip()[:200])]
            else:
                rr = subprocess.run([str(bp)], capture_output=True, timeout=20)
                got = rr.stdout.decode('utf-8', 'replace').split('\n')[:-1]
                if rr.returncode != 0:
                    got.append('EXIT %d' % rr.returncode)
            lines += len(exp)
            if got != exp:
                bad += 1
                out.mkdir(parents=True, exist_ok=True)
                (out / ('r23-%d-%d.sm' % (a.seed, i))).write_text(s, encoding='utf-8')
                (out / ('r23-%d-%d.expected' % (a.seed, i))).write_text('\n'.join(exp) + '\n')
                print('DIFFER  program %d (saved under %s)' % (i, out), flush=True)
    print('fuzz_r23: %d programs, %d printed values compared, %d differ' % (a.count, lines, bad))
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
