#!/usr/bin/env python3
"""tools/check_installer_version.py - the installer must carry the compiler it ships (R93).

WHY: the checked-in Sutram-Setup.exe fell behind the compiler twice (v243 while the compiler was v279,
then v281) and nothing failed. A release gate that does not look at the installer cannot catch that.

WHAT: opens Sutram-Setup.exe, finds the embedded payload.zip (the wizard incbins it), reads the version
string ("Sutram 1.0 (vNNN)") of bin/sutram.exe and win/sutram.exe inside it, and compares both with the
compiler version in src/sutram_compiler.asm (msg_version). R95: the tree's own sutram_compiler (Linux ELF),
sutram.exe and win/sutram.exe (Windows PE) must carry that version too - every binary prints it with
--version, and the string is in each file. It also checks that Sutram-Setup.sha256, when
present, is the SHA-256 of Sutram-Setup.exe - the hash the maintainer verifies after installing.

The embedded compiler's BYTES are not compared with win/sutram.exe: the installer's compiler is built on
Windows, and that toolchain's bytes differ from the Linux cross-build in the tree. The version must match.

Last line: "PASS installer vNNN = compiler vNNN (...)" or "FAIL ...". Exit 0 on PASS, 1 on FAIL.

Usage: python3 tools/check_installer_version.py [--setup PATH] [--repo DIR]
"""
import argparse
import hashlib
import io
import os
import re
import struct
import sys
import zipfile

VERSION = re.compile(rb'Sutram 1\.0 \(v(\d+)\)')


def compiler_version(repo):
    src = open(os.path.join(repo, 'src', 'sutram_compiler.asm'), 'rb').read()
    m = re.search(rb'msg_version[^\n]*\(v(\d+)\)', src)
    if not m:
        raise SystemExit('FAIL no "(vNNN)" in msg_version in src/sutram_compiler.asm')
    return int(m.group(1))


def embedded_payload(setup):
    """The payload.zip the wizard embeds: located from its end-of-central-directory record."""
    j = setup.rfind(b'PK\x05\x06')
    if j < 0:
        return None
    cd_size, cd_off = struct.unpack('<II', setup[j + 12:j + 20])
    comment = struct.unpack('<H', setup[j + 20:j + 22])[0]
    start = j - cd_size - cd_off
    if start < 0:
        return None
    return zipfile.ZipFile(io.BytesIO(setup[start:j + 22 + comment]))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--setup', default=None)
    a = ap.parse_args(argv)
    path = a.setup or os.path.join(a.repo, 'Sutram-Setup.exe')
    want = compiler_version(a.repo)
    if not os.path.exists(path):
        print(f'FAIL no installer at {path} (compiler is v{want})')
        return 1
    setup = open(path, 'rb').read()
    problems = []
    z = None
    try:
        z = embedded_payload(setup)
    except (zipfile.BadZipFile, struct.error) as e:
        problems.append(f'the embedded payload is not a readable zip ({e})')
    found = {}
    if z is not None:
        for name in z.namelist():
            key = name.replace('\\', '/').lower()
            if key in ('bin/sutram.exe', 'win/sutram.exe'):
                m = VERSION.search(z.read(name))
                found[key] = int(m.group(1)) if m else None
        for key in ('bin/sutram.exe', 'win/sutram.exe'):
            if key not in found:
                problems.append(f'{key} is not in the payload')
            elif found[key] is None:
                problems.append(f'{key} has no version string')
            elif found[key] != want:
                problems.append(f'{key} is v{found[key]}')
    elif not problems:
        problems.append('no embedded payload found')
    # R95: the binaries in the tree must be the same version as the source and the installer.
    tree = {}
    for rel in ('sutram_compiler', 'sutram.exe', 'win/sutram.exe'):
        f = os.path.join(a.repo, rel)
        if not os.path.exists(f):
            problems.append(f'{rel} is missing')
            continue
        m = VERSION.search(open(f, 'rb').read())
        tree[rel] = int(m.group(1)) if m else None
        if tree[rel] is None:
            problems.append(f'{rel} has no version string')
        elif tree[rel] != want:
            problems.append(f'{rel} (in the tree) is v{tree[rel]}')
    digest = hashlib.sha256(setup).hexdigest()
    sha_file = os.path.join(os.path.dirname(path), 'Sutram-Setup.sha256')
    if os.path.exists(sha_file):
        recorded = open(sha_file, encoding='utf-8', errors='replace').read().split()
        if not recorded or recorded[0].lower() != digest:
            problems.append(f'Sutram-Setup.sha256 says {recorded[0][:12] if recorded else "nothing"}..., '
                            f'the file is {digest[:12]}...')
    for p in problems:
        print('  ' + p)
    shown = ', '.join(f'{k} v{v}' for k, v in sorted(found.items()) if v is not None)
    if problems:
        print(f'FAIL installer ({shown or "no compiler found"}), compiler v{want}: {"; ".join(problems)} - '
              f'rebuild it on Windows: windows/build-windows-setup.ps1')
        return 1
    print(f'PASS installer v{want} = compiler v{want} ({shown}; sutram_compiler, sutram.exe, win/sutram.exe '
          f'v{want}; sha256 {digest[:16]}...)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
