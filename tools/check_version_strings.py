#!/usr/bin/env python3
"""check_version_strings.py - every document that quotes the compiler version must quote the current one.

Why this exists. In v365 I found four stale figures across three documents: `v246` in two of them while the
compiler was v250. `check_version` already existed but it checks the CHANGELOG, not every document that quotes a
version. So the class was covered in one place and open in the rest.

What it does. Reads the authoritative version from src/sutram_compiler.asm, then scans every tracked .md and .html
for a `v<digits>` token, and reports any that differ from it.

It is deliberately conservative:
  - a HISTORICAL file is exempt (docs/CHANGELOG.md, compiler/verified_snapshots/, backups/)
  - a line containing "was", "was:", "before", "older", "earlier" or "then" is exempt, because a sentence about a
    past version is a record, not a stale claim
  - exit 0 always; a hit is a review item, not a verdict. Wire it into gates.sh as a report, not a failure.

Usage:  python3 tools/check_version_strings.py [--root .] [--verbose]
"""
import argparse
import os
import re
import sys

HISTORICAL = ("docs/CHANGELOG.md", "compiler/verified_snapshots/", "backups/", "docs/sutram-roadmap.html")
PAST_WORDS = ("was ", "was:", "before", "older", "earlier", " then ", "previously", "used to", "changed from")
VER_RE = re.compile(r"\bv(\d{1,4})\b")


def authoritative_version(root):
    path = os.path.join(root, "src", "sutram_compiler.asm")
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as exc:
        return None, "cannot read %s: %s" % (path, exc)
    found = VER_RE.findall(text)
    if not found:
        return None, "no v<number> token in %s" % path
    # the compiler's own banner is the highest-numbered token in that file
    return max(int(n) for n in found), None


def scan(root, current, verbose=False):
    hits = []
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
        for name in filenames:
            if not name.endswith((".md", ".html")):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            if any(rel.startswith(h) or rel == h for h in HISTORICAL):
                continue
            scanned += 1
            try:
                with open(full, encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, 1):
                low = line.lower()
                if any(w in low for w in PAST_WORDS):
                    continue
                for num in VER_RE.findall(line):
                    if int(num) != current:
                        hits.append((rel, lineno, "v" + num, line.strip()[:120]))
    if verbose:
        print("scanned %d documents" % scanned)
    return hits, scanned


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

    hits, scanned = scan(args.root, current, args.verbose)
    if not hits:
        print("documents scanned: %d" % scanned)
        print("stale version strings: 0")
        print("RESULT: PASS")
        return 0

    print("documents scanned: %d" % scanned)
    print("stale version strings: %d" % len(hits))
    for rel, lineno, got, text in hits:
        print("  %s:%d  says %s, compiler is v%d  |  %s" % (rel, lineno, got, current, text))
    print("RESULT: REVIEW (%d hits, not a failure)" % len(hits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
