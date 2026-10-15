#!/usr/bin/env python3
"""Verify exact R68 review inputs and stage the NASM entry, without rewriting main.

The output is a complete entry WRAPPER, not an expanded 545-KiB compiler source.
Build from repository root: nasm -f elf64 -I. /tmp/r68-entry.asm -o /tmp/r68.o
This tool never installs tools, fetches data, starts CI, or assembles the compiler.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER_BLOB = '64ea028a5ccf56117c132a7efd0673cbe2df3fc6'

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def verify_inputs(root: Path, pins: dict[str, str]) -> dict[str, str]:
    observed = {}
    for name, wanted in pins.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('unsafe locked path: ' + name)
        resolved = (root / relative).resolve()
        if not resolved.is_relative_to(root.resolve()):
            raise ValueError('locked input escapes repository: ' + name)
        actual = git_blob(resolved.read_bytes())
        if actual != wanted:
            raise ValueError(f'input drift: {name}: expected {wanted}, got {actual}')
        observed[name] = actual
    return observed

def stage(root: Path, output: Path, pins: dict[str, str]) -> dict[str, object]:
    observed = verify_inputs(root, pins)
    output = output.resolve()
    if output in {(root / name).resolve() for name in pins}:
        raise ValueError('output must not overwrite any review input')
    content = (root / 'src/r68_compiler_entry.asm').read_bytes()
    with output.open('xb') as f:
        f.write(content)
    return {'input_compiler_git_blob': observed['src/sutram_compiler.asm'],
            'entry_output_git_blob': git_blob(content),
            'entry_output_sha256': hashlib.sha256(content).hexdigest(),
            'entry_output_bytes': len(content),
            'output_kind': 'NASM entry wrapper; includes the pinned inherited compiler',
            'expanded_compiler_source_git_blob': None,
            'native_assembly_run': False, 'verified_inputs': observed}

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    try:
        pins = json.loads((ROOT / 'tools/r68_review.lock.json').read_text('utf-8'))
        if pins.get('src/sutram_compiler.asm') != COMPILER_BLOB:
            raise ValueError('compiler pin in lock does not match this review')
        result = stage(ROOT, args.output, pins)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        p.exit(2, 'R68_PREPARE_REFUSED: ' + str(exc) + '\n')
    print(json.dumps(result, indent=2))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
