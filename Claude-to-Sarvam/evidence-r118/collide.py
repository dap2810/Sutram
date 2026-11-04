#!/usr/bin/env python3
"""R118: every proposed new name against every namespace: keywords, builtins (new and old rows), retired
spellings, library prakriya, every identifier in examples/ lib/ tests/, the eleven .lang packs (word and target),
the eleven .sandesh files, and compiled as an identifier, as a prakriya name and as a call on v296."""
import os, re, subprocess, sys, tempfile, glob
import os
ROOT = os.environ.get('R118_ROOT', '/home/claude/sutram')
NEW = sys.argv[1:]
asm = open(f'{ROOT}/src/sutram_compiler.asm', encoding='utf-8', errors='replace').read()
inc = ''.join(open(p, encoding='utf-8', errors='replace').read() for p in glob.glob(f'{ROOT}/src/*.inc'))
strings = set(re.findall(r'db\s+"([^"]*)"', asm + inc))
lib = {}
for p in glob.glob(f'{ROOT}/lib/*.smlib'):
    for m in re.finditer(r'^prakriya\s+(\w+)', open(p, encoding='utf-8').read(), re.M):
        lib[m.group(1)] = os.path.basename(p)
idents = {}
for d in ('examples', 'lib', 'tests', 'tools'):
    for p in glob.glob(f'{ROOT}/{d}/**/*', recursive=True):
        if not os.path.isfile(p) or not p.endswith(('.sm', '.smlib', '.py', '.out', '.err', '.json')): continue
        for w in set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', open(p, encoding='utf-8', errors='replace').read())):
            idents.setdefault(w, []).append(os.path.relpath(p, ROOT))
packs = {}
for p in glob.glob(f'{ROOT}/lang/*.lang') + glob.glob(f'{ROOT}/lang/*.sandesh'):
    for w in set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', open(p, encoding='utf-8').read())):
        packs.setdefault(w, []).append(os.path.basename(p))
bad = 0
with tempfile.TemporaryDirectory() as d:
    for n in NEW:
        hits = []
        if n in strings: hits.append('a compiler string (keyword/builtin/retired table or message): ' + n)
        if n in lib: hits.append('library prakriya in ' + lib[n])
        if n in idents: hits.append('identifier in ' + ', '.join(sorted(idents[n])[:5]))
        if n in packs: hits.append('pack ' + ', '.join(sorted(packs[n])))
        res = []
        for tag, src in (('variable', f'mukhya() {{\n    vitti {n} = 3\n    likha({n})\n}}\n'),
                         ('prakriya', f'prakriya {n}(x) {{\n    nivartanam x + 1\n}}\nmukhya() {{\n    likha({n}(2))\n}}\n'),
                         ('call with a space', f'prakriya {n}(x) {{\n    nivartanam x + 1\n}}\nmukhya() {{\n    likha({n} (2))\n}}\n')):
            open(f'{d}/t.sm', 'w').write(src)
            r = subprocess.run([f'{ROOT}/sutram_compiler', f'{d}/t.sm', f'{d}/t.bin'], capture_output=True, text=True)
            out = subprocess.run([f'{d}/t.bin'], capture_output=True, text=True).stdout.strip() if r.returncode == 0 else 'NO COMPILE ' + (r.stdout + r.stderr)[:120]
            ok = out == ('3' if tag == 'variable' else '3') and 'suchana' not in r.stderr
            res.append(f'{tag}: {"ok" if ok else "FAIL " + out}')
            if not ok: hits.append(f'{tag} on v296: {out}')
        print(f'{n:28s} {"FREE" if not hits else "COLLIDES"}  | ' + '; '.join(res) + ('' if not hits else '\n      ' + '\n      '.join(hits)))
        bad += bool(hits)
print(f'{len(NEW)} names, {bad} collide')
