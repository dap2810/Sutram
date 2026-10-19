#!/usr/bin/env python3
"""Read a log written by tools/accept-windows.ps1 and say what it proves about THIS tree.

Runs anywhere (Linux included): it does not run Windows, it checks the evidence.

    python3 tools/check_accept_windows_log.py path/to/accept-windows.json [--root .]

It prints the environment, every check with its status and environment, and, for each binary
the log names, whether its SHA-256 matches the file of the same name in --root. It accepts the
log as Windows acceptance of the tree only when all of these hold:

  * the run was on Windows (not Wine) and not elevated,
  * no required check FAILed and none is NOT-RUN,
  * every repository binary the log hashed matches the file in --root.

Exit 0 when accepted, 1 when not (with the reasons), 2 when the file is not a valid log.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROLE_FILES = {
    'setup': 'Sutram-Setup.exe',
    'repo-compiler win\\sutram.exe': 'win/sutram.exe',
    'repo-compiler sutram.exe': 'sutram.exe',
    'repo-ide sutram-ide-gui.exe': 'sutram-ide-gui.exe',
}
STATUSES = {'PASS', 'FAIL', 'NOT-RUN'}


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    for key in ('tool', 'verdict', 'environment', 'artefacts', 'checks'):
        if key not in data:
            raise ValueError(f'missing key: {key}')
    if data['tool'] != 'tools/accept-windows.ps1':
        raise ValueError(f"not an accept-windows log: tool={data['tool']!r}")
    for c in data['checks']:
        if c.get('status') not in STATUSES:
            raise ValueError(f"check {c.get('id')!r} has status {c.get('status')!r}")
    return data


def evaluate(data: dict, root: Path) -> tuple[list[str], list[str]]:
    """Returns (report lines, reasons the log is not acceptance of this tree)."""
    out: list[str] = []
    why: list[str] = []
    env = data['environment']
    out.append(f"environment: {env.get('environment')}  windows {env.get('windows_product')} "
               f"{env.get('windows_display_version')} build {env.get('windows_build')}.{env.get('windows_ubr')}  "
               f"PowerShell {env.get('powershell')}  elevated={env.get('elevated')}  commit={env.get('git_commit')}")
    if env.get('environment') != 'Windows' or env.get('wine'):
        why.append('the run was under Wine, not Windows')
    if env.get('elevated'):
        why.append('the run was elevated: least privilege is not shown')
    out.append(f"verdict in log: {data['verdict']}")
    for c in data['checks']:
        req = '' if c.get('required', True) else ' (advisory)'
        out.append(f"  {c['status']:<8} {c['id']:<30} [{c.get('environment')}]{req}  {c.get('detail', '')}"[:200])
        if c.get('required', True) and c['status'] == 'FAIL':
            why.append(f"required check FAILed: {c['id']}")
        if c.get('required', True) and c['status'] == 'NOT-RUN':
            why.append(f"required check NOT-RUN: {c['id']}")
    out.append('binaries:')
    for a in data['artefacts']:
        rel = ROLE_FILES.get(a.get('role', ''))
        logged = a.get('sha256')
        if rel is None:
            out.append(f"  {a.get('role')}: {logged} (installed copy; not in the tree)")
            continue
        here = sha256(root / rel)
        if logged is None:
            state = 'not present on the tested machine'
        elif here is None:
            state = f'no {rel} in --root'
        elif here == logged:
            state = 'MATCHES this tree'
        else:
            state = f'DIFFERS from this tree ({here})'
            why.append(f'{rel} in the log is not the file in this tree')
        out.append(f"  {rel}: {logged}  {state}")
    return out, why


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('log', type=Path)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args(argv)
    try:
        data = load(args.log)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f'INVALID LOG: {e}')
        return 2
    lines, why = evaluate(data, args.root)
    print('\n'.join(lines))
    if why:
        print('NOT ACCEPTED as Windows acceptance of this tree:')
        for w in why:
            print('  - ' + w)
        return 1
    print('ACCEPTED: Windows, not elevated, every required check PASS, binaries match this tree')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
