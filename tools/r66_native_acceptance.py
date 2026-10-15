#!/usr/bin/env python3
"""R66 complete-compiler acceptance for Sarvam, not run by helper tests.

Run against the R66 STAGED default compiler. --reference is the independently
built accepted R65 default compiler. --reference is optional but missing A/B
is explicitly NOT RUN. No installation, downloads, or accepted-golden edits.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples/r66'
EXPECTED_DIGITS = '123456789\n123456789\n1234\n12.500000\n-7.250000\n9\n42\n7\n०૧॰૰\n'.encode()
EXPECTED_PACK = b'15\n6\n1\n7\n7\n1\n'
ASCII_CONTROL = b'''mukhya() {
    vitti x = 7
    likha(42)
    likha(x * 3 + 1)
    likha(12.5)
    likha(0x2A)
}
'''

def run(cmd: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=12, check=False)


def compile_program(compiler: Path, src: Path, output: Path, lang: str | None = None) -> None:
    cmd = [str(compiler)] + (['--lang', lang] if lang else []) + [str(src), str(output)]
    completed = run(cmd)
    if completed.returncode or not output.is_file():
        raise AssertionError(f'compile failed {src.name}: exit={completed.returncode}, '
                             f'stdout={completed.stdout!r}, stderr={completed.stderr!r}')


def exact_case(compiler: Path, source: Path, output: Path, expected: bytes, lang=None) -> dict:
    compile_program(compiler, source, output, lang)
    completed = run([str(output)])
    if completed.returncode != 0 or completed.stdout != expected:
        raise AssertionError(f'{source.name}: exit={completed.returncode}, '
                             f'expected={expected!r}, observed={completed.stdout!r}')
    return {'case': source.name, 'status': 'PASS', 'exit': completed.returncode,
            'stdout_hex': completed.stdout.hex(), 'executable_bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compiler', type=Path, required=True)
    p.add_argument('--reference', type=Path)
    args = p.parse_args()
    compiler = args.compiler.resolve()
    reference = args.reference.resolve() if args.reference else None
    for path in (compiler, reference):
        if path is not None and not path.is_file():
            p.error(f'missing compiler: {path}')
    results = []
    with tempfile.TemporaryDirectory(prefix='sutram-r66-') as tmp:
        work = Path(tmp)
        for name, lang, expected in (('native_digits.sm', None, EXPECTED_DIGITS),
                                     ('sanskrit_native.sm', 'sanskrit', EXPECTED_PACK),
                                     ('gujarati_native.sm', 'gujarati', EXPECTED_PACK)):
            results.append(exact_case(compiler, EXAMPLES / name, work / (name + '.bin'), expected, lang))
        # Equivalent numeric spellings must preserve native behavior. Do not
        # rewrite string/comment bytes in the product compiler to achieve this.
        source = (EXAMPLES / 'native_digits.sm').read_text('utf-8')
        # Deliberately only alter digit tokens in this generated control, leaving
        # n२ and the quoted UTF-8 string unchanged (their bytes matter separately).
        control_text = source.replace('०१२३४५६७८९', '0123456789').replace('૦૧૨૩૪૫૬૭૮૯', '0123456789')
        for a, b in [('१२3૪', '1234'), ('१२.५', '12.5'), ('૭.૨૫', '7.25'),
                     ('५ + ૪', '5 + 4'), ('n२ = ७', 'n२ = 7')]:
            control_text = control_text.replace(a, b)
        control = work / 'numeric_ascii_control.sm'
        control.write_text(control_text, encoding='utf-8')
        results.append(exact_case(compiler, control, work / 'numeric_ascii.bin', EXPECTED_DIGITS))
        before = work / 'ascii_control.sm'
        before.write_bytes(ASCII_CONTROL)
        newbin = work / 'new_ascii.bin'
        results.append(exact_case(compiler, before, newbin, b'42\n22\n12.500000\n42\n'))
        if reference:
            oldbin = work / 'old_ascii.bin'
            compile_program(reference, before, oldbin)
            if oldbin.read_bytes() != newbin.read_bytes():
                raise AssertionError('R66_DEFAULT_ASCII_BINARY_CHANGED: do not rewrite goldens')
            results.append({'case': 'default ASCII binary identity', 'status': 'PASS',
                            'bytes': len(newbin.read_bytes())})
        else:
            results.append({'case': 'default ASCII binary identity', 'status': 'NOT RUN'})
        for i, tail in enumerate((b'\xe0', b'\xe0\xa5', b'\xe0\xab', b'\xe0\x9f\xbf')):
            bad = work / f'truncated_{i}.sm'
            bad.write_bytes(b'mukhya() { vitti ' + tail)
            failed = run([str(compiler), str(bad), str(work / f'bad_{i}.bin')])
            if failed.returncode != 1 or b'E_UTF8' not in failed.stdout + failed.stderr:
                raise AssertionError(f'UTF8 rejection failed: exit={failed.returncode}, '
                                     f'output={failed.stdout!r} {failed.stderr!r}')
            results.append({'case': f'malformed Indic {i}', 'status': 'PASS', 'exit': 1})
    print(json.dumps({'scope': 'R66 full compiler native acceptance', 'results': results},
                     indent=2, ensure_ascii=False))
    print('R66_NATIVE_CASES_PASSED; inspect NOT RUN entries separately')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
