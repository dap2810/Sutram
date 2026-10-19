#!/usr/bin/env python3
"""R9 (WS6): the IDE's transliteration engine (NASM) against tools/translit.py.

Builds tests/translit/r9_translit_test.asm on Linux, feeds it every keyword of every pack plus
generated words (every token alone, every consonant with every vowel, conjuncts, words with
digits and _), for all 11 packs, and requires byte-identical UTF-16 to the reference.
The keyword table lookup is the IDE's, not the engine's, so this checks the phonetic path.
"""
import itertools
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import translit as T  # noqa: E402


def words():
    toks = [t[0] for t in T.TOKENS]
    vow = [t[0] for t in T.TOKENS if t[1] == 'V']
    con = [t[0] for t in T.TOKENS if t[1] == 'C']
    ws = set(toks)
    ws |= {c + v for c in con for v in vow}
    ws |= {c1 + c2 + 'a' for c1, c2 in itertools.product(con, repeat=2)}
    ws |= {'mukhya', 'likha', 'kamala', 'yavat', 'lakShmii', 'x_1', 'ankaganana', 'a1b2', 'Ri', 'kRiShNa',
           'saMskRitam', 'duHkha', 'aaiiuu', 'zzz', 'Q', 'B', 'k', 'kk', 'aM', 'aH', 'jodaa_2'}
    for p, _ in T.PACKS:
        ws |= set(T.pack_keywords(p))
    return sorted(w for w in ws if w and w[0].isascii() and w[0].isalpha() and len(w) < 60)


def main():
    with tempfile.TemporaryDirectory() as d:
        o, exe = Path(d, 't.o'), Path(d, 't')
        subprocess.run(['nasm', '-f', 'elf64', '-I', str(ROOT) + '/',
                        str(ROOT / 'tests/translit/r9_translit_test.asm'), '-o', str(o)], check=True)
        subprocess.run(['ld', '-o', str(exe), str(o)], check=True)
        ws = words()
        cases = [(i, p, b, w) for i, (p, b) in enumerate(T.PACKS) for w in ws]
        inp = ''.join(f'{i} {w}\n' for i, _, _, w in cases).encode()
        out = subprocess.run([str(exe)], input=inp, capture_output=True, check=True).stdout.decode('utf-16-le')
        got = out.split('\n')[:-1]
        bad = [(p, w, g, T.phonetic(w, b)) for (i, p, b, w), g in zip(cases, got) if g != T.phonetic(w, b)]
        print(f'{len(cases)} cases ({len(ws)} words x {len(T.PACKS)} packs), {len(bad)} differ')
        for b in bad[:20]:
            print('  DIFF', b)
        return 1 if bad or len(got) != len(cases) else 0


if __name__ == '__main__':
    raise SystemExit(main())
