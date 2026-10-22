#!/usr/bin/env python3
"""R103 review gate: unreviewed nirmmita expressions, NOT numerical safety."""
import argparse
from pathlib import Path
import re
import sys

REVIEWED = {
 'aadhar.smlib': {'c * 8', 'c * 4 * 8'},
 'brihat.smlib': {'c * 8', 'c * 2 * 8'},
 'mala.smlib': {'sz'},
 'nighantu.smlib': {'sz', 'oldcap * 33 + 1', 'scap * 33 + 1'},
 'roop.smlib': {'22 * 8', '70 * 8', '32'},
 'sangrah.smlib': {'cap * 33 + 1', 'bcap * 33 + 1', 'cap * 32 + 1', 'cap * 8'},
 'shreni.smlib': {'n * 8'},
 'suchi.smlib': {'3 * 8', '4 * 8', 'sz', 'ncap * 8'},
 'vakyank.smlib': {'22 * 8', '70 * 8'},
}
ALLOC = re.compile(r'\bnirmmita\s*\(')
FUNC = re.compile(r'^\s*prakriya\s+([A-Za-z_][\w]*)\s*\(')

def scan(path):
    errors, calls, function = [], [], '(top level)'
    for no, line in enumerate(path.read_text(encoding='utf8').splitlines(), 1):
        source = line.split('#', 1)[0]
        f = FUNC.search(source)
        if f:
            function = f.group(1)
        for m in ALLOC.finditer(source):
            start = m.end()
            depth = 1
            end = start
            while end < len(source) and depth:
                if source[end] == '(':
                    depth += 1
                elif source[end] == ')':
                    depth -= 1
                end += 1
            if depth:
                errors.append(f'{path.name}:{no}: UNPARSED nirmmita call')
                continue
            expr = ' '.join(source[start:end-1].split())
            calls.append((function, no, expr))
            if expr not in REVIEWED.get(path.name, set()):
                errors.append(f'{path.name}:{no}: UNREVIEWED allocation expression {expr!r}')
    return calls, errors

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('lib', type=Path)
    args = parser.parse_args(argv)
    if not args.lib.is_dir():
        parser.error('library directory required')
    files = sorted(args.lib.glob('*.smlib'))
    all_calls, errors = [], []
    for file in files:
        calls, problems = scan(file)
        all_calls.extend((file.name, *x) for x in calls)
        errors.extend(problems)
    for file, func, no, expr in all_calls:
        print(f'ALLOC {file}:{no} {func}: {expr}')
    for err in errors:
        print('FAIL', err)
    print(f'R103 ALLOC SCAN files={len(files)} calls={len(all_calls)} findings={len(errors)}')
    print('BOUNDARY: reviewed allocation spellings only; NOT a numeric range, index, or pointer safety proof')
    return int(bool(errors))

if __name__ == '__main__':
    sys.exit(main())
