#!/usr/bin/env python3
"""Which standard-library functions does a proof actually check? (ROUND-08, Step 5)

    python3 tools/lib_proof_gaps.py [--compiler ./sutram_compiler] [--only MODULE] [--jobs 2]
            [--json build/lib-proof-gaps.json] [--md build/lib-proof-gaps.md]

"Has a test" is not the question. For each of the library's prakriya this tool asks:
if this function were broken, would any proof notice? It answers by mutation:

  1. The function's body is replaced with `prati 7777777` (signature kept), in a private
     copy of lib/. Nothing in the repository is modified.
  2. Every proof program that could reach it (it imports the module, directly or through
     another module) is re-run against that copy:
       * tests/stdlib/*.sm       -> stdout and exit must equal the golden (as proof_lib.py)
       * examples/*.sm + goldens -> stdout and exit must equal the golden (as run_tests.py)
       * tools/proof_props.py    -> each property's own pass/fail verdict
  3. The function is DETECTED if at least one of those proofs fails.

Each function then gets one status:
  PROVEN           a proof that names it fails when it is broken
  PROVEN-INDIRECT  no proof names it, but one fails when it is broken (via a caller)
  NAMED-NOT-CHECKED a proof calls it, yet breaking it fails nothing (looks like coverage, is not)
  UNPROVEN         no proof reaches it at all

The whole-body mutant only shows that a function's result reaches a checked output. --deep
also asks whether its boundaries are checked, with mutants shaped like real bugs:
  R      every `prati e` becomes `prati (e) + 1` (an off-by-one result)
  C<k>   the k-th comparison in the body flipped, one at a time: < <=, > >=, == !=
         (a boundary moved by one), at most 12 per function
A mutant that does not compile proves nothing and is not counted. A surviving mutant is a
candidate gap: tools/lib_mutant_witness.py looks for an input that tells it apart, and
tools/lib_gap_report.py gives each survivor a verdict and writes the module-by-module list.

The properties use a fresh random.Random(SEED + index) each, so they can run alone; the
baseline run of every proof must pass first, or the tool stops.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'lib'
SENTINEL = '7777777'
NAME_RE = re.compile(r'^prakriya\s+([^\s(]+)\s*\(([^)]*)\)\s*(\{)?\s*(#.*)?$')


# --------------------------------------------------------------------------- library model
def strip_code(line: str) -> str:
    """Remove string literals and # comments, for brace counting."""
    out, i, q = [], 0, None
    while i < len(line):
        c = line[i]
        if q:
            if c == '\\':
                i += 2
                continue
            if c == q:
                q = None
            i += 1
            continue
        if c in '"\'':
            q = c
        elif c == '#':
            break
        else:
            out.append(c)
        i += 1
    return ''.join(out)


def parse_module(path: Path) -> list[dict]:
    lines = path.read_text(encoding='utf-8').split('\n')
    funcs, i = [], 0
    while i < len(lines):
        m = NAME_RE.match(lines[i])
        if not m:
            i += 1
            continue
        name, params, brace = m.group(1), m.group(2).strip(), m.group(3)
        # contract: the comment block directly above
        j, doc = i - 1, []
        while j >= 0 and lines[j].lstrip().startswith('#'):
            doc.insert(0, lines[j].lstrip('# ').rstrip())
            j -= 1
        if brace:
            depth, k = 0, i
            while k < len(lines):
                s = strip_code(lines[k])
                depth += s.count('{') - s.count('}')
                if depth == 0 and k > i or (k == i and depth == 0):
                    break
                k += 1
            end = k
        else:  # braceless body: exactly one statement, the next code line
            k = i + 1
            while k < len(lines) and (not lines[k].strip() or lines[k].lstrip().startswith('#')):
                k += 1
            end = k
        funcs.append({'module': path.stem, 'name': name, 'params': params, 'start': i, 'end': end,
                      'braceless': not brace, 'doc': ' '.join(d for d in doc if d)})
        i = end + 1
    return funcs


