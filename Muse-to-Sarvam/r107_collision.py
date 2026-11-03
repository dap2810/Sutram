#!/usr/bin/env python3
"""R107 collision audit: exact-identifier hits for the six replacement / re-named
words (four Sarvam replacements + smaran_pratilip + sahayata) across builtins,
REPL commands, keywords, lib functions, lang-pack Latin tokens, and example
identifiers (code-stripped). Same method as R106's collision_audit.py, re-run
on the v291 tree (worktree at a430defb). Usage: python3 r107_collision.py <tree>"""
import re, glob, os, sys
NEW = ["kosh_apanay", "anka_akshar", "likha_santat", "vartani_sandhi",
       "smaran_pratilip", "sahayata"]
tree = sys.argv[1] if len(sys.argv) > 1 else "."
builtins, repl, keywords, libfns, langtok, exids = set(), set(), set(), set(), set(), {}
for f in glob.glob(f"{tree}/src/*.asm") + glob.glob(f"{tree}/src/*.inc"):
    t = open(f, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r'bn_[A-Za-z0-9_]+\s+db\s+"([^"]+)"', t):
        builtins.add(m.group(1))
t = open(f"{tree}/src/sutram_compiler.asm", encoding="utf-8", errors="replace").read()
for m in re.finditer(r'str_(?:exit|help|sarvam|nirgat|sahayata)[0-9]*\s+db\s+"([^"]+)"', t):
    repl.add(m.group(1))
for m in re.finditer(r'kw_[A-Za-z0-9_]+\s+db\s+"([^"]+)"', t):
    keywords.add(m.group(1))
for f in glob.glob(f"{tree}/lib/*.smlib"):
    t = open(f, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r'\bprakriya\s+([A-Za-z_][A-Za-z0-9_]*)', t):
        libfns.add(m.group(1))
for f in glob.glob(f"{tree}/lang/*.lang"):
    for ln in open(f, encoding="utf-8", errors="replace"):
        if ln.strip().startswith('#') or not ln.strip():
            continue
        for tok in ln.split():
            if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', tok):
                langtok.add(tok)
for f in sorted(glob.glob(f"{tree}/examples/*.sm")):
    t = open(f, encoding="utf-8", errors="replace").read()
    t = re.sub(r'"(?:[^"\\]|\\.)*"', '""', t)
    code = '\n'.join(ln.split('#', 1)[0] for ln in t.splitlines())
    for tok in set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*', code)):
        if tok not in keywords and tok not in builtins:
            exids.setdefault(tok, set()).add(os.path.basename(f))
print(f"builtins={len(builtins)} repl={sorted(repl)} keywords={len(keywords)} "
      f"lib={len(libfns)} lang={len(langtok)} exids={len(exids)}")
for n in NEW:
    hits = []
    if n in builtins: hits.append("BUILTIN")
    if n in repl: hits.append("REPL")
    if n in keywords: hits.append("KEYWORD")
    if n in libfns: hits.append("LIBFN")
    if n in langtok: hits.append("LANG")
    if n in exids: hits.append(f"EXAMPLES({len(exids[n])})")
    print(f"  {n:18} {'NONE' if not hits else ' | '.join(hits)}")
