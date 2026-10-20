#!/usr/bin/env python3
"""ROUND-15 WS1: shrink a fuzz_valid counterexample to a small program that
fails the same way.

It works on the generated program's structure, not on its text, so every
candidate is still a valid program, and the reference interpreter still gives
its expected output. A candidate is kept only if it fails with the same kind of
failure as the original (compiler crash, wrong output, crash at run time, hang,
compile error).

Steps, repeated until nothing more can be removed:
  - delete a function (its calls become 0)
  - delete a statement (anything that used a name it declared becomes 0)
  - replace an expression by 0, by 1, or by one of its operands
The guards that keep a program valid (`(e & 15) + 1` divisors, `& 63` shift
counts) are never removed.

usage:
  python3 -B tools/fuzz_reduce.py --seed 1 --program 17 [--compiler ./sutram_compiler] [--out DIR]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fuzz_valid as fv  # noqa: E402

DECLS = {'decl': 2, 'kpop': 1, 'snew': 1, 'kdecl': 1, 'arrdecl': 1}
USES_NAME = {'set': 1, 'arrset': 1, 'fset': 1, 'kpush': 1, 'kpop': 2}


def classify(comp, prog, structs, minimal, td):
    fdefs, body = prog
    it = fv.Interp(fdefs, budget=400000, structs=structs)
    try:
        it.run(body, {})
    except fv.Budget:
        return None, None
    except Exception:
        return None, None
    src = fv.program_src(prog, structs, minimal)
    sp, bp = Path(td, 'r.sm'), Path(td, 'r.bin')
    sp.write_text(src, encoding='utf-8')
    if bp.exists():
        bp.unlink()
    c = subprocess.run([comp, str(sp), str(bp)], capture_output=True, text=True, timeout=60)
    if c.returncode < 0:
        return 'COMPILER-CRASH', src
    if c.returncode != 0 or not bp.exists():
        return 'COMPILE-ERROR', src
    try:
        r = subprocess.run([str(bp)], capture_output=True, timeout=20)
    except subprocess.TimeoutExpired:
        return 'HANG', src
    if r.returncode < 0:
        return 'CRASH', src
    if r.stdout.decode('utf-8', 'replace').split() != it.out:
        return 'WRONG-OUTPUT', src
    return 'ok', src


# ------------------------------------------------------------ name removal
def kill_expr(e, dead):
    k = e[0]
    if k == 'var' and e[1] in dead: return ('lit', 0)
    if k in ('arr', 'fld', 'kget', 'klen') and e[1] in dead: return ('lit', 0)
    if k == 'call' and e[1] in dead: return ('lit', 0)
    if k in ('neg', 'not'): return (k, kill_expr(e[1], dead))
    if k == 'bin': return ('bin', e[1], kill_expr(e[2], dead), kill_expr(e[3], dead))
    if k == 'tern': return ('tern',) + tuple(kill_expr(x, dead) for x in e[1:])
    if k == 'call': return ('call', e[1], [kill_expr(a, dead) for a in e[2]])
    if k == 'arr': return ('arr', e[1], e[2], kill_expr(e[3], dead))
    return e


def kill_block(body, dead):
    out = []
    for st in body:
        k = st[0]
        if k in USES_NAME and st[USES_NAME[k]] in dead:
            if k == 'kpop':
                dead.add(st[1])
            continue
        out.append(kill_stmt(st, dead))
    return out


def kill_stmt(st, dead):
    k = st[0]
    E = lambda e: kill_expr(e, dead)
    if k == 'decl': return ('decl', st[1], st[2], E(st[3]))
    if k == 'set': return ('set', st[1], st[2], E(st[3]))
    if k == 'arrdecl': return ('arrdecl', st[1], st[2], [E(x) for x in st[3]])
    if k == 'arrset': return ('arrset', st[1], st[2], E(st[3]), E(st[4]))
    if k == 'if': return ('if', E(st[1]), kill_block(st[2], dead),
                          None if st[3] is None else kill_block(st[3], dead))
    if k == 'for': return ('for', st[1], st[2], st[3], kill_block(st[4], dead))
    if k in ('while', 'dowhile'): return (k, st[1], st[2], kill_block(st[3], dead))
    if k in ('brk', 'cnt', 'print', 'ret'): return (k, E(st[1]))
    if k == 'fset': return ('fset', st[1], st[2], E(st[3]))
    if k == 'kpush': return ('kpush', st[1], E(st[2]))
    return st


def declared(st):
    k = st[0]
    if k in DECLS: return {st[DECLS[k]]}
    return set()


def apply_dead(prog, dead):
    fdefs, body = prog
    nf = []
    for n, p, b in fdefs:
        if n in dead:
            continue
        nf.append((n, p, kill_block(b, set(dead))))
    return (nf, kill_block(body, set(dead)))


# --------------------------------------------------------------- candidates
def stmt_lists(prog):
    """Yield (path, list) for every statement list. path is used to rebuild."""
    fdefs, body = prog
    def walk(lst, path):
        yield path, lst
        for i, st in enumerate(lst):
            if st[0] == 'if':
                yield from walk(st[2], path + [(i, 2)])
                if st[3] is not None:
                    yield from walk(st[3], path + [(i, 3)])
            elif st[0] == 'for':
                yield from walk(st[4], path + [(i, 4)])
            elif st[0] in ('while', 'dowhile'):
                yield from walk(st[3], path + [(i, 3)])
    for fi, (n, p, b) in enumerate(fdefs):
        yield from walk(b, [('f', fi)])
    yield from walk(body, [('m',)])


def replace_list(prog, path, newlist):
    fdefs, body = prog
    def rebuild(lst, steps):
        if not steps:
            return newlist
        (i, slot), rest = steps[0], steps[1:]
        st = list(lst[i])
        st[slot] = rebuild(st[slot], rest)
        return lst[:i] + [tuple(st)] + lst[i + 1:]
    head = path[0]
    if head[0] == 'f':
        fi = head[1]
        n, p, b = fdefs[fi]
        nf = list(fdefs)
        nf[fi] = (n, p, rebuild(b, path[1:]))
        return (nf, body)
    return (fdefs, rebuild(body, path[1:]))


def all_names(st):
    """Names a statement declares, including those inside its blocks."""
    out = set(declared(st))
    k = st[0]
    if k == 'for': out.add(st[1])
    if k in ('while', 'dowhile'): out.add(st[1])
    for slot in {'if': (2, 3), 'for': (4,), 'while': (3,), 'dowhile': (3,)}.get(k, ()):
        if st[slot]:
            for s in st[slot]:
                out |= all_names(s)
    return out


def expr_sites(prog):
    """Every expression position: (function index or None, path-in-tuples)."""
    fdefs, body = prog
    sites = []
    def ex(e, rebuild, guard=False):
        if not guard and e[0] != 'lit':
            sites.append((e, rebuild))
        k = e[0]
        if k in ('neg', 'not'):
            ex(e[1], lambda x, e=e, r=rebuild: r((e[0], x)))
        elif k == 'bin':
            g = e[1] in ('/', '%', '<<', '>>')
            ex(e[2], lambda x, e=e, r=rebuild: r(('bin', e[1], x, e[3])))
            if g:   # keep the guard; reduce inside it
                b = e[3]
                inner = b[2][2] if e[1] in ('/', '%') else b[2]
                if e[1] in ('/', '%'):
                    mk = lambda x, e=e, r=rebuild: r(('bin', e[1], e[2],
                         ('bin', '+', ('bin', '&', x, ('lit', 15)), ('lit', 1))))
                else:
                    mk = lambda x, e=e, r=rebuild: r(('bin', e[1], e[2], ('bin', '&', x, ('lit', 63))))
                ex(inner, mk)
            else:
                ex(e[3], lambda x, e=e, r=rebuild: r(('bin', e[1], e[2], x)))
        elif k == 'tern':
            for j in (1, 2, 3):
                ex(e[j], lambda x, e=e, j=j, r=rebuild: r(e[:j] + (x,) + e[j + 1:]))
        elif k == 'call':
            for j, a in enumerate(e[2]):
                ex(a, lambda x, e=e, j=j, r=rebuild: r(('call', e[1], e[2][:j] + [x] + e[2][j + 1:])))
        elif k == 'arr':
            ex(e[3], lambda x, e=e, r=rebuild: r(('arr', e[1], e[2], x)), guard=True)
    for path, lst in stmt_lists(prog):
        for i, st in enumerate(lst):
            setl = lambda newst, path=path, lst=lst, i=i: replace_list(prog, path, lst[:i] + [newst] + lst[i + 1:])
            k = st[0]
            slots = {'decl': [3], 'set': [3], 'arrset': [4], 'if': [1], 'brk': [1], 'cnt': [1],
                     'print': [1], 'ret': [1], 'fset': [3], 'kpush': [2]}.get(k, [])
            for sl in slots:
                ex(st[sl], lambda x, st=st, sl=sl, setl=setl: setl(st[:sl] + (x,) + st[sl + 1:]))
    return sites


def simpler(e):
    out = [('lit', 0), ('lit', 1)]
    k = e[0]
    if k in ('neg', 'not'): out.append(e[1])
    if k == 'bin' and e[1] not in ('/', '%', '<<', '>>'): out += [e[2], e[3]]
    if k == 'bin' and e[1] in ('/', '%', '<<', '>>'): out.append(e[2])
    if k == 'tern': out += [e[2], e[3]]
    return out


def size(prog):
    return len(fv.program_src(prog, [], True))


def reduce(comp, prog, structs, minimal, want, log):
    with tempfile.TemporaryDirectory() as td:
        def ok(p):
            sig, _ = classify(comp, p, structs, minimal, td)
            return sig == want
        changed = True
        while changed:
            changed = False
            # functions, last first (later ones may call earlier ones)
            for fi in range(len(prog[0]) - 1, -1, -1):
                if fi >= len(prog[0]):
                    continue
                cand = apply_dead(prog, {prog[0][fi][0]})
                if ok(cand):
                    prog, changed = cand, True
            # statements
            progress = True
            while progress:
                progress = False
                for path, lst in list(stmt_lists(prog)):
                    for i in range(len(lst) - 1, -1, -1):
                        st = lst[i]
                        if st[0] == 'ret' and i == len(lst) - 1 and path[0][0] == 'f' and len(path) == 1:
                            continue
                        cand = replace_list(prog, path, lst[:i] + lst[i + 1:])
                        dead = all_names(st)
                        if dead:
                            cand = apply_dead(cand, dead)
                        if ok(cand):
                            prog, progress, changed = cand, True, True
                            log('  statements: %d bytes' % size(prog))
                            break
                    if progress:
                        break
            # expressions
            progress = True
            while progress:
                progress = False
                for e, rebuild in expr_sites(prog):
                    for s in simpler(e):
                        if s == e:
                            continue
                        cand = rebuild(s)
                        if ok(cand):
                            prog, progress, changed = cand, True, True
                            break
                    if progress:
                        break
            # struct declarations nobody uses
        used = fv.program_src(prog, [], True)
        structs = [s for s in structs if (s[1] if s[0] == '@g' else s[0]) in used]
        sig, src = classify(comp, prog, structs, minimal, td)
        it = fv.Interp(prog[0], structs=structs); it.run(prog[1], {})
        return prog, structs, src, it.out, sig


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--program', type=int, required=True)
    ap.add_argument('--compiler', default='./sutram_compiler')
    ap.add_argument('--out', default='fuzz-valid-out')
    a = ap.parse_args(argv)
    comp = os.path.abspath(a.compiler)
    prog, structs, minimal, exp = fv.make(a.seed, a.program)
    with tempfile.TemporaryDirectory() as td:
        want, _ = classify(comp, prog, structs, minimal, td)
    print('program %d of seed %d: %s, %d bytes' % (a.program, a.seed, want, size(prog)))
    if want == 'ok':
        return 0
    prog, structs, src, exp, sig = reduce(comp, prog, structs, minimal, want, lambda m: None)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tag = 'reduced-%d-%d' % (a.seed, a.program)
    hdr = '# fuzz_reduce: seed=%d program=%d, %s\n# expected: %s\n' % (a.seed, a.program, sig, ' '.join(exp))
    (out / (tag + '.sm')).write_text(hdr + src, encoding='utf-8')
    print('reduced to %d bytes: %s' % (len(src), out / (tag + '.sm')))
    sys.stdout.write(hdr + src)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