def mutate(path: Path, f: dict) -> str:
    """S: the whole body replaced by `prati 7777777` (the function does nothing, returns junk)."""
    lines = path.read_text(encoding='utf-8').split('\n')
    new = lines[:f['start']] + [f"prakriya {f['name']}({f['params']}) {{ prati {SENTINEL} }}"] + lines[f['end'] + 1:]
    return '\n'.join(new)


RET_RE = re.compile(r'\bprati\s+([^{}#\n]+?)(\s*(?:\}|#|$))')
REL = [('<=', '<'), ('>=', '>'), ('==', '!='), ('!=', '=='), ('<', '<='), ('>', '>=')]


def code_spans(line: str) -> list[tuple[int, int]]:
    """Index ranges of a line that are code (outside strings and # comments)."""
    spans, i, start, q = [], 0, 0, None
    while i < len(line):
        c = line[i]
        if q:
            if c == '\\':
                i += 2
                continue
            if c == q:
                q, start = None, i + 1
        elif c in '"\'':
            spans.append((start, i))
            q = c
        elif c == '#':
            spans.append((start, i))
            return spans
        i += 1
    if not q:
        spans.append((start, len(line)))
    return spans


def deep_mutants(path: Path, f: dict, cap: int = 12) -> list[tuple[str, str]]:
    """R: every `prati e` becomes `prati (e) + 1`.  C<k>: the k-th comparison operator in the
    body flipped (< <=, > >=, == !=), one at a time. These are the shapes real bugs take:
    an off-by-one result, a boundary moved by one."""
    lines = path.read_text(encoding='utf-8').split('\n')
    body = range(f['start'] + (0 if f['braceless'] else 0), f['end'] + 1)
    out = []
    # R
    new, changed = list(lines), False
    for k in body:
        if k == f['start'] and not f['braceless'] and lines[k].rstrip().endswith('{'):
            continue
        t = lines[k]
        m = RET_RE.search(t)
        if m and m.group(1).strip():
            new[k] = t[:m.start(1)] + '(' + m.group(1).strip() + ') + 1' + t[m.end(1):]
            changed = True
    if changed:
        out.append(('R', '\n'.join(new)))
    # C
    sites = []
    for k in body:
        if k == f['start']:
            continue
        t = lines[k]
        for a, b in code_spans(t):
            j = a
            while j < b:
                for op, rep in REL:
                    if t.startswith(op, j) and not (op in ('<', '>') and t[j + 1:j + 2] in ('=', '<', '>')) \
                            and not (op in ('<', '>') and j > 0 and t[j - 1] in '<>-'):
                        sites.append((k, j, op, rep))
                        j += len(op) - 1
                        break
                j += 1
    for n, (k, j, op, rep) in enumerate(sites[:cap]):
        new = list(lines)
        new[k] = lines[k][:j] + rep + lines[k][j + len(op):]
        out.append((f'C{n + 1}:{op}->{rep}@L{k + 1}', '\n'.join(new)))
    return out


def module_imports(text: str) -> set[str]:
    return {m.group(1) for m in re.finditer(r'^\s*yoj\s+([A-Za-z0-9_]+)', text, re.M)}


def closure(mods: set[str], deps: dict[str, set[str]]) -> set[str]:
    seen, todo = set(), list(mods)
    while todo:
        m = todo.pop()
        if m in seen:
            continue
        seen.add(m)
        todo.extend(deps.get(m, ()))
    return seen


# --------------------------------------------------------------------------- proofs
def load_run_tests():
    spec = importlib.util.spec_from_file_location('run_tests', ROOT / 'tests/run_tests.py')
    mod = importlib.util.module_from_spec(spec)
    sys.argv, saved = ['run_tests.py'], sys.argv
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod


