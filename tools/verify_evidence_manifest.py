#!/usr/bin/env python3
"""tools/verify_evidence_manifest.py - check an evidence manifest against the tree, following the privacy records.

    python3 tools/verify_evidence_manifest.py MANIFEST [MANIFEST ...]
    python3 tools/verify_evidence_manifest.py --all          (every *.sha256, *SHA256*.txt, evidence-sha256.json)

A manifest records the digests of evidence as it was delivered. Since 9 November 2026 some of that evidence has been
normalised (the owner's system details replaced) or, for screenshots, removed. A plain `sha256sum -c` then fails on
those files, and a reader cannot tell that from damage. This tool says which it is, for each entry:

    OK          the file's bytes are the ones recorded
    NORMALISED  the recorded digest is the file's digest before a normalisation, and the file is now exactly what the
                last normalisation wrote (each step is in a record: ChatGPT-to-Sarvam/ROUND-226-PRIVACY-NORMALIZATION.json,
                Claude-to-Sarvam/evidence-r164/normalization-record.json, Claude-to-Sarvam/evidence-r166/normalization-record-2.json)
    REMOVED     the file is a screenshot removed under the privacy rule (Claude-to-Sarvam/evidence-r164/screenshots-removed.tsv)
    COPY-KEPT   the file was removed as a byte-identical copy (R159, Claude-to-Sarvam/evidence-r159/removed-identical-copies.tsv)
                and the copy that stays has the same bytes (or is that copy, normalised)
    MISMATCH    none of these: the bytes differ and no record explains it
    MISSING     the file is not in the tree and no record explains it

It changes nothing. Exit 1 if any entry is MISMATCH or MISSING. The original bytes of a NORMALISED or REMOVED file are
in the history: `git show <commit>:<path> | sha256sum` for a commit before 9 November 2026's normalisation.
"""
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
RECORDS = ['ChatGPT-to-Sarvam/ROUND-226-PRIVACY-NORMALIZATION.json',
           'Claude-to-Sarvam/evidence-r164/normalization-record.json',
           'Claude-to-Sarvam/evidence-r166/normalization-record-2.json']
REMOVED = 'Claude-to-Sarvam/evidence-r164/screenshots-removed.tsv'
COPIES = 'Claude-to-Sarvam/evidence-r159/removed-identical-copies.tsv'
LINE = re.compile(r'^\s*([0-9a-fA-F]{64})\s+\*?(.+?)\s*$')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load_records():
    chain = {}
    for r in RECORDS:
        p = os.path.join(ROOT, r)
        if not os.path.exists(p):
            continue
        for e in json.load(open(p)).get('files', []):
            chain.setdefault(e['path'], []).append((e['before_sha256'], e['after_sha256']))
    removed = set()
    p = os.path.join(ROOT, REMOVED)
    if os.path.exists(p):
        for line in open(p):
            if line.strip() and not line.startswith('#'):
                removed.add(line.split('\t')[0])
    copies = {}
    p = os.path.join(ROOT, COPIES)
    if os.path.exists(p):
        for line in open(p):
            f = line.rstrip('\n').split('\t')
            if len(f) == 4 and not line.startswith(('#', 'removed path')):
                copies[f[0]] = (f[2], f[3])
    return chain, removed, copies


def entries(manifest):
    text = open(manifest, encoding='utf-8-sig', errors='replace').read()
    if manifest.endswith('.json'):
        try:
            data = json.loads(text)
        except ValueError:
            return []
        items = data if isinstance(data, list) else data.get('files', []) if isinstance(data, dict) else []
        out = []
        for it in items:
            if isinstance(it, dict):
                name = it.get('file') or it.get('path') or it.get('name')
                digest = it.get('sha256') or it.get('SHA256') or it.get('hash')
                if name and isinstance(digest, str) and re.fullmatch(r'[0-9a-fA-F]{64}', digest):
                    out.append((digest.lower(), name))
        return out
    return [(m.group(1).lower(), m.group(2)) for m in map(LINE.match, text.splitlines()) if m]


def resolve(manifest, name):
    """The tracked path an entry names: relative to the manifest's folder, else to the repository."""
    name = name.replace('\\', '/')
    for base in (os.path.dirname(manifest), ROOT):
        p = os.path.normpath(os.path.join(base, name))
        if p.startswith(ROOT):
            rel = os.path.relpath(p, ROOT)
            if os.path.exists(p):
                return rel, p
    p = os.path.normpath(os.path.join(os.path.dirname(manifest), name))
    return os.path.relpath(p, ROOT), p


def verify(manifest, chain, removed, copies):
    counts, unexplained = {}, []
    for digest, name in entries(manifest):
        rel, p = resolve(manifest, name)
        if os.path.exists(p) and os.path.isfile(p):
            cur = sha(p)
            if cur == digest:
                state = 'OK'
            elif rel in chain and digest in [b for b, _ in chain[rel]] and cur == chain[rel][-1][1]:
                state = 'NORMALISED'
            else:
                state = 'MISMATCH'
        elif rel in removed:
            state = 'REMOVED'
        elif rel in copies and copies[rel][0] == digest and os.path.exists(os.path.join(ROOT, copies[rel][1])) \
                and sha(os.path.join(ROOT, copies[rel][1])) in (digest, (chain.get(copies[rel][1]) or [(0, 0)])[-1][1]):
            state = 'COPY-KEPT'
        else:
            state = 'MISSING'
        counts[state] = counts.get(state, 0) + 1
        if state in ('MISMATCH', 'MISSING'):
            unexplained.append((state, rel))
    return counts, unexplained


def main(argv):
    os.chdir(ROOT)
    if '--all' in argv:
        ms = sorted(set(glob.glob('**/*.sha256', recursive=True) + glob.glob('**/*SHA256*.txt', recursive=True)
                        + glob.glob('**/evidence-sha256.json', recursive=True)))
        ms = [m for m in ms if not m.startswith(('backups/', 'tools/', 'tests/'))]
    else:
        ms = [a for a in argv if not a.startswith('--')]
    chain, removed, copies = load_records()
    bad = 0
    for m in ms:
        counts, unexplained = verify(os.path.abspath(m), chain, removed, copies)
        if not counts:
            continue
        line = ', '.join(f'{k} {v}' for k, v in sorted(counts.items()))
        print(f'{m}: {line}')
        if '--all' not in argv:
            for state, rel in unexplained[:20]:
                print(f'   {state:9s} {rel}')
        bad += bool(unexplained)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
