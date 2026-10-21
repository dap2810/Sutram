#!/usr/bin/env python3
"""ROUND-17 WS2: the crash corpus. Inputs that once made the compiler crash.

Every file under tests/negative/r17/ is an INVALID program on which the compiler
crashed with SIGSEGV before ROUND-17 (found by tools/fuzz_robust.py, R15-02):
  R*.sm               one hand-written input per crash kind (ROUND-17)
  r15-original/       the 102 mutation inputs exactly as the fuzzer produced them (ROUND-20)
  r15-reduced/        the same 102, shrunk by --reduce to the bytes that still crashed
The rule: the compiler must ERROR on invalid input, never crash. So for each
input this runner requires

  * exit status 1 (not a signal, not 0),
  * a diagnostic on stdout that starts with "Sutram Error" (after any
    leading newline the diagnostic convention prints), and
  * no output file.

tests/negative/r17/SHA256SUMS pins the bytes of every committed file (ROUND-21). Four of
the original inputs hold bytes that are not valid UTF-8 (the mutator writes raw bytes), and
a copy that reads them as text and writes them back turns those bytes into U+FFFD; one such
copy no longer crashed the compiler it was pinned against. So the runner first checks the
manifest and FAILs any file whose bytes differ, before running anything.

ROUND-24: those four are stored as NAME.sm.b64 (base64 text, ASCII), so a merge that copies
files as text cannot change them; the runner decodes them and the manifest pins the decoded
bytes under NAME.sm, unchanged. A NAME.sm beside its NAME.sm.b64 is a stale text copy and
FAILs; any .sm in the corpus that is not valid UTF-8 FAILs too: store it as .sm.b64.

The 100,000-deep nesting inputs (R6) are generated here rather than committed:
parentheses (closed and unclosed), yadi blocks, unary minus and nested calls, each at
20,000 and 100,000 levels, plus the same four at a depth that must COMPILE: 400 for the expressions
(the parser allows 1,024 expression levels; a call or a unary minus with its
parentheses takes two) and 100 for braces (the block limit is 128).

usage:
  python3 -B tools/crash_corpus.py [--compiler ./sutram_compiler] [--timeout 20]
Exit 0 when every case holds. Prints one line per case: PASS / FAIL.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'tests/negative/r17'


def deep(kind: str, n: int) -> bytes:
    if kind == 'parens':
        return b'mukhya() {\n    likha(' + b'(' * n + b'1' + b')' * n + b')\n}\n'
    if kind == 'parens-unclosed':
        return b'mukhya() {\n    likha(' + b'(' * n + b'1)\n}\n'
    if kind == 'braces':          # a bare { } is not a statement, so the blocks are yadi blocks
        return b'mukhya() {\n' + b'yadi (1) {\n' * n + b'likha(1)\n' + b'}\n' * n + b'}\n'
    if kind == 'unary-minus':
        return b'mukhya() {\n    likha(' + b'-(' * n + b'1' + b')' * n + b')\n}\n'
    if kind == 'calls':
        return (b'prakriya f(a) {\n    prati a\n}\nmukhya() {\n    likha(' +
                b'f(' * n + b'1' + b')' * n + b')\n}\n')
    raise ValueError(kind)


def run(comp: str, src: Path, out: Path, timeout: float):
    if out.exists():
        out.unlink()
    try:
        r = subprocess.run([comp, str(src), str(out)], capture_output=True, timeout=timeout, cwd=str(ROOT))
    except subprocess.TimeoutExpired:
        return 'HANG', b'', False
    produced = out.exists()
    if out.exists():
        out.unlink()
    if r.returncode < 0:
        return 'CRASH %s' % signal.Signals(-r.returncode).name, r.stdout, produced
    return str(r.returncode), r.stdout, produced


def judge(code: str, stdout: bytes, produced: bool, must_compile: bool) -> str:
    if must_compile:
        return '' if code == '0' and produced else 'expected to compile, got exit %s' % code
    if code != '1':
        return 'exit %s, expected 1' % code
    if not stdout.lstrip(b'\n').startswith(b'Sutram Error'):
        return 'no "Sutram Error" diagnostic on stdout'
    if produced:
        return 'an output file was written'
    return ''


def corpus_inputs() -> dict:
    """relative name -> bytes: every NAME.sm, and every NAME.sm.b64 decoded (as NAME.sm)."""
    out = {}
    for p in sorted(CORPUS.rglob('*.sm')):
        out[str(p.relative_to(CORPUS))] = p.read_bytes()
    for p in sorted(CORPUS.rglob('*.sm.b64')):
        text = ''.join(l for l in p.read_text(encoding='ascii').splitlines() if not l.startswith('#'))
        rel = str(p.relative_to(CORPUS))[:-4]
        out[rel] = base64.b64decode(text)
    return out


def check_manifest() -> int:
    """Every file in SHA256SUMS has those bytes, and every input is in SHA256SUMS. Returns the count of failures."""
    want = {}
    for line in (CORPUS / 'SHA256SUMS').read_text().splitlines():
        h, _, rel = line.partition('  ')
        want[rel[2:] if rel.startswith('./') else rel] = h
    bad = 0
    inputs = corpus_inputs()
    for p in sorted(CORPUS.rglob('*.sm.b64')):
        twin = p.with_name(p.name[:-4])
        if twin.exists():
            print('FAIL  manifest: %s is a stale text copy of %s; delete it' % (twin.relative_to(CORPUS), p.name)); bad += 1
    for p in sorted(CORPUS.rglob('*.sm')):
        try:
            p.read_bytes().decode('utf-8')
        except UnicodeDecodeError:
            print('FAIL  manifest: %s is not valid UTF-8; store it as %s.b64 (a text copy would change it)'
                  % (p.relative_to(CORPUS), p.name)); bad += 1
    for rel, h in sorted(want.items()):
        if rel not in inputs:
            print('FAIL  manifest: %s is missing' % rel); bad += 1
        elif hashlib.sha256(inputs[rel]).hexdigest() != h:
            print('FAIL  manifest: %s does not have the pinned bytes (re-encoded or edited)' % rel); bad += 1
    for rel in sorted(inputs):
        if rel not in want:
            print('FAIL  manifest: %s is not in SHA256SUMS' % rel); bad += 1
    print('%s  manifest: %d files pinned' % ('FAIL' if bad else 'PASS', len(want)))
    return bad


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--compiler', default=str(ROOT / 'sutram_compiler'))
    ap.add_argument('--timeout', type=float, default=20)
    a = ap.parse_args(argv)
    comp = os.path.abspath(a.compiler)
    fails = check_manifest()
    cases = [(rel, data, False) for rel, data in sorted(corpus_inputs().items())]
    for kind in ('parens', 'parens-unclosed', 'braces', 'unary-minus', 'calls'):
        if kind != 'parens-unclosed':
            ok_n = 100 if kind == 'braces' else 400
            cases.append(('R6-%s-%d-must-compile' % (kind, ok_n), deep(kind, ok_n), True))
        for n in (20000, 100000):
            cases.append(('R6-%s-%d' % (kind, n), deep(kind, n), False))
    with tempfile.TemporaryDirectory() as td:
        src, out = Path(td, 'in.sm'), Path(td, 'out.bin')
        for name, data, must_compile in cases:
            src.write_bytes(data)
            code, stdout, produced = run(comp, src, out, a.timeout)
            why = judge(code, stdout, produced, must_compile)
            first = stdout.lstrip(b'\n').split(b'\n')[0].decode('utf-8', 'replace')[:70]
            print('%s  %-46s %s' % ('FAIL' if why else 'PASS', name, why or first))
            fails += bool(why)
    print('crash corpus: %d cases + manifest, %d failed' % (len(cases), fails))
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