def golden_proofs() -> list[dict]:
    rt = load_run_tests()
    langs, cwds = getattr(rt, 'LANG', {}), getattr(rt, 'CWD', {})
    out = []
    for sm in sorted((ROOT / 'tests/stdlib').glob('*.sm')):
        o, e = sm.with_suffix('.out'), sm.with_suffix('.exit')
        if o.exists():
            out.append({'kind': 'stdlib', 'id': 'tests/stdlib/' + sm.name, 'src': sm.read_text(encoding='utf-8'),
                        'out': o.read_bytes(), 'exit': int(e.read_text()) if e.exists() else 0,
                        'lang': None, 'cwd': str(ROOT)})
    exp = ROOT / 'tests/expect'
    for sm in sorted((ROOT / 'examples').glob('*.sm')):
        n = sm.stem
        o, e = exp / (n + '.out'), exp / (n + '.exit')
        if not o.exists() or (exp / (n + '.compile_fail')).exists():
            continue
        cwd = cwds.get(n, str(ROOT))
        out.append({'kind': 'example', 'id': 'examples/' + sm.name, 'src': sm.read_text(encoding='utf-8'),
                    'out': o.read_bytes(), 'exit': int(e.read_text()) if e.exists() else 0,
                    'lang': langs.get(n), 'cwd': cwd if os.path.isabs(cwd) else str(ROOT / cwd)})
    return out


def make_tree(base: Path, lib_override: dict[str, str] | None = None) -> Path:
    """base/lib = repository lib/ + examples/lib/ (+ an overridden module)."""
    lib = base / 'lib'
    if lib.exists():
        shutil.rmtree(lib)
    lib.mkdir(parents=True)
    for d in (ROOT / 'examples/lib', LIB):
        for p in d.glob('*.smlib'):
            shutil.copyfile(p, lib / p.name)
    for name, text in (lib_override or {}).items():
        (lib / (name + '.smlib')).write_text(text, encoding='utf-8')
    return base


def run_golden(compiler: str, tree: Path, p: dict) -> tuple[bool, str]:
    src = tree / 'prog.sm'
    src.write_text(p['src'], encoding='utf-8')
    exe = tree / 'prog.bin'
    cmd = [compiler] + (['--lang', p['lang']] if p['lang'] else []) + [str(src), str(exe)]
    try:
        c = subprocess.run(cmd, capture_output=True, cwd=p['cwd'], timeout=30)
        if c.returncode != 0:
            return False, 'compile failed'
        r = subprocess.run([str(exe)], capture_output=True, cwd=p['cwd'], timeout=10)
    except subprocess.TimeoutExpired:
        return False, 'timeout'
    finally:
        exe.unlink(missing_ok=True)
    ok = r.stdout == p['out'] and r.returncode == p['exit']
    return ok, '' if ok else f'stdout/exit differ (exit {r.returncode})'


_PROPS = None


