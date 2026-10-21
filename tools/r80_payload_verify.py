#!/usr/bin/env python3
"""Read-only source/build/ZIP/PE consistency gate for the Sutram installer.

No downloads, extraction, compiler replacement, or Windows execution. A PASS
means only the checked artifacts agree; it does not mean Windows acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import struct
import sys
import zipfile
import zlib
from pathlib import Path
from typing import Any

MAX_BYTES = 512 * 1024 * 1024
MAX_FILE = 64 * 1024 * 1024
CORE = 'src/sutram_compiler.asm'
ENTRY = 'src/r68_compiler_entry.asm'
INCLUDE = re.compile(r'^\s*%(?:include|incbin)\s+([^;\r\n]+)', re.M)
RESERVED = re.compile(r'^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', re.I)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def normalized(name: str) -> str:
    """Canonical Windows destination name. Do not extract archive members."""
    name = name.replace('\\', '/')
    parts = name.split('/')
    if (not name or name.startswith('/') or ':' in name or any(
            not p or p in ('.', '..') or p[-1:] in (' ', '.') or
            RESERVED.match(p) or any(ord(c) < 32 for c in p) for p in parts)):
        raise ValueError('unsafe package/source path: ' + repr(name))
    return name


def read_regular(path: Path, limit: int = MAX_FILE) -> bytes:
    path = path.absolute()
    for node in (path, *path.parents):
        if node.is_symlink():
            raise ValueError('symlink/reparse input refused: ' + str(node))
        if node.exists() and getattr(node.lstat(), 'st_file_attributes', 0) & 0x400:
            raise ValueError('reparse input refused: ' + str(node))
    mode = path.stat().st_mode
    if not stat.S_ISREG(mode) or path.stat().st_size > limit:
        raise ValueError('nonregular/oversized input: ' + str(path))
    data = path.read_bytes()
    if len(data) > limit:
        raise ValueError('input grew beyond limit: ' + str(path))
    return data


def source_inputs(root: Path) -> dict[str, dict[str, Any]]:
    raw = read_regular(root / 'tools/r69_build.lock.json')
    lock = json.loads(raw)
    pins = lock.get('pins', {})
    if (lock.get('schema') != 1 or lock.get('entry') != ENTRY or
            not isinstance(pins, dict) or CORE not in pins or ENTRY not in pins):
        raise ValueError('invalid canonical source lock')
    observed = {}
    for name, expected in pins.items():
        if normalized(name) != name or not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{40}', expected):
            raise ValueError('invalid source pin: ' + name)
        data = read_regular(root / name)
        if blob(data) != expected:
            raise ValueError('source drift: ' + name)
        observed[name] = {'git_blob': expected, 'sha256': sha(data), 'bytes': len(data)}
        for match in INCLUDE.finditer(data.decode('utf-8')):
            token = match.group(1).strip()
            if (len(token) < 3 or token[0] not in ('"', "'") or token[-1] != token[0]
                    or token[1:-1] not in pins):
                raise ValueError('unlocked or nonliteral include in ' + name + ': ' + token)
    observed['tools/r69_build.lock.json'] = {'git_blob': blob(raw), 'sha256': sha(raw), 'bytes': len(raw)}
    return observed


def pe_headers(data: bytes) -> tuple[int, list[tuple[int, int, int]]]:
    if len(data) < 64 or data[:2] != b'MZ':
        raise ValueError('not a PE image')
    pe = struct.unpack_from('<I', data, 60)[0]
    if pe < 64 or pe + 26 > len(data) or data[pe:pe + 4] != b'PE\0\0':
        raise ValueError('invalid PE signature')
    machine, sections = struct.unpack_from('<HH', data, pe + 4)
    optional = struct.unpack_from('<H', data, pe + 20)[0]
    if machine != 0x8664 or optional < 112 or pe + 24 + optional > len(data):
        raise ValueError('not bounded PE32+ AMD64')
    if struct.unpack_from('<H', data, pe + 24)[0] != 0x20b:
        raise ValueError('not PE32+')
    start = pe + 24 + optional
    if not 1 <= sections <= 96 or start + 40 * sections > len(data):
        raise ValueError('invalid PE section table')
    rows = []
    for n in range(sections):
        off = start + n * 40
        virtual, _, size, pointer = struct.unpack_from('<IIII', data, off + 8)
        if pointer + size > len(data):
            raise ValueError('section exceeds PE image')
        rows.append((pointer, size, virtual))
    return pe, rows


def embedded_payload(setup: bytes, payload: bytes) -> dict[str, Any]:
    """Resolve real NASM blob_payload symbols; appended decoy ZIPs do not count."""
    pe, sections = pe_headers(setup)
    pointer, count = struct.unpack_from('<II', setup, pe + 12)
    end = pointer + count * 18
    if not pointer or not count or count > 1_000_000 or end + 4 > len(setup):
        raise ValueError('missing/bad COFF symbols; cannot prove embedded payload location')
    length = struct.unpack_from('<I', setup, end)[0]
    if length < 4 or end + length > len(setup):
        raise ValueError('bad COFF string table')
    symbols: dict[str, tuple[int, int]] = {}
    i = 0
    wanted = {'blob_payload', 'blob_payload_end', 'hash_payload'}
    while i < count:
        off = pointer + i * 18
        name = setup[off:off + 8]
        if name[:4] == b'\0' * 4:
            index = struct.unpack_from('<I', name, 4)[0]
            if index < 4 or index >= length:
                raise ValueError('bad COFF symbol name offset')
            stop = setup.find(b'\0', end + index, end + length)
            if stop < 0:
                raise ValueError('unterminated COFF symbol name')
            name = setup[end + index:stop]
        else:
            name = name.split(b'\0', 1)[0]
        decoded = name.decode('ascii', 'replace')
        value, section = struct.unpack_from('<Ih', setup, off + 8)
        aux = setup[off + 17]
        if i + aux >= count:
            raise ValueError('bad auxiliary-symbol count')
        if decoded in wanted:
            if decoded in symbols or not 1 <= section <= len(sections):
                raise ValueError('duplicate or invalid payload symbol: ' + decoded)
            symbols[decoded] = (section, value)
        i += aux + 1
    if set(symbols) != wanted:
        raise ValueError('required payload/hash symbols missing; unstripped candidate needed')
    a, b = symbols['blob_payload'], symbols['blob_payload_end']
    if a[0] != b[0] or b[1] < a[1]:
        raise ValueError('payload span is not within one section')
    pointer, size, _ = sections[a[0] - 1]
    if b[1] > size or b[1] - a[1] != len(payload):
        raise ValueError('embedded payload span differs from checked ZIP')
    if setup[pointer + a[1]:pointer + b[1]] != payload:
        raise ValueError('embedded payload bytes differ from checked ZIP')
    hsection, hvalue = symbols['hash_payload']
    hp, hs, _ = sections[hsection - 1]
    if hvalue + 32 > hs or setup[hp + hvalue:hp + hvalue + 32] != hashlib.sha256(payload).digest():
        raise ValueError('embedded payload hash constant differs')
    return {'offset': pointer + a[1], 'bytes': len(payload), 'sha256': sha(payload)}


def verify(root: Path, compiler: Path, report_path: Path, payload_path: Path,
           setup_path: Path | None = None) -> dict[str, Any]:
    inputs = source_inputs(root)
    built = read_regular(compiler)
    pe_headers(built)
    report_raw = read_regular(report_path)
    report = json.loads(report_raw)
    wanted_inputs = {k: v for k, v in inputs.items() if k != 'tools/r69_build.lock.json'}
    if (report.get('status') != 'BUILT_FORMAT_CHECKED' or report.get('target') != 'windows'
            or report.get('mode') != 'default' or report.get('entry') != ENTRY
            or report.get('binary_sha256') != sha(built)
            or report.get('inputs') != wanted_inputs):
        raise ValueError('canonical build report does not match current source and compiler bytes')
    payload_raw = read_regular(payload_path, MAX_BYTES)
    # Open the exact bytes hashed above, not a second pathname that can change.
    import io
    with zipfile.ZipFile(io.BytesIO(payload_raw)) as archive:
        files: dict[str, zipfile.ZipInfo] = {}
        seen = set()
        total = 0
        for info in archive.infolist():
            raw_name = info.orig_filename
            name = normalized(raw_name[:-1] if raw_name.endswith('/') else raw_name)
            key = name.casefold()
            if key in seen:
                raise ValueError('duplicate/case-colliding ZIP entry: ' + name)
            seen.add(key)
            mode = stat.S_IFMT(info.external_attr >> 16)
            if mode not in (0, stat.S_IFREG, stat.S_IFDIR) or info.flag_bits & 1:
                raise ValueError('nonregular/encrypted ZIP entry: ' + name)
            if info.is_dir():
                continue
            if info.file_size > MAX_FILE:
                raise ValueError('oversized ZIP entry: ' + name)
            total += info.file_size
            if total > MAX_BYTES:
                raise ValueError('ZIP expansion budget exceeded')
            files[name] = info
        file_keys = {name.casefold() for name in files}
        for name in files:
            parts = name.casefold().split('/')
            if any('/'.join(parts[:i]) in file_keys for i in range(1, len(parts))):
                raise ValueError('file/directory ZIP path conflict: ' + name)
        manifest_name = 'payload.manifest.sha256'
        if manifest_name not in files:
            raise ValueError('payload manifest missing')
        manifest = archive.read(files[manifest_name])
        declared: dict[str, str] = {}
        for line in manifest.decode('utf-8-sig').splitlines():
            match = re.fullmatch(r'([0-9a-fA-F]{64}) \*(.+)', line)
            if not match:
                raise ValueError('malformed manifest row')
            name = normalized(match[2])
            if name.casefold() in declared or name == manifest_name:
                raise ValueError('duplicate/self-referential manifest entry')
            declared[name.casefold()] = match[1].lower()
        if set(declared) != {n.casefold() for n in files if n != manifest_name}:
            raise ValueError('manifest and archive file sets differ')
        compiler_hashes = {}
        for name, info in files.items():
            data = archive.read(info)
            if len(data) != info.file_size:
                raise ValueError('ZIP member size mismatch: ' + name)
            if name != manifest_name and sha(data) != declared[name.casefold()]:
                raise ValueError('payload manifest hash mismatch: ' + name)
            if name in ('bin/sutram.exe', 'win/sutram.exe'):
                if data != built:
                    raise ValueError('stale payload compiler bytes: ' + name)
                compiler_hashes[name] = sha(data)
        if len(compiler_hashes) != 2:
            raise ValueError('both payload compiler copies are required')
    result = {'status': 'PASS', 'scope': 'source_build_payload_consistency',
              'native_windows_acceptance': 'NOT_RUN', 'source_inputs': wanted_inputs,
              'source_lock_sha256': inputs['tools/r69_build.lock.json']['sha256'],
              'build_report_sha256': sha(report_raw), 'compiler_sha256': sha(built),
              'payload_sha256': sha(payload_raw), 'manifest_sha256': sha(manifest),
              'payload_files': len(files), 'payload_compilers': compiler_hashes,
              'installer_sha256': None, 'embedded_payload': None}
    if setup_path is not None:
        setup = read_regular(setup_path, MAX_BYTES)
        result['embedded_payload'] = embedded_payload(setup, payload_raw)
        result['installer_sha256'] = sha(setup)
    if source_inputs(root) != inputs or read_regular(compiler) != built:
        raise ValueError('source or compiler changed during verification')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--build-report', type=Path, required=True)
    parser.add_argument('--payload', type=Path, required=True)
    parser.add_argument('--setup', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    # Never permit a report pathname to overwrite an input, including failures.
    stream = args.report.open('x', encoding='utf-8') if args.report else None
    try:
        try:
            result = verify(args.repo, args.compiler, args.build_report, args.payload, args.setup)
            code = 0
        except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, struct.error, zlib.error, RuntimeError) as exc:
            result = {'status': 'FAIL', 'scope': 'source_build_payload_consistency',
                      'native_windows_acceptance': 'NOT_RUN', 'reason': str(exc)}
            code = 2
        text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        print(text, end='')
        if stream:
            stream.write(text)
        return code
    finally:
        if stream:
            stream.close()


if __name__ == '__main__':
    raise SystemExit(main())
