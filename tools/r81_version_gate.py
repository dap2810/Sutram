#!/usr/bin/env python3
"""Read-only Sutram packaging release-version gate.

Require the version encoded in the canonical compiler source to equal the
first current entry in docs/CHANGELOG.md. This prevents silently shipping an
old --version banner under a new project release. Not native acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

RELEASE_RE = re.compile(r'^## v([0-9]+)\b', re.MULTILINE)
BANNER_RE = re.compile(
    r'^\s*msg_version\s+db\s+"Sutram 1\.0 \(v([0-9]+)\)[^"\n]*"',
    re.MULTILINE,
)


def check(changelog: str, source: str) -> dict:
    """Fail closed on missing/ambiguous versions, no interpretation of comments."""
    heads = RELEASE_RE.findall(changelog)
    banners = BANNER_RE.findall(source)
    if not heads:
        return {'status': 'FAIL', 'reason': 'missing current CHANGELOG version heading'}
    if len(banners) != 1:
        return {'status': 'FAIL', 'reason': 'expected exactly one msg_version compiler banner',
                'banner_matches': len(banners), 'project_version': heads[0]}
    result = {'project_version': 'v' + heads[0],
              'compiler_banner_version': 'v' + banners[0],
              'status': 'PASS' if heads[0] == banners[0] else 'FAIL'}
    if result['status'] == 'FAIL':
        result['reason'] = ('STALE COMPILER VERSION: do not package an installer until '
                            'the accepted NASM source is rebuilt, reviewed and re-pinned')
    return result


def run(root: Path) -> dict:
    source_path = root / 'src' / 'sutram_compiler.asm'
    history_path = root / 'docs' / 'CHANGELOG.md'
    if source_path.is_symlink() or history_path.is_symlink():
        raise ValueError('symlinked release input refused')
    source = source_path.read_bytes()
    history = history_path.read_bytes()
    result = check(history.decode('utf-8'), source.decode('utf-8'))
    result.update({'compiler_source_sha256': hashlib.sha256(source).hexdigest(),
                   'changelog_sha256': hashlib.sha256(history).hexdigest(),
                   'gate': 'source_release_banner_only',
                   'native_binary_executed': False})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        result = run(args.repo)
    except (OSError, UnicodeError, ValueError) as error:
        result = {'status': 'FAIL', 'reason': str(error),
                  'native_binary_executed': False}
    output = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    print(output, end='')
    if args.report is not None:
        try:
            with args.report.open('x', encoding='utf-8') as handle:
                handle.write(output)
        except OSError as error:
            print('cannot create report: ' + str(error), file=sys.stderr)
            return 2
    return 0 if result['status'] == 'PASS' else 2

if __name__ == '__main__':
    raise SystemExit(main())
