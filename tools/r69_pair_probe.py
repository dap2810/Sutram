#!/usr/bin/env python3
"""Measure the pure-pair mode with three explicit, independently built compilers.

This does not assemble compilers or download anything. Native Linux programs are
run only for the two safe fixtures; the raw-ASM nonmatching control is compiled
but NEVER run. A successful probe is not a general performance benchmark.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any
from r69_build import clean_environment, regular_input, refuse_output, validate_image, verify_release

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/r69/pairs'
NAMES = ('all_registers', 'no_pairs', 'nonmatching')
REGISTERS = ('rax', 'rcx', 'rdx', 'rbx', 'rbp', 'rsi', 'rdi',
             'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fixture_contract(root: Path = ROOT) -> tuple[dict[str, bytes], int]:
    directory = root / 'tests/r69/pairs'
    lock = json.loads((directory / 'manifest.json').read_text('utf-8'))
    if lock.get('schema') != 1:
        raise ValueError('unsupported fixture contract')
    inputs = {}
    required = {name + '.sm' for name in NAMES} | {'all_registers.out', 'no_pairs.out'}
    if set(lock.get('sha256', {})) != required:
        raise ValueError('fixture manifest is incomplete or expanded without review')
    for name, expected in lock['sha256'].items():
        data = regular_input(root, 'tests/r69/pairs/' + name).read_bytes()
        if sha(data) != expected:
            raise ValueError('fixture drift: ' + name)
        inputs[name] = data
    text = inputs['all_registers.sm'].decode('ascii')
    lines = re.findall(r'yantra\("([0-9A-F ]+)"\)\s*# (\w+)', text)
    if tuple(register for _, register in lines) != REGISTERS:
        raise ValueError('the probe must cover exactly the 15 reviewed non-RSP GPRs')
    # Each source operation is its entire hex block; the code delta is derived
    # from those bytes, not entered in a report as a precomputed observation.
    expected_removed = sum(len(bytes.fromhex(code)) for code, _ in lines)
    if expected_removed != 46:
        raise ValueError('probe definition changed; expected 7*2 + 8*4 bytes')
    return inputs, expected_removed


def validate_compilers(compilers: dict[str, Path]) -> dict[str, dict[str, Any]]:
    report = {}
    if set(compilers) != {'default', 'reference', 'pairs'}:
        raise ValueError('three named compiler builds are mandatory')
    for name, path in compilers.items():
        if path.is_symlink() or not path.is_file():
            raise ValueError('compiler must be a regular nonsymlink file: ' + str(path))
        data = path.read_bytes()
        validate_image(data, 'linux')
        if not os.access(path, os.X_OK):
            raise ValueError('compiler is not executable: ' + str(path))
        report[name] = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
    values = list(compilers.values())
    for i, left in enumerate(values):
        for right in values[i+1:]:
            if os.path.samefile(left, right):
                raise ValueError('default/reference/pairs must not alias the same file or hardlink')
    return report


def execute(args: list[Path | str], root: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([str(x) for x in args], cwd=root, env=clean_environment(),
                          stdin=subprocess.DEVNULL, capture_output=True, timeout=20, check=False)


def compile_one(compiler: Path, source: Path, output: Path, root: Path) -> bytes:
    refuse_output(output)
    result = execute([compiler, source, output], root)
    if result.returncode != 0:
        raise RuntimeError(f'compiler rejected {source.name}: exit={result.returncode}; '
                           f'stdout={result.stdout!r}; stderr={result.stderr!r}')
    if output.is_symlink() or not output.is_file() or output.stat().st_nlink != 1:
        raise ValueError('compiler failed to create a fresh regular executable')
    data = output.read_bytes()
    validate_image(data, 'linux')
    if not os.access(output, os.X_OK):
        raise ValueError('compiler output is not executable; not repairing it inside the probe')
    return data


def compare_generated(generated: dict[tuple[str, str], bytes], expected: int) -> dict[str, Any]:
    for name in NAMES:
        if generated['default', name] != generated['reference', name]:
            raise ValueError('default/reference identity failed: ' + name)
    if generated['pairs', 'all_registers'] != generated['pairs', 'no_pairs']:
        raise ValueError('pair mode differs from the pair-free native program')
    if generated['pairs', 'no_pairs'] != generated['default', 'no_pairs']:
        raise ValueError('pair-free control changed under the optional mode')
    if generated['pairs', 'nonmatching'] != generated['default', 'nonmatching']:
        raise ValueError('nonmatching/RSP/nonadjacent control changed')
    before = generated['default', 'all_registers']
    after = generated['pairs', 'all_registers']
    measured = len(before) - len(after)
    if measured != expected:
        raise ValueError(f'measured delta {measured} != expected fixture delta {expected}')
    return {'before_bytes': len(before), 'after_bytes': len(after),
            'measured_removed_bytes': measured, 'expected_removed_bytes': expected,
            'default_vs_reference': 'BYTE_IDENTICAL_ALL_THREE_FIXTURES',
            'pair_free_control': 'BYTE_IDENTICAL', 'nonmatching_control': 'BYTE_IDENTICAL',
            'instruction_timing': 'NOT_MEASURED', 'speedup': None}


def run_probe(compilers: dict[str, Path], root: Path = ROOT) -> dict[str, Any]:
    source_inputs = verify_release(root)
    fixtures, expected = fixture_contract(root)
    compiler_info = validate_compilers(compilers)
    generated = {}
    executions = []
    with tempfile.TemporaryDirectory(prefix='sutram-r69-pairs-') as temporary:
        work = Path(temporary)
        for mode, compiler in compilers.items():
            for name in NAMES:
                source = work / (name + '.sm')
                if not source.exists():
                    source.write_bytes(fixtures[name + '.sm'])
                output = work / (mode + '-' + name)
                generated[mode, name] = compile_one(compiler, source, output, root)
                if name == 'nonmatching':
                    executions.append({'mode': mode, 'fixture': name, 'run': 'NOT_RUN_RAW_ASM_CONTROL'})
                    continue
                result = execute([output], root)
                wanted = fixtures[name + '.out']
                if result.returncode != 0 or result.stdout != wanted or result.stderr:
                    raise ValueError(f'program mismatch {mode}/{name}: exit={result.returncode}; '
                                     f'stdout={result.stdout!r}; stderr={result.stderr!r}')
                executions.append({'mode': mode, 'fixture': name, 'exit': result.returncode,
                                   'stdout_hex': result.stdout.hex(), 'run': 'PASS'})
        comparison = compare_generated(generated, expected)
    # Do not report a passing run after the user replaces one of its inputs.
    if validate_compilers(compilers) != compiler_info or verify_release(root) != source_inputs:
        raise ValueError('compiler/source identity changed during the probe')
    fixture_contract(root)
    return {'status': 'PASS', 'compiler_executed': True, 'safe_programs_executed': 6,
            'compiled_programs': 9, 'compilers': compiler_info, 'comparison': comparison,
            'outputs': {mode + '/' + name: {'bytes': len(data), 'sha256': sha(data)}
                        for (mode, name), data in generated.items()},
            'execution': executions, 'source_inputs': source_inputs,
            'build_provenance': 'Record the separate build reports; source/binary hashes alone do not prove correspondence.',
            'scope': 'Whole canonical pure push/pop blocks, same non-RSP GPR only; no observed transient stack effects, external entry or handcoded relative offsets.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--pair-compiler', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--validate-fixtures', action='store_true')
    args = parser.parse_args()
    try:
        if args.report:
            refuse_output(args.report)
        if args.validate_fixtures:
            _, expected = fixture_contract()
            report = {'status': 'FIXTURES_VALID', 'compiler_executed': False,
                      'native_status': 'NOT_RUN', 'expected_removed_bytes': expected,
                      'measured_removed_bytes': None}
        else:
            if not all((args.compiler, args.reference, args.pair_compiler)):
                parser.error('--compiler, --reference and --pair-compiler are all required')
            paths = {'default': args.compiler.absolute(), 'reference': args.reference.absolute(),
                     'pairs': args.pair_compiler.absolute()}
            report = run_probe(paths)
        text = json.dumps(report, indent=2) + '\n'
        if args.report:
            with args.report.open('x', encoding='utf-8') as f:
                f.write(text)
        print(text, end='')
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, 'R69_PAIR_PROBE_FAILED: ' + str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
