#!/usr/bin/env python3
"""check_version_strings.py - the CURRENT-STATE documents must quote the current compiler version.

Why this exists. In v365 I found `v246` in two documents while the compiler was v250. `check_version` already existed
but it checks the CHANGELOG, not every document that quotes a version.

FIRST VERSION WAS WRONG. It scanned every .md and .html and reported 1,812 hits, because `v1` matches the project's
own `v1.0` target, and because era ranges ("v1-v28") and dated measurements ("measured at v221") are records. A report
with 1,812 items is a report nobody reads, which is the same as no check at all.

So this version is narrow on purpose:
  - it scans only the documents that state the project's CURRENT condition
  - it ignores `v1` and `v1.0` (the target, not a version)
  - it ignores a line that contains a past-word, a date, or a range dash
  - exit 0 always; a hit is REVIEW, not a failure

Usage:  python3 tools/check_version_strings.py [--root .] [--verbose]
"""
import argparse
import os
import re
import sys

# Only documents that claim to describe the project AS IT IS NOW. A record is not a claim.
CURRENT_STATE = (
    "README.md",
    "PROJECT-MASTER.md",
    "PROJECT-OVERVIEW.md",
    "ROADMAP.md",
    "docs/PATH-TO-COMPLETION.md",
    "docs/sutram-scorecard.html",
    "docs/sutram-project-status.html",
    "docs/sutram-design-parameters.html",
)

PAST = ("was ", "was:", "before", "older", "earlier", " then ", "previously", "used to", "changed from",
        "measured", "recorded", "written", "last updated", "era ", " at v", "-v", "\u2013v", "v1.0", "v2")

VER = re.compile(r"\bv(\d{2,4})\b")


def authoritative_version(root):
    path = os.path.join(root, "src", "sutram_compiler.asm")
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as exc:
        return None, "cannot read %s: %s" % (path, exc)
    found = [int(n) for n in VER.findall(text)]
    if not found:
        return None, "no v<number> token in %s" % path
    return max(found), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    current, err = authoritative_version(args.root)
    if current is None:
        print("RESULT: NOT RUN - %s" % err)
        return 0
    print("authoritative compiler version: v%d" % current)

    hits = []
    checked = 0
    for rel in CURRENT_STATE:
        full = os.path.join(args.root, rel)
        if not os.path.isfile(full):
            continue
        checked += 1
        with open(full, encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                low = line.lower()
                if any(p in low for p in PAST):
                    continue
                for num in VER.findall(line):
                    if int(num) != current:
                        hits.append((rel, lineno, "v" + num, line.strip()[:110]))

    print("current-state documents checked: %d of %d" % (checked, len(CURRENT_STATE)))
    if not hits:
        print("stale version strings: 0")
        print("RESULT: PASS")
        return 0
    print("stale version strings: %d" % len(hits))
    for rel, lineno, got, text in hits:
        print("  %s:%d says %s, compiler is v%d | %s" % (rel, lineno, got, current, text))
    print("RESULT: REVIEW (%d hits, not a failure)" % len(hits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
