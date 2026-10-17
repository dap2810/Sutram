#!/usr/bin/env python3
"""Verify reviewed inputs and copy the experimental R71 NASM entry.

No compiler replacement, downloads, permission changes or automatic CI. A
successful preparation is source identity evidence, not a compiler build.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
CORE_PINS = {
    'src/sutram_compiler.asm': '64ea028a5ccf56117c132a7efd0673cbe2df3fc6',
    'src/r68_compiler_entry.asm': '42389aaf73179726d91e23359aee2199734036e1',
    'src/r66_indic_lexer.vardh': '3633bd55775dc8b9bb94724ef3685976e61d9593',
    'src/r67_stack_pair.vardh': 'e8472bd1cad767cf06b0c00fcf88793419362db5',
    'src/r68_unicode_helpers.vardh': '69103e059634aa6b5b871ce7c06c2f4b9c742ff1',
    'src/r68_diagnostics.vardh': '4e2ec29fe16cda9c0d5762ba340ec75694c6f23d',
    'win/native_host.asm': '66e04838b79a1d1ced99b06e9051b2fecb8b1de8',
    'win/rtblob.vardh': '3cdc4f7916e08930a79e8c277539620ac46264f4',
    'win/winapi.asm': '2c83ab01c776b987c811b67a28458243ec42a92b',
    'win/winio.asm': 'bbdd00d0c84b0778913b48b1eeaa5e99232bbc84',
    'win/winrt.vardh': 'd296c62fd5afd4b820778677865a83d86b1ab613',
    'win/winrt_blob.asm': 'd556399d94cd922906a2249604a6943968fbed9d',
}
# Pin the reviewed extensions in this tool too: a changed JSON lock must not
# override a core pin or silently authorize a different compiler extension.
EXTENSION_PINS = {
    'src/r71_compiler_entry.asm': '6ba05e206556d9b18349b633ac1bda73ac89aab1',
    'src/r71_unsafe_tokens.vardh': 'caf01f1fb6403e34dc9d153882536283b68b8778',
    'src/r71_unsafe_integration.vardh': '697a4fafcd40e2c8c48bd8b9d05dd129e81fd69b',
}


def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def regular(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name:
        raise ValueError('invalid input name')
    p = PurePosixPath(name)
    if (p.is_absolute() or any(x in ('', '..', '.') for x in name.split('/'))
            or '\\' in name or ':' in name or '\0' in name):
        raise ValueError('invalid path ' + name)
    q = root
    for part in p.parts:
        q = q / part
        if q.is_symlink():
            raise ValueError('symlink input ' + name)
    if not q.is_file():
        raise ValueError('missing regular input ' + name)
    return q


def verify(root: Path, pins: dict[str, str]) -> dict:
    if not isinstance(pins, dict) or not pins:
        raise ValueError('empty or invalid pin set')
    observed = {}
    for name, want in pins.items():
        if not isinstance(want, str) or not re.fullmatch(r'[0-9a-f]{40}', want):
            raise ValueError('invalid Git blob pin')
        data = regular(root, name).read_bytes()
        actual = blob(data)
        if actual != want:
            raise ValueError(f'input drift {name}: {actual} != {want}')
        observed[name] = {'git_blob': actual, 'sha256': hashlib.sha256(data).hexdigest(),
                          'bytes': len(data)}
    return observed


def reviewed_lock(root: Path) -> dict:
    lock = json.loads(regular(root, 'tools/r71_source.lock.json').read_text('utf-8'))
    if not isinstance(lock, dict) or lock.get('schema') != 1:
        raise ValueError('unsupported lock schema')
    if lock.get('core_pins') != CORE_PINS:
        raise ValueError('unreviewed core lock')
    if lock.get('extension_pins') != EXTENSION_PINS:
        raise ValueError('unreviewed extension lock')
    return lock


def prepare(root: Path, output: Path) -> dict:
    reviewed_lock(root)
    observed = verify(root, {**CORE_PINS, **EXTENSION_PINS})
    if os.path.lexists(output):
        raise ValueError('refuse existing output')
    data = regular(root, 'src/r71_compiler_entry.asm').read_bytes()
    # Recheck before publishing. Concurrent modification after this check is
    # outside the contract; builds must run from a stable reviewed checkout.
    if blob(data) != EXTENSION_PINS['src/r71_compiler_entry.asm']:
        raise ValueError('entry changed during preparation')
    with output.open('xb') as stream:
        stream.write(data)
    return {'status': 'SOURCE_PREPARED', 'compiler_executed': False,
            'native_status': 'NOT_RUN',
            'core_input_blob': CORE_PINS['src/sutram_compiler.asm'],
            'unchanged_core_output_blob': CORE_PINS['src/sutram_compiler.asm'],
            'output_entry_blob': blob(data),
            'output_entry_sha256': hashlib.sha256(data).hexdigest(),
            'output_entry_bytes': len(data), 'inputs': observed}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(ROOT, args.output), indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, 'R71_PREPARE_REFUSED: ' + str(exc) + '\n')
