#!/usr/bin/env python3
"""tools/version_gate.py — the version-consistency gate.

Why this exists: the compiler's `--version` string is the FIRST line a user reads and the LAST
thing anyone remembers to update. It is hand-written, with no test behind it, and it has drifted
silently twice:

  * it once read `v160` while the project was at v182  (the owner found it himself, on install)
  * it then read `v182` while the compiler had changed twice more (found in an audit)

Every other number in this project is measured by a gate. This one was typed by hand. So:

  FAIL  the version string is missing or malformed - nothing can be checked without it
  PASS  the version string is present and well-formed
  NOTE  it lags the CHANGELOG by more than a small amount (reported, not failed)

The NOTE is not a FAIL on purpose. The compiler may change several times between releases, and
a hard failure would fire on every one of them - which trains people to ignore the gate. What
matters is that the lag is VISIBLE rather than discovered by a user on install.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "src", "sutram_compiler.asm")
LOG = os.path.join(ROOT, "docs", "CHANGELOG.md")
LAG_WARN = 5          # more than this many changelog versions behind -> NOTE


def main():
    if not os.path.exists(SRC):
        print("  src/sutram_compiler.asm not found")
        return 2

    src = open(SRC, encoding="utf-8", errors="replace").read()

    # the version string the compiler prints
    m = re.findall(r"Sutram 1\.0 \(v(\d+)\)", src)
    if not m:
        print("  FAIL: no version string of the form 'Sutram 1.0 (vNNN)' in the compiler source")
        return 1
    vers = sorted({int(x) for x in m})
    if len(vers) > 1:
        print(f"  FAIL: the compiler carries {len(vers)} different version strings: {vers}")
        return 1
    ver = vers[0]

    # the changelog's newest version
    top = 0
    if os.path.exists(LOG):
        log = open(LOG, encoding="utf-8", errors="replace").read()
        tops = re.findall(r"^## v(\d+)", log, re.M)
        if tops:
            top = max(int(x) for x in tops)

    print(f"  compiler says: v{ver}")
    print(f"  CHANGELOG top: v{top}")
    if top and top - ver > LAG_WARN:
        print(f"  NOTE: the version string lags the CHANGELOG by {top - ver} versions.")
        print("        Not a failure - the compiler may change between releases. But it is the")
        print("        first line a user reads, and it has drifted silently twice. Bump it.")
    elif top:
        print(f"  version string is within {LAG_WARN} of the CHANGELOG")
    print("  version string present and well-formed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
