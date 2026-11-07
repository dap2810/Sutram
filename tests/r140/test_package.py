#!/usr/bin/env python3
"""R140: one exact package - the manifest checked against the embedded ZIP, the payload's text LF, every payload
source LF in every checkout, and the package's bytes independent of when or where the tree was checked out.

ChatGPT's release condition 3, and the v309 Windows run's Task C: the checked-in package was internally valid,
but a Windows checkout's README.md and docs/LANGUAGE-REFERENCE.md differed from it by CRLF alone (the root
.gitattributes had no rule for *.md), and a package built from such a checkout replaced 153 unchanged files on
upgrade. Checked here, on the built Sutram-Setup.exe (not the working tree):

  1. the embedded payload.zip's manifest lists every entry once, and every entry's bytes hash to its line;
  2. no text entry (.md .html .txt .out .exit .sm .smlib .lang .sandesh) contains CR LF;
  3. every entry equals the tree's file it was made from, byte for byte (on a Linux checkout);
  4. every payload text path has eol=lf in .gitattributes (git check-attr), so a Windows checkout gives the bytes;
  5. every ZIP entry has the fixed date 1980-01-01 00:00 (no checkout time in the package);
  6. Sutram-Setup.sha256 is the setup's hash.
Building twice from trees with different file times gives the same Sutram-Setup.exe: the R140 hand-back records
it (it needs Wine for the wizard's self-test, so it is not run by this gate).
Last line: "r140 package: N checks, M failed".
"""
import hashlib, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from check_installer_version import embedded_payload  # noqa: E402

TEXT = ('.md', '.html', '.txt', '.out', '.exit', '.sm', '.smlib', '.lang', '.sandesh')
TREE = {'bin/sutram.exe': 'win/sutram.exe', 'win/sutram.exe': 'win/sutram.exe', 'bin/sutram-link.exe': 'sutram-link.exe',
        'assets/sutram.ico': 'icons/sutram.ico'}


def source_of(name):
    if name in TREE:
        return TREE[name]
    for pre in ('bin/', 'win/'):
        if name.startswith(pre):
            return name[len(pre):]
    return name


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    setup = open(os.path.join(ROOT, 'Sutram-Setup.exe'), 'rb').read()
    z = embedded_payload(setup)
    infos = [i for i in z.infolist() if not i.filename.endswith(('/', '\\'))]
    names = {i.filename.replace('\\', '/'): i for i in infos}
    man = z.read([i.filename for i in infos if i.filename.endswith('payload.manifest.sha256')][0]).decode('utf-8')
    lines = {}
    dup = 0
    for l in man.replace('\r\n', '\n').split('\n'):
        if not l:
            continue
        h, n = l.split(' *', 1)
        n = n.replace('\\', '/')
        dup += n in lines
        lines[n] = h.lower()
    entries = {n for n in names if n != 'payload.manifest.sha256'}
    check(dup == 0 and set(lines) == entries,
          f'the manifest lists every entry once ({len(lines)} lines, {len(entries)} entries, {dup} duplicates, '
          f'{len(entries ^ set(lines))} unmatched)')
    wrong = [n for n in entries if n in lines and hashlib.sha256(z.read(names[n])).hexdigest() != lines[n]]
    check(not wrong, f'every embedded entry hashes to its manifest line ({len(entries) - len(wrong)}/{len(entries)}; {wrong[:3]})')
    crlf = [n for n in entries if n.lower().endswith(TEXT) and b'\r\n' in z.read(names[n])]
    check(not crlf, f'no text entry contains CR LF ({len(crlf)}: {crlf[:3]})')
    differ, missing = [], []
    for n in sorted(entries):
        if n == 'sutram-ide-gui.exe':
            src = 'sutram-ide-gui.exe'
        else:
            src = source_of(n)
        p = os.path.join(ROOT, src)
        if not os.path.exists(p):
            missing.append(n)
        elif open(p, 'rb').read() != z.read(names[n]):
            differ.append(n)
    check(not differ and not missing, f'every entry equals the tree file it was made from ({len(entries) - len(differ) - len(missing)}'
          f'/{len(entries)}; differ {differ[:3]}, no source {missing[:3]})')
    texts = sorted({source_of(n) for n in entries if n.lower().endswith(TEXT)})
    try:
        out = subprocess.run(['git', 'check-attr', 'eol', '--'] + texts, cwd=ROOT, capture_output=True, text=True).stdout
        notlf = [l.split(':')[0] for l in out.splitlines() if not l.endswith(': lf')]
        check(len(out.splitlines()) == len(texts) and not notlf,
              f'every payload text path is eol=lf in .gitattributes ({len(texts) - len(notlf)}/{len(texts)}; {notlf[:3]})')
    except OSError:
        print('NOT RUN  git is not available for check-attr')
    dated = [i.filename for i in infos if i.date_time != (1980, 1, 1, 0, 0, 0)]
    check(not dated, f'every ZIP entry has the fixed date 1980-01-01 ({len(dated)} do not: {dated[:2]})')
    shaf = os.path.join(ROOT, 'Sutram-Setup.sha256')
    if os.path.exists(shaf):
        check(open(shaf).read().split()[0].lower() == hashlib.sha256(setup).hexdigest(), 'Sutram-Setup.sha256 is the setup\'s hash')
    print(f'r140 package: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
