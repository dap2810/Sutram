#!/usr/bin/env python3
"""Stage a hash-checked R76 v183-Sanskrit Linux kosh-reclamation compiler, without editing input.

This is a source preparation tool, not a replacement parser/compiler/backend.
The stage contains the inherited NASM compiler with three call sites added and
one inline helper body appended. Every inherited include is copied and pinned.
NASM/native Sutram acceptance is a separate mandatory operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE = 'src/sutram_compiler.asm'
ENTRY = 'src/r68_compiler_entry.asm'
PAYLOAD = 'src/r75_kosh_reclaim.inc'
PINS = {
    CORE: 'cc5cfbe48ac3ea1360958cb8f203385744d094b8',
    'src/r66_indic_lexer.inc': '998b6cb75a7e11cf6d488cf84a84a2154ffdebf0',
    'src/r67_stack_pair.inc': 'e8472bd1cad767cf06b0c00fcf88793419362db5',
    'src/r68_unicode_helpers.inc': '69103e059634aa6b5b871ce7c06c2f4b9c742ff1',
    'src/r68_diagnostics.inc': 'a6f7bb196702626d6b7f116f32e678d9daf73eba',
    ENTRY: '42389aaf73179726d91e23359aee2199734036e1',
    'win/native_host.asm': '66e04838b79a1d1ced99b06e9051b2fecb8b1de8',
    'win/rtblob.inc': 'f855c01ed63d673c41ac0ca9bde2d99cb5654f99',
    'win/winapi.asm': '2c83ab01c776b987c811b67a28458243ec42a92b',
    'win/winio.asm': 'bbdd00d0c84b0778913b48b1eeaa5e99232bbc84',
    'win/winrt.inc': '9e73bd45cf0b1f2fbd0f86452d8e9fcaf5fb8b37',
    'win/winrt_blob.asm': '69a4618028e9c6ac16af4b3a389854962227b69c',
    'win/pe_layout.inc': 'acf9933226a44fcb325c22cb855a806206ec69a3',
    'win/pe_imports.inc': 'fc8491c6192d34058f6ac7c9a203fa335bec04cc',
    PAYLOAD: 'e9a6f5d02f2b4c98343de6f85c3442ab8890d59a',
}
BEGIN = b'.ge_call_koshpush:\n'
END = b'.ge_call_koshpush_param_bad:\n'
GROWTH = b'    ; newcap = cap ? cap*2 : 4\n'
ALLOCATE = b'    call emit_nirmmita_from_rax\n'
PUBLISH = (b'    call emit_store_named_var\n'
           b'    mov dil, 0x4D             ; mov r8,r10\n')


def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def describe(data: bytes) -> dict[str, Any]:
    return {'git_blob': blob(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'bytes': len(data)}


def regular_read(root: Path, relative: str) -> bytes:
    parts = PurePosixPath(relative)
    if (parts.is_absolute() or any(p in ('', '.', '..') for p in relative.split('/'))
            or '\\' in relative or ':' in relative):
        raise ValueError('invalid relative source path: ' + relative)
    path = root.absolute()
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink():
            raise ValueError('symlink source root')
    for part in parts.parts:
        path /= part
        if path.is_symlink():
            raise ValueError('symlink source input: ' + relative)
    st = path.stat()
    if not stat.S_ISREG(st.st_mode):
        raise ValueError('nonregular source input: ' + relative)
    return path.read_bytes()


def patch_core(core: bytes, helper: bytes) -> bytes:
    """Exact source transformation; caller must validate complete input identities."""
    if b'\r' in core or b'\0' in core or b'\0' in helper:
        raise ValueError('unsupported source encoding/line endings')
    core.decode('utf-8', 'strict')
    helper.decode('utf-8', 'strict')
    if b'r71_emit_kosh_reclaim' in core:
        raise ValueError('reclamation already present or conflicting source')
    if core.count(BEGIN) != 1 or core.count(END) != 1:
        raise ValueError('missing/duplicate kosh-push scope')
    lo, hi = core.index(BEGIN), core.index(END)
    if lo >= hi:
        raise ValueError('reversed kosh-push scope')
    region = core[lo:hi]
    for anchor in (GROWTH, ALLOCATE, PUBLISH):
        if region.count(anchor) != 1:
            raise ValueError('missing/duplicate growth transformation anchor')
    if not region.index(GROWTH) < region.index(ALLOCATE) < region.index(PUBLISH):
        raise ValueError('unexpected allocation/publish order')
    region = region.replace(GROWTH, b'    call r71_emit_kosh_growth_guard\n' + GROWTH)
    region = region.replace(ALLOCATE, ALLOCATE + b'    call r71_emit_kosh_allocation_guard\n')
    region = region.replace(PUBLISH, b'    call emit_store_named_var\n'
                            b'    call r71_emit_kosh_reclaim\n'
                            b'    mov dil, 0x4D             ; mov r8,r10\n')
    return core[:lo] + region + core[hi:] + b'\n; R71 revised WS2 helper, inlined at preparation.\n' + helper


def verified_inputs(root: Path) -> dict[str, bytes]:
    result = {}
    for name, expected in PINS.items():
        data = regular_read(root, name)
        actual = blob(data)
        if actual != expected:
            raise ValueError(f'source drift: {name}: expected {expected}, got {actual}')
        result[name] = data
    return result


def stage_sources(root: Path, stage: Path, experimental_unsafe_alias: bool = False) -> dict[str, Any]:
    """Validate all source bytes before creating a new, private stage directory."""
    if not experimental_unsafe_alias:
        raise ValueError('EXPERIMENTAL: raw pointers into old kosh buffers become invalid; explicit --experimental-unsafe-alias is required')
    root, stage = root.absolute(), stage.absolute()
    if os.path.lexists(stage):
        raise ValueError('stage must not already exist (including symlinks)')
    for ancestor in (stage.parent, *stage.parent.parents):
        if ancestor.is_symlink():
            raise ValueError('symlink output ancestor')
    if not stage.parent.is_dir():
        raise ValueError('stage parent must already exist')
    inputs = verified_inputs(root)
    updated = patch_core(inputs[CORE], inputs[PAYLOAD])
    outputs = {name: data for name, data in inputs.items() if name != PAYLOAD}
    outputs[CORE] = updated
    # Recheck before writing; no network, assembly, compiler or user program run.
    if verified_inputs(root) != inputs:
        raise ValueError('inputs changed during preparation')
    report = {
        'status': 'SOURCES_STAGED', 'native_status': 'NOT_RUN', 'compiler_executed': False,
        'source_root': str(root), 'stage': str(stage), 'entry': ENTRY,
        'input_compiler': describe(inputs[CORE]), 'output_compiler': describe(updated),
        'inputs': {p: describe(b) for p, b in inputs.items()},
        'outputs': {p: describe(b) for p, b in outputs.items()},
        'target_scope': 'Experimental Linux ELF; kosh-push PE emission deliberately rejected',
        'alias_safety': 'UNPROVEN; do not merge as default',
        'notes': ['Source identity is not executable correctness.',
                  'Run NASM from the stage CWD to select the staged compiler.',
                  'Inherited source locks need reviewed updates before integration.'],
    }
    stage.mkdir(mode=0o700)
    for name, data in outputs.items():
        destination = stage / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as f:
            f.write(data)
    with (stage / 'SOURCE-IDENTITIES.json').open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--stage', type=Path, required=True)
    p.add_argument('--experimental-unsafe-alias', action='store_true',
                   help='Required opt-in: reclamation is not proven safe for outstanding raw aliases')
    args = p.parse_args()
    try:
        print(json.dumps(stage_sources(args.root, args.stage, args.experimental_unsafe_alias), indent=2))
    except (OSError, ValueError) as exc:
        p.exit(2, 'R76_RECLAIM_PREPARE_REFUSED: ' + str(exc) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
