#!/usr/bin/env python3
"""R77 WS2/WS3: whitespace mutator over examples.

For each example .sm file:
  - run pristine twice (empty stdin, CWD=repo root, 10s timeout); if the two
    runs differ -> NONDET (excluded from failure counts)
  - if pristine does not compile -> PRISTINE_FAIL (excluded, reported)
  - else apply each of 5 mutations, compile + run, compare stdout+exitcode
    to pristine. Failure = compile-status change OR output/exit difference.
    (A fail->pass change under M4 is reported as FIXED, not as a failure.)
Mutations:
  M1 blank-space-lines: blank lines inside indented blocks become "   ";
       if none exist, insert "   " after the first indented line
  M2 crlf: all \\n -> \\r\\n
  M3 trailing-spaces: append "   " to every non-blank line
  M4 prakriya-above-mukhya: move top-level prakriya blocks after mukhya above it
  M5 tabs: leading spaces -> 1 tab per 4 spaces (remainder kept)
Usage: mutator.py [--devanagari-only] [--out FILE]
"""
import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path('/home/hatch/workspace/Sutram')
COMP = str(ROOT / 'sutram_compiler')
DEV_RE = re.compile(r'[\u0900-\u097f]')


def run_prog(sm_path, timeout=10):
    """Return (compiled, stdout, exitcode). compiled False if compiler failed."""
    with tempfile.TemporaryDirectory() as td:
        binp = str(Path(td) / 'prog.bin')
        c = subprocess.run([COMP, str(sm_path), binp],
                           capture_output=True, text=True, timeout=timeout)
        if c.returncode != 0 or not Path(binp).exists():
            return (False, '', c.returncode)
        try:
            r = subprocess.run([binp], input='', capture_output=True,
                               text=True, timeout=timeout, cwd=str(ROOT))
            return (True, r.stdout, r.returncode)
        except subprocess.TimeoutExpired:
            return (True, '<TIMEOUT>', -1)


def is_indented(line):
    return line.startswith((' ', '\t')) and line.strip() != ''


def m1_blank_space_lines(text):
    lines = text.split('\n')
    out, changed = [], False
    for i, ln in enumerate(lines):
        if ln == '':
            prev = next((x for x in reversed(lines[:i]) if x != ''), '')
            nxt = next((x for x in lines[i + 1:] if x != ''), '')
            if is_indented(prev) and is_indented(nxt):
                out.append('   ')
                changed = True
                continue
        out.append(ln)
    if not changed:
        # insert a space-only line after the first indented line
        for i, ln in enumerate(out):
            if is_indented(ln):
                out.insert(i + 1, '   ')
                changed = True
                break
    return '\n'.join(out), changed


def m2_crlf(text):
    return text.replace('\n', '\r\n'), True


def m3_trailing_spaces(text):
    lines = text.split('\n')
    changed = False
    out = []
    for ln in lines:
        if ln.strip() != '':
            out.append(ln + '   ')
            changed = True
        else:
            out.append(ln)
    return '\n'.join(out), changed


def block_end(lines, start):
    """End index (exclusive) of the block starting at line `start`.
    Braced: match braces. Indented (no brace on the header line): following
    indented lines + blank lines between them."""
    header = lines[start]
    if '{' in header:
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count('{') - lines[i].count('}')
            if i > start and depth <= 0:
                return i + 1
        return len(lines)
    # indented body
    i = start + 1
    while i < len(lines):
        if lines[i].strip() == '' or is_indented(lines[i]):
            i += 1
        else:
            break
    return i


def m4_prakriya_above(text):
    lines = text.split('\n')
    muk = None
    for i, ln in enumerate(lines):
        if re.match(r'\s*mukhya\s*\(', ln):
            muk = i
            break
    if muk is None:
        return text, False
    mend = block_end(lines, muk)
    # top-level prakriya blocks after mukhya's block
    blocks, rest, i = [], [], mend
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('prakriya ') or re.match(r'prakriya\s', ln):
            e = block_end(lines, i)
            blocks.append(lines[i:e])
            i = e
        else:
            rest.append(ln)
            i += 1
    if not blocks:
        return text, False
    head = lines[:muk]
    moved = [ln for b in blocks for ln in b]
    return '\n'.join(head + moved + lines[muk:mend] + rest), True


def m5_tabs(text):
    lines = text.split('\n')
    changed = False
    out = []
    for ln in lines:
        m = re.match(r'^( +)', ln)
        if m:
            n = len(m.group(1))
            tabs, rem = divmod(n, 4)
            if tabs:
                out.append('\t' * tabs + ' ' * rem + ln[n:])
                changed = True
                continue
        out.append(ln)
    return '\n'.join(out), changed


MUTS = [('M1', m1_blank_space_lines), ('M2', m2_crlf),
        ('M3', m3_trailing_spaces), ('M4', m4_prakriya_above),
        ('M5', m5_tabs)]


def process(path):
    text = path.read_text(encoding='utf-8')
    p1 = run_prog(path)
    p2 = run_prog(path)
    rec = {'file': path.name}
    if p1 != p2:
        rec['status'] = 'NONDET'
        return rec
    if not p1[0]:
        rec['status'] = 'PRISTINE_FAIL'
        return rec
    rec['status'] = 'OK'
    rec['pristine'] = {'stdout': p1[1][:200], 'exit': p1[2]}
    results = {}
    with tempfile.TemporaryDirectory() as td:
        for name, fn in MUTS:
            try:
                mutated, changed = fn(text)
            except Exception as e:  # noqa
                results[name] = {'error': repr(e)}
                continue
            if not changed:
                results[name] = {'noop': True}
                continue
            mp = Path(td) / (name + '.sm')
            mp.write_text(mutated, encoding='utf-8', newline='')
            got = run_prog(mp)
            if got[0] != p1[0]:
                results[name] = {'result': 'FIXED' if got[0] else 'COMPILE_FAIL',
                                 'mut_exit': got[2]}
            elif got[1] != p1[1] or got[2] != p1[2]:
                results[name] = {'result': 'OUTPUT_DIFF',
                                 'mut_stdout': got[1][:200],
                                 'mut_exit': got[2]}
            else:
                results[name] = {'result': 'SAME'}
    rec['mutations'] = results
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--devanagari-only', action='store_true')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    files = sorted((ROOT / 'examples').glob('*.sm'))
    if args.devanagari_only:
        files = [f for f in files if DEV_RE.search(f.read_text(encoding='utf-8'))]
    print(f"{len(files)} examples", file=sys.stderr)
    recs = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for rec in ex.map(process, files):
            recs.append(rec)
            print(f"{rec['file']}: {rec['status']}", file=sys.stderr)
    Path(args.out).write_text(json.dumps(recs, ensure_ascii=False, indent=1))
    from collections import Counter
    print(Counter(r['status'] for r in recs), file=sys.stderr)
    for name, _ in MUTS:
        c = Counter((r.get('mutations', {}).get(name, {}) or {}).get('result', 'noop')
                    for r in recs if r['status'] == 'OK')
        print(name, dict(c), file=sys.stderr)


if __name__ == '__main__':
    main()
