#!/usr/bin/env python3
"""R159 no personal paths (Sarvam ROUND-164 WS2, ROUND-165 WS3; the owner's standing instruction, 9 November 2026).

The repository is public. No tracked file may carry the owner's system details, or a build machine's:

  home      a home folder by name: C:<sep>Users<sep><name> with any separator (one backslash, two, a slash, the
            long-path prefix), /mnt/c/Users/<name>, /home/<name>, /Users/<name>, and anything under /root - a
            placeholder (<you>, %USERPROFILE%, $HOME, {user}, &lt;x&gt;) and the shared folders (Public, Default)
            are not names
  drive     a drive letter other than C: starting a path (the owner's projects drive, another drive, Wine's Z:)
  machine   a build machine's own folder: Claude's cloud scratch (/tmp/claude-<n>, its -home-<user> folder name),
            ChatGPT's /workspace/scratch/<id>
  account   a PowerShell transcript's user and computer lines with a value, and the COMPUTERNAME, USERDOMAIN and
            USERNAME variables set to one
  name      the owner's account, computer and projects-folder names, as words, in text and in binary files. They
            are not written here: each word of the tree is compared by its SHA-256 (lower case). A SHA-256 of a
            short word can be reversed by trying every word, so this hides the names from a reader and a search
            engine, not from an attacker - who has them anyway in the history (`git log -p`), which this gate does
            not and cannot clean.
  build     an operating-system build number: "build <five digits>", 10.0.<build>, PowerShell 5.1.<build>.<n>
  hardware  a CPU model name

It decodes UTF-16 text (a BOM, or a NUL in every other byte) and JSON-style \\u escapes before it reads, reads a binary
for the names as ASCII and as UTF-16, applies every check to each file name too, never prints a name it found (a file
whose name matches is shown by its number), and fails if any tracked file cannot be read. It reports the known
identifiers and the policy forms apart: neither is a proof that nothing else is there.
What it cannot see: text inside an image, inside a compressed archive or an installer's payload, in an encoding other
than UTF-8 / UTF-16, and anything only in history.
The self-test builds every forbidden form at run time (none is written in this file) and requires each to fail and
its placeholder form to pass. Usage: python3 tests/r159/test_no_personal_paths.py [--root DIR]
Exit 0: none found. 1: found (each file, line and kind is printed; the matched text is not).
"""
import hashlib
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
# SHA-256 of the lower-case word -> what it names (tools/normalize_personal_paths.py uses the same table)
NAME_HASHES = {
    '0c2bb9f47411027052d559f61a4f281f4367df5dd211c011cb9279d6bb177901': 'account',
    '0b3659243e3eb91cd2da518ebbad79997209e1284fe70756b3e8b8bc8701ac83': 'machine',
    'a9472bb71c9036d21da0068e0ba0c91f7d2342022b6ec9b20ad51497e9f63c88': 'projects',
}
NAME_LENGTHS = {5, 15}
SEP = rb'(?:\\\\|\\|/)'
PLACE = rb'(?![<%${]|&lt;|\.\.\.|\*|(?i:public|default|all users)\b)'
PATTERNS = [
    ('home', re.compile(rb'(?i)(?<![A-Za-z0-9])[a-z]:' + SEP + rb'users' + SEP + PLACE + rb'[A-Za-z0-9_.~-]{1,40}')),
    ('home', re.compile(rb'(?i)/mnt/[a-z]/users/' + PLACE + rb'[A-Za-z0-9_.-]+')),
    ('home', re.compile(rb'(?<![\w.~-])/home/' + PLACE + rb'[A-Za-z0-9_.-]+')),
    ('home', re.compile(rb'(?<![\w.~:-])/Users/' + PLACE + rb'[A-Za-z0-9_.-]+')),
    ('home', re.compile(rb'(?<![\w/.~-])/root/[A-Za-z0-9_.-]')),
    ('drive', re.compile(rb'(?<![A-Za-z0-9%$\\])[D-Zd-z]:' + SEP + rb'[A-Za-z0-9_.$-]')),
    ('machine', re.compile(rb'/tmp/claude-[0-9]|-home-' rb'claude\b|/workspace/scratch/[0-9a-f]{6,}')),
    ('account', re.compile(rb'(?m)\b(?:Username|RunAs User): +(?![<%(\[\'"`]|&lt;)\S|\bMachine: +(?![<%]|&lt;)[A-Za-z0-9-]{2,15} +\(Microsoft Windows'
                           rb'|^\s*(?:COMPUTERNAME|USERDOMAIN|USERNAME)=(?![<%]|&lt;)\S')),
    ('build', re.compile(rb'(?i)\bbuild\s+2[0-9]{4}\b|\b10\.0\.2[0-9]{4}\b|\b5\.1\.2[0-9]{4}\.[0-9]+\b')),
    ('build', re.compile(rb'(?i)\b[0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?-(?:microsoft-standard-WSL2|fc-v[0-9]+)\b'
                         rb'|\b(?:linux|kernel)[ -]+[0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?-[A-Za-z0-9._-]+')),
    ('hardware', re.compile(rb'(?i)\bryzen\s+[0-9]|intel\(r\)\s+core|\bcore\(tm\)\s+i[0-9]|\bgeforce\s+[a-z]*\s*[0-9]|\bradeon\s+rx')),
    # an IPv4 address other than unspecified, loopback, broadcast and the documentation ranges, and not a version
    ('address', re.compile(rb'(?<![\w.])(?<!ersion: )(?<!ersion )(?<!v)(?!0\.0\.0\.0|127\.|255\.255\.255\.255|192\.0\.2\.|198\.51\.100\.|203\.0\.113\.)'
                           rb'(?:(?:25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])(?![\w.-])')),
    ('address', re.compile(rb'(?<![\w:-])[0-9A-Fa-f]{2}([:-])[0-9A-Fa-f]{2}(?:\1[0-9A-Fa-f]{2}){4}(?![\w:-])')),
]
WORD = re.compile(rb'[A-Za-z0-9_]+')


