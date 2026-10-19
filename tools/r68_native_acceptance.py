#!/usr/bin/env python3
"""R68 full-compiler acceptance for Sarvam; no build, download, installation or CI.

--compiler must be built from the checked R68 entry for diagnostics.
--reference is an independently built accepted-R67 default compiler.
--pair-compiler uses identical build settings plus SUTRAM_R67_PURE_STACK_PAIRS=1.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ('odia', 'kannada', 'marathi', 'tamil', 'telugu', 'hindi')

def execute(command: list[str | Path], timeout: float = 20) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env.pop('SUTRAM_LANG', None)
    return subprocess.run([str(x) for x in command], cwd=ROOT, env=env,
                          capture_output=True, check=False, timeout=timeout)

def compile_case(compiler: Path, src: Path, out: Path, lang: str | None = None) -> None:
    if out.exists():
        raise AssertionError('refuse stale generated executable ' + str(out))
    cmd = [compiler] + (['--lang', lang] if lang else []) + [src, out]
    result = execute(cmd)
    if result.returncode != 0 or not out.is_file():
        raise AssertionError(f'compile failed {src}: exit={result.returncode}; '
                             f'stdout={result.stdout!r}; stderr={result.stderr!r}')

def run_expected(exe: Path, expected: bytes, exit_code: int = 0) -> None:
    result = execute([exe])
    if result.returncode != exit_code or result.stdout != expected:
        raise AssertionError(f'execution mismatch {exe}: exit={result.returncode}; '
                             f'expected={expected!r}; actual={result.stdout!r}; '
                             f'stderr={result.stderr!r}')

def require_error(compiler: Path, src: Path, out: Path, message: bytes, lang=None) -> None:
    cmd = [compiler] + (['--lang', lang] if lang else []) + [src, out]
    result = execute(cmd)
    # A crash/signal or an unrelated compiler failure must NEVER pass this gate.
    if result.returncode != 1 or not result.stdout.endswith(message) or out.exists():
        raise AssertionError(f'wrong diagnostic: {src}; exit={result.returncode}; '
                             f'want={message!r}; stdout={result.stdout!r}; stderr={result.stderr!r}')

def pair_probe(default: Path, reference: Path, pairs: Path, work: Path) -> dict[str, object]:
    source = ROOT / 'examples/r68/pairs'
    paths = {}
    for mode, compiler in [('default', default), ('reference', reference), ('pairs', pairs)]:
        for name in ('all_registers', 'no_pairs', 'nonmatching'):
            out = work / (mode + '-' + name)
            compile_case(compiler, source / (name + '.sm'), out)
            # nonmatching is a codegen control, not a promised safe arbitrary-ASM run.
            if name != 'nonmatching':
                run_expected(out, (source / (name + '.out')).read_bytes())
            paths[mode, name] = out.read_bytes()
    for name in ('all_registers', 'no_pairs', 'nonmatching'):
        if paths['default', name] != paths['reference', name]:
            raise AssertionError('default-code identity failed: ' + name)
    if paths['pairs', 'all_registers'] != paths['pairs', 'no_pairs']:
        raise AssertionError('pair mode did not match the pair-free native program')
    if paths['pairs', 'nonmatching'] != paths['default', 'nonmatching']:
        raise AssertionError('nonmatching/RSP/nonadjacent control changed')
    before, after = paths['default', 'all_registers'], paths['pairs', 'all_registers']
    if len(before) - len(after) != 46:
        raise AssertionError(f'expected exactly 46 removed bytes, got {len(before)-len(after)}')
    return {'probe': 'R68_PURE_PAIR_AB_PASS', 'before_bytes': len(before),
            'after_bytes': len(after), 'removed_bytes': 46, 'registers': 15,
            'default_sha256': hashlib.sha256(before).hexdigest(),
            'pair_sha256': hashlib.sha256(after).hexdigest(),
            'default_vs_reference': 'byte identical for all three cases',
            'timing_measurement': 'not measured'}

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compiler', required=True, type=Path)
    p.add_argument('--reference', type=Path)
    p.add_argument('--pair-compiler', type=Path)
    p.add_argument('--suite', action='store_true')
    a = p.parse_args()
    for key in ('compiler', 'reference', 'pair_compiler'):
        value = getattr(a, key)
        if value:
            value = value.resolve()
            if not value.is_file(): p.error('missing compiler ' + str(value))
            setattr(a, key, value)
    if bool(a.reference) != bool(a.pair_compiler):
        p.error('provide BOTH --reference and --pair-compiler for the pair A/B')
    with tempfile.TemporaryDirectory(prefix='sutram-r68-') as temp:
        work = Path(temp)
        for lang in LANGUAGES:
            src = ROOT / 'examples/r68' / (lang + '.sm')
            out = work / lang
            compile_case(a.compiler, src, out, lang)
            run_expected(out, src.with_suffix('.out').read_bytes(),
                         int(src.with_suffix('.exit').read_text()))
            print('R68_SCRIPT_PASS', lang)
        for i, malformed in enumerate((b'\xe0\xad ', b'\xe0\xb3', b'\xe0\xaf\xff',
                                        b'\xe0\xb1\xa8\x80')):
            src = work / ('bad-' + str(i) + '.sm')
            src.write_bytes(b'mukhya() {\n    vitti x = 1\n    vitti y = ' + malformed + b'\n}\n')
            want = ('Sutram Error [E_UTF8]: ' + str(src) +
                    ':3: srot me ashuddh ya khandit UTF-8\n').encode()
            require_error(a.compiler, src, work / ('bad-out-' + str(i)), want)
            print('R68_UTF8_DIAGNOSTIC_PASS', i)
        src = work / 'alias.sm'
        src.write_text('मुख्य() {\n    चर x = मु॰\n}\n', encoding='utf-8')
        want = ("Sutram Error [E_ABBREVIATION_VALUE]: " + str(src) +
                ":2: sankshep shabd mulya nahi: 'मु॰'\n").encode()
        require_error(a.compiler, src, work / 'alias-out', want, 'hindi')
        print('R68_ABBREVIATION_DIAGNOSTIC_PASS')
        if a.reference and a.pair_compiler:
            print(json.dumps(pair_probe(a.compiler, a.reference, a.pair_compiler, work), indent=2))
        else:
            print('R68_PAIR_AB_NOT_RUN: independent reference and pair compiler not supplied')
    if a.suite:
        env = os.environ.copy(); env['SUTRAM_COMPILER'] = str(a.compiler)
        result = subprocess.run(['python3', str(ROOT/'tests/run_tests.py')], cwd=ROOT, env=env)
        if result.returncode:
            raise AssertionError('full accepted suite failed; no expectations were rewritten')
    print('R68_NATIVE_GATES_PASS: only the gates actually requested above')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
