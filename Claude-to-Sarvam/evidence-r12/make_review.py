#!/usr/bin/env python3
"""ROUND-12 (WS1): write one native-speaker review sheet per language pack.

    python3 make_review.py <repo> <out-dir>

Reads lang/<pack>.sandesh through tools/sandesh.py, so a sheet always shows what the
compiler prints. Run it again after corrections to regenerate the sheets.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
import sandesh  # noqa: E402


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = load('gloss').G
F = load('flags')

NAMES = {'sanskrit': 'Sanskrit (संस्कृतम्)', 'hindi': 'Hindi (हिन्दी)', 'marathi': 'Marathi (मराठी)',
         'gujarati': 'Gujarati (ગુજરાતી)', 'bengali': 'Bengali (বাংলা)', 'punjabi': 'Punjabi (ਪੰਜਾਬੀ)',
         'odia': 'Odia (ଓଡ଼ିଆ)', 'tamil': 'Tamil (தமிழ்)', 'telugu': 'Telugu (తెలుగు)',
         'kannada': 'Kannada (ಕನ್ನಡ)', 'malayalam': 'Malayalam (മലയാളം)'}
SUFFIXES = {'marathi': ['ला', 'मधून', 'ची', 'चे', 'साठी'], 'gujarati': ['ને', 'માંથી', 'ની', 'માટે'],
            'bengali': ['কে', 'থেকে', 'এর'], 'odia': ['କୁ', 'ରୁ', 'ର ', 'ପାଇଁ', 'ରେ'],
            'tamil': ['க்கு', 'இலிருந்து', 'இல்'], 'telugu': ['కు', 'కి', 'నుండి', 'లో'],
            'kannada': ['ಗೆ', 'ದಿಂದ', 'ನಲ್ಲಿ', 'ಕ್ಕಿಂತ'], 'malayalam': ['ന്', 'ൽ']}
LANGNAME = {p: NAMES[p].split(' ')[0] for p in NAMES}


def show(t):
    return t.replace('\r\n', '⏎').replace('\n', '⏎')


def assemble(template, own, pack_tr):
    def part(m):
        k = m.group(1)
        return own if k == '.' else pack_tr.get(k, '?')
    return re.sub(r'«([^»]+)»', part, template)


def flags_for(pack, key, text):
    notes = []
    if key in F.PACK.get(pack, {}):
        notes.append(F.PACK[pack][key])
    if key in F.COMMON:
        notes.append(F.COMMON[key])
    for s in SUFFIXES.get(pack, []):
        if text.startswith("' " + s):
            notes.append(F.SUFFIX_NOTE.format(lang=LANGNAME[pack]))
            break
    return notes


def sheet(pack, defs):
    raw = sandesh.read_pack(pack)
    tr = {k: sandesh.expand(pack, v) for k, v in raw.items()}
    keys = list(sandesh.KEYS) + ['ide.' + k for k in sandesh.IDE_KEYS]
    rows, unsure = [], []
    for n, k in enumerate(keys, 1):
        notes = flags_for(pack, k, tr[k])
        level = 'LIKELY WRONG' if any(x.startswith(('LIKELY WRONG', 'LIKELY TO CHANGE')) for x in notes) \
            else ('UNSURE' if notes else 'DRAFT')
        if level != 'DRAFT':
            unsure.append((n, k, level))
        where, gloss, tpl = G[k]
        printed = assemble(tpl, tr[k], tr)
        default_printed = assemble(tpl, defs[k], defs)
        multiline = '\n' in tr[k].rstrip('\n')
        block = [f'### {n}. `{k}` — **{level}**', '',
                 f'- **Where:** {where}',
                 f'- **Meaning:** {gloss}']
        if multiline:
            block += ['- **Default (romanised Sanskrit):**', '', '```', defs[k].rstrip('\n'), '```', '',
                      '- **This pack, as printed:**', '', '```', tr[k].rstrip('\n'), '```']
        else:
            block += [f'- **Default (romanised Sanskrit), as printed:** `{show(default_printed)}`',
                      f'- **This pack, as printed:** `{show(printed)}`']
            if printed != tr[k]:
                block += [f'- **This message alone:** `{show(tr[k])}`']
        if raw[k] != tr[k]:
            block += [f'- **In the pack file:** `{show(raw[k])}`  (`{{kw:…}}` is the pack\'s own keyword)']
        for x in notes:
            block += [f'- **Doubt:** {x}']
        block += ['- **Correction:** ', '']
        rows.append('\n'.join(block))
    head = [f'# Review sheet: {NAMES[pack]}', '',
            '**The wording here is UNVERIFIED.** Claude wrote every message in ROUND-11. The automatic checks',
            'prove only the form: the identifiers, the punctuation, the script, no Latin prose. No native',
            'speaker has read these messages.', '',
            '## How to review', '',
            '- Read each **"This pack, as printed"** line: it is exactly what the compiler or the IDE shows,',
            '  with sample names and numbers (`prog.sm`, `y`, `f`, `1`, `2`, `hindi`) filled in.',
            '- **Meaning** is a gloss in English for the reviewer. It is never shown to a user.',
            '- Write a better wording under **Correction**. Leave it empty if the message is right.',
            '- **Keep as they are:** `Sutram Error`, the `[E_…]` tags, the quotes `\'…\'` around a name, the',
            '  leading `: ` and the line breaks (⏎), and code (`lib/`, `.smlib`, `--lang`, keywords).',
            '- **The parts are joined by the compiler in a fixed order.** Some messages are pieces of one',
            '  sentence (marked "middle of …"). Judge the whole printed line, and say if the order itself',
            '  cannot work in this language.',
            '- **Return the corrections** as this file, edited, or as a list of `number: correction`.',
            '  They go into `lang/' + pack + '.sandesh`.', '',
            '## Levels', '',
            '| Level | Meaning |', '|---|---|',
            '| **LIKELY WRONG** | I think it is wrong, or it must be decided; please correct it first |',
            '| **UNSURE** | I have a specific doubt, written under the message |',
            '| **DRAFT** | no specific doubt, but still unverified |', '']
    counts = {lv: sum(1 for _, _, l in unsure if l == lv) for lv in ('LIKELY WRONG', 'UNSURE')}
    head += [f'**{len(keys)} messages:** {counts["LIKELY WRONG"]} LIKELY WRONG, {counts["UNSURE"]} UNSURE, '
             f'{len(keys) - len(unsure)} DRAFT.', '']
    if unsure:
        head += ['| # | Message | Level |', '|---|---|---|']
        head += [f'| {n} | `{k}` | {lv} |' for n, k, lv in unsure]
        head += ['']
    head += ['---', '']
    return '\n'.join(head) + '\n'.join(rows) + '\n', counts, len(keys)


def main():
    sandesh.ROMAN_KW.update(sandesh.roman_keywords())
    defs = sandesh.defaults()
    defs.update(sandesh.ide_defaults())
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    for p in sandesh.PACK_ORDER:
        text, counts, n = sheet(p, defs)
        (OUT / f'{p}.md').write_text(text, encoding='utf-8')
        summary[p] = {'messages': n, **counts, 'DRAFT': n - sum(counts.values())}
    print(json.dumps(summary, indent=1))
    return summary


if __name__ == '__main__':
    main()
