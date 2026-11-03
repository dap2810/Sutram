#!/usr/bin/env python3
"""ROUND-106 WS1: collision audit. For every new name, count hits in:
builtins (bn_ table + REPL commands), keywords (kw_ table),
library functions (prakriya names in lib/*.smlib),
lang entries (lang/*.lang, Latin tokens),
example identifiers (code tokens in examples/*.sm, comments and
string literals stripped, keywords and builtins excluded).
Usage: python3 collision_audit.py <tree> [tree2 ...]
Prints per-name hits by category. Exact identifier match only
(word boundaries) -- asti does NOT collide with asti_yugm."""
import re, os, sys, glob

NEW = ["asti", "nasti",
       "truti", "patra", "rekha", "kuru",
       "kosh_kship", "kosh_hri", "kosh_gan", "kosh_ksham", "kosh_iksh",
       "kosh_rikt", "kosh_shodh", "kosh_yuj", "kosh_muc", "pankti_gan",
       "tyaj", "saha", "jala", "jala_bandh", "jala_shru", "jala_grah",
       "akshar_laghu", "akshar_guru", "akshar_tas", "vartani_yoj",
       "likha_bindu", "likha_rup", "sankhya_bindu", "smaran_kriti"]

def strip_code(text):
    # strip string literals ( "..." with escapes ) then # comments
    text = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)
    lines = []
    for ln in text.splitlines():
        lines.append(ln.split('#', 1)[0])
    return '\n'.join(lines)

def collect(tree):
    builtins = set()
    for f in glob.glob(f"{tree}/src/*.asm") + glob.glob(f"{tree}/src/*.inc"):
        try:
            t = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in re.finditer(r'bn_[A-Za-z0-9_]+\s+db\s+"([^"]+)"', t):
            builtins.add(m.group(1))
    # REPL commands (str_ labels, the shell's command words)
    repl = set()
    for f in glob.glob(f"{tree}/src/sutram_compiler.asm"):
        t = open(f, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'str_(?:exit|help)[0-9]+\s+db\s+"([^"]+)"', t):
            repl.add(m.group(1))
        for m in re.finditer(r'str_(?:sarvam|nirgat|sahayata)\s+db\s+"([^"]+)"', t):
            repl.add(m.group(1))
    keywords = set()
    for f in glob.glob(f"{tree}/src/sutram_compiler.asm"):
        t = open(f, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'kw_[A-Za-z0-9_]+\s+db\s+"([^"]+)"', t):
            keywords.add(m.group(1))
    libfns = set()
    for f in glob.glob(f"{tree}/lib/*.smlib"):
        t = open(f, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'\bprakriya\s+([A-Za-z_][A-Za-z0-9_]*)', t):
            libfns.add(m.group(1))
    langtok = set()
    for f in glob.glob(f"{tree}/lang/*.lang"):
        t = open(f, encoding="utf-8", errors="replace").read()
        for ln in t.splitlines():
            if ln.strip().startswith('#') or not ln.strip():
                continue
            for tok in ln.split():
                if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', tok):
                    langtok.add(tok)
    exids = {}  # name -> set of example files
    for f in sorted(glob.glob(f"{tree}/examples/*.sm")):
        t = strip_code(open(f, encoding="utf-8", errors="replace").read())
        for tok in set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*', t)):
            if tok in keywords or tok in builtins:
                continue
            exids.setdefault(tok, set()).add(os.path.basename(f))
    return {"builtins": builtins, "repl": repl, "keywords": keywords,
            "libfns": libfns, "langtok": langtok, "exids": exids}

for tree in sys.argv[1:]:
    d = collect(tree)
    print(f"=== {tree}")
    print(f"builtins={len(d['builtins'])} repl={sorted(d['repl'])} "
          f"keywords={len(d['keywords'])} libfns={len(d['libfns'])} "
          f"lang-Latin-tokens={len(d['langtok'])} example-identifiers={len(d['exids'])}")
    for n in NEW:
        hits = []
        if n in d['builtins']:
            hits.append("BUILTIN")
        if n in d['repl']:
            hits.append("REPL")
        if n in d['keywords']:
            hits.append("KEYWORD")
        if n in d['libfns']:
            hits.append("LIBFN")
        if n in d['langtok']:
            hits.append("LANG")
        if n in d['exids']:
            hits.append(f"EXAMPLES({len(d['exids'][n])}):{sorted(d['exids'][n])[:6]}")
        print(f"  {n:15} {'NONE' if not hits else ' | '.join(hits)}")
