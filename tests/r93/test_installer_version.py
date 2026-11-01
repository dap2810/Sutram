#!/usr/bin/env python3
"""R93: tools/check_installer_version.py passes a current installer and fails every stale one.

Builds stand-in installers (bytes, then a payload zip, then bytes - the shape the wizard's incbin gives)
from this tree's win/sutram.exe and checks the verdicts. Last line: "r93 installer gate: N checks, M failed".
"""
import hashlib, io, os, re, subprocess, sys, tempfile, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOL = os.path.join(ROOT, 'tools', 'check_installer_version.py')


def setup_with(d, members, sha=True, sha_text=None):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        for name, data in members.items():
            z.writestr(name, data)
    blob = b'MZ' + b'\0' * 4000 + buf.getvalue() + b'#install script\r\n' * 50
    path = os.path.join(d, 'Sutram-Setup.exe')
    open(path, 'wb').write(blob)
    if sha:
        open(os.path.join(d, 'Sutram-Setup.sha256'), 'w').write(
            sha_text or hashlib.sha256(blob).hexdigest() + ' *Sutram-Setup.exe\n')
    elif os.path.exists(os.path.join(d, 'Sutram-Setup.sha256')):
        os.remove(os.path.join(d, 'Sutram-Setup.sha256'))
    return path


def verdict(path):
    r = subprocess.run([sys.executable, TOOL, '--setup', path], capture_output=True, text=True)
    return r.returncode, r.stdout.strip().splitlines()[-1]


def main():
    exe = open(os.path.join(ROOT, 'win', 'sutram.exe'), 'rb').read()
    v = int(re.search(rb'Sutram 1\.0 \(v(\d+)\)', exe).group(1))
    old = exe.replace(b'Sutram 1.0 (v%d)' % v, b'Sutram 1.0 (v%d)' % (v - 1))
    checks = fails = 0
    with tempfile.TemporaryDirectory() as d:
        cases = [
            ('current, both compilers', {'bin\\sutram.exe': exe, 'win\\sutram.exe': exe}, True, None, 0),
            ('current, no .sha256 file', {'bin/sutram.exe': exe, 'win/sutram.exe': exe}, False, None, 0),
            ('bin compiler one version behind', {'bin\\sutram.exe': old, 'win\\sutram.exe': exe}, True, None, 1),
            ('win compiler one version behind', {'bin\\sutram.exe': exe, 'win\\sutram.exe': old}, True, None, 1),
            ('win compiler missing', {'bin\\sutram.exe': exe}, True, None, 1),
            ('a compiler with no version', {'bin\\sutram.exe': b'MZ', 'win\\sutram.exe': exe}, True, None, 1),
            ('.sha256 of another file', {'bin\\sutram.exe': exe, 'win\\sutram.exe': exe}, True,
             '0' * 64 + ' *Sutram-Setup.exe\n', 1),
        ]
        for name, members, sha, sha_text, want in cases:
            rc, last = verdict(setup_with(d, members, sha, sha_text))
            ok = rc == want and last.startswith('PASS' if want == 0 else 'FAIL')
            checks += 1
            fails += not ok
            print(('PASS  ' if ok else 'FAIL  ') + f'{name}: exit {rc}, {last[:110]}')
        # R95: a tree binary one version behind fails even with a current installer
        repo = os.path.join(d, 'repo')
        for sub in ('src', 'win'):
            os.makedirs(os.path.join(repo, sub), exist_ok=True)
        open(os.path.join(repo, 'src', 'sutram_compiler.asm'), 'wb').write(
            open(os.path.join(ROOT, 'src', 'sutram_compiler.asm'), 'rb').read())
        open(os.path.join(repo, 'sutram_compiler'), 'wb').write(open(os.path.join(ROOT, 'sutram_compiler'), 'rb').read())
        open(os.path.join(repo, 'win', 'sutram.exe'), 'wb').write(exe)
        open(os.path.join(repo, 'sutram.exe'), 'wb').write(old)
        good = setup_with(d, {'bin\\sutram.exe': exe, 'win\\sutram.exe': exe})
        r = subprocess.run([sys.executable, TOOL, '--repo', repo, '--setup', good], capture_output=True, text=True)
        last = r.stdout.strip().splitlines()[-1]
        ok = r.returncode == 1 and 'sutram.exe (in the tree) is v' in last
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + f'tree sutram.exe one version behind: exit {r.returncode}, {last[:110]}')
        rc, last = verdict(os.path.join(d, 'absent.exe'))
        checks += 1
        fails += not (rc == 1 and last.startswith('FAIL no installer'))
        print(('PASS  ' if rc == 1 else 'FAIL  ') + f'no installer at all: exit {rc}, {last[:110]}')
    print(f'r93 installer gate: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
