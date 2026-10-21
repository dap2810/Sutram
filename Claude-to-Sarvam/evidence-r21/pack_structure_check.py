#!/usr/bin/env python3
"""R21-01: an independent structural check of the eleven language packs.

Written from the pack files alone (lang/<pack>.sandesh: `key<TAB>"json string"`,
each entry preceded by a `# "default"` comment holding the romanised Sanskrit
default). It shares no code with tools/sandesh.py or tools/r83_pack_structure.py;
the only thing taken from the project is the list of code words a translation
may keep in Latin letters, and that is derived here from the DEFAULT text of each
message (a Latin word in the pack is allowed only if the same word is in the
default), not from any allowlist.

Checks, per row (HARD = a violation; REVIEW = a candidate for a human):
  H1  key unknown (not in the Sanskrit pack), duplicate, or missing
  H2  empty text
  H3  the text is not valid JSON, or its default comment is missing
  H4  `Sutram Error` and every `[E_CODE]` tag of the default are present, the same number of times
  H5  a Latin-letter word that the default does not have (English, or a misspelt code word)
  H6  a letter outside the pack's own script(s), Latin aside
  H7  the leading newline / `: ` and the trailing newline or opening quote of the default are kept
  H8  a placeholder `{kw:X}` whose word X the default does not print, or `{ver}` where
      the default has no version; or a code word / version of the default missing from the
      pack (a code word: a word the Sanskrit pack, the reference translation, keeps in Latin
      letters or as `{kw:X}`; it is required as often as the Sanskrit pack keeps it, because
      a default can use one word as code and as prose: `vitti x = 5   vitti-ghoshana`)
      (the default comment is the PRINTED text: the pack writes `{kw:likha}` where the
      default prints `likha`, and `{ver}` where it prints `v208`)
  H9  untranslated: no letter of the pack's script at all (the row is the romanised
      default, or code only, while the default has prose)
  R1  a placeholder appears more often than its word does in the default
  R2  the text is byte-identical to the Sanskrit pack's (Devanagari packs only)
  R3  the count of single quotes differs from the default's

usage: python3 -B Claude-to-Sarvam/evidence-r21/pack_structure_check.py [--json OUT] [--root DIR]
       (selftest.py corrupts rows in a copy and shows each corruption is caught)
"""
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKS = ['sanskrit', 'bengali', 'gujarati', 'hindi', 'kannada', 'malayalam', 'marathi', 'odia',
         'punjabi', 'tamil', 'telugu']
# Unicode block ranges each pack may use for its letters
SCRIPT = {
    'sanskrit': [(0x0900, 0x097F), (0xA8E0, 0xA8FF)], 'hindi': [(0x0900, 0x097F), (0xA8E0, 0xA8FF)],
    'marathi': [(0x0900, 0x097F), (0xA8E0, 0xA8FF)], 'bengali': [(0x0980, 0x09FF)],
    'gujarati': [(0x0A80, 0x0AFF)], 'punjabi': [(0x0A00, 0x0A7F)], 'odia': [(0x0B00, 0x0B7F)],
    'tamil': [(0x0B80, 0x0BFF)], 'telugu': [(0x0C00, 0x0C7F)], 'kannada': [(0x0C80, 0x0CFF)],
    'malayalam': [(0x0D00, 0x0D7F)],
}
TAG = re.compile(r'\[E_[A-Z0-9_]+\]')
PH = re.compile(r'\{kw:[^}]*\}|\{ver\}')
LATIN = re.compile(r'[A-Za-z][A-Za-z0-9_]*')
VER = re.compile(r'\bv\d+\b')


def read_pack(name):
    rows, defaults, problems, seen = {}, {}, [], Counter()
    pend = None
    for n, line in enumerate((ROOT / 'lang' / (name + '.sandesh')).read_text(encoding='utf-8').split('\n'), 1):
        if line.startswith('# "'):
            try:
                pend = json.loads(line[2:])
            except json.JSONDecodeError:
                pend = None
            continue
        if not line.strip() or line.startswith('#'):
            continue
        if '\t' not in line:
            problems.append(('H3', '?', 'line %d has no tab' % n)); continue
        key, text = line.split('\t', 1)
        seen[key] += 1
        try:
            rows[key] = json.loads(text)
        except json.JSONDecodeError:
            problems.append(('H3', key, 'not a JSON string')); continue
        if pend is None:
            problems.append(('H3', key, 'no default comment above it'))
        else:
            defaults[key] = pend
        pend = None
    for k, c in seen.items():
        if c > 1:
            problems.append(('H1', k, 'duplicate key (%d times)' % c))
    return rows, defaults, problems


def ends(s):
    lead = '\n' if s.startswith('\n') else (': ' if s.startswith(': ') else '')
    trail = s[-1] if s and s[-1] in '\n"\'' else ''
    return lead, trail