def names_in(b):
    out = []
    for m in WORD.finditer(b):
        w = m.group(0)
        if len(w) in NAME_LENGTHS and hashlib.sha256(w.lower()).hexdigest() in NAME_HASHES:
            out.append((m.start(), NAME_HASHES[hashlib.sha256(w.lower()).hexdigest()]))
    return out


UNESCAPE = re.compile(rb'\\u([0-9a-fA-F]{4})')


def text_forms(b):
    """The forms of a file the patterns read: (forms, binary). UTF-16 (a BOM, or a NUL in every other byte) is
    decoded; a JSON-style \\uXXXX escape is decoded into a second form. A file that is neither is binary: it is
    read for the names only, as ASCII and as UTF-16."""
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        t = b.decode('utf-16', 'replace').encode('utf-8')
    elif len(b) >= 4 and b'\0' in b[:8000] and b[1:8000:2].count(0) > 0.9 * len(b[1:8000:2]):
        t = b.decode('utf-16-le', 'replace').encode('utf-8')
    elif b'\0' in b[:8000]:
        return [b] + [b[k:].decode('utf-16-le', 'ignore').encode('utf-8', 'ignore') for k in (0, 1)], True
    else:
        t = b
    forms = [t]
    if UNESCAPE.search(t):
        forms.append(UNESCAPE.sub(lambda m: chr(int(m.group(1), 16)).encode('utf-8', 'replace'), t))
    return forms, False


def scan(b, binary=None):
    """Every (position, kind) found in a file's bytes. `binary` is ignored: the bytes decide (kept for callers)."""
    forms, is_bin = text_forms(b)
    found = set()
    for t in forms:
        found |= {(pos, 'name ' + kind) for pos, kind in names_in(t)}
        if not is_bin:
            for kind, rx in PATTERNS:
                found |= {(m.start(), kind) for m in rx.finditer(t)}
    return sorted(found)


def mask(b, pos):
    """Nothing of the matched text: printing it would put it in every log that keeps this gate's output."""
    return 'text not shown'


