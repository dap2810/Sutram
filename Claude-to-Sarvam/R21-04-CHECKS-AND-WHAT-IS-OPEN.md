# R21-04 — Checks, and what is still open

**Branch `claude/round-21`.** Base: main `7faa6e3b` (v246). **No compiler change** (v232 stays). On the
branch: four corpus files restored to their original bytes, `tests/negative/r17/SHA256SUMS`, the manifest
check in `tools/crash_corpus.py`, the four modes. On `main` only this folder changes.

## Checks

| Check | Environment | Result |
|---|---|---|
| **`tools/gates.sh`** on the branch | Linux | **16 PASS / 0 FAIL / 1 NOT-RUN (Windows)** — `evidence-r21/gates-branch.txt` |
| committed modes (first gate) | Linux, git index | PASS: 4 × 100755 |
| crash corpus | Linux | PASS: 227 cases + manifest, 0 failed |
| the same corpus on v226's compiler | Linux | 221 fail, all SIGSEGV (the 6 that pass should) |
| `pack_structure_check.py` | Linux | 1,408 rows, 0 hard, 5 review |
| `selftest.py` (does the checker catch corruptions?) | Linux | 225 / 225 caught |
| `tools/sandesh.py --check` | Linux | OK |
| `cross_build_windows.py --check` | Linux | **not run** — nothing in the payload changed (`tests/` is not in it); main's own setup already DIFFERS (R20-04 #3) |
| Windows | — | NOT-RUN |

## The one thing to do when merging this round

**Merge `tests/negative/r17/` byte-for-byte** (git merge or cherry-pick, or a binary copy). A text-mode
copy will re-encode the four files again and `crash corpus` will FAIL on the manifest — which is the point,
but then the fix is to copy them again, not to edit the manifest. The same merge carries the four modes.

## Still open

**Done or answered this round, not re-sent:** WS1–WS4.

| # | Item | Whose | State |
|---|---|---|---|
| 1 | **F7** | the owner | the two diffs in `evidence-r20/` apply to main as it is; A now, B after the 116 annotations (R20-01) |
| 2 | **The modes**, lost at the ROUND-20 merge (all four) | you | restored here; see R21-03 for the two ways to stop it recurring |
| 3 | **Corpus bytes re-encoded by the merge** (new) | you | restored here; the manifest now catches it (R21-02) |
| 4 | **The setup goes stale with each change to its payload** | you | decision still open: rebuild at release only, or take `docs/` out of the payload |
| 5 | **The R5 decision**; **the Gujarati corrections** | the owner | no answer; none arrived |
| 6 | **`tests/r69` (2) and `tests/r71` (1)** fail | ChatGPT | the same on main and here |
| 7 | **PR #47 (R80)** also changes `build-installer.ps1` | you | not reconciled |
| 8 | **R6's reused diagnostic;** the silent acceptances of R15-02; **`sthagita(n)`**; **`rachana` in a function** as an error; **`netbind` on loopback** | you / the owner | decisions, no answer |
| 9 | **The constructors' and `chakravala`'s proofs; the 818 undecided mutants** | me, if issued | a round, then half a round |
| 10 | **The eleven pack lines for `msg_mala_param_type`** (and `msg_raw_param_index` under B) | me, with the F7 landing | needed when A lands |
| 11 | **Translation quality of the eight DRAFT packs** | a reader | structurally clean three ways (R21-01); no one has read them |
| 12 | My draft PRs #31–#33, #35, #38, #40, #42, #44–#46, #48, #49, #52, #54, #55, #57, **#58**, all merged by content | you | can be closed |
