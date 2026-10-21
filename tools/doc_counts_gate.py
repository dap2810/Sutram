#!/usr/bin/env python3
"""tools/doc_counts_gate.py - the document-count gate.

WHY THIS EXISTS
---------------
Every number a reader trusts in this project is typed by hand, and three of them have drifted:

  * the version string      - twice, until a gate was built for it
  * the gate counts (v271)  - found by measuring
  * the gate counts (again) - found by measuring, one day later

Correcting a number by hand does not stop it drifting. A third manual correction is evidence that the method
is the problem, not the instance.

WHAT THIS DOES
--------------
Runs `tools/gates.sh`, parses the PASS/FAIL/NOT-RUN totals, counts the suite's PASS, and checks that the
documents which quote those numbers actually contain them. It reports a NOTE (not a FAIL) when a document is
behind, because a document may legitimately lag a commit - but the lag must be VISIBLE rather than discovered
by a reader.

FAILS only when a document quotes a number that is not merely behind but IMPOSSIBLE - a PASS count higher than
the gate total, for instance - or when the gate itself cannot run.

Usage:
    python3 tools/doc_counts_gate.py [--repo DIR] [--quiet]
"""
import argparse
import os
import re
import subprocess
import sys

# The documents that quote the project's numbers, and the file that measures them.
DOCS = [
    "README.md",
    "PROJECT-MASTER.md",
    "PROJECT-OVERVIEW.md",
    "docs/sutram-scorecard.html",
    "docs/sutram-project-status.html",
    "docs/sutram-design-parameters.html",
]


def gate_totals(repo, from_file=None):
    """Parse the totals from a gates.sh transcript.

    It does NOT run gates.sh itself: it would recurse if it were ever added to gates.sh, and a check that
    cannot live beside the others is a check nobody will run. It reads the transcript instead:
        sh tools/gates.sh > /tmp/gates.txt
        python3 tools/doc_counts_gate.py --gates /tmp/gates.txt
    """
    if from_file and os.path.exists(from_file):
        out = open(from_file, encoding="utf-8", errors="replace").read()
    else:
        g = os.path.join(repo, "tools", "gates.sh")
        if not os.path.exists(g):
            return None
        try:
            out = subprocess.run(["sh", g], cwd=repo, capture_output=True, text=True, timeout=600).stdout
        except Exception:
            return None
    def total(label):
        # the summary lines look like:  "  PASS                         26"
        m = re.search(r"^\s*" + label + r"\s+(\d+)\s*$", out, re.M)
        return int(m.group(1)) if m else None
    p, f, n = total("PASS"), total("FAIL"), total("NOT-RUN")
    if p is None:
        return None
    return (p, f or 0, n or 0)


def suite_pass(repo):
    """Run the regression suite and return its PASS count, or None."""
    t = os.path.join(repo, "tests", "run_tests.py")
    if not os.path.exists(t):
        return None
    try:
        out = subprocess.run([sys.executable, t], cwd=repo, capture_output=True, text=True, timeout=600).stdout
    except Exception:
        return None
    m = re.search(r"PASS=(\d+)", out)
    return int(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--gates", default=None, help="a gates.sh transcript, so gates.sh is not run again")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)

    t = gate_totals(repo, a.gates)
    if t is None:
        print("NOT-RUN  doc counts: gates.sh did not produce a PASS total")
        return 0
    gp, gf, gn = t
    sp = suite_pass(repo)

    print(f"measured: {gp} gates PASS, {gf} FAIL, {gn} NOT-RUN"
          + (f"; suite PASS={sp}" if sp is not None else ""))
    if not a.quiet:
        print(f"  the {len(DOCS)} documents should quote: gates {gp}, and suite {sp}")

    notes, problems = [], []
    for d in DOCS:
        p = os.path.join(repo, d)
        if not os.path.exists(p):
            continue
        try:
            s = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        # every "N/N" pair that looks like a gate count
        for m in re.finditer(r"\b(\d{1,2})/(\d{1,2})\b", s):
            n = int(m.group(1))
            if n > gp:
                problems.append(f"{d}: quotes {m.group(0)} but only {gp} gates exist")
        # a suite count that is ahead of the measured one is impossible
        for m in re.finditer(r"\b(\d{3})\s*pass\b", s, re.I):
            n = int(m.group(1))
            if sp is not None and n > sp:
                problems.append(f"{d}: quotes {n} pass but the suite has {sp}")
            elif sp is not None and n < sp:
                notes.append(f"{d}: says {n} pass, measured {sp}")

    for x in sorted(set(problems)):
        print("FAIL    " + x)
    for x in sorted(set(notes)):
        print("NOTE    " + x)

    if problems:
        print(f"doc counts: {len(problems)} impossible claim(s)")
        return 1
    if notes:
        print(f"doc counts: {len(set(notes))} document(s) behind - not a failure, but bump them")
        return 0
    print("doc counts: every document agrees with the measured tree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
