#!/usr/bin/env python3
"""Read-only R74 old-keyword audit of the *tracked* current Sutram checkout.

Reports candidates, not automatic rename instructions. Historical round records,
compatibility diagnostic tables, and ordinary English prose require classification.
"""
import argparse
import html
import json
from pathlib import Path
import re
import subprocess

OLD = {
    'sort': 'shreni', 'list': 'suchi', 'map': 'nighantu', 'set': 'sangrah',
    'array': 'mala', 'string': 'varna', 'file': 'patra', 'hash': 'gudh',
    'result': 'phal', 'fmt': 'roop', 'pankti': 'mala',
    'punaravartana': 'chakra', 'pratiyati': 'prati', 'ayojan': 'yoj',
    'nishkriya': 'yantra', 'nishedha': 'abhava', 'srijana': 'ganana',
    'char_at': 'akshar', 'char_code': 'aksharank', 'set_char': 'akshar_rakh'
}
TOKENS = re.compile(r'(?<![\w])(?:' + '|'.join(map(re.escape, OLD)) + r')(?![\w])')
SUFFIXES = {'.sm', '.smlib', '.asm', '.inc', '.py', '.c', '.h', '.js', '.ps1',
            '.sh', '.html', '.md', '.lang', '.txt'}
ARCHIVE_PREFIXES = ('ChatGPT-to-Sarvam/', 'Sarvam-to-ChatGPT/', 'Claude-to-Sarvam/',
                    'Muse-to-Sarvam/', 'Sarvam-to-Muse/', 'Sarvam-to-Claude/',
                    'ChatGPT-to-Sarvam-Clean/', 'Sarvam-to-ChatGPT-Clean-Project/')


def mask_sm(line):
    """Replace strings/comments with blanks while preserving identifier columns."""
    result = list(line)
    quote, escape, block = None, False, False
    i = 0
    while i < len(line):
        c = line[i]
        two = line[i:i+2]
        if block:
            result[i] = ' '
            if two == '*/':
                result[i:i+2] = '  '
                block = False
                i += 2
                continue
        elif quote:
            result[i] = ' '
            if escape:
                escape = False
            elif c == '\\':
                escape = True
            elif c == quote:
                quote = None
        elif two == '/*':
            block = True
            result[i:i+2] = '  '
            i += 2
            continue
        elif two == '//' or c == '#':
            result[i:] = ' ' * (len(line)-i)
            break
        elif c in ('"', "'"):
            quote = c
            result[i] = ' '
        i += 1
    return ''.join(result)


def scan(path, text):
    """Return line-addressable candidates. to is intentionally not in OLD."""
    kind = Path(path).suffix.lower()
    out = []
    if kind in {'.sm', '.smlib'}:
        for num, line in enumerate(text.splitlines(), 1):
            for m in TOKENS.finditer(mask_sm(line)):
                out.append({'path': path, 'line': num, 'column': m.start()+1,
                            'old': m.group(), 'new': OLD[m.group()],
                            'kind': 'active_sutram', 'context': line.strip()[:130]})
            # Old to is only suspicious in an active range clause.
            old_range = re.search(r'\bchakra\b[^#]*?\bto\b', mask_sm(line))
            if old_range:
                out.append({'path': path, 'line': num,
                            'column': old_range.end()-1, 'old': 'to', 'new': 'tak',
                            'kind': 'active_range', 'context': line.strip()[:130]})
    elif kind in {'.md', '.html'}:
        # Prose is intentionally not scanned: code fences and HTML <pre>/<code> only.
        regions = (r'\x60\x60\x60(?:sutram|sm)\s*\n[\s\S]*?\x60\x60\x60'
                   if kind == '.md' else r'<(?:pre|code)\b[^>]*>[\s\S]*?</(?:pre|code)>')
        for block in re.finditer(regions, text, flags=re.I):
            sub = html.unescape(block.group())
            # A literal backslash-n is two characters; without masking it,
            # the preceding 'n' defeats an ordinary identifier boundary.
            searchable = re.sub(r'\\[nr]', '  ', sub)
            for m in TOKENS.finditer(searchable):
                abspos = block.start() + m.start()
                out.append({'path': path, 'line': text.count('\n', 0, abspos)+1,
                            'column': 0, 'old': m.group(), 'new': OLD[m.group()],
                            'kind': 'documentation_code_review', 'context': sub[max(0,m.start()-30):m.end()+45].replace('\n',' ')[:130]})
    else:
        # A code literal used for dispatch can be stale, but ordinary variables,
        # Windows API names and diagnostic migration strings can also match.
        pattern = re.compile(r'''["'](''' + '|'.join(map(re.escape, OLD)) + r''')["']''')
        for num, line in enumerate(text.splitlines(), 1):
            for m in pattern.finditer(line):
                out.append({'path': path, 'line': num, 'column': m.start()+1,
                            'old': m.group(1), 'new': OLD[m.group(1)],
                            'kind': 'quoted_literal_review', 'context': line.strip()[:130]})
    return out


def audit(root):
    raw = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z'], timeout=30)
    paths = [Path(p.decode('utf8')) for p in raw.split(b'\0') if p]
    results, errors = [], []
    counters = {'tracked': len(paths), 'scanned': 0, 'archived_excluded': 0,
                'non_source_excluded': 0}
    for name in paths:
        rel = name.as_posix()
        if rel.startswith(ARCHIVE_PREFIXES):
            counters['archived_excluded'] += 1
            continue
        if name.suffix.lower() not in SUFFIXES:
            counters['non_source_excluded'] += 1
            continue
        p = root / name
        if p.is_symlink() or not p.is_file():
            errors.append(rel + ': missing or symlink')
            continue
        try:
            source = p.read_text('utf8')
        except UnicodeError:
            errors.append(rel + ': invalid UTF-8')
            continue
        counters['scanned'] += 1
        results.extend(scan(rel, source))
    return {'summary': counters, 'findings': sorted(results, key=lambda x:(x['path'],x['line'],x['column'])),
            'errors': errors, 'status': 'PASS' if not errors else 'FAIL',
            'note': 'Findings are review candidates, not automatically confirmed bugs.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    report = audit(a.repo.resolve())
    data = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if a.output:
        with a.output.open('x', encoding='utf8') as f:
            f.write(data)
    print(json.dumps({'summary': report['summary'], 'findings': len(report['findings']),
                      'errors': report['errors'], 'status': report['status']}))
    return 0 if report['status'] == 'PASS' else 2

if __name__ == '__main__':
    raise SystemExit(main())