def self_test():
    bs, fs = '\\', '/'
    bad = ['C:' + bs + 'Users' + bs + 'alice' + bs + 'AppData', 'C:' + bs * 2 + 'Users' + bs * 2 + 'alice',
           'c:' + fs + 'users' + fs + 'alice', fs + 'home' + fs + 'alice' + fs + 'x', fs + 'mnt/c/Users/alice',
           'E:' + bs + 'Projects' + bs + 'Sutram', 'Z:' + bs * 2 + 'tmp' + bs * 2 + 'x', fs + 'tmp' + fs + 'claude-0/x',
           'Username: ' + 'HOST' + bs + 'alice', 'Machine: ' + 'HOST (Microsoft Windows NT)', 'Windows 11 build ' + '26300',
           'PowerShell 5.1.' + '26100.9711', 'AMD ' + 'Ry' + 'zen 7 7700X', fs + 'root' + fs + '.cache',
           'e:' + bs + 'projects' + bs + 'x', 'kernel ' + '6.6.87' + '.2-microsoft-standard-WSL2', 'Linux ' + '6.18' + '.44-fc-v310',
           'host ' + '192.168.' + '1.20', 'mac ' + '00:1A:2B:' + '3C:4D:5E', 'C:' + bs + 'u005cUsers' + bs + 'u005calice']
    bad_utf16 = ['C:' + bs + 'Users' + bs + 'alice' + bs + 'x', 'E:' + bs + 'Projects']
    good = ['%USERPROFILE%' + bs + 'AppData', 'C:' + bs + 'Users' + bs + '<you>' + bs + 'x', 'C:' + bs + 'Users' + bs + 'Public',
            '<repo>' + bs + 'win', fs + 'home' + fs + '<anything>', 'C:' + bs + 'Program Files' + bs + 'x',
            'Username: <user>', 'Machine: Advanced Micro Devices X86-64', 'Windows 11 build (redacted)', 'no `E:' + bs + '`, no `D:' + bs + '`',
            'noun' + fs + 'root' + fs + 'compound', 'https://github.com/dap2810/Sutram', 'C:' + bs + 'Sutram' + bs + 'bin',
            'bind ' + '127.0.0.1', 'address ' + '0.0.0.0', 'SerializationVersion: ' + '1.1.' + '0.1', 'v' + '1.2.' + '3.4',
            'a' + bs + 'n:' + bs + 'n2', 'Windows NT 10.0 (build redacted)']
    ok = True
    for s in bad:
        if not scan(s.encode(), False):
            print('FAIL  self-test: not caught: ' + s); ok = False
    for s in good:
        if scan(s.encode(), False):
            print('FAIL  self-test: a placeholder was caught: ' + s); ok = False
    for s in bad_utf16:
        if not scan(s.encode('utf-16'), False):
            print('FAIL  self-test: not caught in UTF-16: ' + s); ok = False
    # the name check, with a stand-in word added for the test only
    test_word = 'qz' + 'xwv'
    NAME_HASHES[hashlib.sha256(test_word.encode()).hexdigest()] = 'test'
    if not scan(('path ' + test_word.upper() + ' here').encode(), True):
        print('FAIL  self-test: a name by hash not caught (binary)'); ok = False
    if not scan(b'\x00\x01\x02' + ('path ' + test_word + ' here').encode('utf-16-le'), True):
        print('FAIL  self-test: a name by hash not caught (UTF-16 inside a binary)'); ok = False
    del NAME_HASHES[hashlib.sha256(test_word.encode()).hexdigest()]
    print(('PASS' if ok else 'FAIL') + f'  self-test: {len(bad) + len(bad_utf16)} forbidden forms caught ({len(bad_utf16)} in UTF-16), '
          f'{len(good)} placeholders pass, a name by its hash caught in text, a binary and UTF-16')
    return ok


def main(argv):
    root = os.path.abspath(argv[argv.index('--root') + 1]) if '--root' in argv else ROOT
    ok = self_test()
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import normalize_personal_paths  # the tool that fixes what this finds must refuse an unsafe rewrite (its self-test)
    ok = normalize_personal_paths.self_test() and ok
    files = subprocess.run(['git', '-C', root, 'ls-files', '-z'], capture_output=True, check=True).stdout.decode().split('\0')[:-1]
    bad_files, unread, kinds, n, shown = 0, [], {}, 0, 0
    for i, f in enumerate(files):
        p = os.path.join(root, f)
        try:
            b = open(p, 'rb').read()
        except OSError as e:
            unread.append((i, e.__class__.__name__))
            continue
        hits = scan(b) + [(0, kind + ' in the file name') for _, kind in scan(f.encode())]
        if hits:
            bad_files += 1
            for pos, kind in hits:
                kinds[kind] = kinds.get(kind, 0) + 1
            n += len(hits)
            if shown < 40:
                shown += 1
                pos, kind = hits[0]
                line = b.count(b'\n', 0, pos) + 1
                # a file name that itself matches is not printed: the log would republish it
                label = f if not scan(f.encode()) else f'tracked file #{i} (its name matches; not printed)'
                print(f'FAIL  {label}:{line}: {kind} ({len(hits)} in the file) ~ text not shown')
    if bad_files > shown:
        print(f'FAIL  ... and {bad_files - shown} more files')
    for i, why in unread:
        print(f'FAIL  tracked file #{i} could not be read ({why}) - not inspected, so the gate cannot pass')
    names = sum(v for k, v in kinds.items() if k.startswith('name'))
    policy = n - names
    print(f'known identifiers (the owner\'s names, by hash): {names} places')
    print(f'policy forms (home folders, other drives, build machines, accounts, builds, hardware, addresses): {policy} places')
    print(f'r159 no personal paths: {len(files) - len(unread)} of {len(files)} tracked files inspected, {bad_files} with system details'
          + (f' ({n}: ' + ', '.join(f'{k} {v}' for k, v in sorted(kinds.items())) + ')' if n else ''))
    return 0 if ok and not bad_files and not unread else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
