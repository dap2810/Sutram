#!/usr/bin/env python3
"""R167 evidence manifests (Sarvam ROUND-167 WS3): a manifest nothing verifies is a claim nothing checks.

The Windows evidence folders carry manifests of their files as delivered (seven EVIDENCE.sha256 and one
evidence-sha256.json: 3,362 entries). They are kept as delivered - a regenerated manifest would match whatever is in
the folder and prove nothing about what was published (Muse R158, ChatGPT R226 follow-up). This gate reads them:

  every entry is OK (the bytes recorded), or explained by a record -
      NORMALISED  the recorded digest is a "before" in a normalisation record and the file is the last "after"
      REMOVED     a screenshot in the owner's removal list
      COPY-KEPT   a byte-identical copy removed in R159 whose kept copy still matches
  and none is MISMATCH or MISSING.

So evidence cannot change, or go, without a record that says how: an edit to a listed file that no record covers
fails this gate. Each folder also has a PRIVACY-NOTE.md saying why `sha256sum -c` alone now fails and what to run.
The self-test makes a manifest with a true digest, a wrong one and a file that is not there, and needs OK,
MISMATCH and MISSING for them.
Usage: python3 tests/r167/test_evidence_manifests.py
"""
import glob
import hashlib
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import verify_evidence_manifest as v  # noqa: E402

EXPECTED = 8      # seven EVIDENCE.sha256 and win-v307-fixes' evidence-sha256.json


def main():
    os.chdir(ROOT)
    checks = fails = 0

    def report(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    chain, removed, copies = v.load_records()
    with tempfile.TemporaryDirectory() as tmp:
        m = os.path.join(tmp, 'T.sha256')
        true = hashlib.sha256(open('LICENSE.txt', 'rb').read()).hexdigest()
        open(m, 'w').write(f'{true} *LICENSE.txt\n{"0" * 64} *README.md\n{"1" * 64} *no-such-file.txt\n')
        counts, unexplained = v.verify(m, chain, removed, copies)
    report(counts == {'OK': 1, 'MISMATCH': 1, 'MISSING': 1} and len(unexplained) == 2,
           f'self-test: a true digest is OK, a wrong one MISMATCH, an absent file MISSING ({counts})')
    manifests = sorted(glob.glob('Windows-to-Sarvam/*/EVIDENCE.sha256') + glob.glob('Windows-to-Sarvam/*/evidence-sha256.json'))
    report(len(manifests) == EXPECTED, f'the {EXPECTED} evidence manifests are in the tree ({len(manifests)} found)')
    total = {}
    for m in manifests:
        counts, unexplained = v.verify(os.path.abspath(m), chain, removed, copies)
        for k, n in counts.items():
            total[k] = total.get(k, 0) + n
        line = ', '.join(f'{k} {n}' for k, n in sorted(counts.items()))
        report(bool(counts) and not unexplained, f'{m}: {line}'
               + ('' if not unexplained else f' -- {unexplained[0][0]} {unexplained[0][1]}'))
        report(os.path.exists(os.path.join(os.path.dirname(m), 'PRIVACY-NOTE.md')),
               f'{os.path.dirname(m)}: PRIVACY-NOTE.md says why sha256sum -c alone fails and what to run')
    entries = sum(total.values())
    print(f'r167 evidence manifests: {len(manifests)} manifests, {entries} entries ('
          + ', '.join(f'{k} {n}' for k, n in sorted(total.items())) + f'); {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
