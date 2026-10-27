#!/usr/bin/env python3
"""ROUND-43 WS4: which names in lib/ begin with a keyword - a REPORT, not a naming rule.

For every keyword K (both columns of lang/sanskrit.lang: the Latin core keywords and builtins, and their
Devanagari spellings) and every name I DECLARED in lib/*.smlib (a prakriya, its parameters, a vitti, a mala,
a kosh, a rachana and its fields): if I starts with K and I != K, it is listed.

Such a name is LEGAL. The lexer reads a whole word before it looks for a keyword, so `prati` never matches
inside `vartani_pratilip`; tests/r43/test_keyword_boundary.py proves it for every keyword. The list exists so
the answer stays visible instead of being re-derived, and so nobody picks a worse word to avoid a collision
that does not happen.

It FAILS only when a declared name IS a keyword (I == K) - that cannot compile - or when lib/ cannot be read.
No NASM, no subprocesses. In the shape of tools/check_doc_signatures.py.

usage: python3 tools/check_keyword_prefix.py [--repo-root DIR] [--quiet]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME = r'[A-Za-z_][A-Za-z0-9_]*'
DECL = [
    re.compile(rf'^\s*prakriya\s+({NAME})\s*\(([^)]*)\)'),       # name and parameters
    re.compile(rf'^\s*vitti\s+({NAME})\b'),
    re.compile(rf'^\s*mala\s+({NAME})\b'),
    re.compile(rf'^\s*kosh(?:\s+dasham)?\s+({NAME})\b'),
    re.compile(rf'^\s*rachana\s+({NAME})\s*=\s*\{{([^}}]*)\}}'),  # name and fields
]


def keywords(root: Path) -> set[str]:
    kw: set[str] = set()
    for line in (root / 'lang' / 'sanskrit.lang').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            kw.update(line.split()[:2])
    return kw


def declared(root: Path) -> dict[str, list[str]]:
    """name -> ['module:line', ...] for every name declared in lib/*.smlib."""
    out: dict[str, list[str]] = {}
    for f in sorted((root / 'lib').glob('*.smlib')):
        for n, raw in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
            line = raw.split('#', 1)[0]
            for rx in DECL:
                m = rx.match(line)
                if not m:
                    continue
                names = [m.group(1)]
                if m.lastindex and m.lastindex >= 2:
                    names += [p.strip() for p in m.group(2).split(',') if p.strip()]
                for nm in names:
                    nm = nm.split()[-1] if nm.split() else nm          # a typed parameter: the last word
                    if re.fullmatch(NAME, nm):
                        out.setdefault(nm, []).append(f'{f.stem}:{n}')
    return out


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo-root', default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args(argv)
    root = Path(a.repo_root)
    try:
        kw = keywords(root)
        names = declared(root)
    except OSError as e:
        print(f'keyword prefix: cannot read the tree: {e}')
        print('RESULT: FAIL')
        return 1
    if not names:
        print('keyword prefix: no declared names found in lib/ - the parser is broken')
        print('RESULT: FAIL')
        return 1

    clash = sorted(nm for nm in names if nm in kw)
    prefixed = {}
    for nm in sorted(names):
        if nm in kw:
            continue
        ks = sorted(k for k in kw if nm.startswith(k))
        if ks:
            prefixed[nm] = ks

    if not a.quiet:
        print(f'{len(kw)} keywords (lang/sanskrit.lang, both columns); {len(names)} names declared in lib/*.smlib')
        print(f'REPORT - legal, listed so the answer stays visible ({len(prefixed)} names begin with a keyword):')
        for nm, ks in prefixed.items():
            print(f'  {nm:32} begins with {", ".join(ks):20} {names[nm][0]}')
    for nm in clash:
        print(f'FAIL  {nm} is a keyword, declared at {", ".join(names[nm][:3])}')
    print(f'keyword prefix: {len(prefixed)} of {len(names)} lib names begin with a keyword (allowed: '
          f'tests/r43); {len(clash)} is a keyword')
    print('RESULT: ' + ('FAIL' if clash else 'PASS'))
    return 1 if clash else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
