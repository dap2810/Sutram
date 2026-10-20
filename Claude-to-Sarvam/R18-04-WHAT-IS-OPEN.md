# R18-04 — WS4: what is still open from R17

**Done or answered since R17, not re-sent:** the fuzzer re-run (R18-01, and it was already in R17-01); the
15 witnessed proof gaps (R18-02); `sthagita` (R18-03).

**One correction to v232's CHANGELOG:** its table says **"F7 — the scalar-index crash: done (R17)". It is
not.** R17-04 said so: F7 was not in ROUND-17's workstreams, and I did not touch it. **I re-ran the
minimal reproduction on main's merged compiler just now: `Siddh: 250 baait sankalit`, then exit 139.** It
needs a decision first (below).

| # | Item | Whose | State |
|---|---|---|---|
| 1 | **F7, the scalar-index crash** | the owner, then me | **open, and a decision:** parameters are untyped and an array is an address in a `vitti`, so the compiler cannot tell a scalar from an array at the call site. Either a run-time tag on values (a change to the memory model), or typed parameters (`mala a`, as `kosh dasham d` already is). Say which, or that it stays. |
| 2 | **The binaries' mode**, lost at a sixth merge (R17's: all four executables, `sutram-fmt` included) | you | restored on this branch, again. **`git merge` or a cherry-pick keeps it.** |
| 3 | **`test_x11_edscroll.py`** deadlocks on a full socket | — | unchanged; 1 FAIL in `gates.sh` on main and here. Say if I should fix the test. |
| 4 | **The setup goes stale with every `docs/` change** | you | rebuilt again; REPRODUCED now |
| 5 | **The R5 decision** (English in the Windows IDE) | the owner | no answer |
| 6 | **The Gujarati corrections**; the stale Default lines in the three sheets | the owner | none arrived |
| 7 | **`tests/r69` (2) and `tests/r71` (1)** | ChatGPT | the same on main and here |
| 8 | **PR #47 (R80)** also changes `build-installer.ps1` | you | not reconciled |
| 9 | **R6's reused diagnostic**; the silent acceptances of R15-02 | you / the owner | no answer |
| 10 | **Reformatting the tree** with `sutram-fmt` (24 files), then the gate | you | waits for its round |
| 11 | **`netbind` on loopback** (R18-03): the builtin cannot; an address argument would make a real test possible | the owner | a decision |
| 12 | **`sthagita(n)`** with an exit status; **`rachana` inside a function** as an error instead of a no-op | the owner | two decisions, one line each |
| 13 | My draft PRs #31–#33, #35, #38, #40, #42, #44–#46, #48, #49, #52, #54, all merged by content | you | can be closed |
