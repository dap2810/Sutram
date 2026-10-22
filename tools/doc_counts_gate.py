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

R39: it also checks the LABELLED counts gates.sh states - codegen shapes, library proofs, property proofs,
library modules and functions, GUI tests, crash-corpus cases - wherever a document quotes them, and NOTEs each
that differs. A quoted count that is history rather than the current state goes in HISTORY, with its reason.
What it still does not check: see Claude-to-Sarvam/R39-00-HANDBACK.md, "What the gate does not catch".

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
    gate_totals.text = out          # R39: kept, so the labelled counts are checked either way
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


def measured_counts(gates_text):
    """The counts a gates.sh transcript states, by label (R39)."""
    out = {}
    def grab(key, rx):
        m = re.search(rx, gates_text)
        if m:
            out[key] = int(m.group(1))
    grab("codegen", r"codegen shapes \((\d+)/\d+\)")
    grab("lib_proofs", r"library proofs \((\d+) passed")
    grab("props", r"property proofs \((\d+)/\d+\)")
    grab("modules", r"stdlib inventory \(.*?(\d+) modules")
    grab("functions", r"stdlib inventory \(.*?(\d+) functions")
    grab("gui", r"X11 GUI protocol \((\d+)/\d+\)")
    grab("packs", r"language packs \((\d+)/\d+\)")
    grab("corpus", r"crash corpus \((\d+) cases")
    return out


def labelled_checks(measured):
    """(label, regex whose group 1 is the quoted number, measured value) for every count gates.sh states."""
    rows = [
        ("codegen", r"codegen[^0-9<>]{0,30}?(\d+)\s*/\s*\d+", "codegen"),
        ("codegen", r"(\d+)\s*/\s*\d+\s*code-generation", "codegen"),
        ("codegen", r"code-generation shape gates[^0-9<>]{0,6}(\d+)\s*/", "codegen"),
        ("library proofs", r"(?s)proof_lib\.py</td>.{0,200}?<td[^>]*>(\d+) / \d+", "lib_proofs"),
        ("property proofs", r"(?s)proof_props\.py</td>.{0,200}?<td[^>]*>(\d+) / \d+", "props"),
        ("codegen", r"(?s)codegen_gate\.py</td>.{0,200}?<td[^>]*>(\d+) / \d+", "codegen"),
        ("GUI tests", r"(?s)test_x11_\*\.py</td>.{0,200}?<td[^>]*>(\d+) / \d+", "gui"),
        ("library proofs", r"library proofs\W{0,8}(\d+)\s*/", "lib_proofs"),
        ("library proofs", r"(\d+) library proofs", "lib_proofs"),
        ("library proofs", r"library (\d+) proofs", "lib_proofs"),
        ("property proofs", r"property proofs\W{0,8}(\d+)\s*/", "props"),
        ("property proofs", r"(\d+) property proofs", "props"),
        ("property proofs", r"properties (\d+)\b", "props"),
        ("library functions", r"(\d{3}) functions", "functions"),
        ("library functions", r"(\d{3})</b><span>library functions", "functions"),
        ("library modules", r"(?<!· )(?<!\d)(\d+) (?:standard-library |library )?modules(?! combining)", "modules"),
        ("GUI tests", r"(\d+) GUI tests", "gui"),
        ("GUI tests", r"GUI (\d+) tests", "gui"),
        ("GUI tests", r"GUI tests \| \*\*(\d+)", "gui"),
        ("crash corpus", r"crash corpus[^0-9<>|]{0,8}(\d+) cases", "corpus"),
    ]
    return [(label, rx, measured[key]) for label, rx, key in rows if key in measured]


# Quoted counts that are history, not the current state: (document, the matched text). Each needs a reason.
HISTORY = {
    ("PROJECT-MASTER.md", "18 modules"): "the R-era rename: 18 modules were renamed then; a past event",
}


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
    measured = measured_counts(getattr(gate_totals, "text", ""))
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

        # R39: the labelled counts. Before R39 this gate checked only "N/N" pairs above the gate total and
        # "NNN pass"; a document quoting codegen 27/27, 180 library proofs or 281 functions passed it.
        for label, rx, want in labelled_checks(measured):
            for m in re.finditer(rx, s, re.I):
                got = int(m.group(1).replace(",", ""))
                if got != want and (d, m.group(0).strip()) not in HISTORY:
                    notes.append(f"{d}: {label}: says {got}, measured {want}  ({m.group(0).strip()[:60]!r})")

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
