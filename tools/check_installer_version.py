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

R109: the verdict names WHAT it read. The version is the payload's - the two compilers packed inside
Sutram-Setup.exe - not the wizard's: the wizard (the bytes before the payload) carries no version string of
its own, and the line says so. "payload v243" means the compilers the wizard would install are v243; it
does not mean the wizard is. The payload's packing date and how many of its lib/ and lang/ files differ
from the tree's are reported too (CR/LF ignored). docs/INSTALLER-REBUILD.md is the rebuild procedure.

Last line: "PASS payload vNNN = compiler vNNN (...)" or "FAIL payload vMMM inside Sutram-Setup.exe ...".
Exit 0 on PASS, 1 on FAIL.

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


def payload_bounds(setup):
    """(start, end) of the embedded payload in the installer's bytes, or None."""
    j = setup.rfind(b'PK\x05\x06')
    if j < 0:
        return None
    cd_size, cd_off = struct.unpack('<II', setup[j + 12:j + 20])
    comment = struct.unpack('<H', setup[j + 20:j + 22])[0]
    start = j - cd_size - cd_off
    return (start, j + 22 + comment) if start >= 0 else None


def tree_drift(z, repo):
    """(differ, compared): payload lib/ and lang/ files (under bin/, win/ or the root) against the tree's, CR/LF ignored."""
    differ = compared = 0
    for info in z.infolist():
        n = info.filename.replace('\\', '/')
        if n.endswith('/'):
            continue
        for pre, d in (('bin/lib/', 'lib'), ('win/lib/', 'lib'), ('lib/', 'lib'),
                       ('bin/lang/', 'lang'), ('win/lang/', 'lang'), ('lang/', 'lang')):
            if n.lower().startswith(pre):
                t = os.path.join(repo, d, n[len(pre):])
                if os.path.isfile(t):
                    compared += 1
                    a = z.read(info).replace(b'\r\n', b'\n')
                    b = open(t, 'rb').read().replace(b'\r\n', b'\n')
                    differ += a != b
                break
    return differ, compared


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
    packed = set()
    if z is not None:
        for info in z.infolist():
            key = info.filename.replace('\\', '/').lower()
            if key in ('bin/sutram.exe', 'win/sutram.exe'):
                m = VERSION.search(z.read(info))
                found[key] = int(m.group(1)) if m else None
                packed.add('%04d-%02d-%02d' % info.date_time[:3])
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
    # R109: what the version belongs to. The wizard is the bytes outside the payload.
    b = payload_bounds(setup)
    outside = setup[:b[0]] + setup[b[1]:] if b else setup
    m = VERSION.search(outside)
    wizard = f'the wizard says v{int(m.group(1))}' if m else 'the wizard has no version of its own'
    drift = ''
    if z is not None:
        differ, compared = tree_drift(z, a.repo)
        if compared:
            drift = f'; {differ} of its {compared} lib/lang files differ from the tree'
    vs = sorted({v for v in found.values() if v is not None})
    if not vs:
        payload = 'payload (no compiler version found)'
    elif len(vs) == 1:
        payload = f'payload v{vs[0]}'
    else:
        payload = 'payload ' + ', '.join(f'{k} v{v}' for k, v in sorted(found.items()) if v is not None)
    when = f', packed {"/".join(sorted(packed))}' if packed else ''
    for p in problems:
        print('  ' + p)
    if problems:
        print(f'FAIL {payload} inside Sutram-Setup.exe ({wizard}); compiler v{want}{when}{drift}: '
              f'{"; ".join(problems)} - rebuild the payload on Windows: '
              f'windows\\native-installer\\build-installer.ps1 (docs/INSTALLER-REBUILD.md)')
        return 1
    print(f'PASS {payload} = compiler v{want} (bin/ and win/sutram.exe{when}; {wizard}{drift}; '
          f'sutram_compiler, sutram.exe, win/sutram.exe v{want}; sha256 {digest[:16]}...)')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