def load_props():
    global _PROPS
    if _PROPS is None:
        spec = importlib.util.spec_from_file_location('proof_props', ROOT / 'tools/proof_props.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        src = (ROOT / 'tools/proof_props.py').read_text(encoding='utf-8')
        listing = re.findall(r'\("([^"]+)",\s*(prop_\w+)\)', src)
        _PROPS = (mod, [(label, getattr(mod, fn)) for label, fn in listing if hasattr(mod, fn)])
    return _PROPS


def run_prop(compiler: str, tree: Path, index: int, record: list | None = None) -> tuple[bool, str]:
    mod, props = load_props()
    label, fn = props[index]

    def run_sm(_compiler, name, code):
        if record is not None:
            record.append(code)
        sm = tree / f'prop_{index}.sm'
        sm.write_text(code, encoding='utf-8')
        exe = tree / f'prop_{index}.bin'
        try:
            c = subprocess.run([compiler, str(sm), str(exe)], capture_output=True, text=True, errors='replace', cwd=str(ROOT), timeout=30)
            if c.returncode != 0:
                return False, 'compile failed'
            r = subprocess.run([str(exe)], capture_output=True, text=True, errors='replace', cwd=str(ROOT), timeout=30)
        except subprocess.TimeoutExpired:
            return False, 'timeout'
        finally:
            exe.unlink(missing_ok=True)
        if r.returncode != 0:
            return False, f'runtime exit {r.returncode}'
        return True, r.stdout.strip()

    mod.run_sm = run_sm
    try:
        res = fn(compiler, random.Random(mod.SEED + index))
        ok = bool(res[0]) if isinstance(res, tuple) else bool(res)
    except Exception as e:  # a crash or timeout inside the property is a failure
        return False, f'{type(e).__name__}: {e}'[:120]
    return ok, ''


# --------------------------------------------------------------------------- worker
def mutant_compiles(compiler: str, tree: Path, header: str | None) -> bool:
    """A mutant that does not compile proves nothing; it must not count as detected."""
    if header is None:
        return True
    src = tree / 'probe.sm'
    src.write_text(header + 'mukhya() {\n    likha(1)\n}\n', encoding='utf-8')
    r = subprocess.run([compiler, str(src), str(tree / 'probe.bin')], capture_output=True, cwd=str(ROOT))
    (tree / 'probe.bin').unlink(missing_ok=True)
    return r.returncode == 0


def probe_header(compiler: str, tree: Path, module: str) -> tuple[str | None, bool]:
    """The `yoj` lines a program needs for the unmutated module to compile.
    Returns (header, standalone). standalone is False when the module does not compile on its own."""
    h = f'yoj {module}\n'
    if mutant_compiles(compiler, tree, h):
        return h, True
    allh = ''.join(f'yoj {m.stem}\n' for m in sorted(LIB.glob('*.smlib')))
    if mutant_compiles(compiler, tree, allh):
        return allh, False
    return None, False


def kill(compiler: str, tree: Path, proofs: list, prop_idx: list) -> list[str]:
    for p in proofs:
        ok, why = run_golden(compiler, tree, p)
        if not ok:
            return [p['id']]                  # one failing proof is enough
    for i in prop_idx:
        ok, why = run_prop(compiler, tree, i)
        if not ok:
            return ['proof_props: ' + load_props()[1][i][0]]
    return []


def check_function(args) -> dict:
    compiler, f, proofs, prop_idx, workroot, deep = args
    tree = Path(tempfile.mkdtemp(dir=workroot))
    path = LIB / (f['module'] + '.smlib')
    res = {'module': f['module'], 'name': f['name'], 'detected_by': [], 'stillborn_S': False, 'mutants': []}
    try:
        make_tree(tree)
        header, res['standalone'] = probe_header(compiler, tree, f['module'])
        make_tree(tree, {f['module']: mutate(path, f)})
        if not mutant_compiles(compiler, tree, header):
            res['stillborn_S'] = True
        else:
            res['detected_by'] = kill(compiler, tree, proofs, prop_idx)
        if deep:
            for tag, text in deep_mutants(path, f):
                make_tree(tree, {f['module']: text})
                if not mutant_compiles(compiler, tree, header):
                    res['mutants'].append({'mutant': tag, 'result': 'stillborn'})
                    continue
                by = kill(compiler, tree, proofs, prop_idx)
                res['mutants'].append({'mutant': tag, 'result': 'killed' if by else 'SURVIVED', 'by': by[:1]})
        return res
    finally:
        shutil.rmtree(tree, ignore_errors=True)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--compiler', default=str(ROOT / 'sutram_compiler'))
    ap.add_argument('--only', help='one module')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--json', default=str(ROOT / 'build/lib-proof-gaps.json'))
    ap.add_argument('--md', default=str(ROOT / 'build/lib-proof-gaps.md'))
    ap.add_argument('--deep', action='store_true', help='also off-by-one return and boundary mutants')
    a = ap.parse_args(argv)
    compiler = str(Path(a.compiler).resolve())

    funcs = []
    for p in sorted(LIB.glob('*.smlib')):
        funcs += parse_module(p)
    deps = {p.stem: module_imports(p.read_text(encoding='utf-8')) for p in LIB.glob('*.smlib')}
    print(f'library: {len(set(f["module"] for f in funcs))} modules, {len(funcs)} functions', flush=True)

    workroot = Path(tempfile.mkdtemp(prefix='libgaps-'))
    base = make_tree(workroot / 'base')
    golds = golden_proofs()
    for p in golds:
        p['mods'] = closure(module_imports(p['src']), deps)
    bad = [p['id'] for p in golds if p['mods'] and not run_golden(compiler, base, p)[0]]
    if bad:
        print('BASELINE FAILS (fix these first):', bad)
        return 2
    _, props = load_props()
    prop_src, prop_mods = [], []
    for i, (label, _) in enumerate(props):
        rec: list = []
        ok, why = run_prop(compiler, base, i, rec)
        if not ok:
            print(f'BASELINE property fails with its own seed: {label}: {why}')
            return 2
        text = '\n'.join(rec)
        prop_src.append(text)
        prop_mods.append(closure(module_imports(text), deps))
    lib_golds = [p for p in golds if p['mods']]
    print(f'proofs: {sum(p["kind"] == "stdlib" for p in lib_golds)} stdlib goldens, '
          f'{sum(p["kind"] == "example" for p in lib_golds)} example goldens that import lib, {len(props)} properties', flush=True)

    todo = [f for f in funcs if not a.only or f['module'] == a.only]
    jobs = []
    for f in todo:
        word = re.compile(r'(?<![\w])' + re.escape(f['name']) + r'(?![\w])')
        rel = [p for p in lib_golds if f['module'] in p['mods']]
        relp = [i for i in range(len(props)) if f['module'] in prop_mods[i]]
        f['named_by'] = [p['id'] for p in rel if word.search(p['src'])] + \
                        ['proof_props: ' + props[i][0] for i in relp if word.search(prop_src[i])]
        # programs that name the function first, so a detection usually comes on the first run
        rel.sort(key=lambda p: not word.search(p['src']))
        relp.sort(key=lambda i: not word.search(prop_src[i]))
        jobs.append((compiler, f, rel, relp, str(workroot), a.deep))
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        results = list(ex.map(check_function, jobs, chunksize=1))
    byname = {(r['module'], r['name']): r for r in results}
    rows = []
    for f in todo:
        r = byname[(f['module'], f['name'])]
        det, named = r['detected_by'], f['named_by']
        status = ('PROVEN' if det and named else 'PROVEN-INDIRECT' if det else
                  'NAMED-NOT-CHECKED' if named else 'UNPROVEN')
        if r['stillborn_S']:
            status = 'MUTANT-DID-NOT-COMPILE'
        ms = r['mutants']
        rows.append({**{k: f[k] for k in ('module', 'name', 'params', 'doc', 'braceless')},
                     'status': status, 'standalone': r.get('standalone', True), 'detected_by': det[:1], 'named_by': named[:3], 'named_count': len(named),
                     'mutants_total': sum(m['result'] != 'stillborn' for m in ms),
                     'mutants_killed': sum(m['result'] == 'killed' for m in ms),
                     'survivors': [m['mutant'] for m in ms if m['result'] == 'SURVIVED']})
    shutil.rmtree(workroot, ignore_errors=True)
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps(rows, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    counts = {s: sum(r['status'] == s for r in rows) for s in ('PROVEN', 'PROVEN-INDIRECT', 'NAMED-NOT-CHECKED', 'UNPROVEN', 'MUTANT-DID-NOT-COMPILE')}
    if a.deep:
        counts['deep: all mutants killed'] = sum(r['mutants_total'] > 0 and not r['survivors'] for r in rows)
        counts['deep: some survive'] = sum(bool(r['survivors']) for r in rows)
        counts['deep: mutants killed'] = f"{sum(r['mutants_killed'] for r in rows)}/{sum(r['mutants_total'] for r in rows)}"
    md = [f'# Library proof gaps (tools/lib_proof_gaps.py)', '',
          f'{len(rows)} functions: ' + ' · '.join(f'{k} {v}' for k, v in counts.items()), '',
          '| module | function | status | detected by | deep mutants killed | surviving mutants | contract (source comment) |',
          '|---|---|---|---|---|---|---|']
    for r in sorted(rows, key=lambda r: (r['module'], r['status'] != 'UNPROVEN', r['name'])):
        md.append(f"| {r['module']} | `{r['name']}({r['params']})` | {r['status']} | "
                  f"{(r['detected_by'] or [''])[0]} | {r['mutants_killed']}/{r['mutants_total']} | "
                  f"{' '.join(r['survivors'][:4])} | {r['doc'][:90]} |")
    Path(a.md).write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(' '.join(f'{k}={v}' for k, v in counts.items()))
    print('wrote', a.json, 'and', a.md)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
