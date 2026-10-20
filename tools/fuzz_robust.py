#!/usr/bin/env python3
"""ROUND-15 WS2: a robustness fuzzer for the Sutram compiler.

The compiler is given INVALID (or merely hostile) input. It must answer with a
diagnostic and a non-zero exit, or compile the input; it must never crash or
hang. A crash on bad input is a defect even though the input is wrong.

Two parts:
  1. FIXED cases, one per kind of hostile input (empty file, NUL bytes,
     unclosed braces, deep nesting, malformed UTF-8, very long lines, a 100 MB
     line, very many functions or locals ...). Each is generated here.
  2. MUTATIONS of valid programs (every examples/*.sm and programs from
     tools/fuzz_valid.py): truncate, delete, insert, duplicate, flip bits,
     splice tokens. Deterministic from --seed.

Each run of the compiler is classified:
  CRASH    killed by a signal (SIGSEGV, SIGBUS, SIGFPE, SIGABRT ...)
  HANG     still running after --timeout seconds
  ERROR    non-zero exit (the expected answer for invalid input)
  ACCEPTED exit 0 (for a mutation that happens to be valid, or that the
           compiler does not reject; reported, not a failure)

Every CRASH and HANG input is saved under --out with the command to reproduce.

usage:
  python3 -B tools/fuzz_robust.py --seed 15 --mutations 5000 [--compiler ./sutram_compiler]
                                  [--out DIR] [--no-big] [--timeout 20]
Exit 0 when no input crashed or hung, 1 otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import resource
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fuzz_valid as fv  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HELLO = b'mukhya() {\n    likha(1)\n}\n'


def fixed_cases(big: bool):
    """(name, bytes or a callable that writes the file) for each hostile input."""
    c = []
    add = lambda n, b: c.append((n, b))
    add('empty', b'')
    add('only-newlines', b'\n' * 1000)
    add('only-spaces', b' ' * 100000)
    add('only-comment', b'# nothing here\n')
    add('only-block-comment-unclosed', b'/* never closed\nmukhya() { likha(1) }\n')
    add('nul-alone', b'\0')
    add('nul-many', b'\0' * 100000)
    add('nul-in-identifier', b'mukhya() {\n    vitti a\0b = 1\n    likha(1)\n}\n')
    add('nul-in-string', b'mukhya() {\n    likha("ab\0cd")\n}\n')
    add('nul-after-program', HELLO + b'\0\0\0')
    add('unclosed-brace', b'mukhya() {\n    likha(1)\n')
    add('unclosed-brace-function', b'prakriya f(a) {\n    prati a\nmukhya() {\n    likha(f(1))\n}\n')
    add('extra-close-brace', HELLO + b'}\n}\n')
    add('unclosed-paren', b'mukhya() {\n    likha((1 + 2)\n}\n')
    add('unclosed-string', b'mukhya() {\n    likha("abc)\n}\n')
    add('unclosed-string-eof', b'mukhya() {\n    likha("abc')
    add('unclosed-index', b'mukhya() {\n    mala a[4]\n    a[1 = 2\n}\n')
    add('operator-at-eof', b'mukhya() {\n    vitti x = 1 +')
    add('keyword-only', b'yadi')
    add('mukhya-only', b'mukhya')
    add('mukhya-twice', HELLO + HELLO)
    add('no-mukhya', b'prakriya f(a) {\n    prati a\n}\n')
    add('return-in-mukhya-no-value', b'mukhya() {\n    prati\n}\n')
    add('lone-else', b'mukhya() {\n    anya { likha(1) }\n}\n')
    add('lone-bang', b'mukhya() {\n    likha(!)\n}\n')
    add('double-minus', b'mukhya() {\n    likha(--4)\n}\n')
    add('seven-params', b'prakriya f(a, b, c, d, e, g, h) {\n    prati a\n}\nmukhya() {\n    likha(f(1,2,3,4,5,6,7))\n}\n')
    add('call-100-args', b'prakriya f(a) {\n    prati a\n}\nmukhya() {\n    likha(f(' + b', '.join(b'1' for _ in range(100)) + b'))\n}\n')
    add('call-undefined', b'mukhya() {\n    likha(nope(1))\n}\n')
    add('recursive-type', b'rachana P = { P }\nmukhya() {\n    likha(1)\n}\n')
    add('rachana-unclosed', b'rachana P = { a, b\nmukhya() {\n    likha(1)\n}\n')
    add('mala-zero', b'mukhya() {\n    mala a[0]\n    likha(1)\n}\n')
    add('mala-negative', b'mukhya() {\n    mala a[-5]\n    likha(1)\n}\n')
    add('mala-huge', b'mukhya() {\n    mala a[99999999999999]\n    likha(1)\n}\n')
    add('kosh-huge', b'mukhya() {\n    kosh k[99999999999999]\n    likha(1)\n}\n')
    add('literal-overflow', b'mukhya() {\n    likha(99999999999999999999999999999)\n}\n')
    add('literal-10k-digits', b'mukhya() {\n    likha(' + b'9' * 10000 + b')\n}\n')
    add('float-literal-10k-digits', b'mukhya() {\n    dasham x = 1.' + b'5' * 10000 + b'\n    likha(1)\n}\n')
    add('float-exponent', b'mukhya() {\n    dasham x = 1e999999\n    likha(1)\n}\n')
    add('identifier-1MB', b'mukhya() {\n    vitti ' + b'a' * (1 << 20) + b' = 1\n    likha(1)\n}\n')
    add('string-1MB', b'mukhya() {\n    likha("' + b'x' * (1 << 20) + b'")\n}\n')
    add('comment-1MB', b'# ' + b'c' * (1 << 20) + b'\n' + HELLO)
    for n in (100, 1000, 10000, 100000):
        add('parens-%d' % n, b'mukhya() {\n    likha(' + b'(' * n + b'1' + b')' * n + b')\n}\n')
        add('parens-unclosed-%d' % n, b'mukhya() {\n    likha(' + b'(' * n + b'1)\n}\n')
        add('braces-%d' % n, b'mukhya() ' + b'{' * n + b'\n    likha(1)\n' + b'}' * n + b'\n')
        add('yadi-nest-%d' % n, b'mukhya() {\n' + b'yadi (1) {\n' * n + b'likha(1)\n' + b'}\n' * n + b'}\n')
        add('unary-minus-%d' % n, b'mukhya() {\n    likha(' + b'-(' * n + b'1' + b')' * n + b')\n}\n')
        add('ternary-chain-%d' % n, b'mukhya() {\n    likha(' + b'1 ? ' * n + b'1' + b' : 0' * n + b')\n}\n')
        add('sum-chain-%d' % n, b'mukhya() {\n    likha(' + b' + '.join(b'1' for _ in range(n)) + b')\n}\n')
        add('statements-%d' % n, b'mukhya() {\n' + b'    likha(1)\n' * n + b'}\n')
        add('locals-%d' % n, b'mukhya() {\n' + b''.join(b'    vitti v%d = %d\n' % (i, i) for i in range(n)) + b'    likha(v0)\n}\n')
        add('called-locals-%d' % n, b'prakriya f(x) {\n' + b''.join(b'    vitti v%d = x\n' % i for i in range(n)) +
            b'    prati v0\n}\nmukhya() {\n    likha(f(1))\n}\n')
        add('functions-%d' % n, b''.join(b'prakriya f%d(a) {\n    prati a\n}\n' % i for i in range(n)) + HELLO)
        add('globals-%d' % n, b''.join(b'vitti g%d = %d\n' % (i, i) for i in range(n)) + HELLO)
        add('fields-%d' % n, b'rachana P = { ' + b', '.join(b'f%d' % i for i in range(n)) + b' }\n' + HELLO)
        add('call-depth-%d' % n, b'prakriya f(a) {\n    prati a\n}\nmukhya() {\n    likha(' + b'f(' * n + b'1' + b')' * n + b')\n}\n')
    # malformed UTF-8
    for name, seq in [('utf8-lone-continuation', b'\x80'), ('utf8-ff', b'\xff'), ('utf8-fe', b'\xfe'),
                      ('utf8-truncated-2', b'\xc3'), ('utf8-truncated-3', b'\xe0\xa4'),
                      ('utf8-truncated-4', b'\xf0\x9f\x98'), ('utf8-overlong-slash', b'\xc0\xaf'),
                      ('utf8-overlong-nul', b'\xc0\x80'), ('utf8-surrogate', b'\xed\xa0\x80'),
                      ('utf8-above-10ffff', b'\xf4\x90\x80\x80'), ('utf8-5-byte', b'\xf8\x88\x80\x80\x80')]:
        add(name + '-in-identifier', b'mukhya() {\n    vitti a' + seq + b'b = 1\n    likha(1)\n}\n')
        add(name + '-in-string', b'mukhya() {\n    likha("a' + seq + b'b")\n}\n')
        add(name + '-in-comment', b'# a' + seq + b'b\n' + HELLO)
        add(name + '-at-eof', HELLO + seq)
        add(name + '-in-devanagari', 'मुख्य() {\n    लिख(१'.encode() + seq + b')\n}\n')
    add('bom', b'\xef\xbb\xbf' + HELLO)
    add('bom-twice', b'\xef\xbb\xbf\xef\xbb\xbf' + HELLO)
    add('cr-only', HELLO.replace(b'\n', b'\r'))
    add('crlf', HELLO.replace(b'\n', b'\r\n'))
    add('utf16le', HELLO.decode().encode('utf-16-le'))
    add('binary-random-64k', random.Random(7).randbytes(65536))
    add('elf-binary-as-source', (ROOT / 'sutram_compiler').read_bytes()[:200000])
    add('yoj-missing', b'yoj nahi_asti_module\n' + HELLO)
    add('yoj-empty-name', b'yoj\n' + HELLO)
    add('yoj-path-traversal', b'yoj ../../etc/passwd\n' + HELLO)
    add('yoj-long-name', b'yoj ' + b'm' * 5000 + b'\n' + HELLO)
    add('yoj-three-modules', b'yoj ganit\nyoj ank\nyoj shreni\n' + HELLO)
    add('yoj-eight-modules', b''.join(b'yoj %s\n' % m for m in
        (b'ganit', b'ank', b'shreni', b'ganita', b'madhava', b'varna', b'roop', b'vakyank')) + HELLO)
    add('lang-pack-word-mix', 'मुख्य() {\n    likha(1)\n}\n'.encode())
    if big:
        add('file-10MB-statements', lambda p: _write_statements(p, 10 << 20))
        add('file-50MB-statements', lambda p: _write_statements(p, 50 << 20))
        add('line-100MB', lambda p: _write_one_line(p, 100 << 20))
        add('line-100MB-in-mukhya', lambda p: _write_line_in_mukhya(p, 100 << 20))
    return c


def _write_statements(path, size):
    with open(path, 'wb') as f:
        f.write(b'mukhya() {\n')
        line = b'    vitti x = 1 + 2\n'
        f.write(line * (size // len(line)))
        f.write(b'}\n')


def _write_one_line(path, size):
    with open(path, 'wb') as f:
        chunk = b'likha(1); ' * 100000
        n = 0
        f.write(b'mukhya() { ')
        while n < size:
            f.write(chunk); n += len(chunk)
        f.write(b'}\n')


def _write_line_in_mukhya(path, size):
    with open(path, 'wb') as f:
        f.write(b'mukhya() {\n    likha(')
        chunk = b'1 + ' * 250000
        n = 0
        while n < size:
            f.write(chunk); n += len(chunk)
        f.write(b'1)\n}\n')


# ------------------------------------------------------------------ mutations
TOKENS = [b'{', b'}', b'(', b')', b'[', b']', b',', b';', b'"', b'=', b'==', b'+', b'-', b'*', b'/', b'%',
          b'<<', b'>>', b'?', b':', b'.', b'\n', b'\0', b'yadi', b'anya', b'chakra', b'tak', b'yavat',
          b'kuru', b'krama', b'agrim', b'prati', b'prakriya', b'mukhya', b'vitti', b'mala', b'kosh',
          b'rachana', b'dasham', b'sutra', b'yoj', b'likha', b'nirmmita', b'kosh_push', b'kosh_pop',
          b'9223372036854775808', b'-1', b'0', b'1.5', b'\xff', b'\xe0\xa4', '॥'.encode(), '।'.encode(),
          '/*'.encode(), b'#', b'//']


def mutate(rng: random.Random, src: bytes) -> bytes:
    b = bytearray(src)
    for _ in range(rng.choice([1, 1, 1, 2, 3, 5])):
        op = rng.randrange(8)
        n = len(b)
        if n == 0:
            b += rng.choice(TOKENS); continue
        i = rng.randrange(n)
        if op == 0:                                   # truncate
            del b[rng.randrange(n):]
        elif op == 1:                                 # delete a run
            del b[i:i + rng.randint(1, 20)]
        elif op == 2:                                 # insert a token
            b[i:i] = rng.choice(TOKENS)
        elif op == 3:                                 # insert random bytes
            b[i:i] = rng.randbytes(rng.randint(1, 8))
        elif op == 4:                                 # flip a bit
            b[i] ^= 1 << rng.randrange(8)
        elif op == 5:                                 # duplicate a run
            j = rng.randrange(i, min(n, i + 200) + 1)
            b[j:j] = b[i:j]
        elif op == 6:                                 # replace a byte with a delimiter
            b[i:i + 1] = rng.choice([b'{', b'}', b'(', b')', b'"', b'\n', b'\0'])
        else:                                         # swap two lines
            lines = bytes(b).split(b'\n')
            if len(lines) > 2:
                x, y = rng.randrange(len(lines)), rng.randrange(len(lines))
                lines[x], lines[y] = lines[y], lines[x]
                b = bytearray(b'\n'.join(lines))
    return bytes(b)


def seeds(rng):
    out = [p.read_bytes() for p in sorted((ROOT / 'examples').glob('*.sm'))]
    for i in range(60):
        prog, decls, minimal, _ = fv.make(rng.randrange(1 << 30), i, False)
        out.append(fv.program_src(prog, decls, minimal).encode())
    return out


# --------------------------------------------------------------------- runner
def limit():
    resource.setrlimit(resource.RLIMIT_AS, (4 << 30, 4 << 30))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run(comp, path, outbin, timeout):
    try:
        r = subprocess.run([comp, str(path), str(outbin)], capture_output=True, timeout=timeout,
                           preexec_fn=limit, cwd=str(ROOT))
    except subprocess.TimeoutExpired:
        return 'HANG', ''
    msg = (r.stdout + r.stderr).decode('utf-8', 'replace').strip().splitlines()
    first = msg[0][:160] if msg else ''
    if r.returncode < 0:
        return 'CRASH %s' % signal.Signals(-r.returncode).name, first
    if r.returncode != 0:
        return 'ERROR', first
    return 'ACCEPTED', first


def reduce_bytes(comp, data, timeout, want='CRASH'):
    """Delta-debug an input down to a small one that still CRASHes (or HANGs):
    first whole lines, then runs of bytes."""
    with tempfile.TemporaryDirectory() as td:
        sp, bp = Path(td, 'in.sm'), Path(td, 'out.bin')

        def bad(b):
            sp.write_bytes(b)
            return run(comp, sp, bp, timeout)[0].startswith(want)
        if not bad(data):
            return None
        for sep in (b'\n', None):
            parts = data.split(b'\n') if sep else [bytes([c]) for c in data]
            join = (lambda ps: b'\n'.join(ps)) if sep else (lambda ps: b''.join(ps))
            n = 2
            while len(parts) >= 2:
                chunk = max(1, len(parts) // n)
                removed = False
                for i in range(0, len(parts), chunk):
                    cand = parts[:i] + parts[i + chunk:]
                    if cand and bad(join(cand)):
                        parts, removed = cand, True
                        n = max(n - 1, 2)
                        break
                if not removed:
                    if chunk == 1:
                        break
                    n = min(n * 2, len(parts))
            data = join(parts)
        return data


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=15)
    ap.add_argument('--mutations', type=int, default=2000)
    ap.add_argument('--compiler', default=str(ROOT / 'sutram_compiler'))
    ap.add_argument('--out', default='fuzz-robust-out')
    ap.add_argument('--timeout', type=float, default=20)
    ap.add_argument('--no-big', action='store_true', help='skip the 10-100 MB inputs')
    ap.add_argument('--no-fixed', action='store_true')
    ap.add_argument('--reduce', metavar='FILE', help='shrink one crashing input and print it')
    a = ap.parse_args(argv)
    comp = os.path.abspath(a.compiler)
    if a.reduce:
        r = reduce_bytes(comp, Path(a.reduce).read_bytes(), a.timeout)
        if r is None:
            print('does not crash'); return 0
        dst = Path(a.reduce).with_suffix('.reduced.sm')
        dst.write_bytes(r)
        print('%d bytes -> %s' % (len(r), dst)); sys.stdout.write(r.decode('utf-8', 'replace') + '\n')
        return 0
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    counts = {}
    bad = 0
    report = []
    with tempfile.TemporaryDirectory() as td:
        sp, bp = Path(td, 'in.sm'), Path(td, 'out.bin')

        def one(name, data, kind):
            nonlocal bad
            if callable(data):
                data(sp)
            else:
                sp.write_bytes(data)
            if bp.exists():
                bp.unlink()
            v, first = run(comp, sp, bp, a.timeout)
            key = v.split()[0]
            counts.setdefault(kind, {}).setdefault(key, 0)
            counts[kind][key] += 1
            report.append('%-9s %-40s %s' % (v.split()[0], name, (v + ' ' + first).strip()))
            if key in ('CRASH', 'HANG'):
                bad += 1
                size = sp.stat().st_size
                if size <= (1 << 20):
                    dst = out / (name + '.sm')
                    dst.write_bytes(sp.read_bytes())
                    where = str(dst)
                else:
                    where = '(not saved: %d bytes; regenerate with this tool)' % size
                print('%s  %s  %s' % (v, name, where), flush=True)

        if not a.no_fixed:
            for name, data in fixed_cases(not a.no_big):
                one(name, data, 'fixed')
        rng = random.Random(a.seed)
        base = seeds(rng)
        for i in range(a.mutations):
            src = rng.choice(base)
            m = mutate(rng, src)
            one('mutation-%d-%d' % (a.seed, i), m, 'mutation')
    (out / 'report.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
    for kind, c in counts.items():
        print('%-9s %s' % (kind, '  '.join('%s %d' % kv for kv in sorted(c.items()))))
    print('CRASH or HANG: %d' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
