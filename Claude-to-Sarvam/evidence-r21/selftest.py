#!/usr/bin/env python3
"""Does pack_structure_check.py have teeth? Corrupt one row at a time in a copy of
lang/ (eight kinds of corruption, 40 random rows each, seed 21) and count how many
corruptions the checker reports as HARD. A checker that reports 0 hard violations
on the real packs is only worth something if it reports them when they are there."""
import json, random, re, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
CHECK = Path(__file__).resolve().parent / 'pack_structure_check.py'
PACKS = ['bengali', 'gujarati', 'hindi', 'kannada', 'malayalam', 'marathi', 'odia', 'punjabi', 'tamil', 'telugu']
rng = random.Random(21)

def rows(pack):
    out = []
    for n, line in enumerate((ROOT / 'lang' / (pack + '.sandesh')).read_text(encoding='utf-8').split('\n')):
        if line and not line.startswith('#') and '\t' in line:
            out.append((n, line))
    return out

KINDS = {
    'english word':        lambda t: t[:-1] + ' please"' if t.endswith('"') else t + ' please',
    'tag dropped':         lambda t: re.sub(r'\[E_[A-Z0-9_]+\]', '', t, count=1),
    'Sutram Error dropped': lambda t: t.replace('Sutram Error', 'Sutram', 1),
    'placeholder dropped': lambda t: re.sub(r'\{kw:[^}]*\}', '', t, count=1),
    'trailing newline dropped': lambda t: t.replace('\\n"', '"') if t.endswith('\\n"') else t,
    'foreign script letter': lambda t: t[:-1] + 'ก"',
    'row emptied':          lambda t: '""',
    'romanised default':    None,   # replaced by the default comment's text
}
caught = {k: 0 for k in KINDS}; tried = {k: 0 for k in KINDS}
with tempfile.TemporaryDirectory() as td:
    for kind, f in KINDS.items():
        for _ in range(40):
            pack = rng.choice(PACKS)
            lines = (ROOT / 'lang' / (pack + '.sandesh')).read_text(encoding='utf-8').split('\n')
            n, line = rng.choice(rows(pack))
            key, text = line.split('\t', 1)
            if kind == 'romanised default':
                new = lines[n - 1][2:] if lines[n - 1].startswith('# "') else None
            else:
                new = f(text)
            if new is None or new == text:
                continue
            tried[kind] += 1
            shutil.rmtree(Path(td, 'lang'), ignore_errors=True)
            shutil.copytree(ROOT / 'lang', Path(td, 'lang'))
            lines[n] = key + '\t' + new
            (Path(td, 'lang') / (pack + '.sandesh')).write_text('\n'.join(lines), encoding='utf-8')
            r = subprocess.run([sys.executable, '-B', str(CHECK), '--root', td], capture_output=True, text=True)
            if 'HARD' in r.stdout and key in r.stdout:
                caught[kind] += 1
for k in KINDS:
    print('%-26s caught %2d of %2d' % (k, caught[k], tried[k]))
