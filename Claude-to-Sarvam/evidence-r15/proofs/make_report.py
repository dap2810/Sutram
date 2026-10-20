#!/usr/bin/env python3
"""R15-03: turn tools/lib_mutant_score.py's JSON into the per-function table and
the ranked list of the weakest proofs.

usage: python3 -B make_report.py score.json witness.json out.md

Survivors are split by witness_r15.py's result:
  W   WITNESS: an input tells it apart (a defect the proofs would miss,
      unless that input is outside the function's contract; not judged here)
  NW  NO-WITNESS: no input in the set told it apart (likely equivalent)
  NT  NOT-TRIED: list, string or record parameters (undecided)
The ranking uses killed / (mutants - NW): likely-equivalent survivors are not
held against a proof; undecided ones are.
"""
import json
import sys
from collections import Counter, defaultdict

rows = json.load(open(sys.argv[1], encoding='utf-8'))
wit = json.load(open(sys.argv[2], encoding='utf-8'))
OUT = sys.argv[3]
WC = defaultdict(Counter)
WLIST = defaultdict(list)
for x in wit:
    key = (x['module'], x['name'])
    WC[key][{'WITNESS': 'W', 'NO-WITNESS': 'NW', 'NOT-TRIED': 'NT'}[x['result']]] += 1
    if x['result'] == 'WITNESS':
        WLIST[key].append(x)
# A NO-WITNESS result only compares return values. For a function whose effect
# is in memory it writes or a file (a constructor returns a handle; patra writes
# files), the witness cannot see the difference, so NO-WITNESS proves nothing:
# those survivors count as NOT-TRIED.
import re
from pathlib import Path
_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_root / 'tools'))
import lib_proof_gaps as G  # noqa: E402
MEM = re.compile(r'\]\s*=[^=]|\blikh8?\s*\(|akshar_rakh\s*\(|nirmmita\s*\(|smaran|\.\w+\s*=[^=]|kosh_push')
EFFECT = set()
for p_ in sorted(G.LIB.glob('*.smlib')):
    text = p_.read_text(encoding='utf-8').split('\n')
    for f in G.parse_module(p_):
        body = '\n'.join(text[f['start']:f['end'] + 1])
        if MEM.search(body) or f['module'] == 'patra':
            EFFECT.add((f['module'], f['name']))
for r in rows:
    c = WC[(r['module'], r['name'])]
    r['W'], r['NW'], r['NT'] = c['W'], c['NW'], c['NT']
    if (r['module'], r['name']) in EFFECT and r['NW']:
        r['NT'] += r['NW']
        r['NW'] = 0
    assert r['W'] + r['NW'] + r['NT'] == r['total'] - r['killed'], r['name']
KIND = {'R': 'R', 'C': 'C', 'N': 'N', 'A': 'A', 'L': 'L', 'K': 'K', 'D': 'D'}


def kind(tag):
    return tag[0]


def ratio(r):
    d = r['total'] - r['NW']
    return r['killed'] / d if d else 1.0


def verdict(r):
    if not r['S_killed']:
        return 'NO PROOF'
    if r['total'] == 0:
        return 'S only (no other mutant compiles)'
    q = ratio(r)
    if r['killed'] == 0:
        return 'DECORATION'
    if q < 0.5:
        return 'WEAK'
    if q < 0.8:
        return 'PARTIAL'
    if q < 1:
        return 'STRONG'
    return 'COMPLETE'


tot_m = sum(r['total'] for r in rows)
tot_k = sum(r['killed'] for r in rows)
by_kind_t, by_kind_k = Counter(), Counter()
for r in rows:
    for tag, res, _ in r['mutants']:
        if res == 'stillborn':
            continue
        by_kind_t[kind(tag)] += 1
        by_kind_k[kind(tag)] += res == 'killed'
vc = Counter(verdict(r) for r in rows)
out = []
out.append('# R15-03 evidence: mutant score of every library function')
out.append('')
out.append('%d functions · %d mutants besides S · %d killed (%.1f%%) · S killed in %d of %d' % (
    len(rows), tot_m, tot_k, 100.0 * tot_k / tot_m, sum(r['S_killed'] for r in rows), len(rows)))
