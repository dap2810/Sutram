#!/usr/bin/env python3
"""R74: prove a canonical Linux build is repeatable in two fresh local clones.

No network, elevated privileges, downloads, CI dispatch or source writes.
A repeatable ELF binary is not proof the compiler or emitted programs work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def command(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, env={k: v for k, v in os.environ.items()
                            if not k.upper().startswith('SUTRAM_')},
                            capture_output=True, text=True, timeout=240, check=False)
    if result.returncode:
        raise RuntimeError(f'{args[0]} exit={result.returncode}: {result.stderr[-1800:]}')
    return result.stdout.strip()


def prove(repo: Path) -> dict:
    if not repo.is_dir():
        raise ValueError(f'not a checkout: {repo}')
    sha = command(['git', '-C', str(repo), 'rev-parse', 'HEAD'])
    # Clone a fixed SHA twice from LOCAL Git objects; never fetch a moving main.
    if command(['git', '-C', str(repo), 'status', '--porcelain']):
        raise ValueError('input checkout dirty; refuse inconsistent snapshot')
    runs = []
    with tempfile.TemporaryDirectory(prefix='sutram-r74-') as td:
        root = Path(td)
        for n in (1, 2):
            clone = root / f'checkout-{n}'
            output = root / f'compiler-{n}'
            report = root / f'build-{n}.json'
            command(['git', 'clone', '--quiet', '--local', '--no-hardlinks', '--no-checkout',
                     '--', str(repo), str(clone)])
            command(['git', '-C', str(clone), 'checkout', '--quiet', '--detach', sha])
            if command(['git', '-C', str(clone), 'status', '--porcelain']):
                raise RuntimeError('new checkout not clean')
            build_tool = clone / 'tools' / 'r69_build.py'
            if not build_tool.is_file():
                raise RuntimeError('missing canonical build tool')
            check = json.loads(command([sys.executable, str(build_tool), '--check-only'], cwd=clone))
            if check.get('status') != 'SOURCE_PINS_CHECKED':
                raise RuntimeError(f'source lock not verified: {check.get("status")}')
            build = json.loads(command([sys.executable, str(build_tool), '--target', 'linux',
                                       '--output', str(output), '--report', str(report)], cwd=clone))
            data = output.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            if (build.get('status') != 'BUILT_FORMAT_CHECKED'
                    or build.get('binary_sha256') != digest
                    or not data.startswith(b'\x7fELF')):
                raise RuntimeError('build metadata/output mismatch')
            runs.append({'run': n, 'commit': sha, 'sha256': digest, 'bytes': len(data),
                         'lock_inputs': len(check['inputs']), 'build_status': build['status'],
                         'runtime_execution': 'NOT_RUN'})
        if (runs[0]['sha256'], runs[0]['bytes']) != (runs[1]['sha256'], runs[1]['bytes']):
            raise RuntimeError('two clean builds produce different compiler binaries: '
                               f'{runs[0]["sha256"]} != {runs[1]["sha256"]}')
    return {'source': 'PASS', 'canonical_build': 'PASS', 'repeatability': 'PASS',
            'compiler_execution': 'NOT_RUN', 'commit': sha, 'runs': runs}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--report', type=Path)
    a = p.parse_args()
    try:
        result = prove(a.repo.resolve())
        rc = 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError,
            RuntimeError, subprocess.TimeoutExpired) as exc:
        result = {'source': 'UNCONFIRMED', 'canonical_build': 'FAIL',
                  'repeatability': 'NOT_RUN', 'reason': str(exc)}
        rc = 2
    serialized = json.dumps(result, indent=2) + '\n'
    print(serialized, end='')
    if a.report:
        try:
            with a.report.open('x', encoding='utf8') as f:
                f.write(serialized)
        except OSError as exc:
            print(f'report write failed: {exc}', file=sys.stderr)
            return 2
    return rc

if __name__ == '__main__':
    raise SystemExit(main())
