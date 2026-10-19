# R7-04 — WS4: what is still open from R6-04 after v178–v180

## Answered by v178–v180, or by this round, so not re-sent

| R6-04 item | Now |
|---|---|
| §9 the committed Windows binaries are stale | **Done this round.** Rebuilt, committed with hashes and their log, and reproducible (R7-03). |
| ChatGPT's baseline blocker | **Answered in v179:** its R74 shows 14/14 pins MATCH and a reproducible build. |

## Still open

1. **Merge order with ChatGPT's ROUND-75. This is new and matters most.**
   - `tools/r75_reclaim_prepare.py` on PR #39 pins `src/sutram_compiler.asm` at **`185b7f06`** (v180).
   - This branch changes that file (it is now `cc5cfbe4`).
   - **Whichever merges second must be re-targeted.** Either ChatGPT's prepare step is re-pinned to the R7
     blob after this merges, or this branch is rebased over its reclamation.
   - PR #39 is otherwise additive (4 new files), so there is no textual conflict, only the pin.
   - **Ask:** merge one, then have the other re-pin, as with R73.
2. **ChatGPT's PR #36** (`r73-repin`) is still open. Its `repinned` text conflicts with every later
   re-pin; keep both texts if it is ever merged. Otherwise it is superseded by v179's 14/14.
3. **The stdlib reference page:** all 26 samples use the non-keyword `samapt`. Still so on v180.
   - v180's Step 6 covered "the six books and the language reference", and that is accurate. **This page
     is a seventh document, not covered.**
   - **Ask:** shall I rewrite and verify its 26 samples?
4. **Devanagari spelling** of the compiled-in aliases (R1-WS2 §3.2). Unchanged.
5. **One diagnostics shape:** stdout vs. stderr; `file:L:C:` vs. `pankti L:C`. **Best decided with R7-02.**
6. **The reserved-word hint, and one place for library signatures.** Unchanged.
7. **`gates.sh`:** line 97 still says Windows was "never executed by anyone". The suggestion stands:
   report Windows from `check_accept_windows_log.py` on the latest committed log.
8. **One version number** (`--version` v160; installer `0.1.0`). Unchanged.
9. **The IDE shows temp file names in diagnostics** (`STGxxxx.tmp:2:11`); this needs a display-name flag.
   Unchanged.
10. **For ChatGPT:**
    - a failed install leaves a half-install that a retry refuses
    - a successful uninstall gives the user no confirmation
    - optional Wine hardening: `IconLocation` with `,0`, and a null check on `TargetPath`
11. **The owner's first Windows run** of `tools\accept-windows.ps1`, now on binaries that match the source.

## New this round — decisions, small

12. **The words of the new diagnostics** (R7-01): `punah ghoshana`, `ek khand { } ya chakra me ghoshit hai;
    uske bahar drishya nahi`, `tark diye; hastakshar me`, `yoj patra aprapt`, `do rachana me alag sthan par`.
    Please confirm or replace them.
13. **Loop variable scoping** (R7-01): it now ends with the loop, as in C. If you want it to stay visible
    after the loop, it is a three-line revert.
14. **Three non-name silent cases** (R7-01, "What is not a name-resolution path"):
    - assigning to a `sutra` constant
    - `agrim` / `krama` outside a loop
    - duplicate `bhavana` labels

    Each is a small check. Say if you want them in Step 1.

## Housekeeping

- **Draft PRs #31–#33, #35 and #38 (ROUND-02 to ROUND-06) are still open**, although their content is on
  main. They can be closed.
- **No `__pycache__` committed.** `git diff --cached --name-only | grep -c pycache` → 0 before every commit.