out.append('')
out.append('| mutant kind | killed / mutants |')
out.append('|---|---|')
NAMES = {'S': 'S whole body', 'R': 'R result + 1', 'C': 'C comparison flipped', 'N': 'N yadi negated',
         'A': 'A arithmetic operator', 'L': 'L && / ||', 'K': 'K literal + 1', 'D': 'D statement deleted'}
for k in 'SRCNALKD':
    if by_kind_t[k]:
        out.append('| %s | %d / %d (%.0f%%) |' % (NAMES[k], by_kind_k[k], by_kind_t[k], 100.0 * by_kind_k[k] / by_kind_t[k]))
out.append('')
nw = sum(r['NW'] for r in rows); w = sum(r['W'] for r in rows); nt = sum(r['NT'] for r in rows)
out.append('Survivors: %d · WITNESS %d · NO-WITNESS (likely equivalent) %d · NOT-TRIED (lists, strings, records, or an effect in memory or a file) %d' % (w + nw + nt, w, nw, nt))
out.append('')
out.append('| verdict (by the score, NO-WITNESS survivors left out) | functions |')
out.append('|---|---|')
for v in ('DECORATION', 'WEAK', 'PARTIAL', 'STRONG', 'COMPLETE', 'S only (no other mutant compiles)', 'NO PROOF'):
    out.append('| %s | %d |' % (v, vc.get(v, 0)))
out.append('')
out.append('Verdicts: DECORATION = the proofs kill S (the whole body broken) and no other mutant; '
           'WEAK = under 50% of the other mutants killed; PARTIAL = 50-79%; STRONG = 80-99%; '
           'COMPLETE = 100%: every mutant killed, or the survivors have no witness. A surviving mutant may be equivalent (no input can tell it apart); '
           'see R15-03 for what that means for the ranking.')
out.append('')
out.append('## Ranked, weakest first')
out.append('')
out.append('| rank | function | killed / mutants | score | verdict | survivors W / NW / NT | surviving mutants (first 6) | proofs that name it |')
out.append('|---|---|---|---|---|---|---|---|')
ranked = sorted(rows, key=lambda r: (ratio(r), -(r['total'] - r['killed']), r['module'], r['name']))
for i, r in enumerate(ranked, 1):
    out.append('| %d | `%s.%s` | %d / %d | %.0f%% | %s | %d / %d / %d | %s | %d |' % (
        i, r['module'], r['name'], r['killed'], r['total'], 100 * ratio(r), verdict(r), r['W'], r['NW'], r['NT'],
        ' '.join(r['survivors'][:6]) + (' …' if len(r['survivors']) > 6 else ''), r['named_count']))
out.append('')
out.append('## Every WITNESS: an input on which the mutant differs and no proof uses it')
out.append('')
out.append('| function | mutant | input | real | mutant gives |')
out.append('|---|---|---|---|---|')
for key in sorted(WLIST):
    for x in WLIST[key]:
        out.append('| `%s.%s` | %s | %s | %s | %s |' % (key[0], key[1], x['mutant'], x['input'], x['real'], x['mutant_gives']))
out.append('')
out.append('## By module')
out.append('')
mods = defaultdict(list)
for r in rows:
    mods[r['module']].append(r)
out.append('| module | functions | killed / mutants | DECORATION | WEAK | PARTIAL | STRONG | ALL KILLED |')
out.append('|---|---|---|---|---|---|---|---|')
for m in sorted(mods):
    rs = mods[m]
    c = Counter(verdict(r) for r in rs)
    out.append('| %s | %d | %d / %d | %d | %d | %d | %d | %d |' % (
        m, len(rs), sum(r['killed'] for r in rs), sum(r['total'] for r in rs),
        c['DECORATION'], c['WEAK'], c['PARTIAL'], c['STRONG'], c['COMPLETE']))
open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out[:14]))
