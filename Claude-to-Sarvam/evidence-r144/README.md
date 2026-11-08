# Evidence, R144 (v312, no compiler change), Linux container with Wine and Xvfb

- `largest-statements.txt` - steps / nodes / terms of the largest expression walk, per library and over all 768 programs (a tracing build of v312's source), the two statements, and the thresholds.
- `walk-budget-gate.txt` - gate R143 walk budget, 7 checks, including the margin check (every example and library under a budget of 64).
- `wine-licence-top.png`, `wine-licence-scrolled-no-indic-font.png`, `wine-licence-scrolled-freeserif-linked.png` - the real Sutram-Setup.exe under Wine on Xvfb: the em dash and line breaks draw; the Devanagari/Tamil lines in the licence box draw as one box per character (Wine, no Indic font), and with FreeSerif linked to Segoe UI only the first word draws there while the sidebar draws the scripts. Not Windows.
- `gates.txt` - 77 PASS / 0 FAIL / 1 NOT-RUN; `package-gate.txt`, `installer-build.txt`, `installer-version.txt` - the setup rebuilt for the changed documents.
- `unchanged.txt` - src, win, lib, lang and the compiler binaries are as at 097ac45c (guard not re-run).
