#!/usr/bin/env python3
"""Latin -> Brahmic transliteration for the IDE's typing mode (ROUND-09, WS6).

This file is the reference. It also writes the data table the Windows IDE assembles,
windows/gui/r9_translit_data.inc, so the IDE and this reference cannot drift:

    python3 tools/translit.py --write-inc          # regenerate the .inc
    python3 tools/translit.py mukhya likha ganana  # show what the IDE would type (Devanagari)
    python3 tools/translit.py --script tamil vitti

How a word is converted (the IDE does this when a word ends: space, punctuation, Enter, Tab):

  1. If the word is a keyword in the selected language pack (lang/<pack>.lang, second
     column), it becomes that pack's own word: `mukhya` -> मुख्य, and in Hindi `vitti` -> चर.
     That is a table lookup, so a keyword always compiles with --lang <pack>.
  2. Otherwise it is spelled phonetically, letter by letter, in the pack's script:
       vowels      a aa/A i ii/I u uu/U Ri e ai o au
       consonants  k kh g gh ~N  c/ch chh j jh ~n  T Th D Dh N  t th d dh n
                   p ph/f b bh m  y r l L v/w  sh Sh s h   x = kSh = क्ष
       signs       M (anusvara)  H (visarga)
     A consonant followed by a consonant gets a virama between them (conjunct); a
     consonant at the end of a word keeps its virama, so type the final vowel you want:
     `kamala` -> कमल, `yavat` -> यवत्. What you type is what you get.
     Digits, `_` and anything else are kept as typed.

All nine Indic scripts Sutram's packs use share one layout (Unicode followed ISCII), so one
table of offsets serves all of them: the code point is the script's base + the offset. Where a
script has no letter at that offset (Tamil has no kha, Gurmukhi no ṣa), the nearest letter it
does have is used: aspirate -> plain, voiced -> unvoiced, ṣa -> śa -> sa. The substitutions
are computed here from the Unicode database and written into the table.
"""
from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INC = ROOT / 'windows/gui/r9_translit_data.inc'

# pack name -> script base code point (packs in the IDE's order: kw_pack_paths)
PACKS = [('sanskrit', 0x0900), ('bengali', 0x0980), ('gujarati', 0x0A80), ('hindi', 0x0900),
         ('kannada', 0x0C80), ('malayalam', 0x0D00), ('marathi', 0x0900), ('odia', 0x0B00),
         ('punjabi', 0x0A00), ('tamil', 0x0B80), ('telugu', 0x0C00)]
SCRIPTS = sorted({b for _, b in PACKS})

VIRAMA = 0x4D
# kind V: (independent vowel offset, matra offset or 0 for the inherent a)
# kind C: tuple of consonant offsets (two for x / kSh)
# kind S: a sign that follows a syllable
TOKENS = [
    ('aa', 'V', (0x06, 0x3E)), ('A', 'V', (0x06, 0x3E)), ('ai', 'V', (0x10, 0x48)), ('au', 'V', (0x14, 0x4C)),
    ('a', 'V', (0x05, 0x00)), ('ii', 'V', (0x08, 0x40)), ('I', 'V', (0x08, 0x40)), ('i', 'V', (0x07, 0x3F)),
    ('uu', 'V', (0x0A, 0x42)), ('U', 'V', (0x0A, 0x42)), ('u', 'V', (0x09, 0x41)), ('Ri', 'V', (0x0B, 0x43)),
    ('e', 'V', (0x0F, 0x47)), ('o', 'V', (0x13, 0x4B)),
    ('kSh', 'C', (0x15, 0x37)), ('x', 'C', (0x15, 0x37)),
    ('kh', 'C', (0x16,)), ('k', 'C', (0x15,)), ('q', 'C', (0x15,)), ('gh', 'C', (0x18,)), ('g', 'C', (0x17,)),
    ('~N', 'C', (0x19,)), ('chh', 'C', (0x1B,)), ('ch', 'C', (0x1A,)), ('c', 'C', (0x1A,)),
    ('jh', 'C', (0x1D,)), ('j', 'C', (0x1C,)), ('z', 'C', (0x1C,)), ('~n', 'C', (0x1E,)),
    ('Th', 'C', (0x20,)), ('T', 'C', (0x1F,)), ('Dh', 'C', (0x22,)), ('D', 'C', (0x21,)), ('N', 'C', (0x23,)),
    ('th', 'C', (0x25,)), ('t', 'C', (0x24,)), ('dh', 'C', (0x27,)), ('d', 'C', (0x26,)), ('n', 'C', (0x28,)),
    ('ph', 'C', (0x2B,)), ('f', 'C', (0x2B,)), ('p', 'C', (0x2A,)), ('bh', 'C', (0x2D,)), ('b', 'C', (0x2C,)),
    ('m', 'C', (0x2E,)), ('y', 'C', (0x2F,)), ('r', 'C', (0x30,)), ('l', 'C', (0x32,)), ('L', 'C', (0x33,)),
    ('v', 'C', (0x35,)), ('w', 'C', (0x35,)), ('sh', 'C', (0x36,)), ('Sh', 'C', (0x37,)), ('s', 'C', (0x38,)),
    ('h', 'C', (0x39,)),
    ('M', 'S', (0x02,)), ('H', 'S', (0x03,)),
]
TOKENS.sort(key=lambda t: -len(t[0]))      # longest match first; stable for equal lengths