def check(name, rows, defaults, sanskrit_rows, code_words):
    hard, review = [], []
    for key, t in rows.items():
        d = defaults.get(key)
        if d is None:
            continue
        if t == '':
            hard.append(('H2', key, 'empty')); continue
        # H4
        for want in ['Sutram Error'] + TAG.findall(d):
            if t.count(want) != d.count(want):
                hard.append(('H4', key, '%s: %d in the default, %d here' % (want, d.count(want), t.count(want))))
        # H5 / H6
        dwords = set(w.lower() for w in LATIN.findall(d))
        for w in LATIN.findall(PH.sub(' ', TAG.sub(' ', t))):
            if w.lower() not in dwords:
                hard.append(('H5', key, 'Latin word not in the default: %r' % w))
        for ch in PH.sub(' ', TAG.sub(' ', t)):
            if unicodedata.category(ch).startswith('L') or unicodedata.category(ch) in ('Mn', 'Mc'):
                o = ord(ch)
                if o < 0x80:
                    continue
                if not any(a <= o <= b for a, b in SCRIPT[name]):
                    hard.append(('H6', key, 'character outside the pack script: %r U+%04X' % (ch, o)))
        # H9
        body = PH.sub(' ', TAG.sub(' ', t))
        if not any(any(a <= ord(ch) <= b for a, b in SCRIPT[name]) for ch in body):
            dprose = [w for w in LATIN.findall(d) if w.lower() not in ('sutram', 'error') and not VER.match(w)]
            if dprose:
                hard.append(('H9', key, 'no letter of the pack script; the default has %d Latin words' % len(dprose)))
        # H7
        if ends(t) != ends(d):
            hard.append(('H7', key, 'ends differ: default %r, pack %r' % (ends(d), ends(t))))
        # H8 / R1: a placeholder stands for a word the default prints
        dcount = Counter(LATIN.findall(d))
        ph = Counter(PH.findall(t))
        for p, c in ph.items():
            if p == '{ver}':
                if not VER.search(d):
                    hard.append(('H8', key, '{ver} but the default has no version'))
                continue
            word = p[4:-1]
            if dcount[word] == 0:
                hard.append(('H8', key, 'placeholder %s: the default does not print %r' % (p, word)))
            elif c > dcount[word]:
                review.append(('R1', key, '%s %d times, the default prints %s %d' % (p, c, word, dcount[word])))
        if VER.search(d) and '{ver}' not in t and not VER.search(t):
            hard.append(('H8', key, 'the default has a version and the pack neither {ver} nor one'))
        # H8 reverse: every CODE word the default prints is in the pack, as the word or as {kw:word},
        # as many times. A code word is a Latin word of the default that some pack writes as {kw:X}
        # or that the Sanskrit pack keeps in Latin letters (the rest of the default is romanised prose,
        # which the packs translate, so it cannot be required).
        tcount = Counter(LATIN.findall(PH.sub(' ', TAG.sub(' ', t))))
        for word, need in code_words.get(key, {}).items():
            need = min(need, dcount[word])
            have = tcount[word] + ph['{kw:%s}' % word]
            if have < need:
                hard.append(('H8', key, 'the code word %r is kept %d times in the Sanskrit pack, %d here (as the word or {kw:%s})' % (word, need, have, word)))
        # R2
        if name != 'sanskrit' and name in ('hindi', 'marathi') and sanskrit_rows.get(key) == t:
            review.append(('R2', key, 'byte-identical to the Sanskrit pack'))
        # R3
        if t.count("'") != d.count("'"):
            review.append(('R3', key, "single quotes: %d, default %d" % (t.count("'"), d.count("'"))))
    return hard, review


def main(argv):
    global ROOT
    out_json = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--root' in argv:
        ROOT = Path(argv[argv.index('--root') + 1])
    sk_rows, sk_def, sk_prob = read_pack('sanskrit')
    keys = set(sk_rows)
    # code words per key: what the Sanskrit pack (the reference translation) keeps in Latin letters or
    # as {kw:X}, and how many times; the other ten packs must keep each at least that often
    code_words = {}
    for key, t in sk_rows.items():
        c = Counter(w for w in LATIN.findall(PH.sub(' ', TAG.sub(' ', t)))
                    if w.lower() not in ('sutram', 'error') and not VER.match(w))
        c.update(p[4:-1] for p in PH.findall(t) if p != '{ver}')
        code_words[key] = c
    report = {}
    tot_rows = tot_hard = tot_rev = 0
    print('%-10s %5s %5s %6s %7s' % ('pack', 'rows', 'hard', 'review', 'missing'))
    for name in PACKS:
        rows, defaults, problems = read_pack(name)
        hard, review = check(name, rows, defaults, sk_rows, code_words)
        hard = problems + hard
        for k in rows:
            if k not in keys:
                hard.append(('H1', k, 'key unknown to the Sanskrit pack'))
        missing = sorted(keys - set(rows))
        for k in missing:
            hard.append(('H1', k, 'missing'))
        tot_rows += len(rows); tot_hard += len(hard); tot_rev += len(review)
        print('%-10s %5d %5d %6d %7d' % (name, len(rows), len(hard), len(review), len(missing)))
        report[name] = {'rows': len(rows), 'hard': hard, 'review': review}
    print('total: %d rows, %d hard violations, %d review candidates' % (tot_rows, tot_hard, tot_rev))
    for name in PACKS:
        for kind, key, why in report[name]['hard']:
            print('HARD   %-10s %-28s %s %s' % (name, key, kind, why))
    for name in PACKS:
        for kind, key, why in report[name]['review']:
            print('REVIEW %-10s %-28s %s %s' % (name, key, kind, why))
    if out_json:
        Path(out_json).write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return 1 if tot_hard else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
