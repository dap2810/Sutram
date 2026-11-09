#!/usr/bin/env python3
"""tools/verify_evidence_manifest.py - check an evidence manifest against the tree, following the privacy records.

    python3 tools/verify_evidence_manifest.py MANIFEST [MANIFEST ...]

A manifest records the digests of evidence as it was delivered. Since 9 November 2026 some of that evidence has been
normalised (the owner's system details replaced) or, for screenshots, removed. A plain `sha256sum -c` then fails on
those files, and a reader cannot tell that from damage. This tool says which it is, for each entry:

    OK          the file's bytes are the ones recorded
    NORMALISED  starting at the recorded digest, the normalisation records lead step by step - each step's "before"
                the digest reached so far - to the file's bytes now
    REMOVED     the file is a screenshot in the owner's removal list, and the recorded digest is the removed image's -
                or leads to it through the recorded covering of that image
    COPY-KEPT   the file was removed as a byte-identical copy (R159), the recorded digest is the removed copy's, and
                the copy that stays has those bytes (or they lead to its bytes now, as for NORMALISED)
    MISMATCH    the bytes differ, or the digest of a removed file is not the removed file's, and no record explains it
    MISSING     the file is not in the tree and no record explains it

It fails closed (ChatGPT, ROUND-226 follow-up 2). Two formats are read, both with paths relative to the manifest's
own folder: `sha256sum` text (`<64 hex> *<path>` on every non-blank line) and the JSON list of win-v307-fixes
(`[{"file": ..., "sha256": ...}, ...]`). A line or an object that is not exactly that, a key repeated in one object,
a path given twice with different digests, a path that leaves the repository, a manifest with no entry, a record
with a malformed digest, or two records that send one digest two ways: each is an error - INVALID, exit 1 - never a
shorter list quietly verified. No manifest named is a usage error (exit 2).

It changes nothing. Exit 0: every entry of every manifest is OK or explained. The records it follows:
ChatGPT-to-Sarvam/ROUND-226-PRIVACY-NORMALIZATION.json, Claude-to-Sarvam/evidence-r164/normalization-record.json,
Claude-to-Sarvam/evidence-r166/normalization-record-2.json (normalisations, in that order);
Claude-to-Sarvam/evidence-r164/screenshot-record.json (images covered before they were removed) and
screenshots-removed.tsv; Claude-to-Sarvam/evidence-r159/removed-identical-copies.tsv. The original bytes of a
NORMALISED or REMOVED file are in the history; this tool never points at them.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
RECORDS = ['ChatGPT-to-Sarvam/ROUND-226-PRIVACY-NORMALIZATION.json',
           'Claude-to-Sarvam/evidence-r164/normalization-record.json',
           'Claude-to-Sarvam/evidence-r166/normalization-record-2.json']
SHOTS = 'Claude-to-Sarvam/evidence-r164/screenshot-record.json'
REMOVED = 'Claude-to-Sarvam/evidence-r164/screenshots-removed.tsv'
COPIES = 'Claude-to-Sarvam/evidence-r159/removed-identical-copies.tsv'
HEX = re.compile(r'[0-9a-f]{64}\Z')
LINE = re.compile(r'([0-9a-fA-F]{64}) [ *](.+)\Z')
EXPLAINED = ('OK', 'NORMALISED', 'REMOVED', 'COPY-KEPT')


class ManifestError(Exception):
    """The manifest or a record cannot be read as what it must be: nothing about it is verified."""


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def strict_json(text, what):
    def pairs(ps):
        d = {}
        for k, v in ps:
            if k in d:
                raise ManifestError(f'{what}: a key is repeated in one object')
            d[k] = v
        return d
    try:
        return json.loads(text, object_pairs_hook=pairs)
    except ValueError as e:
        raise ManifestError(f'{what}: not JSON ({e.__class__.__name__})')


def digest_field(v, what):
    if not isinstance(v, str) or not HEX.match(v.lower()):
        raise ManifestError(f'{what}: a digest is not 64 hex digits')
    return v.lower()


class Records:
    """steps: path -> [(before, after)] in record order; removed: path -> digest; copies: path -> (digest, kept)."""
    def __init__(self):
        self.steps, self.removed, self.copies = {}, {}, {}

    def add_step(self, path, before, after, what):
        if not isinstance(path, str) or not path:
            raise ManifestError(f'{what}: an entry has no path')
        self.steps.setdefault(path, []).append((digest_field(before, what), digest_field(after, what)))


def load_records(root=ROOT):
    rec = Records()
    for r in RECORDS + [SHOTS]:
        p = os.path.join(root, r)
        if not os.path.exists(p):
            raise ManifestError(f'{r}: the record is not in the tree')
        data = strict_json(open(p, encoding='utf-8').read(), r)
        if not isinstance(data, dict) or not isinstance(data.get('files'), list):
            raise ManifestError(f'{r}: not a record with a "files" list')
        for e in data['files']:
            if not isinstance(e, dict):
                raise ManifestError(f'{r}: an entry is not an object')
            rec.add_step(e.get('path'), e.get('before_sha256'), e.get('after_sha256'), r)
    for line in open(os.path.join(root, REMOVED), encoding='utf-8'):
        if line.strip() and not line.startswith('#'):
            f = line.rstrip('\n').split('\t')
            if len(f) != 4:
                raise ManifestError(f'{REMOVED}: a line does not have four fields')
            rec.removed[f[0]] = digest_field(f[2], REMOVED)
    for line in open(os.path.join(root, COPIES), encoding='utf-8'):
        if line.strip() and not line.startswith(('#', 'removed path')):
            f = line.rstrip('\n').split('\t')
            if len(f) != 4:
                raise ManifestError(f'{COPIES}: a line does not have four fields')
            rec.copies[f[0]] = (digest_field(f[2], COPIES), f[3])
    return rec


def follow(steps, start):
    """From digest `start`, take each recorded step whose "before" is the digest reached so far. Returns (the digest
    reached, how many steps). One digest sent two different ways is ambiguous: an error, not a choice."""
    nxt = {}
    for before, after in steps:
        if before == after:
            continue
        if before in nxt and nxt[before] != after:
            raise ManifestError('two records send one digest to two different results')
        nxt[before] = after
    cur, n, seen = start, 0, {start}
    while cur in nxt:
        cur = nxt[cur]
        n += 1
        if cur in seen:
            raise ManifestError('the records lead a digest back to itself')
        seen.add(cur)
    return cur, n


def entries(manifest):
    """[(digest, name)] - every entry the manifest supplies, or ManifestError. Nothing is skipped."""
    raw = open(manifest, 'rb').read()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise ManifestError('not UTF-8 text')
    out = []
    if manifest.lower().endswith('.json'):
        data = strict_json(text, 'manifest')
        if not isinstance(data, list):
            raise ManifestError('a JSON manifest must be a list of {"file", "sha256"} objects')
        for i, it in enumerate(data):
            if not isinstance(it, dict) or not isinstance(it.get('file'), str) or 'sha256' not in it:
                raise ManifestError(f'entry {i + 1}: not an object with "file" and "sha256"')
            out.append((digest_field(it['sha256'], f'entry {i + 1}'), it['file']))
    else:
        for i, line in enumerate(text.splitlines()):
            if not line.strip():
                continue
            m = LINE.match(line.rstrip('\r'))
            if not m:
                raise ManifestError(f'line {i + 1}: not "<64 hex digits> *<path>"')
            out.append((m.group(1).lower(), m.group(2)))
    if not out:
        raise ManifestError('no entry')
    seen = {}
    for digest, name in out:
        if seen.setdefault(name, digest) != digest:
            raise ManifestError('one path is given twice with different digests')
    return out


def resolve(manifest, name, root):
    """The tracked path an entry names: always relative to the manifest's folder, and inside the repository."""
    name = name.replace('\\', '/')
    if name.startswith('/') or re.match(r'[A-Za-z]:', name):
        raise ManifestError('an entry gives an absolute path')
    p = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(manifest)), name))
    root = os.path.abspath(root)
    if os.path.commonpath([root, p]) != root:
        raise ManifestError('an entry\'s path leaves the repository')
    return os.path.relpath(p, root).replace(os.sep, '/'), p


