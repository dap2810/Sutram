#!/usr/bin/env python3
"""R13: the version `sutram --version` prints must be the project's current version.

The version string is typed by hand in src/sutram_compiler.asm (msg_version) and had
drifted twice: v160, then v182 while the project reached v207. Nothing failed. Now this
check does:

  PASS  the compiler's vNNN is the newest `## vNNN` heading in docs/CHANGELOG.md,
        or one more than it (a branch whose merge entry is not written yet)
  FAIL  anything else, with the one line to change

The language packs take the version from the default (`{ver}` in lang/*.sandesh), so a
bump is: edit msg_version, run tools/sandesh.py --write, rebuild the compiler binaries.

    python3 tools/check_version.py            # prints PASS or FAIL, exit 0 / 1
    python3 tools/check_version.py --binary ./sutram_compiler   # also run --version
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source_version() -> int:
    s = (ROOT / 'src/sutram_compiler.asm').read_text(encoding='utf-8')
    m = re.search(r'msg_version\s+db\s+"Sutram [0-9.]+ \(v(\d+)\)', s)
    if not m:
        raise SystemExit('FAIL: no "(vNNN)" in msg_version in src/sutram_compiler.asm')
    return int(m.group(1))


def changelog_version() -> int:
    for line in (ROOT / 'docs/CHANGELOG.md').read_text(encoding='utf-8').splitlines():
        m = re.match(r'##\s+v(\d+)\b', line)
        if m:
            return int(m.group(1))
    raise SystemExit('FAIL: no "## vNNN" heading in docs/CHANGELOG.md')


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--binary', help='also check what this compiler binary prints for --version')
    a = ap.parse_args(argv)
    src, log = source_version(), changelog_version()
    problems = []
    if src not in (log, log + 1):
        problems.append(f'the compiler says v{src}, the CHANGELOG is at v{log}: set msg_version to (v{log}) '
                        'in src/sutram_compiler.asm, run tools/sandesh.py --write, rebuild')
    if a.binary:
        out = subprocess.run([a.binary, '--version'], capture_output=True, text=True).stdout
        if f'(v{src})' not in out:
            problems.append(f'{a.binary} --version prints {out.splitlines()[0] if out else "nothing"!r}, '
                            f'not v{src}: the binary is stale, rebuild it')
    if problems:
        for p in problems:
            print('FAIL', p)
        return 1
    print(f'PASS version v{src} (CHANGELOG v{log})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
