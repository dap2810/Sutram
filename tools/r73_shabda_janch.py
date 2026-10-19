#!/usr/bin/env python3
"""Read-only Sanskrit vocabulary audit across every tracked checkout file.

This is a candidate-finding tool, not a renamer or language compatibility oracle.
It separates active source tables, language mappings, code references and historical
prose, and always includes exact path:line evidence. Requires git; no networking.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess

RENAMED = {
    'pankti': 'mala', 'punaravartana': 'chakra', 'pratiyati': 'prati',
    'ayojan': 'yoj', 'nishkriya': 'yantra', 'srijana': 'ganana',
    'nishedha': 'abhava', 'anyatra': 'anya', 'uddeshya': 'agrim',
    'parigrah': 'satya', 'to': 'tak', 'char_at': 'akshar',
    'char_code': 'aksharank', 'set_char': 'akshar_rakh',
    'sort': 'shreni', 'list': 'suchi', 'map': 'nighantu',
    'set': 'sangrah', 'array': 'mala', 'string': 'varna',
    'file': 'patra', 'hash': 'gudh', 'result': 'phal',
    'fmt': 'roop', 'num': 'ank', 'math': 'ganit',
}
TOKENS = re.compile(r'(?<![\w])(?:' + '|'.join(sorted(map(re.escape, RENAMED), key=len, reverse=True)) + r')(?![\w])')
ACTIVE_SUFFIXES = {'.sm', '.smlib', '.lang', '.asm', '.inc'}
TEXT_SUFFIXES = ACTIVE_SUFFIXES | {'.py', '.sh', '.ps1', '.cmd', '.md', '.html', '.htm', '.txt', '.json', '.yml', '.yaml'}

def listed(root: Path) -> list[str]:
    p = subprocess.run(['git', '-C', str(root), 'ls-files', '-z'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=40)
    return sorted(p.stdout.decode('utf-8', 'strict').strip('\0').split('\0'))

def scrub(line: str) -> str:
    """Ignore string and # or // comments for .sm and .smlib candidates."""
    quote = None
    out = []
    i = 0
    while i < len(line):
        c = line[i]
        if quote:
            if c == '\\' and i + 1 < len(line):
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in ('"', "'"):
            quote = c
        elif c == '#' or line[i:i+2] == '//':
            break
        else:
            out.append(c)
        i += 1
    return ''.join(out)

def inspect(root: Path) -> dict:
    matches, skipped = [], []
    scanned = 0
    for name in listed(root):
        relative = Path(name)
        if relative.suffix.lower() not in TEXT_SUFFIXES:
            continue
        path = root / relative
        if not path.is_file() or path.is_symlink():
            skipped.append({'path': name, 'reason': 'not regular file / symlink'})
            continue
        try:
            text = path.read_text('utf-8')
        except (UnicodeError, OSError):
            skipped.append({'path': name, 'reason': 'unreadable UTF-8'})
            continue
        scanned += 1
        for number, line in enumerate(text.splitlines(), 1):
            test_line = line
            if relative.suffix.lower() in {'.sm', '.smlib'}:
                test_line = scrub(line)
            elif relative.suffix.lower() == '.lang':
                raw = line.split('#', 1)[0].split()
                test_line = raw[1] if len(raw) == 2 else ''
            elif relative.suffix.lower() in {'.asm', '.inc'}:
                if re.search(r'^\s*r4_o_\w+\s+db\b', line):
                    continue   # explicit legacy-keyword diagnostic mapping
                code = line.split(';', 1)[0]
                if re.search(r'^\s*(?:kw_words|bi_words|kw_\w+|bn_\w+)\s+db\b', code):
                    test_line = code
                else:
                    test_line = code  # still report review candidates
            hits = sorted({m.group() for m in TOKENS.finditer(test_line)})
            if not hits:
                continue
            if relative.suffix.lower() == '.lang':
                category = 'ACTIVE_PACK_RHS'
            elif relative.suffix.lower() in {'.sm', '.smlib'}:
                category = 'SOURCE_TOKEN_REVIEW'
            elif relative.suffix.lower() in {'.asm', '.inc'} and re.match(r'^\s*(?:kw_words|bi_words|kw_\w+|bn_\w+)\s+db\b', line):
                category = 'ACTIVE_KEYWORD_TABLE'
            elif relative.suffix.lower() in {'.asm', '.inc'}:
                category = 'ASM_REFERENCE_REVIEW'
            else:
                category = 'DOCUMENT_OR_TOOL_REFERENCE'
            matches.append({'path': name, 'line': number,
                            'category': category, 'old': hits,
                            'new': [RENAMED[k] for k in hits],
                            'excerpt': line.strip()[:280]})
    counts = {}
    for entry in matches:
        counts[entry['category']] = counts.get(entry['category'], 0) + 1
    return {'source': 'git ls-files at checked-out HEAD', 'scanned_text_files': scanned,
            'candidate_count': len(matches), 'categories': counts,
            'skipped': skipped, 'candidates': matches}

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--out', type=Path)
    p.add_argument('--fail-on-active', action='store_true')
    args = p.parse_args()
    result = inspect(args.root.resolve())
    output = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        with args.out.open('x', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output, end='')
    active = {'ACTIVE_PACK_RHS', 'ACTIVE_KEYWORD_TABLE'}
    return 1 if args.fail_on_active and any(x['category'] in active for x in result['candidates']) else 0
if __name__ == '__main__':
    raise SystemExit(main())