def state_of(digest, rel, p, rec, root):
    steps = rec.steps.get(rel, [])
    if os.path.isfile(p):
        cur = sha(p)
        if cur == digest:
            return 'OK'
        reached, n = follow(steps, digest)
        return 'NORMALISED' if n and reached == cur else 'MISMATCH'
    if rel in rec.removed:
        reached, _ = follow(steps, digest)
        return 'REMOVED' if reached == rec.removed[rel] else 'MISMATCH'
    if rel in rec.copies:
        copy_digest, kept = rec.copies[rel]
        kp = os.path.join(root, kept)
        if digest == copy_digest and os.path.isfile(kp):
            cur = sha(kp)
            if cur == copy_digest or follow(rec.steps.get(kept, []), copy_digest)[0] == cur:
                return 'COPY-KEPT'
        return 'MISMATCH'
    return 'MISSING'


def verify(manifest, rec, root=ROOT):
    """(counts by state, [(state, path)] for every entry not OK or explained, entries supplied). ManifestError if
    the manifest cannot be read whole."""
    es = entries(manifest)
    counts, unexplained = {}, []
    for digest, name in es:
        rel, p = resolve(manifest, name, root)
        state = state_of(digest, rel, p, rec, root)
        counts[state] = counts.get(state, 0) + 1
        if state not in EXPLAINED:
            unexplained.append((state, rel))
    if sum(counts.values()) != len(es):
        raise ManifestError('not every entry was verified')
    return counts, unexplained, len(es)


def main(argv):
    ms = [a for a in argv if not a.startswith('--')]
    if not ms or len(ms) != len(argv):
        print(__doc__.split('\n\n')[0] + '\n\n    python3 tools/verify_evidence_manifest.py MANIFEST [MANIFEST ...]')
        return 2
    try:
        rec = load_records()
    except (ManifestError, OSError) as e:
        print(f'INVALID  the records: {e}')
        return 1
    bad = 0
    for m in ms:
        try:
            counts, unexplained, n = verify(m, rec)
        except (ManifestError, OSError) as e:
            print(f'{m}: INVALID - {e}')
            bad += 1
            continue
        print(f'{m}: {n} entries: ' + ', '.join(f'{k} {v}' for k, v in sorted(counts.items())))
        for state, rel in unexplained[:20]:
            print(f'   {state:9s} {rel}')
        bad += bool(unexplained)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
