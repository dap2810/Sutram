#!/usr/bin/env python3
"""R77 WS1: byte-vs-qword audit of nirmmita(N) with literal N.

For each nirmmita(...) site in examples/*.sm, tests/stdlib/*.sm, lib/*.smlib:
  - classify the argument: LITERAL int, FOLDABLE literal expr (digits + * + - / parens),
    or OTHER (variable/call/expression with identifiers)
  - for LITERAL/FOLDABLE: find the assigned variable, find its qword-index uses
    VAR[<idx>] in the same file, compute max literal index and variable-index uses
  - verdict: OK if N >= (maxidx+1)*8; VIOLATION if not; BYTE-ONLY if only byte
    accessors (pad8/likh8/akshar_rakh/akshar) touch it; OPAQUE if never indexed
    in-file (returned/passed on); VARIDX if indexed only by variables.
Prints one line per literal/foldable site + a summary. Output is JSON lines
to stdout; human summary to stderr.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path('/home/hatch/workspace/Sutram')
DIRS = [ROOT / 'examples', ROOT / 'tests', ROOT / 'lib']
PATTERNS = ['*.sm', '*.smlib']

LIT_RE = re.compile(r'^\d+$')
FOLD_RE = re.compile(r'^[\d\s\*\+\-\/\(\)]+$')
ASSIGN_RE = re.compile(
    r'(?:vitti|dasham|mala)\s+(\w+)\s*(?:\[[^\]]*\])?\s*=\s*'
    r'|(\w+)\s*=\s*')
CALL_RE = re.compile(r'nirmmita\s*\(([^()]*)\)')
IDX_RE = re.compile(r'(\w+)\s*\[\s*([^\]]+?)\s*\]')
BYTE_FNS = ('pad8', 'likh8', 'pad8c', 'likh8c', 'akshar', 'akshar_rakh')


def fold(expr):
    expr = expr.strip()
    if LIT_RE.match(expr):
        return int(expr)
    if FOLD_RE.match(expr):
        try:
            return int(eval(expr, {}, {}))
        except Exception:
            return None
    return None


def strip_comments(text):
    out = []
    for line in text.split('\n'):
        # crude: cut at # not inside a string; good enough for a first pass
        if '"' in line:
            parts, in_str = [], False
            cur = ''
            for ch in line:
                if ch == '"':
                    in_str = not in_str
                if ch == '#' and not in_str:
                    break
                cur += ch
            out.append(cur)
        else:
            out.append(line.split('#')[0])
    return '\n'.join(out)


def main():
    sites = []
    for d in DIRS:
        for pat in PATTERNS:
            for f in sorted(d.rglob(pat)):
                try:
                    raw = f.read_text(encoding='utf-8')
                except Exception:
                    continue
                text = strip_comments(raw)
                for m in CALL_RE.finditer(text):
                    arg = m.group(1).strip()
                    n = fold(arg)
                    rec = {'file': str(f.relative_to(ROOT)), 'arg': arg,
                           'line': text[:m.start()].count('\n') + 1}
                    if n is None:
                        rec['kind'] = 'OTHER'
                        sites.append(rec)
                        continue
                    rec['kind'] = 'LITERAL' if LIT_RE.match(arg) else 'FOLDABLE'
                    rec['bytes'] = n
                    # assigned variable: search backwards on the same line/logical stmt
                    line_start = text.rfind('\n', 0, m.start()) + 1
                    line = text[line_start:m.start()]
                    var = None
                    mm = re.search(r'(?:vitti|dasham)\s+(\w+)\s*=', line)
                    if mm:
                        var = mm.group(1)
                    else:
                        mm = re.search(r'(\w+)\s*=\s*$', line)
                        if mm:
                            var = mm.group(1)
                    rec['var'] = var
                    if var is None:
                        rec['verdict'] = 'OPAQUE'
                        sites.append(rec)
                        continue
                    # index uses of var in this file
                    maxidx, varidx, byte_only = None, [], False
                    uses = 0
                    for im in IDX_RE.finditer(text):
                        if im.group(1) != var:
                            continue
                        uses += 1
                        idx = im.group(2).strip()
                        if LIT_RE.match(idx):
                            v = int(idx)
                            maxidx = v if maxidx is None else max(maxidx, v)
                        else:
                            varidx.append(idx)
                    # byte accessors?
                    byte_uses = sum(1 for fn in BYTE_FNS
                                    if re.search(r'\b' + fn + r'\s*\([^)]*\b' + var + r'\b', text))
                    rec['uses'] = uses
                    rec['maxidx'] = maxidx
                    rec['varidx'] = sorted(set(varidx))[:6]
                    rec['byte_uses'] = byte_uses
                    if uses == 0 and byte_uses == 0:
                        rec['verdict'] = 'OPAQUE'
                    elif maxidx is None and byte_uses > 0 and uses == 0:
                        rec['verdict'] = 'BYTE-ONLY'
                    elif maxidx is None:
                        rec['verdict'] = 'VARIDX'
                    else:
                        need = (maxidx + 1) * 8
                        rec['need'] = need
                        rec['verdict'] = 'OK' if n >= need else 'VIOLATION'
                    sites.append(rec)
    for s in sites:
        print(json.dumps(s, ensure_ascii=False))
    from collections import Counter
    c = Counter(s['verdict'] if 'verdict' in s else s['kind'] for s in sites)
    print(f"SUMMARY total={len(sites)} {dict(c)}", file=sys.stderr)


if __name__ == '__main__':
    main()