# nearest-letter fallbacks, tried in order, for a script that lacks an offset
FALLBACK = {
    0x16: [0x15], 0x17: [0x15], 0x18: [0x17, 0x15], 0x19: [0x28],
    0x1B: [0x1A], 0x1C: [0x1A], 0x1D: [0x1C, 0x1A], 0x1E: [0x28],
    0x20: [0x1F], 0x21: [0x1F], 0x22: [0x21, 0x1F], 0x23: [0x28],
    0x25: [0x24], 0x26: [0x24], 0x27: [0x26, 0x24],
    0x2B: [0x2A], 0x2C: [0x2A], 0x2D: [0x2C, 0x2A],
    0x33: [0x32], 0x35: [0x2C], 0x36: [0x38], 0x37: [0x36, 0x38],
    0x0B: [], 0x43: [],                      # vocalic r: dropped where absent
    0x02: [], 0x03: [],
}


def assigned(cp: int) -> bool:
    return unicodedata.name(chr(cp), None) is not None


def subst_table(base: int) -> list[int]:
    """For each offset 0..127: 0 = use as is, 1..127 = use that offset instead, 0xFF = drop."""
    t = []
    for off in range(128):
        if assigned(base + off):
            t.append(0)
            continue
        for alt in FALLBACK.get(off, []):
            if assigned(base + alt):
                t.append(alt)
                break
        else:
            t.append(0xFF)
    return t


def emit(base: int, off: int, out: list[int], table: list[int]):
    s = table[off]
    if s == 0xFF:
        return
    out.append(base + (s or off))


def phonetic(word: str, base: int) -> str:
    table = subst_table(base)
    out: list[int] = []
    i, state = 0, None                       # state 'C' = a consonant without its vowel yet
    while i < len(word):
        for lat, kind, offs in TOKENS:
            if word.startswith(lat, i):
                break
        else:
            out.append(ord(word[i]))
            state = None
            i += 1
            continue
        i += len(lat)
        if kind == 'V':
            if state == 'C':
                if offs[1]:
                    emit(base, offs[1], out, table)
            else:
                emit(base, offs[0], out, table)
            state = None
        elif kind == 'C':
            for off in offs:
                if state == 'C':
                    emit(base, VIRAMA, out, table)
                emit(base, off, out, table)
                state = 'C'
        else:
            emit(base, offs[0], out, table)
            state = None
    if state == 'C':
        emit(base, VIRAMA, out, table)
    return ''.join(map(chr, out))


def pack_keywords(pack: str) -> dict[str, str]:
    kw = {}
    for line in (ROOT / 'lang' / f'{pack}.lang').read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] not in kw:
            kw[parts[1]] = parts[0]
    return kw


def convert(word: str, pack: str) -> str:
    """What the IDE types for `word` in `pack`."""
    kw = pack_keywords(pack)
    if word in kw:
        return kw[word]
    if not word or not (word[0].isalpha() and word[0].isascii()):
        return word
    return phonetic(word, dict(PACKS)[pack])


def write_inc() -> None:
    lines = ['; GENERATED by tools/translit.py --write-inc. Do not edit by hand.',
             '; R9 (WS6): Latin -> Brahmic token table and per-script substitutions.',
             '; Token record: db len, kind (1=V 2=C 3=S), off1, off2, then len ASCII bytes.',
             'section .data', 'r9_tl_tokens:']
    kinds = {'V': 1, 'C': 2, 'S': 3}
    for lat, kind, offs in TOKENS:
        o1, o2 = (offs + (0,))[:2]
        lines.append(f"    db {len(lat)},{kinds[kind]},0x{o1:02X},0x{o2:02X},'{lat}'")
    lines.append('    db 0')
    lines.append('; Per pack (kw_pack_paths order): dw base code point, then 128 substitution bytes')
    lines.append('; (0 = as is, 0xFF = drop, otherwise the offset to use).')
    lines.append('r9_tl_scripts:')
    for name, base in PACKS:
        t = subst_table(base)
        lines.append(f'    dw 0x{base:04X}            ; {name}')
        for k in range(0, 128, 16):
            lines.append('    db ' + ','.join(f'0x{x:02X}' for x in t[k:k + 16]))
    lines.append('R9_TL_SCRIPT_BYTES equ 130')
    INC.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write-inc', action='store_true')
    ap.add_argument('--script', default='sanskrit', help='a pack name: ' + ', '.join(p for p, _ in PACKS))
    ap.add_argument('words', nargs='*')
    a = ap.parse_args(argv)
    if a.write_inc:
        write_inc()
        print('wrote', INC.relative_to(ROOT))
    for w in a.words:
        print(f'{w} -> {convert(w, a.script)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
