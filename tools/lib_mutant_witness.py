#!/usr/bin/env python3
"""Look for an input that tells a surviving mutant apart from the real function.

lib_proof_gaps.py --deep reports, per library function, the off-by-one (R) and boundary (C) mutants that
no proof kills. A survivor is one of two things:

  * a real gap: some input gives a different result, and no proof uses such an input;
  * an equivalent mutant: no input can tell them apart (`a > b ? a : b` vs `a >= b ? a : b`).

This tool runs both versions side by side on the same inputs and prints the first input where they differ
(a WITNESS). It only tries functions whose parameters are all plain numbers (never indexed, never used
with `.`), because a list or a string needs a generator of its own. For the others it says NOT-TRIED.

No witness after the whole input set is evidence of equivalence, not a proof of it.

    python3 tools/lib_mutant_witness.py --compiler ./sutram_compiler --gaps build/lib-proof-gaps.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_proof_gaps as G  # noqa: E402

VALUES = [-7, -2, -1, 0, 1, 2, 3, 4, 5, 7, 10, 12, 16, 100, 1000, 3037000499, 2 ** 62, 2 ** 63 - 1, -(2 ** 63 - 1)]
BATCH = 40


def _split_args(text: str) -> list[str]:
    out, depth, cur = [], 0, ''
    for c in text:
        if c in '([':
            depth += 1
        elif c in ')]':
            if depth == 0:
                break
            depth -= 1
        elif c == ',' and depth == 0:
            out.append(cur)
            cur = ''
            continue
        cur += c
    out.append(cur)
    return [x.strip() for x in out]


def pointer_params(funcs: dict) -> dict[tuple, set[int]]:
    """Which parameter positions of each library function hold a list, string or record.
    A parameter is one if it (or a plain local copy of it) is indexed or used with `.`, or if it is
    passed on to a pointer parameter of another library function. Iterated to a fixed point."""
    bodies, names = {}, {}
    for key, f in funcs.items():
        text = (G.LIB / (f['module'] + '.smlib')).read_text(encoding='utf-8').split('\n')
        bodies[key] = '\n'.join(G.strip_code(t) for t in text[f['start'] + 1:f['end'] + 1]) \
            if not f['braceless'] or True else ''
        names.setdefault(f['name'], key)
    params = {k: [p.strip() for p in f['params'].split(',') if p.strip()] for k, f in funcs.items()}
    ptr: dict[tuple, set[int]] = {k: set() for k in funcs}
    # builtins that read or write memory, and which argument is the address
    for bn in ('akshar', 'akshar_rakh', 'pad8', 'likh8', 'pad8c', 'likh8c', 'pankti_len', 'vartani_len',
               'vartani_cmp', 'vartani_cat', 'vartani_cp', 'smaran', 'smaran_cp', 'kosh_push', 'kosh_pop',
               'kosh_len', 'kosh_cap', 'kosh_clear', 'kosh_empty', 'kosh_peek', 'kosh_enqueue',
               'kosh_dequeue', 'sankhya_yog', 'sankhya_gunan', 'sankhya_dot', 'lkhb'):
        key = ('<builtin>', bn)
        names[bn] = key
        ptr[key] = {0} if bn not in ('vartani_cmp', 'vartani_cat', 'vartani_cp', 'smaran_cp',
                                     'sankhya_yog', 'sankhya_gunan', 'sankhya_dot') else {0, 1}

    def aliases(body, p):
        al = {p}
        for m in re.finditer(r'vitti\s+(\w+)\s*=\s*' + re.escape(p) + r'\b\s*$', body, re.M):
            al.add(m.group(1))
        return al

    changed = True
    while changed:
        changed = False
        for k, body in bodies.items():
            for i, p in enumerate(params[k]):
                if i in ptr[k]:
                    continue
                al = aliases(body, p)
                hit = any(re.search(r'\b' + re.escape(x) + r'\s*[\[.]', body) for x in al)
                if not hit:
                    for m in re.finditer(r'\b(\w+)\s*\(', body):
                        callee = names.get(m.group(1))
                        if not callee or not ptr[callee]:
                            continue
                        args = _split_args(body[m.end():])
                        for j in ptr[callee]:
                            # the parameter itself, or an address computed from it (`p + i * 8`)
                            if j < len(args) and re.search(r'^\s*(' + '|'.join(map(re.escape, al)) +
                                                           r')\b', args[j]):
                                hit = True
                if hit:
                    ptr[k].add(i)
                    changed = True
    return ptr


def inputs(arity: int, rng: random.Random) -> list[tuple]:
    if arity == 0:
        return [()]
    if arity == 1:      # every byte value (character classes), and the usual edges beyond it
        return [(v,) for v in [*range(-20, 300), 1000, 1023, 1024, 4096, 10 ** 6, 10 ** 9, 3037000499,
                               3037000500, 2 ** 31, 2 ** 32, 2 ** 62, 2 ** 63 - 1]]
    if len(VALUES) ** arity <= 400:
        return list(itertools.product(VALUES, repeat=arity))
    return [tuple(rng.choice(VALUES) for _ in range(arity)) for _ in range(600)]


def run(compiler: str, tree: Path, header: str, name: str, args: list[tuple]) -> list[str | None]:
    """One output per input; None where the program crashed or timed out on it."""
    out: list[str | None] = []
    for i in range(0, len(args), BATCH):
        chunk = args[i:i + BATCH]
        res = _run_chunk(compiler, tree, header, name, chunk)
        if res is None:                      # something in the chunk crashed: run them one by one
            res = [(_run_chunk(compiler, tree, header, name, [a]) or [None])[0] for a in chunk]
        out.extend(res)
    return out


def first_difference(compiler, tree, header, name, args, want):
    """args are inputs on which the real function runs cleanly; want its outputs.
    Returns (input, real, mutant) for the first input where the mutant differs (crash = 'CRASH')."""
    for i in range(0, len(args), BATCH):
        chunk, w = args[i:i + BATCH], want[i:i + BATCH]
        got = _run_chunk(compiler, tree, header, name, chunk)
        if got == w:
            continue
        for x, wx in zip(chunk, w):
            g = _run_chunk(compiler, tree, header, name, [x])
            g = g[0] if g else 'CRASH'
            if g != wx:
                return x, wx, g
    return None


def _run_chunk(compiler, tree, header, name, chunk):
    body = ''.join(f'    likha({name}({", ".join(str(v) if v >= 0 else f"0 - {-v}" for v in a)}))\n'
                   for a in chunk)
    src, exe = tree / 'w.sm', tree / 'w.bin'
    src.write_text(header + 'mukhya() {\n' + body + '}\n', encoding='utf-8')
    c = subprocess.run([compiler, str(src), str(exe)], capture_output=True, cwd=str(tree))
    if c.returncode != 0:
        return None
    try:
        r = subprocess.run([str(exe)], capture_output=True, timeout=1, cwd=str(tree))
    except subprocess.TimeoutExpired:
        return None
    lines = r.stdout.decode('utf-8', 'replace').split('\n')
    if r.returncode != 0 or len(lines) < len(chunk):
        return None
    return lines[:len(chunk)]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--compiler', default=str(G.ROOT / 'sutram_compiler'))
    ap.add_argument('--gaps', default=str(G.ROOT / 'build/lib-proof-gaps.json'))
    ap.add_argument('--json', default=str(G.ROOT / 'build/lib-mutant-witness.json'))
    a = ap.parse_args(argv)
    compiler = str(Path(a.compiler).resolve())
    rows = json.load(open(a.gaps, encoding='utf-8'))
    funcs = {(f['module'], f['name']): f for p in sorted(G.LIB.glob('*.smlib')) for f in G.parse_module(p)}
    ptrs = pointer_params(funcs)
    work = Path(tempfile.mkdtemp())
    report = []
    try:
        for r in rows:
            if not r.get('survivors'):
                continue
            f = funcs[(r['module'], r['name'])]
            path = G.LIB / (f['module'] + '.smlib')
            text = path.read_text(encoding='utf-8').split('\n')
            if ptrs[(f['module'], f['name'])]:
                for m in r['survivors']:
                    report.append({'module': f['module'], 'name': f['name'], 'mutant': m, 'result': 'NOT-TRIED',
                                   'why': 'a parameter is a list, string or record'})
                continue
            orig = Path(tempfile.mkdtemp(dir=work))
            G.make_tree(orig)
            header, _ = G.probe_header(compiler, orig, f['module'])
            arity = len([p for p in f['params'].split(',') if p.strip()])
            args = inputs(arity, random.Random(20261019))
            want = run(compiler, orig, header, f['name'], args)
            again = run(compiler, orig, header, f['name'], args)   # drop inputs whose result is not stable (addresses)
            good = [(x, w) for x, w, v in zip(args, want, again) if w is not None and w == v]
            args, want = [x for x, _ in good], [w for _, w in good]
            print(f"{f['module']}.{f['name']}: {len(args)} inputs, {len(r['survivors'])} survivors", flush=True)
            mutants = dict(G.deep_mutants(path, f))
            if not args:
                for m in r['survivors']:
                    report.append({'module': f['module'], 'name': f['name'], 'mutant': m, 'result': 'NOT-TRIED',
                                   'why': 'no number input runs cleanly (the parameters are addresses)'})
                continue
            for m in r['survivors']:
                mt = Path(tempfile.mkdtemp(dir=work))
                G.make_tree(mt, {f['module']: mutants[m]})
                wit = first_difference(compiler, mt, header, f['name'], args, want)
                if wit:
                    report.append({'module': f['module'], 'name': f['name'], 'mutant': m, 'result': 'WITNESS',
                                   'input': list(wit[0]), 'real': wit[1], 'mutant_gives': wit[2]})
                else:
                    report.append({'module': f['module'], 'name': f['name'], 'mutant': m,
                                   'result': 'NO-WITNESS', 'inputs_tried': len(args)})
                shutil.rmtree(mt, ignore_errors=True)
            shutil.rmtree(orig, ignore_errors=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding='utf-8')
    from collections import Counter
    print(dict(Counter(x['result'] for x in report)))
    for x in report:
        if x['result'] == 'WITNESS':
            print(f"WITNESS  {x['module']}.{x['name']}{tuple(x['input'])}  real={x['real']}  {x['mutant']} gives {x['mutant_gives']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
