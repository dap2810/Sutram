# Evidence, R153 (v314, the package rebuilt; compiler unchanged), Linux container with Wine and Xvfb

- `first-contact-gate.txt` - gate R143 installer first contact, 16 checks, including the three R153 ownership checks.
- `first-contact-on-v314-engine.txt` - the same gate on v314's first engine: the three R153 checks fail.
- `flag-definitions.txt` - every line in the tree (briefs, reviews and hand-backs excluded) that names a mutant or budget flag: the source's guards and the two test gates.
- `gates.txt` - 78 PASS / 0 FAIL / 1 NOT-RUN; `package-gate.txt`, `installer-build.txt`, `installer-version.txt` - the rebuilt setup.
- `unchanged.txt` - the compiler and runtime are byte-unchanged since v314 (guard not re-run).

NOT RUN: tests/windows/test_installer_shortcuts.ps1 (no PowerShell here) and anything native.
