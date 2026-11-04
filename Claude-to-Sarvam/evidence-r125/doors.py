#!/usr/bin/env python3
"""R125: which programs' kosh values leave the compiler's tracking - stored in a cell (x[i] = k), arithmetic
(= k + n / k - n), or passed to an untyped (non-kosh) parameter of a prakriya defined in the file or lib/.
A static scan of the source text; argv[1] = the tree root."""
import glob, re, os, sys, collections
ROOT = sys.argv[1]
PAT = ['examples/*.sm', 'tests/stdlib/*.sm', 'tests/r*/*.sm', 'tests/r*/*/*.sm']
progs = sorted({p for pat in PAT for p in glob.glob(os.path.join(ROOT, pat))})
def sigs(text, d):
    for m in re.finditer(r'^\s*prakriya\s+(\w+)\s*\(([^)]*)\)', text, re.M):
        d[m.group(1)] = [x.strip().startswith('kosh ') for x in m.group(2).split(',') if x.strip()]
lib = {}
for f in glob.glob(os.path.join(ROOT, 'lib/*.smlib')): sigs(open(f, encoding='utf-8').read(), lib)
grp = collections.defaultdict(set); declared = 0
for p in progs:
    t = open(p, encoding='utf-8', errors='ignore').read()
    sig = dict(lib); sigs(t, sig)
    ks = set(re.findall(r'^\s*kosh\s+(\w+)\s*\[', t, re.M)) | set(re.findall(r'\bkosh\s+(\w+)\s*[,)]', t))
    if not ks: continue
    declared += 1
    rel = os.path.relpath(p, ROOT)
    for line in t.split('\n'):
        s = line.split('#')[0]
        for k in ks:
            if re.search(r'\[[^\]]*\]\s*=\s*%s\s*$' % k, s): grp['stored in a cell (x[i] = k)'].add(rel)
            if re.search(r'=\s*%s\s*[-+]\s*\w' % k, s): grp['arithmetic on it (= k + n)'].add(rel)
            for m in re.finditer(r'(\w+)\s*\(([^()]*)\)', s):
                fn, args = m.group(1), [a.strip() for a in m.group(2).split(',')]
                if fn in sig and k in args:
                    i = args.index(k)
                    if i < len(sig[fn]) and not sig[fn][i]: grp['passed to an untyped parameter'].add(f'{rel} ({fn})')
print(f'# {len(progs)} programs, {declared} declare a kosh')
allp = set()
for k, v in grp.items():
    print(f'{len(v)} {k}:'); [print('   ', x) for x in sorted(v)]; allp |= {x.split(' (')[0] for x in v}
print(f'{len(allp)} programs in all')
