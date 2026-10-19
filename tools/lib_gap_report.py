#!/usr/bin/env python3
"""Turn the two proof-gap runs into one gap list, module by module.

Inputs:
  build/lib-proof-gaps.json     tools/lib_proof_gaps.py --deep
  build/lib-mutant-witness.json tools/lib_mutant_witness.py

Every surviving mutant gets exactly one verdict:

  GAP          an input tells the mutant apart from the real function, and no proof uses it
               (found by lib_mutant_witness.py; the input is shown)
  EQUIVALENT   no input can tell them apart, by a rule that is checked on the source line:
                 clamp       `yadi (x > K) { x = K }`  (> and >= set the same value)
                 abs-zero    `yadi (x < 0) { x = 0 - x }` or `{ prati 0 - x }` (at 0 both give 0)
                 min/max     `yadi (a[i] < best) { best = a[i] }` (a tie keeps an equal value)
  LIKELY-EQ    a number-only function, and no input in the set tells them apart (count shown);
               evidence, not proof
  OVERRUN      `yavat (i < n)` became `<=`: one extra pass that reads or writes one cell past the
               end. Invisible in the output unless that cell matters; a guard-cell proof finds it.
  REVIEW       a function that takes a list, string or record, not decided by the rules above

A hand verdict in tools/lib_gap_reviewed.json, with its argument, overrides the rules. It may also be
  OUT-OF-CONTRACT  only inputs the function does not promise anything for tell them apart
  FINDING          the witness exposes a defect in the real function (named in the R8 notes)

A function is OPEN while it has a GAP, OVERRUN, REVIEW or FINDING survivor.

    python3 tools/lib_gap_report.py --gaps build/lib-proof-gaps.json \\
        --witness build/lib-mutant-witness.json --md build/lib-gap-list.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLAMP = re.compile(r'yadi \((\w+) (?:>|>=|<|<=) ([^()]+?)\) \{ \1 = \2 \}')
ABS0 = re.compile(r'yadi \((\w+) (?:<|<=) 0\) \{ (?:\1 = 0 - \1|prati 0 - \1) \}')
MINMAX = re.compile(r'yadi \((\w+(?:\[[^\]]+\])?) (?:<|<=|>|>=) (\w+)\) \{ \2 = \1 \}')
LOOP = re.compile(r'yavat \(\s*[\w\s+\-*]+ (?:<|<=) ')


def line_of(module: str, mutant: str) -> str:
    m = re.search(r'@L(\d+)', mutant)
    if not m:
        return ''
    return (ROOT / 'lib' / (module + '.smlib')).read_text(encoding='utf-8').split('\n')[int(m.group(1)) - 1].strip()


REVIEWED = json.loads((ROOT / 'tools/lib_gap_reviewed.json').read_text(encoding='utf-8'))


def verdict(module: str, mutant: str, wit: dict | None, name: str = '') -> tuple[str, str]:
    src = line_of(module, mutant)
    hand = REVIEWED.get(f"{module}.{name} {mutant.split('@')[0]}")
    if hand:
        return hand[0], 'reviewed: ' + hand[1]
    if wit and wit['result'] == 'WITNESS':
        return 'GAP', f"input {tuple(wit['input'])}: real {wit['real']}, mutant {wit['mutant_gives']}"
    if mutant.startswith('C') and src:
        if CLAMP.search(src):
            return 'EQUIVALENT', 'clamp'
        if ABS0.search(src):
            return 'EQUIVALENT', 'abs-zero'
        if MINMAX.search(src):
            return 'EQUIVALENT', 'min/max tie'
    if wit and wit['result'] == 'NO-WITNESS':
        return 'LIKELY-EQ', f"{wit['inputs_tried']} inputs"
    if mutant.startswith('C') and src and LOOP.search(src) and ('<-><=' in mutant):
        return 'OVERRUN', 'one pass past the end'
    return 'REVIEW', (wit or {}).get('why', '')


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--gaps', default=str(ROOT / 'build/lib-proof-gaps.json'))
    ap.add_argument('--witness', default=str(ROOT / 'build/lib-mutant-witness.json'))
    ap.add_argument('--usage', help='optional JSON {module.name: {lib, examples, tests, docs}} to sort by use')
    ap.add_argument('--md', default=str(ROOT / 'build/lib-gap-list.md'))
    ap.add_argument('--json', default=str(ROOT / 'build/lib-gap-list.json'))
    a = ap.parse_args(argv)
    rows = json.load(open(a.gaps, encoding='utf-8'))
    wits = {(w['module'], w['name'], w['mutant']): w for w in json.load(open(a.witness, encoding='utf-8'))}
    usage = json.load(open(a.usage, encoding='utf-8')) if a.usage else {}
    use = lambda r: sum(usage.get(f"{r['module']}.{r['name']}", {}).values())
    out = []
    for r in rows:
        vs = [(m, *verdict(r['module'], m, wits.get((r['module'], r['name'], m)), r['name'])) for m in r['survivors']]
        out.append({**r, 'verdicts': vs, 'use': use(r)})
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')

    tot = Counter(v for r in out for _, v, _ in r['verdicts'])
    killed = sum(r['mutants_killed'] for r in out)
    total = sum(r['mutants_total'] for r in out)
    md = ['# The library gap list', '',
          f"{len(out)} functions in {len({r['module'] for r in out})} modules. "
          f"Whole-body mutant (S) detected for {sum(bool(r['detected_by']) for r in out)}. "
          f"Off-by-one and boundary mutants killed: **{killed}/{total}**. "
          f"Surviving: {', '.join(f'{k} {v}' for k, v in sorted(tot.items()))}.", '',
          '## By module', '',
          '| module | functions | S detected | boundary mutants killed | functions with a GAP | OVERRUN | REVIEW | equivalent / likely |',
          '|---|---|---|---|---|---|---|---|']
    by = defaultdict(list)
    for r in out:
        by[r['module']].append(r)
    for mod in sorted(by):
        rs = by[mod]
        c = Counter(v for r in rs for _, v, _ in r['verdicts'])
        md.append(f"| {mod} | {len(rs)} | {sum(bool(r['detected_by']) for r in rs)} | "
                  f"{sum(r['mutants_killed'] for r in rs)}/{sum(r['mutants_total'] for r in rs)} | "
                  f"{sum(any(v == 'GAP' for _, v, _ in r['verdicts']) for r in rs)} | {c['OVERRUN']} | {c['REVIEW']} | "
                  f"{c['EQUIVALENT']} / {c['LIKELY-EQ']} |")
    OPEN = {'GAP', 'OVERRUN', 'REVIEW', 'FINDING'}
    is_open = lambda r: any(v in OPEN for _, v, _ in r['verdicts'])
    md.insert(4, f"**Closed** (every boundary mutant killed, or only equivalent / likely-equivalent / out-of-contract "
                 f"survivors): **{sum(not is_open(r) for r in out)}** functions. **Open: {sum(is_open(r) for r in out)}.**")
    md.insert(5, '')
    md += ['', '## Open functions, module by module (most-used first)', '']
    for mod in sorted(by):
        op = sorted((r for r in by[mod] if is_open(r)), key=lambda r: -r['use'])
        if op:
            md.append(f"- **{mod}** ({len(op)}/{len(by[mod])}): " + ', '.join(
                f"`{r['name']}` ({'/'.join(sorted({v for _, v, _ in r['verdicts'] if v in OPEN}))})" for r in op))
    md += ['', '## Functions without a direct proof (S mutant not detected directly)', '',
           '| module | function | status | contract (source comment) |', '|---|---|---|---|']
    for r in sorted(out, key=lambda r: (r['module'], r['name'])):
        if r['status'] != 'PROVEN':
            md.append(f"| {r['module']} | `{r['name']}({r['params']})` | {r['status']} | {r['doc'][:120]} |")
    md += ['', '## Every surviving mutant, most-used function first', '',
           '| module | function | uses | mutant | source line | verdict | why |', '|---|---|---|---|---|---|---|']
    for r in sorted(out, key=lambda r: (-r['use'], r['module'], r['name'])):
        for m, v, why in r['verdicts']:
            md.append(f"| {r['module']} | `{r['name']}` | {r['use']} | `{m.split('@')[0]}` | "
                      f"`{line_of(r['module'], m)[:70].replace('|', '¦')}` | {v} | {why} |")
    Path(a.md).write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(dict(tot), f'killed {killed}/{total}')
    print('wrote', a.md, 'and', a.json)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
