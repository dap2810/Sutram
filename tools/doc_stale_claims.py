#!/usr/bin/env python3
"""tools/doc_stale_claims.py - find claims of ABSENCE in the documents that may have gone stale.

WHY THIS EXISTS (ROUND-32)
---------------------------
This project had no check for a claim of absence going stale. Seven documents
stated a limit that had already been removed - separate compilation,
first-class functions, the Windows run - and every gate missed it, because
gates check that things WORK, not that the documents stopped saying they do
not exist.

WHAT THIS DOES
--------------
Scans every `.md` and `.html` file outside the collaboration folders and
`backups/` for sentences shaped like absence claims ("there is no X",
"not yet implemented", "never been run", ...). It reports each hit with the
file, the line number and the sentence, for a human to confirm or clear.

WHAT THIS DOES NOT DO
---------------------
**This check is a floor, not a proof.** It finds sentences shaped like absence
claims; it cannot decide whether a claim is still true. A hit is a prompt for
a person, not a verdict. (The way check_alloc_bounds.py says reviewed
spellings are accepted, NOT certified safe.)

Usage:
    python3 tools/doc_stale_claims.py [--repo DIR] [--quiet]

Exit 0 always; hits are review items, not failures.
"""
import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Top-level directories that are correspondence, not documentation.
EXCLUDE_DIRS = {
    "backups",
    "ChatGPT-to-Sarvam",
    "ChatGPT-to-Sarvam-Clean",
    "Claude-to-Sarvam",
    "Muse-to-Sarvam",
    "Sarvam-to-ChatGPT",
    "Sarvam-to-ChatGPT-Clean-Project",
    "Sarvam-to-ChatGPT-Windows",
    "Sarvam-to-Claude",
    "Sarvam-to-Muse",
    "Windows-to-Sarvam",
}

# Sentence shapes that mean "not yet" / "does not exist". Each is
# (name, regex). The regex should match the claim phrase; the report
# shows the whole sentence around it.
PATTERNS = [
    ("there-is-no",
     r"\bthere\s+(is|are)\s+no\b"),
    ("no-capability",
     r"\bno\s+(separate compilation|first-class functions?|ffi\b|generics|concurrency|events?|"
     r"windows\s+(support|execution|build)|native\s+execution|kernel\s+demonstration)\b"),
    ("not-implemented",
     r"\bnot\s+(yet\s+)?(implemented|supported|available)\b"),
    ("never-done",
     r"\bnever\s+(been|had|run|executed|implemented|tested)\b"),
    ("does-not-exist",
     r"\bdoes\s+not\s+(yet\s+)?(exist|work|support|compile|run)\b"),
    ("no-longer-true",
     r"\bis\s+not\s+(true|correct|the case)\s+anymore\b"),
    ("missing-feature",
     r"\b(missing|absent|lacking)\s+(feature|support|implementation)\b"),
    ("not-on-roadmap",
     r"\bnot\s+on\s+the\s+(critical path|roadmap)\b"),
]

TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text):
    return TAG_RE.sub(" ", text)


def sentences_around(text, start, end, width=200):
    """The sentence containing the match, crudely cut at . ! ? boundaries."""
    lo = max(0, text.rfind(".", 0, start), text.rfind("!", 0, start),
             text.rfind("?", 0, start)) + 1
    hi = len(text)
    for c in (".", "!", "?"):
        p = text.find(c, end)
        if p != -1:
            hi = min(hi, p + 1)
    s = text[lo:hi].strip()
    s = re.sub(r"\s+", " ", s)
    if len(s) > 2 * width:
        # cut around the match instead
        mid = (start + end) // 2 - lo
        a = max(0, mid - width)
        s = ("..." if a > 0 else "") + s[a:a + 2 * width] + "..."
    return s


def scan_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except OSError:
        return []
    text = strip_html(raw) if path.endswith(".html") else raw
    # line numbers refer to the stripped text for html; good enough for a human
    lines = text.split("\n")
    hits = []
    for name, rx in PATTERNS:
        for m in re.finditer(rx, text, re.I):
            lineno = text.count("\n", 0, m.start()) + 1
            sent = sentences_around(text, m.start(), m.end())
            # skip code spans that merely name a negative test
            if re.search(r"`[^`]*" + re.escape(m.group(0)) + r"[^`]*`", sent, re.I):
                continue
            hits.append((lineno, name, m.group(0), sent,
                         lines[lineno - 1].strip()[:120] if lineno <= len(lines) else ""))
    # de-dup identical (line, phrase) pairs
    seen, out = set(), []
    for h in hits:
        key = (h[0], h[2].lower())
        if key not in seen:
            seen.add(key)
            out.append(h)
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--quiet", action="store_true",
                    help="only the summary line")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)

    files, hits = 0, []
    for root, dirs, names in os.walk(repo):
        rel = os.path.relpath(root, repo)
        top = rel.split(os.sep)[0]
        if top in EXCLUDE_DIRS or rel.startswith(".git"):
            dirs[:] = []
            continue
        # do not descend into excluded dirs nested deeper either
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and d != ".git"]
        for n in sorted(names):
            if n.endswith((".md", ".html")):
                p = os.path.join(root, n)
                files += 1
                for h in scan_file(p):
                    hits.append((os.path.relpath(p, repo),) + h)

    if not a.quiet:
        print("stale-claim scan: %d documents, %d absence-shaped sentences" %
              (files, len(hits)))
        print("THIS CHECK IS A FLOOR, NOT A PROOF: it finds sentences shaped like")
        print("absence claims; it cannot decide whether a claim is still true.")
        print("Each hit is for a human to confirm or clear.")
        print()
        for path, lineno, name, phrase, sent, _ in hits:
            print(f"{path}:{lineno} [{name}]")
            print(f"    {sent}")
    else:
        print(f"stale-claim scan: {files} documents, {len(hits)} hits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
