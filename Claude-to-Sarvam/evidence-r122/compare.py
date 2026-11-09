#!/usr/bin/env python3
"""R122: every program in the arena branch's tree, compiled by its base (main 416637b, v289) and by the branch
(3a6292e), each in its own tree (so each with its own lib/), ELF; then both run (stdin from run_tests' table).
Classes: identical bytes; both refused; refused by one only; different bytes - same run; different run."""
import glob, os, subprocess, sys, tempfile, json
G = '<scratch>/r122'
BASE, ARENA = G + '/base', G + '/arena'
sys.path.insert(0, ARENA + '/tests'); import run_tests as RT
PAT = ['examples/*.sm', 'tests/stdlib/*.sm', 'tests/r*/*.sm', 'tests/r*/*/*.sm']
rels = sorted({os.path.relpath(p, ARENA) for pat in PAT for p in glob.glob(os.path.join(ARENA, pat))})
out = tempfile.mkdtemp(dir=G)
cls = {}
rows = []
def build(tree, rel, tag):
    o = os.path.join(out, rel.replace('/', '_') + '.' + tag)
    lang = RT.LANG.get(os.path.basename(rel)[:-3]) if rel.startswith('examples/') else None
    cmd = [tree + '/sutram_compiler'] + (['--lang', lang] if lang else []) + [os.path.join(tree, rel), o]
    r = subprocess.run(cmd, capture_output=True, cwd=os.path.dirname(os.path.join(tree, rel)), timeout=60)
    return o if r.returncode == 0 and os.path.exists(o) else None, (r.stdout + r.stderr).decode('utf-8', 'replace')
def run(b, rel, tree):
    stem = os.path.basename(rel)[:-3]
    stdin = RT.STDIN.get(stem, '') if rel.startswith('examples/') else ''
    try:
        r = subprocess.run([b], input=stdin.encode(), capture_output=True, timeout=30, cwd=tree)
        return r.stdout, r.returncode
    except subprocess.TimeoutExpired:
        return b'TIMEOUT', None
for rel in rels:
    if not os.path.exists(os.path.join(BASE, rel)):
        cls.setdefault('new on the branch', []).append(rel); continue
    a, ea = build(BASE, rel, 'base'); b, eb = build(ARENA, rel, 'arena')
    if not a and not b: k = 'both refused'
    elif not a or not b: k = 'refused by ' + ('the base only' if not a else 'the branch only')
    elif open(a, 'rb').read() == open(b, 'rb').read(): k = 'identical bytes'
    else:
        ra, rb = run(a, rel, BASE), run(b, rel, ARENA)
        k = 'different bytes, same output and exit' if ra == rb else 'DIFFERENT OUTPUT OR EXIT'
        if ra != rb: rows.append((rel, ra, rb))
    cls.setdefault(k, []).append(rel)
print(f'# {len(rels)} programs in the branch tree; base 416637b (v289) vs branch 3a6292e, ELF')
for k, v in sorted(cls.items(), key=lambda x: -len(x[1])):
    print(f'{len(v):4d}  {k}')
for k in ("refused by the branch only", "refused by the base only", "new on the branch", "different bytes, same output and exit"):
    for r in cls.get(k, []): print(f'      {k}: {r}')
for rel, ra, rb in rows:
    print(f'      CHANGED {rel}: base exit {ra[1]} {ra[0][-80:]!r} -> branch exit {rb[1]} {rb[0][-80:]!r}')
