# R8-04 — WS4: what is still open from R7-04 (checked on main `221eee96`)

## Answered since R7-04, so not re-sent

| R7-04 item | Answered by |
|---|---|
| §1 merge order with ChatGPT's R75 | R7 merged first (v181/v182) |
| §10 ChatGPT installer defects | assigned in ROUND-76 (`ChatGPT-to-Sarvam/ROUND-76-WS4-INSTALLER.md`) |
| §13 the loop variable ends with the loop | accepted with the R7 merge; no action |
| §14 the non-name silent cases | answered by this round's WS2 (R8-02) |

## Still open

1. **First: F1, a function with more than 21 variables silently computes wrong values** (R8-01 §2).
   - It affects `chakravala`, `varna_bhed` and `khand_bhed` in the library today.
   - **Ask:** make the 15-site displacement fix the next round's first item, measured first.
2. **F2 to F6** (R8-01 §2). These are small; each needs a yes or no:

   | Finding | What | Size |
   |---|---|---|
   | F2 | `nirmmita` returns `-errno` on Linux | 4 instructions |
   | F3 | `guna` evaluates its value once per case | see R8-02 3b |
   | F4 | the `ganit_seemit` comment is wrong | comment or code |
   | F5 | `aadhar` lacks `yoj brihat` | 1 line |
   | F6 | the committed Linux binaries are not executable | `chmod` in git |

3. **R8-02: approve 1 + 2 + 3** (errors for assigning a `sutra`, for a misplaced `krama`, for a duplicate
   `bhavana`) **and 3b** (evaluate a `guna` value once)? Or a subset.
4. **The diagnostics decision** (R8-03): A–E, and whether the IDE follows it.
5. **The stdlib reference page** (`docs/sutram-stdlib-reference.html`) still has **30 lines** using the
   non-keyword `samapt`. Shall I rewrite and verify its samples?
6. **Devanagari spelling** of the compiled-in aliases (R1-WS2 §3.2). Unchanged.
7. **One diagnostics shape:** stdout vs. stderr; `file:L:C:` vs. `pankti L:C`. Best decided with item 4.
8. **The reserved-word hint, and one place for library signatures.** Unchanged.
9. **`gates.sh`** line 102 still says Windows was "never executed by anyone". The suggestion stands: report
   Windows from `check_accept_windows_log.py` on the latest committed log.
10. **One version number.** `--version` still prints **v160** on v183; the installer is `0.1.0`.
11. **The IDE shows temp file names in diagnostics** (`STGxxxx.tmp:2:11`). Unchanged.
12. **The owner's first Windows run** of `tools\accept-windows.ps1`. Still the only Windows evidence that
    would count.
13. **The words of the R7 diagnostics** (`punah ghoshana`, `tark diye; hastakshar me`, …). Still to confirm.
14. **ChatGPT's PR #36** (`r73-repin`) is still open. It is superseded unless you want its text.

## Housekeeping

- **Draft PRs #31–#33, #35, #38 and now #40** (ROUND-02 to ROUND-07) are still open, although their content is
  on main. They can be closed.
- **This round's PR is draft #42** (`claude/round-08`). It holds tools and tests only.
- **No `__pycache__` committed** (checked before the commit).
