#!/usr/bin/env python3
"""tools/normalize_personal_paths.py - R164/R165: take the owner's system details (and the build machines') out of
the tracked text, keeping what each line claims.

    python3 tools/normalize_personal_paths.py [--apply --record FILE.json [--allow-key-changes]] [--self-test] [PATH ...]

Without --apply it only reports: per rule, per folder, and the three things that would make a replacement break
something (ROUND-165 WS1): a file whose digest another file cites (a SHA-256 preimage), a path inside a JSON key, a
path inside a file name. With --apply it rewrites the files and writes each changed file's digest before and after
(--record, required; the provenance ChatGPT's ROUND-226 record uses), so a hash cited elsewhere can still be traced.
It fails closed (ChatGPT, ROUND-226 follow-up): every proposed file is checked before anything is written - a tracked
file it cannot read, a JSON file that would no longer parse, a key repeated in one object (a collision two distinct
paths would make), a JSON structure or non-text value that would move, or a key that would change without
--allow-key-changes - and any of them stops it, exit 1, nothing written. UTF-16 text is decoded, normalised and
written back in its own encoding; a binary is never changed. Its own self-test runs first (--self-test alone).
Applying is checked before, not transactional: the record is written, then each file; if a write fails part-way it
says which files are as before, as after, or neither, and exits 1.

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
    r.append(('kernel build', re.compile(rb'(?i)\b[0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?-(?:microsoft-standard-WSL2|fc-v[0-9]+)\b'),
              b'(kernel build redacted)'))
    r.append(('kernel build (platform string)', re.compile(rb'(?i)\b(linux|kernel)([ -]+)[0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?-[A-Za-z0-9._-]+'),
              b'\\1\\2(kernel build redacted)'))
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


def decode(b):
    """(text as UTF-8 bytes, how to write it back) - UTF-16 with a BOM or one NUL in every other byte is decoded;
    None for a binary, which is never changed."""
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        enc = 'utf-16'
        return b.decode(enc).encode('utf-8'), lambda t: t.decode('utf-8').encode(enc)
    if len(b) >= 4 and b'\0' in b[:8000] and b[1:8000:2].count(0) > 0.9 * len(b[1:8000:2]):
        return b.decode('utf-16-le').encode('utf-8'), lambda t: t.decode('utf-8').encode('utf-16-le')
    if b'\0' in b[:8000]:
        return None, None
    return b, lambda t: t


class DuplicateKey(ValueError):
    pass


def strict_json(b):
    """Parse JSON refusing a duplicate key in any object (json.loads would keep the last one silently)."""
    def pairs(ps):
        d = {}
        for k, v in ps:
            if k in d:
                raise DuplicateKey(f'duplicate key in one object ({len(k)} characters)')
            d[k] = v
        return d
    return json.loads(b.decode('utf-8-sig'), object_pairs_hook=pairs)


def json_problems(before, after):
    """Why a JSON rewrite is unsafe: it parses no longer, a key repeats in one object, the structure moved, or a key
    changed (a change is allowed only with --allow-key-changes; a collision never). Returns (problems, keys changed)."""
    try:
        a = strict_json(before)
    except ValueError as e:
        return [f'it did not parse before: {e.__class__.__name__}'], 0
    try:
        z = strict_json(after)
    except ValueError as e:
        return [f'it would no longer parse: {e.__class__.__name__}: {e}'], 0
    problems, changed = [], 0

    def walk(x, y, where):
        nonlocal changed
        if type(x) is not type(y):
            problems.append(f'{where}: a {type(x).__name__} would become a {type(y).__name__}')
        elif isinstance(x, dict):
            if len(x) != len(y):
                problems.append(f'{where}: {len(x)} keys would become {len(y)}')
                return
            for (k0, v0), (k1, v1) in zip(x.items(), y.items()):
                changed += k0 != k1
                walk(v0, v1, where + '/{key}')
        elif isinstance(x, list):
            if len(x) != len(y):
                problems.append(f'{where}: a list of {len(x)} would become {len(y)}')
                return
            for v0, v1 in zip(x, y):
                walk(v0, v1, where + '/[]')
        elif not isinstance(x, str) and x != y:
            problems.append(f'{where}: a value that is not text would change')
    walk(a, z, '')
    return problems, changed


def self_test():
    """The checks that keep a rewrite from writing something unsafe, on made-up JSON (no real name in it)."""
    bs = '\\'
    ok = True
    p, _ = json_problems(b'{"a": "x"}', b'{"a": "x' + bs.encode() + b'q"}')
    ok &= bool(p) and 'no longer parse' in p[0]
    one, two = '"C:' + bs * 2 + 'Users' + bs * 2 + 'ann' + bs * 2 + 'x"', '"C:' + bs * 2 + 'Users' + bs * 2 + 'bob' + bs * 2 + 'x"'
    same = '"%USERPROFILE%' + bs * 2 + 'x"'
    p, _ = json_problems(('{' + one + ': 1, ' + two + ': 2}').encode(), ('{' + same + ': 1, ' + same + ': 2}').encode())
    ok &= bool(p) and 'no longer parse' in p[0] and 'DuplicateKey' in p[0]
    p, n = json_problems(('{' + one + ': 1}').encode(), ('{' + same + ': 1}').encode())
    ok &= not p and n == 1
    p, n = json_problems(('{"k": ' + one + '}').encode(), ('{"k": ' + same + '}').encode())
    ok &= not p and n == 0
    p, _ = json_problems(b'{"k": 1}', b'{"k": 2}')
    ok &= bool(p)
    t = 'path ' + 'C:' + bs[0] + 'Users' + bs[0] + 'ann'
    text, back = decode(t.encode('utf-16'))
    ok &= text == t.encode() and back(text) == t.encode('utf-16')
    print(('PASS' if ok else 'FAIL') + '  normaliser self-test: an invalid escape and a key collision are refused; a key '
          'change is counted; a non-text value may not change; UTF-16 round-trips')
    return ok


def main(argv):
    if '--self-test' in argv:
        return 0 if self_test() else 1
    apply = '--apply' in argv
    allow_keys = '--allow-key-changes' in argv
    record = argv[argv.index('--record') + 1] if '--record' in argv else None
    only = [a for a in argv if not a.startswith('--') and a != record]
    if apply and not record:
        print('refused: --apply needs --record FILE.json (the digests before and after are part of the change)')
        return 2
    if not self_test():
        return 1
    os.chdir(ROOT)
    files = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, check=True).stdout.decode().split('\0')[:-1]
    if only:
        files = [f for f in files if any(f == o or f.startswith(o.rstrip('/') + '/') for o in only)]
    hashes = load_names()
    problems, raw = [], {}
    for f in files:
        try:
            raw[f] = open(f, 'rb').read()
        except OSError as e:
            problems.append(f'{f}: could not be read ({e.__class__.__name__})')
    names = {}
    for f, b in raw.items():
        t, _ = decode(b)
        for w in words_by_hash(t if t is not None else b, hashes) | (words_by_hash(b.decode('utf-16-le', 'ignore').encode(), hashes) if t is None else set()):
            names[w] = hashes[sha(w)]
    rs = rules(names)
    changed, per_rule, per_dir, key_changes, binaries = {}, {}, {}, [], []
    for f, b in raw.items():
        t, back = decode(b)
        if t is None:
            if words_by_hash(b, hashes) or words_by_hash(b.decode('utf-16-le', 'ignore').encode(), hashes):
                binaries.append(f)
            continue
        nt, hits = apply_rules(f, t, rs)
        if nt == t:
            continue
        nb = back(nt)
        if decode(nb)[0] != nt:
            problems.append(f'{f}: would not read back as written')
            continue
        if f.lower().endswith('.json'):
            pr, kc = json_problems(t, nt)      # the decoded text: a UTF-16 JSON file is checked like any other
            problems += [f'{f}: {x}' for x in pr]
            if kc:
                key_changes.append(f'{f}: {kc} keys change')
        changed[f] = (b, nb)
        for h in hits:
            per_rule[h] = per_rule.get(h, 0) + 1
        d = f.split('/')[0] if '/' in f else '(top)'
        per_dir[d] = per_dir.get(d, 0) + 1
    if key_changes and not allow_keys:
        problems += [k + ' (a key is structure: rerun with --allow-key-changes once each is checked)' for k in key_changes]
    # digests other files cite: the first 16 hex digits of the SHA-256 and the first 12 of the SHA-1 / git blob id
    cites = []
    if changed:
        idx = {}
        for f, (b, _) in changed.items():
            for d in (sha(b)[:16], hashlib.sha1(b).hexdigest()[:12],
                      hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()[:12]):
                idx[d.encode()] = f
        pat = re.compile(b'|'.join(re.escape(k) for k in idx))
        for g, t in raw.items():
            if b'\0' in t[:8000]:
                continue
            for m in pat.finditer(t):
                cites.append(f'{g} cites {idx[m.group(0)]} ({m.group(0).decode()})')
    names_in_paths = [i for i, f in enumerate(files) if words_by_hash(f.encode(), hashes)]
    print(f'files that change: {len(changed)}')
    for d, n in sorted(per_dir.items(), key=lambda x: -x[1]):
        print(f'  {n:5d}  {d}/')
    print('replacements by rule:')
    for r_, n in sorted(per_rule.items(), key=lambda x: -x[1]):
        print(f'  {n:6d}  {r_}')
    print(f'a digest of a changed file cited elsewhere: {len(cites)}')
    for c in cites:
        print('  ' + c)
    print(f'JSON keys that change: {len(key_changes)}')
    for k in key_changes:
        print('  ' + k)
    print(f'file names with a name in them: {len(names_in_paths)} (tracked file numbers: {names_in_paths[:20]})')
    print(f'binary files with a name in them (never changed): {len(binaries)}')
    for f in binaries:
        print('  ' + f)
    if problems:
        print(f'REFUSED - {len(problems)} problems; nothing written:')
        for x in problems:
            print('  ' + x)
        return 1
    if apply:
        rec = [{'path': f, 'before_sha256': sha(b), 'after_sha256': sha(nb)} for f, (b, nb) in sorted(changed.items())]
        json.dump({'scope': 'normalization of personal and build-machine system details (tools/normalize_personal_paths.py)',
                   'note': 'Before digests identify the historical bytes (git history keeps them); after digests '
                           'identify the normalized text, not new executions. Embedded product hashes are unchanged. '
                           'No history rewrite.',
                   'files': rec}, open(record, 'w'), indent=1)
        open(record, 'a').write('\n')
        # Not a transaction: the record (what is intended) is written first, then the files one by one. If a write
        # fails part-way, some files are as before and some as after; say exactly which, so nothing is guessed.
        failure = None
        for f, (_, nb) in changed.items():
            try:
                open(f, 'wb').write(nb)
            except OSError as e:
                failure = f'{f}: {e.__class__.__name__}'
                break
        state = {'before': [], 'after': [], 'neither': []}
        for f, (b, nb) in changed.items():
            try:
                cur = open(f, 'rb').read()
            except OSError:
                cur = None
            state['after' if cur == nb else 'before' if cur == b else 'neither'].append(f)
        if failure or state['before'] or state['neither']:
            print(f'FAILED - applied in part ({failure or "a file does not read back as written"}). The record {record} '
                  f'lists what was intended, not what is: {len(state["after"])} files are as after, '
                  f'{len(state["before"])} as before, {len(state["neither"])} neither.')
            for k in ('before', 'neither'):
                for f in state[k][:20]:
                    print(f'  {k}: {f}')
            return 1
        print(f'applied: {len(changed)} files; record {record}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
