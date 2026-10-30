"""R71: in a tree, find every control header with no '{' whose body is on the following lines.
usage: scan_braceless.py TREE"""
import re, sys, glob, os
root = sys.argv[1]
H = re.compile(r'^(\s*)(yadi|yavat|chakra|kuru|anya|guna|bhavana|यदि|यावत्|पुनरावर्तन|कुरु|अन्यत्र)\b(.*)$')
files = [f for pat in ('examples/*.sm', 'examples/*/*.sm', 'lib/*.smlib', 'tests/**/*.sm', 'tests/**/*.smlib', 'benchmarks/*.sm')
         for f in glob.glob(os.path.join(root, pat), recursive=True) if '/negative/' not in f]
files = sorted(set(files))
hits = []; one_line = []
for f in files:
    lines = open(f, encoding='utf-8', errors='replace').read().split('\n')
    code = [(i, l) for i, l in enumerate(lines) if l.split('#')[0].strip()]
    for k, (i, l) in enumerate(code):
        c = l.split('#')[0].rstrip()
        m = H.match(c)
        if not m or '{' in c or c.strip().startswith('}'):
            continue
        rest = m.group(3).strip()
        # a body on the header's own line: something after the condition's ')'
        depth = 0; tail = None
        for j, ch in enumerate(rest):
            if ch == '(': depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0: tail = rest[j + 1:].strip(); break
        if m.group(2) in ('anya', 'kuru', 'अन्यत्र', 'कुरु'): tail = rest
        if tail:
            one_line.append(f'{os.path.relpath(f, root)}:{i + 1}: {c.strip()}')
            continue
        if k + 1 < len(code):
            ni, nl = code[k + 1]
            if len(nl) - len(nl.lstrip()) > len(c) - len(c.lstrip()):
                hits.append(f'{os.path.relpath(f, root)}:{i + 1}: {c.strip()}  /  next: {nl.strip()}')
print(f'{len(files)} files scanned')
print(f'braceless header, body on the following lines indented deeper: {len(hits)}')
for h in hits: print('  ' + h)
print(f'braceless header with its body on the same line: {len(one_line)}')
for h in one_line[:20]: print('  ' + h)
