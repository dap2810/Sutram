#!/usr/bin/env python3
"""R167 evidence manifests (Sarvam ROUND-167 WS3): a manifest nothing verifies is a claim nothing checks.

The Windows evidence folders carry manifests of their files as delivered (seven EVIDENCE.sha256 and one
evidence-sha256.json: 3,362 entries). They are kept as delivered - a regenerated manifest would match whatever is in
the folder and prove nothing about what was published (Muse R158, ChatGPT R226 follow-up). This gate reads them, with
tools/verify_evidence_manifest.py:

  every entry is OK (the bytes recorded), or explained by a record -
      NORMALISED  the records lead, step by connected step, from the recorded digest to the file's bytes now
      REMOVED     a screenshot in the owner's removal list, whose recorded digest is (or leads to) the removed image's
      COPY-KEPT   a byte-identical copy removed in R159 whose kept copy still has those bytes
  and none is MISMATCH or MISSING; every manifest is read whole (an unreadable line is an error, not a skip).

So evidence cannot change, or go, without a record that says how: an edit to a listed file that no record covers
fails this gate. Each folder also has a PRIVACY-NOTE.md saying why `sha256sum -c` alone now fails and what to run.

The self-test (ChatGPT R226 follow-up 2's fixtures, in a made-up tree): a true digest, a wrong one and an absent
file; a connected chain of two records, a broken one, an ambiguous one; a removed image with its digest, with the
digest before its covering, and with a wrong digest; and manifests that must be refused whole - malformed JSON, a
JSON shape that is not the list, a missing digest, a malformed digest, a repeated key, one path with two digests, a
text line that is not an entry, an empty manifest, a path that leaves the tree - and no manifest named at all.
Usage: python3 tests/r167/test_evidence_manifests.py
"""
import glob
import hashlib
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import verify_evidence_manifest as v  # noqa: E402

EXPECTED = 8      # seven EVIDENCE.sha256 and win-v307-fixes' evidence-sha256.json


def h(b):
    return hashlib.sha256(b).hexdigest()


