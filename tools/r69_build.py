#!/usr/bin/env python3
"""Build the pinned canonical NASM entry. Developer tooling, not a compiler backend.

Requires an existing NASM and GNU ld. Never downloads, changes policy or starts CI.
A successful build/format check does not mean the resulting program was executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import subprocess
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPILER = 'src/sutram_compiler.asm'
ENTRY = 'src/r68_compiler_entry.asm'
COMPILER_BLOB = '319297aa6bcf57f5bf27c5c38470248ad30b5436'  # R73 re-pin (v269; previous blob ac7194e5); R72 re-pin (v268; previous blob 88bbf91e); R71 re-pin (v267; previous blob 79fd623f); R71 re-pin (v266; previous blob da24e91d); R70 re-pin (v265; previous blob bac58af8); R69 re-pin (v264; previous blob 2cef0233); R65b (Claude, 2026-10-29) re-pin (v263; previous blob c1b8803d); R65a (Claude, 2026-10-29) re-pin (v262; previous blob e64bcce5); R56c (Claude, 2026-10-28) re-pin (v261; previous blob a42bd106); R56b (Claude, 2026-10-28) re-pin (v260; previous blob aedeb313); R56a (Claude, 2026-10-28) re-pin (v259; previous blob 569ffdeb); R54 re-pin (expanded source 128 KiB; v258; R52 blob 7f23de90); R52 re-pin (likha up to six values, lkhb dasham, the yoj hint, arabhya/paryantam; v257; R53 blob c0c60560); R53 re-pin (nivartanam the return keyword, prati the alias; v256; R50 blob 08ce2608); R50 re-pin (Sanskrit keywords by default, प्रति; v255; R49 blob 811f09ed); R49 re-pin (repeated debug flags, --debug-from; v254; R46 blob 89495406); R46 re-pin (--debug=<names>[@N[-M]], the counter and the summary; v253; R45b blob 3df625fe); R45b re-pin (--debug shows only in-scope variables; v252; R45 blob 95751af5); R45 re-pin (--debug, src/r45_debug.inc; v251; R44 blob 7b0d8217); R44 re-pin (vartani_aayam, vartani_tul, vartani_pratilip; v250; R42 blob 03e9845c); R42 re-pin (the bounds guard, r38_mark_alias; v249; R41 blob b9dbbb5f); R41 re-pin (windows-ffi merged into main: --ffi on Windows too; v248; R38 blob 7db83d38); R38 re-pin (--fail-alloc N, src/r38_fail_alloc.inc; v246; R34b blob 8b7875c0); R34b re-pin (the FFI sidecar's version: v1 i64 only, v2 the R33 kinds; v244; R34 blob 160233e2); R34 re-pin (the Windows linker: --object/--separate on Windows, SUTRAMO2; the runtime-call table bounded; v243; R33 blob a7bc308b); R33 re-pin (the FFI's kinds: f64, ptr, void; v242; R32 blob 52950849); R32 re-pin (the FFI: --ffi, src/r32_ffi.inc, v241; R30 blob 9e4df8f8); R30 re-pin (vitti in an object, v240; R29 blob 4aa08517); R29 re-pin (--separate, v239; R28 blob eadca952); R28 re-pin (--object, v238; R26 blob 46517cdb); R26 re-pin (the handler, v237; R25 blob 836a6d34); R25 re-pin (the error type, v236; R24 blob b204bcc0); R24 re-pin (the method hint, v235; R23 blob 1f6377e3); R23 re-pin (function values, methods, slices, v234; R22 blob 8648e097); R22 re-pin (F8: the keyword packs built in, v233; R18 blob 4547e473); R18 re-pin (sthagita exits 0, rachana in a function is a no-op, v232; R17 blob 5b144a70); R17 re-pin (D1-D4, the six crash kinds, v229; R13 blob d96aa571); R13 re-pin (Sanskrit-grammar defaults, v208); R11 8625095a re-pin (messages per --lang pack; src/r11_sandesh.inc pinned with it); R10 5ade34ed re-pin (F1: rbp displacements beyond disp8 emitted as disp32); R9 5caa9b6e re-pin (nirmmita 0 on failure, guna evaluated once; v188's version-string blob ea5ff808 was never pinned); R7 cc5cfbe4, R5 185b7f06, R4 4b137114, R3 ea2a1e91, pre-v157 64ea028a
ENTRY_BLOB = '42389aaf73179726d91e23359aee2199734036e1'
MODES = {
    'default': (),
    'peepholes': ('SUTRAM_R65_PEEPHOLES=1',),
    'trap': ('SUTRAM_R65_TRAP_INT=1',),
    'combined': ('SUTRAM_R65_PEEPHOLES=1', 'SUTRAM_R65_TRAP_INT=1'),
    'pairs': ('SUTRAM_R67_PURE_STACK_PAIRS=1',),
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def clean_environment() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if not k.upper().startswith('SUTRAM_')}


def regular_input(root: Path, relative: str) -> Path:
    p = PurePosixPath(relative)
    if (p.is_absolute() or not p.parts or any(x in ('.', '..') for x in relative.split('/'))
            or '\\' in relative or ':' in relative):
        raise ValueError('unsafe input path: ' + relative)
    result = root
    for part in p.parts:
        result = result / part
        if result.is_symlink():
            raise ValueError('symlink input is not allowed: ' + relative)
    if not result.is_file() or not stat.S_ISREG(result.stat().st_mode):
        raise ValueError('missing regular input: ' + relative)
    return result


def verify_files(root: Path, pins: dict[str, str]) -> dict[str, dict[str, Any]]:
    if not pins:
        raise ValueError('empty source lock')
    observed = {}
    for name, expected in pins.items():
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{40}', expected):
            raise ValueError('invalid Git blob pin: ' + name)
        path = regular_input(root, name)
        data = path.read_bytes()
        actual = git_blob(data)
        if actual != expected:
            raise ValueError(f'input drift: {name}: expected {expected}, got {actual}')
        observed[name] = {'git_blob': actual, 'sha256': hashlib.sha256(data).hexdigest(),
                          'bytes': len(data)}
    return observed


def verify_release(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    path = regular_input(root, 'tools/r69_build.lock.json')
    lock = json.loads(path.read_text('utf-8'))
    if lock.get('schema') != 1 or lock.get('entry') != ENTRY:
        raise ValueError('unsupported build contract')
    pins = lock.get('pins', {})
    if pins.get(COMPILER) != COMPILER_BLOB or pins.get(ENTRY) != ENTRY_BLOB:
        raise ValueError('compiler/entry pins do not match this reviewed build tool')
    observed = verify_files(root, pins)
    # Include closure is checked without expanding or rewriting the NASM source.
    # Both conditional host paths are deliberately covered by this lock.
    for name in pins:
        text = (root / name).read_text('utf-8')
        for match in re.finditer(r'^\s*%(?:include|incbin)\s+([^\r\n;]+)', text, re.M):
            token = match.group(1).strip()
            if len(token) < 3 or token[0] not in ('"', "'") or token[-1] != token[0]:
                raise ValueError('nonliteral include needs review: ' + name + ': ' + token)
            if token[1:-1] not in pins:
                raise ValueError('unlocked include: ' + name + ' -> ' + token[1:-1])
    return observed


def validate_image(data: bytes, target: str) -> None:
    if target == 'linux':
        if (len(data) < 64 or data[:4] != b'\x7fELF' or data[4:7] != b'\x02\x01\x01'
                or struct.unpack_from('<H', data, 18)[0] != 62
                or struct.unpack_from('<H', data, 16)[0] not in (2, 3)):
            raise ValueError('output is not a little-endian x86-64 ELF executable')
    elif target == 'windows':
        if len(data) < 64 or data[:2] != b'MZ':
            raise ValueError('output is not PE32+ AMD64')
        pe = struct.unpack_from('<I', data, 0x3c)[0]
        if (pe < 64 or pe + 26 > len(data) or data[pe:pe+4] != b'PE\0\0'
                or struct.unpack_from('<H', data, pe+4)[0] != 0x8664
                or struct.unpack_from('<H', data, pe+24)[0] != 0x20b):
            raise ValueError('invalid PE32+ AMD64 headers')
    else:
        raise ValueError('unsupported target: ' + target)


def build_commands(root: Path, obj: Path, exe: Path, target: str, mode: str,
                   nasm: str, linker: str) -> list[list[str]]:
    if target not in ('linux', 'windows') or mode not in MODES:
        raise ValueError('unknown build configuration')
    asm = [nasm, '-f', 'win64' if target == 'windows' else 'elf64', '-I', str(root) + os.sep]
    if target == 'windows':
        asm += ['-DWINDOWS=1']
    asm += ['-D' + flag for flag in MODES[mode]]
    asm += [str(root / ENTRY), '-o', str(obj)]
    link = [linker]
    if target == 'windows':
        link += ['-mi386pep', '--subsystem', 'console', '--entry=_start']
    link += ['-o', str(exe), str(obj)]
    return [asm, link]


def refuse_output(path: Path, replace: bool = False) -> None:
    if path.is_symlink():
        raise ValueError('refuse symlink output: ' + str(path))
    if os.path.lexists(path):
        if not replace or not path.is_file() or path.stat().st_nlink != 1:
            raise ValueError('refuse existing/nonregular/linked output: ' + str(path))
    if not path.parent.is_dir():
        raise ValueError('output parent must already exist: ' + str(path.parent))


def build(root: Path, output: Path, target: str, mode: str, nasm: str, linker: str,
          replace: bool = False) -> dict[str, Any]:
    inputs = verify_release(root)
    output = output.absolute()
    refuse_output(output, replace)
    if output.resolve() in {(root / p).resolve() for p in inputs}:
        raise ValueError('output must not overwrite a source input')
    logs = []
    with tempfile.TemporaryDirectory(prefix='sutram-r69-build-', dir=output.parent) as tmp:
        obj, candidate = Path(tmp) / 'compiler.o', Path(tmp) / 'compiler'
        for command in build_commands(root, obj, candidate, target, mode, nasm, linker):
            result = subprocess.run(command, cwd=root, env=clean_environment(),
                                    capture_output=True, timeout=120, check=False)
            logs.append({'command': command, 'exit': result.returncode,
                         'stdout': result.stdout.decode('utf-8', errors='replace'),
                         'stderr': result.stderr.decode('utf-8', errors='replace')})
            if result.returncode:
                raise RuntimeError('build command failed: ' + json.dumps(logs[-1]))
        if candidate.is_symlink() or not candidate.is_file():
            raise ValueError('linker did not create a regular candidate')
        content = candidate.read_bytes()
        validate_image(content, target)
        # Recheck pins after tool execution; nothing is published after source drift.
        if verify_release(root) != inputs:
            raise ValueError('source changed during build')
        refuse_output(output, replace)
        candidate.chmod(0o755)
        if replace:
            os.replace(candidate, output)
        else:
            # O_EXCL refuses even dangling links and races with another publisher.
            with output.open('xb') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            output.chmod(0o755)
    return {'status': 'BUILT_FORMAT_CHECKED', 'runtime_execution': 'NOT_RUN',
            'target': target, 'mode': mode, 'entry': ENTRY,
            'input_compiler_git_blob': inputs[COMPILER]['git_blob'],
            'output_compiler_source_git_blob': inputs[COMPILER]['git_blob'],
            'entry_git_blob': inputs[ENTRY]['git_blob'],
            'binary_sha256': hashlib.sha256(content).hexdigest(), 'binary_bytes': len(content),
            'output': str(output), 'inputs': inputs, 'commands': logs}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=('linux', 'windows'), default='linux')
    parser.add_argument('--mode', choices=tuple(MODES), default='default')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--nasm', default='nasm')
    parser.add_argument('--linker', default='ld')
    parser.add_argument('--replace', action='store_true', help='replace a regular, nonlinked build output only')
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        if args.report and args.output and args.report.absolute() == args.output.absolute():
            raise ValueError('report must not alias the compiler output')
        if args.report:
            refuse_output(args.report)
        if args.check_only:
            report = {'status': 'SOURCE_PINS_CHECKED', 'compiler_executed': False,
                      'runtime_execution': 'NOT_RUN', 'entry': ENTRY, 'inputs': verify_release()}
        else:
            if args.output is None:
                parser.error('--output is required for a build')
            report = build(ROOT, args.output, args.target, args.mode, args.nasm, args.linker, args.replace)
        text = json.dumps(report, indent=2) + '\n'
        if args.report:
            with args.report.open('x', encoding='utf-8') as f:
                f.write(text)
        print(text, end='')
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.exit(2, 'R69_BUILD_REFUSED: ' + str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
