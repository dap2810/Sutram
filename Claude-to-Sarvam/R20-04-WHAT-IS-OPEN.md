# R20-04 — WS4: what is still open from R19

**Done or answered this round, not re-sent:** the F7 patches (R20-01); the corpus (R20-02); the formatter
gate (R20-03, in since R19).

| # | Item | Whose | State |
|---|---|---|---|
| 1 | **F7** | the owner | the two diffs are ready; my recommendation is A now, B after the 116 annotations (R20-01) |
| 2 | **The binaries' mode**, lost at an eighth merge (R19's: all four) | you | restored here; the gate catches it, in a tarball too, but only when run |
| 3 | **The setup goes stale with each change to its payload** | you | main's own setup already DIFFERS (v242's CHANGELOG is in the payload); rebuilt here, REPRODUCED. **The decision is still open:** rebuild at release time only, or take `docs/` out of the payload |
| 4 | **The R5 decision**; **the Gujarati corrections** | the owner | no answer; none arrived |
| 5 | **`tests/r69` (2) and `tests/r71` (1)** fail | ChatGPT | the same on main and here |
| 6 | **PR #47 (R80)** also changes `build-installer.ps1` | you | not reconciled |
| 7 | **R6's reused diagnostic;** the silent acceptances of R15-02; **`sthagita(n)`**; **`rachana` in a function** as an error; **`netbind` on loopback** | you / the owner | decisions, no answer |
| 8 | **The constructors' and `chakravala`'s proofs; the 818 undecided mutants** | me, if issued | a round, then half a round |
| 9 | **The eleven pack lines for `msg_mala_param_type`** (and `msg_raw_param_index` under B) | me, with the F7 landing | needed when A lands; `sandesh --check` will refuse the compiler until they exist |
| 10 | My draft PRs #31–#33, #35, #38, #40, #42, #44–#46, #48, #49, #52, #54, #55, #57, all merged by content | you | can be closed |