def self_test():
    out = []
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, 'ev')
        os.makedirs(d)

        def put(name, data):
            open(os.path.join(d, name), 'wb').write(data)

        def manifest(name, text):
            p = os.path.join(d, name)
            open(p, 'w', encoding='utf-8').write(text)
            return p

        v0, v1, v2 = b'as delivered', b'normalised once', b'normalised twice'
        put('same.txt', v0)
        put('changed.txt', v2)
        put('edited.txt', b'edited with no record')
        rec = v.Records()
        rec.add_step('ev/changed.txt', h(v0), h(v1), 't')          # two records, connected
        rec.add_step('ev/changed.txt', h(v1), h(v2), 't')
        rec.add_step('ev/broken.txt', h(v0), h(v1), 't')           # ... and not connected: v1 -> ? ; x -> v2
        rec.add_step('ev/broken.txt', h(b'something else'), h(v2), 't')
        put('broken.txt', v2)
        rec.add_step('ev/shot-covered.png', h(b'image'), h(b'image, covered'), 't')
        rec.removed['ev/shot.png'] = h(b'image 2')
        rec.removed['ev/shot-covered.png'] = h(b'image, covered')
        m = manifest('M.sha256', ''.join(f'{dg} *{n}\n' for dg, n in (
            (h(v0), 'same.txt'), (h(v0), 'changed.txt'), (h(v0), 'edited.txt'), (h(v0), 'gone.txt'),
            (h(v0), 'broken.txt'), (h(b'image 2'), 'shot.png'), (h(b'image'), 'shot-covered.png'))))
        counts, unexplained, n = v.verify(m, rec, root)
        want = {'OK': 1, 'NORMALISED': 1, 'MISMATCH': 2, 'MISSING': 1, 'REMOVED': 2}
        out.append((counts == want and n == 7 and sorted(r for _, r in unexplained) == ['ev/broken.txt', 'ev/edited.txt', 'ev/gone.txt'],
                    f'self-test: the recorded bytes are OK; a connected chain of two records NORMALISED; an edit with no record, '
                    f'and a chain that does not connect, MISMATCH; an absent file MISSING; a removed image, by its digest or '
                    f'the one before its covering, REMOVED ({counts})'))
        m = manifest('W.sha256', f'{h(b"not that image")} *shot.png\n')
        counts, _, _ = v.verify(m, rec, root)
        out.append((counts == {'MISMATCH': 1}, f'self-test: a wrong digest for a removed image is not explained by its removal ({counts})'))
        amb = v.Records()
        amb.add_step('ev/changed.txt', h(v0), h(v1), 't')
        amb.add_step('ev/changed.txt', h(v0), h(v2), 't')
        refused = []
        for label, name, text, records in (
                ('two records sending one digest two ways', 'A.sha256', f'{h(v0)} *changed.txt\n', amb),
                ('malformed JSON', 'a.json', '[{"file": "same.txt", "sha256": ', rec),
                ('a JSON shape that is not the list', 'b.json', '{"same.txt": "' + h(v0) + '"}', rec),
                ('a missing digest', 'c.json', '[{"file": "same.txt"}]', rec),
                ('a malformed digest', 'd.json', '[{"file": "same.txt", "sha256": "abc"}]', rec),
                ('a repeated key', 'e.json', '[{"file": "same.txt", "file": "x", "sha256": "' + h(v0) + '"}]', rec),
                ('one path with two digests', 'F.sha256', f'{h(v0)} *same.txt\n{h(v1)} *same.txt\n', rec),
                ('a line that is not an entry', 'G.sha256', f'{h(v0)} *same.txt\nthis is not an entry\n', rec),
                ('an empty manifest', 'H.sha256', '\n', rec),
                ('a path that leaves the tree', 'I.sha256', f'{h(v0)} *../../outside.txt\n', rec)):
            try:
                v.verify(manifest(name, text), records, root)
                refused.append((label, False))
            except v.ManifestError:
                refused.append((label, True))
        bad = [label for label, ok in refused if not ok]
        out.append((not bad, f'self-test: {len(refused)} manifests that cannot be read whole are refused, not partly verified'
                    + ('' if not bad else f' -- NOT refused: {bad}')))
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'verify_evidence_manifest.py')], capture_output=True)
    out.append((r.returncode == 2, f'self-test: no manifest named is a usage error (exit {r.returncode})'))
    return out


def main():
    os.chdir(ROOT)
    checks = fails = 0

    def report(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    for ok, what in self_test():
        report(ok, what)
    try:
        rec = v.load_records()
    except v.ManifestError as e:
        report(False, f'the records load: {e}')
        print(f'r167 evidence manifests: 0 manifests; {checks} checks, {fails} failed')
        return 1
    manifests = sorted(glob.glob('Windows-to-Sarvam/*/EVIDENCE.sha256') + glob.glob('Windows-to-Sarvam/*/evidence-sha256.json'))
    report(len(manifests) == EXPECTED, f'the {EXPECTED} evidence manifests are in the tree ({len(manifests)} found)')
    total, entries = {}, 0
    for m in manifests:
        try:
            counts, unexplained, n = v.verify(m, rec)
        except v.ManifestError as e:
            report(False, f'{m}: INVALID - {e}')
            continue
        entries += n
        for k, c in counts.items():
            total[k] = total.get(k, 0) + c
        line = ', '.join(f'{k} {c}' for k, c in sorted(counts.items()))
        report(not unexplained, f'{m}: {n} entries: {line}'
               + ('' if not unexplained else f' -- {unexplained[0][0]} {unexplained[0][1]}'))
        report(os.path.exists(os.path.join(os.path.dirname(m), 'PRIVACY-NOTE.md')),
               f'{os.path.dirname(m)}: PRIVACY-NOTE.md says why sha256sum -c alone fails and what to run')
    print(f'r167 evidence manifests: {len(manifests)} manifests, {entries} entries ('
          + ', '.join(f'{k} {c}' for k, c in sorted(total.items())) + f'); {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
