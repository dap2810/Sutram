#!/usr/bin/env python3
"""ROUND-15 WS3: how strong is the proof of each of the 303 library functions?

For every `prakriya` in lib/*.smlib this tool makes mutants shaped like real
bugs, runs every proof that can reach the function against each mutant (the
same proofs and the same rules as tools/lib_proof_gaps.py: tests/stdlib
goldens, example goldens, tools/proof_props.py properties), and counts how many
mutants the proofs kill.

Mutant kinds (one change each):
  S   the whole body replaced by `prati 7777777`        (the smoke test)
  R   every `prati e` becomes `prati (e) + 1`           (off-by-one result)
  C   one comparison flipped: < <=, > >=, == !=          (a boundary moved)
  N   one `yadi (c)` condition negated: `yadi ((c) == 0)`
  A   one arithmetic operator replaced: + -, - +, * +, / *, % /
  L   one logical operator swapped: && ||, || &&
  K   one integer literal n becomes n + 1
  D   one statement line deleted (an assignment, a store, a call statement)

A mutant that does not compile proves nothing and is not counted. A run that
times out or crashes counts as killed (the proof noticed).

The score of a function is (non-S mutants killed) / (non-S mutants). The S
mutant is reported separately: a proof that kills S and nothing else is a
smoke test. Surviving mutants are not all bugs the proofs miss: some are
EQUIVALENT (no input can tell them apart). Survivors that tools/lib_gap_reviewed.json
or the R8-R11 rules already decided are marked; the rest are undecided.

usage:
  python3 -B tools/lib_mutant_score.py [--only MODULE] [--jobs 2] [--cap 40]
         [--json build/lib-mutant-score.json] [--md build/lib-mutant-score.md]
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_proof_gaps as g  # noqa: E402

ROOT = g.ROOT
LIB = g.LIB
INT_RE = re.compile(r'(?<![\w.])(\d+)(?![\w.])')
ASSIGN_RE = re.compile(r'^\s*[A-Za-z_][\w]*(\s*\.\s*\w+|\s*\[[^\]]*\])?\s*(=|\+=|-=|\*=|/=|%=)(?!=)')
CALLST_RE = re.compile(r'^\s*[A-Za-z_]\w*\s*\(.*\)\s*$')
KEYWORDS = {'prati', 'yadi', 'anya', 'chakra', 'yavat', 'kuru', 'vitti', 'mala', 'kosh', 'likha',
            'lkhb', 'shabda', 'krama', 'agrim', 'prakriya', 'sutra', 'anka', 'sankhya', 'dasham', 'satya'}
ARITH = {'+': '-', '-': '+', '*': '+', '/': '*', '%': '/'}


def body_lines(f):
    if f['braceless']:
        return [f['end']]
    return list(range(f['start'] + 1, f['end'] + 1))


def code_positions(line):
    """Indexes of the line that are code (outside strings and # comments)."""
    out = set()
    for a, b in g.code_spans(line):
        out.update(range(a, b))
    return out


def mutants(path: Path, f: dict, cap: int, rng: random.Random):
    lines = path.read_text(encoding='utf-8').split('\n')
    out = [('S', g.mutate(path, f))]
    # R and C exactly as lib_proof_gaps.py --deep, but without its cap of 12
    for tag, text in g.deep_mutants(path, f, cap=10 ** 6):
        out.append((tag, text))
    extra = []
    for k in body_lines(f):
        t = lines[k]
        code = code_positions(t)
        stripped = t.strip()
        if not stripped or stripped.startswith('#'):
            continue
        # N: negate a yadi condition
        for m in re.finditer(r'\byadi\s*\(', t):
            if m.start() not in code:
                continue
            j, depth = m.end(), 1
            while j < len(t) and depth:
                depth += {'(': 1, ')': -1}.get(t[j], 0)
                j += 1
            if depth == 0:
                cond = t[m.end():j - 1]
                extra.append(('N@L%d' % (k + 1), k, t[:m.end()] + '(' + cond + ') == 0' + t[j - 1:]))
        # A, L: operators in code
        for j, c in enumerate(t):
            if j not in code:
                continue
            two = t[j:j + 2]
            if two in ('&&', '||') and (j == 0 or t[j - 1] not in '&|'):
                rep = '||' if two == '&&' else '&&'
                extra.append(('L:%s@L%d' % (two, k + 1), k, t[:j] + rep + t[j + 2:]))
            if c in ARITH:
                prev = t[:j].rstrip()
                nxt = t[j + 1:j + 2]
                if not prev or not (prev[-1].isalnum() or prev[-1] in ')]_'):
                    continue                          # unary minus, or start of line
                if nxt in ('=',) or nxt == c or (c in '<>'):
                    continue                          # compound assignment, ++, --
                if prev.split()[-1] in KEYWORDS:
                    continue
                extra.append(('A:%s@L%d' % (c, k + 1), k, t[:j] + ARITH[c] + t[j + 1:]))
        # K: integer literals (not in array or kosh sizes, not in nirmmita)
        if not re.match(r'^\s*(mala|kosh)\b', t) and 'nirmmita' not in t:
            for m in INT_RE.finditer(t):
                if m.start() in code:
                    extra.append(('K:%s@L%d' % (m.group(1), k + 1), k,
                                  t[:m.start()] + str(int(m.group(1)) + 1) + t[m.end():]))
        # D: delete a statement line
        if k != f['end'] or f['braceless'] is False:
            s = stripped.split('#')[0].strip()
            word = re.match(r'[A-Za-z_]\w*', s)
            if s and not s.endswith('{') and not s.startswith('}') and word and word.group(0) not in KEYWORDS:
                if ASSIGN_RE.match(s) or CALLST_RE.match(s):
                    extra.append(('D@L%d' % (k + 1), k, ''))
    if len(extra) > cap:
        extra = rng.sample(extra, cap)
        extra.sort(key=lambda e: (e[1], e[0]))
    for tag, k, new in extra:
        nl = list(lines)
        nl[k] = new
        out.append((tag, '\n'.join(nl)))
    return out


def score_function(args):
    compiler, f, proofs, prop_idx, workroot, cap = args
    tree = Path(tempfile.mkdtemp(dir=workroot))
    path = LIB / (f['module'] + '.smlib')
    rng = random.Random('%s.%s' % (f['module'], f['name']))
    res = {'module': f['module'], 'name': f['name'], 'mutants': []}
    t0 = time.time()
    try:
        g.make_tree(tree)
        header, _ = g.probe_header(compiler, tree, f['module'])
        for tag, text in mutants(path, f, cap, rng):
            g.make_tree(tree, {f['module']: text})
            if not g.mutant_compiles(compiler, tree, header):
                res['mutants'].append({'mutant': tag, 'result': 'stillborn'})
                continue
            by = g.kill(compiler, tree, proofs, prop_idx)
            res['mutants'].append({'mutant': tag, 'result': 'killed' if by else 'SURVIVED',
                                   'by': by[:1]})
        res['seconds'] = round(time.time() - t0, 1)
        return res
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiler', default=str(ROOT / 'sutram_compiler'))
    ap.add_argument('--only', help='one module')
    ap.add_argument('--function', help='one function')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--cap', type=int, default=40, help='at most this many N/A/L/K/D mutants per function')
    ap.add_argument('--json', default=str(ROOT / 'build/lib-mutant-score.json'))
    ap.add_argument('--count-only', action='store_true')
    a = ap.parse_args(argv)
    compiler = str(Path(a.compiler).resolve())

    funcs = []
    for p in sorted(LIB.glob('*.smlib')):
        funcs += g.parse_module(p)
    todo = [f for f in funcs if (not a.only or f['module'] == a.only) and (not a.function or f['name'] == a.function)]
    if a.count_only:
        n = {}
        for f in todo:
            for tag, _ in mutants(LIB / (f['module'] + '.smlib'), f, a.cap, random.Random('%s.%s' % (f['module'], f['name']))):
                n[tag[0]] = n.get(tag[0], 0) + 1
        print(len(todo), 'functions;', sum(n.values()), 'mutants:', n)
        return 0
    deps = {p.stem: g.module_imports(p.read_text(encoding='utf-8')) for p in LIB.glob('*.smlib')}
    workroot = Path(tempfile.mkdtemp(prefix='libscore-'))
    base = g.make_tree(workroot / 'base')
    golds = g.golden_proofs()
    for p in golds:
        p['mods'] = g.closure(g.module_imports(p['src']), deps)
    bad = [p['id'] for p in golds if p['mods'] and not g.run_golden(compiler, base, p)[0]]
    if bad:
        print('BASELINE FAILS:', bad); return 2
    _, props = g.load_props()
    prop_src, prop_mods = [], []
    for i, (label, _) in enumerate(props):
        rec = []
        ok, why = g.run_prop(compiler, base, i, rec)
        if not ok:
            print('BASELINE property fails:', label, why); return 2
        text = '\n'.join(rec)
        prop_src.append(text)
        prop_mods.append(g.closure(g.module_imports(text), deps))
    lib_golds = [p for p in golds if p['mods']]
    jobs = []
    for f in todo:
        word = re.compile(r'(?<![\w])' + re.escape(f['name']) + r'(?![\w])')
        rel = [p for p in lib_golds if f['module'] in p['mods']]
        relp = [i for i in range(len(props)) if f['module'] in prop_mods[i]]
        f['named_by'] = [p['id'] for p in rel if word.search(p['src'])] + \
                        ['proof_props: ' + props[i][0] for i in relp if word.search(prop_src[i])]
        rel.sort(key=lambda p: not word.search(p['src']))
        relp.sort(key=lambda i: not word.search(prop_src[i]))
        jobs.append((compiler, f, rel, relp, str(workroot), a.cap))
    print('%d functions; proofs: %d goldens that import lib, %d properties' % (len(todo), len(lib_golds), len(props)), flush=True)
    rows = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        for n, r in enumerate(ex.map(score_function, jobs, chunksize=1)):
            f = todo[n]
            ms = r['mutants']
            live = [m for m in ms if m['result'] != 'stillborn']
            nons = [m for m in live if m['mutant'] != 'S']
            row = {'module': f['module'], 'name': f['name'], 'params': f['params'],
                   'named_by': f['named_by'][:5], 'named_count': len(f['named_by']),
                   'S_killed': any(m['mutant'] == 'S' and m['result'] == 'killed' for m in ms),
                   'total': len(nons), 'killed': sum(m['result'] == 'killed' for m in nons),
                   'stillborn': sum(m['result'] == 'stillborn' for m in ms),
                   'survivors': [m['mutant'] for m in nons if m['result'] == 'SURVIVED'],
                   'killed_by': sorted({m['by'][0] for m in live if m.get('by')}),
                   'mutants': [[m['mutant'], m['result'], (m.get('by') or [''])[0]] for m in ms],
                   'seconds': r.get('seconds')}
            rows.append(row)
            print('%-10s %-28s S=%s %3d/%-3d %5.1fs  (%d done, %.0f s)' % (
                f['module'], f['name'], 'k' if row['S_killed'] else '-', row['killed'], row['total'],
                row['seconds'] or 0, n + 1, time.time() - t0), flush=True)
    shutil.rmtree(workroot, ignore_errors=True)
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps(rows, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('wrote', a.json)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
