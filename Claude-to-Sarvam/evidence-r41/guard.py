#!/usr/bin/env python3
"""The guard: compile every program the ordinary way with two compilers, compare bytes.
usage: guard.py ROOT OLD NEW OUTDIR [--pe]"""
import sys, subprocess, os, glob, hashlib, shutil
root, old, new, out = sys.argv[1:5]; pe = '--pe' in sys.argv
pats = ['examples/*.sm', 'examples/*/*.sm', 'tests/stdlib/*.sm', 'tests/r*/*.sm', 'tests/r*/*/*.sm']
progs = sorted({p for pat in pats for p in glob.glob(os.path.join(root, pat))})
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
ident = refused = differ = 0; lines = []
for i, p in enumerate(progs):
    res = []
    for tag, c in (('old', old), ('new', new)):
        o = os.path.join(out, f'{i}.{tag}' + ('.exe' if pe else ''))
        try:
            r = subprocess.run([c, p, o], cwd=root, capture_output=True, timeout=60)
            rc = r.returncode
        except subprocess.TimeoutExpired:
            rc = 'timeout'
        data = open(o, 'rb').read() if os.path.exists(o) else None
        res.append((rc, data))
    (orc, od), (nrc, nd) = res
    rel = os.path.relpath(p, root)
    if od is None and nd is None and orc == nrc:
        refused += 1; lines.append(f'REFUSED-SAME {rel} rc={orc}')
    elif od is not None and od == nd and orc == nrc:
        ident += 1; lines.append(f'IDENTICAL    {rel} {hashlib.sha256(od).hexdigest()[:16]}')
    else:
        differ += 1; lines.append(f'DIFFER       {rel} old rc={orc} {len(od) if od else None}B, new rc={nrc} {len(nd) if nd else None}B')
for l in lines: print(l)
print(f'{len(progs)} programs: {ident} byte-identical executables, {refused} refused identically, {differ} DIFFER')
sys.exit(1 if differ else 0)
