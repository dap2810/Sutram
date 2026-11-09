#!/usr/bin/env python3
"""tools/normalize_personal_paths.py - R164/R165: take the owner's system details (and the build machines') out of
the tracked text, keeping what each line claims.

    python3 tools/normalize_personal_paths.py [--apply] [--record FILE.json] [PATH ...]

Without --apply it only reports: per rule, per folder, and the three things that would make a replacement break
something (ROUND-165 WS1): a file whose digest another file cites (a SHA-256 preimage), a path inside a JSON key, a
path inside a file name. With --apply it rewrites the files and, with --record, writes each changed file's digest
before and after (the provenance ChatGPT's ROUND-226 record uses), so a hash cited elsewhere can still be traced.

The rules are byte rules, ordered; each keeps the separators and the rest of the path. Placeholders:
%USERPROFILE% for the home folder, <repo> for the repository's folder, <user> / <machine> for an account and a
computer name, "(build redacted)" for an operating-system build number, [hardware detail redacted] for a CPU, and
<scratch> / <tmp> / <workspace> for a build machine's own folders. In Markdown outside code, and in HTML and XML,
an angle-bracket placeholder is written so that it shows (`<repo>` in backticks; &lt;repo&gt;).

The account and computer names are not written here (the repository is public): they are matched by the SHA-256 of
the lower-case word, as the gate tests/r159/test_no_personal_paths.py matches them.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SEP = rb'(?:\\\\|\\|/)'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def words_by_hash(text, hashes):
    found = set()
    for w in set(re.findall(rb'[A-Za-z0-9_]{3,40}', text)):
        if sha(w.lower()) in hashes:
            found.add(w.lower())
    return found


def load_names():
    """The names come from the hashes in the gate; the words themselves are read from the tree they occur in."""
    sys.path.insert(0, os.path.join(ROOT, 'tests', 'r159'))
    import test_no_personal_paths as gate
    return gate.NAME_HASHES


def rules(names):
    """names: the matched words (bytes, lower case), in the order user, machine, projects folder."""
    acc = [n for n, k in names.items() if k == 'account']
    mach = [n for n, k in names.items() if k == 'machine']
    proj = [n for n, k in names.items() if k == 'projects']
    alt = lambda ws: b'(?:' + b'|'.join(re.escape(w) for w in ws) + b')'
    who = alt(acc + mach)            # a profile folder has been named after either
    r = []
    if not (acc or mach):
        who = b'(?!x)x'              # nothing to match: never an empty alternative, which would match everywhere
    # the home folder, every spelling: one backslash, two (JSON), a slash, the long-path prefix, an 8.3 short name
    r.append(('home folder', re.compile(rb'(?i)(?:\\\\\?\\|\\\\\\\\\?\\\\)?[a-z]:' + SEP + rb'users' + SEP + who + rb'(?:~\d)?\b'), b'%USERPROFILE%'))
    r.append(('home folder (WSL, MSYS)', re.compile(rb'(?i)(?:/mnt)?/c/users/' + who + rb'\b'), b'%USERPROFILE%'))
    # the repository's folder on the owner's machine, and the folder that holds it
    if proj:
        r.append(('repository folder', re.compile(rb'(?i)(?:[a-z]:|/[a-z])' + SEP + rb'(?:' + b'|'.join(re.escape(p).replace(b'_', b'[ _]') for p in proj) + rb')' + SEP + rb'sutram\b'), b'<repo>'))
        r.append(('projects folder', re.compile(rb'(?i)(?:[a-z]:|/[a-z])' + SEP + rb'(?:' + b'|'.join(re.escape(p).replace(b'_', b'[ _]') for p in proj) + rb')\b'), b'<projects>'))
    r.append(('repository folder (elided)', re.compile(rb'(?<![A-Za-z0-9])E' rb':\\\.\.\.\\Sutram\b'), b'<repo>'))
    r.append(('a test folder on another drive', re.compile(rb'(?<![A-Za-z0-9])I' rb':\\sutram-windows-test_2\\Sutram-Windows-Test'), b'<test-folder>'))
    # an account and a computer name on their own: DOMAIN\user, Machine: X, and the word
    if mach and acc:
        r.append(('machine\\account', re.compile(rb'(?i)\b' + alt(mach) + rb'(\\\\|\\)' + alt(acc) + rb'\b'), b'<machine>\\1<user>'))
    if mach:
        r.append(('machine name', re.compile(rb'(?i)(Machine:\s*)' + alt(mach) + rb'\b'), b'\\1<machine>'))
    if acc:
        r.append(('account name', re.compile(rb'(?i)\b' + alt(acc) + rb'\b'), b'<user>'))
    if mach:
        r.append(('owner named', re.compile(rb'\b' + alt([m.capitalize() for m in mach]) + rb'\b'), b'Owner'))
    # operating-system build numbers (PowerShell's version carries the build too)
    r.append(('OS build', re.compile(rb'(?i)\bbuild\s+2[0-9]{4}(?:\.[0-9]+)?'), b'build (redacted)'))
    r.append(('OS build (10.0.x)', re.compile(rb'\b10\.0\.2[0-9]{4}(?:\.[0-9]+)?\b'), b'10.0 (build redacted)'))
    r.append(('PowerShell build', re.compile(rb'\b5\.1\.2[0-9]{4}\.[0-9]+\b'), b'5.1 (build redacted)'))
    r.append(('OS build (nnnnn.nnnn)', re.compile(rb'\b2[0-9]{4}\.[0-9]{3,4}\b(?=[^\n]{0,80}(?i:windows|powershell|build))|(?<=(?i:build) )2[0-9]{4}\.[0-9]{3,4}\b'), b'(build redacted)'))
    # hardware
    r.append(('CPU', re.compile(rb'(?i)(?:AMD\s+)?Ryzen\s+\d\s+\w+(?:\s+\d+-Core(?:\s+Processor)?)?'), b'[hardware detail redacted]'))
    # the build machines' own folders (Claude's cloud container, under Wine too, and Muse's)
    r.append(('cloud scratch (Wine view)', re.compile(rb'(?i)Z' rb':(\\\\|\\|/)tmp\1claude-0\1-home-' rb'claude\1[0-9a-f-]{36}(?:\1scratchpad)?'), b'<scratch>'))
    r.append(('cloud scratch', re.compile(rb'/tmp/claude-' rb'0/-home-' rb'claude/[0-9a-f-]{36}(?:/scratchpad)?'), b'<scratch>'))
    r.append(('cloud tmp', re.compile(rb'(?i)(?:Z' rb':(?:\\\\|\\|/))?/?tmp(\\\\|\\|/)claude-' rb'0\b'), b'<tmp>'))
    r.append(('cloud repo', re.compile(rb'/ho' rb'me/claude/sutram\b'), b'<repo>'))
    r.append(('cloud home', re.compile(rb'/ho' rb'me/claude\b'), b'~'))
    r.append(('Muse workspace', re.compile(rb'/ho' rb'me/hatch/workspace\b'), b'<workspace>'))
    r.append(('Muse home', re.compile(rb'/ho' rb'me/hatch\b'), b'~'))
    r.append(('cloud folder name (a wrapped line)', re.compile(rb'-home-' rb'claude\b'), b'-home-<user>'))
    r.append(('Wine profile', re.compile(rb'(?i)C:(\\\\|\\|/)users\1root\b'), b'%USERPROFILE%'))
    r.append(('Wine profile (elided)', re.compile(rb'\u2026/users/root/'.decode('unicode_escape').encode('utf-8')), '…/%USERPROFILE%/'.encode('utf-8')))
    r.append(('example home', re.compile(rb'/ho' rb'me/u/hello\.sm'), b'/ho' b'me/<you>/hello.sm'))
    return r


def in_md_code(b, pos):
    """Is byte offset pos inside a fenced block or an inline code span of a Markdown file?"""
    fences = len(re.findall(rb'(?m)^\s*```', b[:pos]))
    if fences % 2:
        return True
    ls = b.rfind(b'\n', 0, pos) + 1
    return b[ls:pos].count(b'`') % 2 == 1


def apply_rules(path, b, rs):
    ext = os.path.splitext(path)[1].lower()
    hits = []
    for name, rx, rep in rs:
        out, last = [], 0
        for m in rx.finditer(b):
            new = m.expand(rep)
            if b'<' in new:
                if ext in ('.html', '.htm', '.xml', '.svg'):
                    new = new.replace(b'<', b'&lt;').replace(b'>', b'&gt;')
                elif ext == '.md' and not in_md_code(b, m.start()):
                    new = b'`' + new + b'`'
            out.append(b[last:m.start()]); out.append(new); last = m.end()
            hits.append(name)
        if last:
            out.append(b[last:]); b = b''.join(out)
    return b, hits


def main(argv):
    apply = '--apply' in argv
    record = argv[argv.index('--record') + 1] if '--record' in argv else None
    only = [a for a in argv if not a.startswith('--') and a != record]
    os.chdir(ROOT)
    files = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, check=True).stdout.decode().split('\0')[:-1]
    if only:
        files = [f for f in files if any(f == o or f.startswith(o.rstrip('/') + '/') for o in only)]
    hashes = load_names()
    names = {}
    for f in files:
        try:
            b = open(f, 'rb').read()
        except OSError:
            continue
        for w in words_by_hash(b, hashes):
            names[w] = hashes[sha(w)]
    rs = rules(names)
    changed, per_rule, per_dir, keys, binaries = {}, {}, {}, [], []
    for f in files:
        try:
            b = open(f, 'rb').read()
        except OSError:
            continue
        if b'\0' in b[:8000]:
            if words_by_hash(b, hashes):
                binaries.append(f)
            continue
        nb, hits = apply_rules(f, b, rs)
        if nb != b:
            changed[f] = (b, nb)
            for h in hits:
                per_rule[h] = per_rule.get(h, 0) + 1
            d = f.split('/')[0] if '/' in f else '(top)'
            per_dir[d] = per_dir.get(d, 0) + 1
            if f.endswith('.json'):
                try:
                    j0, j1 = json.loads(b), json.loads(nb)
                except ValueError as e:
                    keys.append(f'{f}: JSON {e}')
                    continue
                def walk(o, acc):
                    if isinstance(o, dict):
                        for k, v in o.items():
                            acc.append(k); walk(v, acc)
                    elif isinstance(o, list):
                        for v in o:
                            walk(v, acc)
                    return acc
                k0, k1 = walk(j0, []), walk(j1, [])
                if k0 != k1:
                    keys.append(f'{f}: {sum(1 for a, c in zip(k0, k1) if a != c)} keys change')
    # digests other files cite: the first 16 hex digits of the SHA-256 and the first 12 of the SHA-1 / git blob id
    cites = []
    if changed:
        idx = {}
        for f, (b, _) in changed.items():
            for d in (sha(b)[:16], hashlib.sha1(b).hexdigest()[:12],
                      hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()[:12]):
                idx[d.encode()] = f
        pat = re.compile(b'|'.join(re.escape(k) for k in idx))
        for g in files:
            try:
                t = open(g, 'rb').read()
            except OSError:
                continue
            if b'\0' in t[:8000]:
                continue
            for m in pat.finditer(t):
                cites.append(f'{g} cites {idx[m.group(0)]} ({m.group(0).decode()})')
    names_in_paths = [f for f in files if words_by_hash(f.encode(), hashes)]
    print(f'files that change: {len(changed)}')
    for d, n in sorted(per_dir.items(), key=lambda x: -x[1]):
        print(f'  {n:5d}  {d}/')
    print('replacements by rule:')
    for r_, n in sorted(per_rule.items(), key=lambda x: -x[1]):
        print(f'  {n:6d}  {r_}')
    print(f'a digest of a changed file cited elsewhere: {len(cites)}')
    for c in cites:
        print('  ' + c)
    print(f'JSON keys that change, or JSON that stops parsing: {len(keys)}')
    for k in keys:
        print('  ' + k)
    print(f'file names with a name in them: {len(names_in_paths)}')
    print(f'binary files with a name in them (not changed): {len(binaries)}')
    for f in binaries:
        print('  ' + f)
    if apply:
        rec = []
        for f, (b, nb) in sorted(changed.items()):
            open(f, 'wb').write(nb)
            rec.append({'path': f, 'before_sha256': sha(b), 'after_sha256': sha(nb)})
        if record:
            json.dump({'scope': 'R164/R165 normalization of personal and build-machine system details, 9 November 2026',
                       'note': 'Before digests identify the historical bytes (git history keeps them); after digests '
                               'identify the normalized text, not new executions. Embedded product hashes are unchanged. '
                               'No history rewrite.',
                       'files': rec}, open(record, 'w'), indent=1)
            open(record, 'a').write('\n')
        print(f'applied: {len(changed)} files')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
