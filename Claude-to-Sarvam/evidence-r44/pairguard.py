"""Pairwise guard: OLD tree + OLD compiler vs NEW tree + NEW compiler, per program path."""
import sys, subprocess, glob, os, hashlib, shutil
old_root, old_c, new_root, new_c, out = sys.argv[1:6]
pe = '--pe' in sys.argv
pats = ['examples/*.sm', 'examples/*/*.sm', 'tests/stdlib/*.sm', 'tests/r*/*.sm', 'tests/r*/*/*.sm']
rel = sorted({os.path.relpath(p, new_root) for pat in pats for p in glob.glob(os.path.join(new_root, pat))})
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
ident = refused = new = 0; differ = []; callers = []
def comp(c, root, r, o):
    try: rc = subprocess.run([c, os.path.join(root, r), o], cwd=root, capture_output=True, timeout=60).returncode
    except subprocess.TimeoutExpired: rc = 'timeout'
    return rc, (open(o, 'rb').read() if os.path.exists(o) else None)
for i, r in enumerate(rel):
    ext = '.exe' if pe else ''
    if not os.path.exists(os.path.join(old_root, r)):
        new += 1; print(f'NEW          {r}'); continue
    src_old = open(os.path.join(old_root, r), 'rb').read(); src_new = open(os.path.join(new_root, r), 'rb').read()
    if src_old != src_new: callers.append(r)
    orc, od = comp(old_c, old_root, r, f'{out}/{i}.old{ext}')
    nrc, nd = comp(new_c, new_root, r, f'{out}/{i}.new{ext}')
    tag = ' (source renamed)' if src_old != src_new else ''
    if od is None and nd is None and orc == nrc: refused += 1; print(f'REFUSED-SAME {r}{tag}')
    elif od is not None and od == nd and orc == nrc: ident += 1; print(f'IDENTICAL    {r}{tag}')
    else: differ.append(r); print(f'DIFFER       {r}{tag} old rc={orc} new rc={nrc}')
print(f'source files whose text changed (renamed callers): {len(callers)}')
print(f'{len(rel)} programs: {ident} byte-identical, {refused} refused identically, {len(differ)} DIFFER, {new} new')
