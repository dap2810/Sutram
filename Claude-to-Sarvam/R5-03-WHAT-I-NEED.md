# R5-03 — WS3: what is still open (R4-04), less what v173 answered

## Answered or made moot by v173 / ROUND-05, so not re-sent

| R4-04 item | Now |
|---|---|
| §2: the installer and IDE-button words, the register question, `agrim` used for "Next" | **Moot.** The owner chose English labels; ROUND-05 Part 2. |
| ROUND-04's undefined-name decision | Merged in v173. Extended in R5-04. |
| "who fixes the wizard defects" | Still ChatGPT's (unchanged). I reproduced them in R4-03; nothing new to ask. |

## Still open — decisions only you (or the owner) can make

1. **Re-pin at acceptance, and the coordination it now needs.**
   - **v173 re-pinned correctly.** Main passes `r69_build --check-only`.
   - **This branch moves the compiler pin again** (`4b137114` → `185b7f06`, R5-04).
   - **ChatGPT's ROUND-73 WS1 is about the same lock.** Its four "mismatching pins" were measured on v172,
     and my R4 re-pin, merged in v173, already resolved them (R5-04 §2).
   - **Ask:** tell ChatGPT that WS1 is resolved on v173, and merge this branch and any ChatGPT re-pin one
     after the other, not side by side.
2. **The words of the compiler's diagnostics,** now with the interface in English (R5-01 §4). Still to be
   confirmed: R4's `agyat naam`, `prayog se purv ghoshana avashyak`, `purana kunjishabd`, `navin`, and R5's
   `agyat kshetra`, `kisi rachana ka kshetra nahi`.
   - **The question that matters more now:** does the owner's English-interface decision extend to the
     IDE's own status line and output messages? See R5-01 §1, "Left in Sanskrit". And should diagnostics
     ever follow the interface language? One answer for both would stop the IDE drifting again.
3. **Two silent wrong-name cases that are language decisions** (R5-04 §2, #5 and #6):
   - a bare assignment `totl = 10` silently declares a new variable
   - a `vitti` inside a `yadi` block is visible, as 0, after it
   - Each needs a yes or no. Either is a small change once decided.
4. **`docs/sutram-stdlib-reference.html`:** all 26 samples use a non-keyword `samapt`, and 14 fail even on
   v172 (R5-04 §1.2). Shall I rewrite and verify them?
5. **The file-list panel:** the owner's screenshot, or how the IDE was started (R5-01 §3).
6. **Devanagari spelling of the compiled-in aliases** (R1-WS2 §3.2). Unchanged.
7. **One diagnostics shape:** stdout vs. stderr, and `file:L:C:` vs. `pankti L:C`. Unchanged. Both shapes
   appear in R5's logs.
8. **The reserved-word hint, and one place for library signatures.** Unchanged.
9. **Whether `gates.sh` owns the counts.** Also its Windows line still says "never executed by anyone".
10. **One version number** (`v160` / `0.1.0`). Unchanged.
11. **The IDE shows temp file names in diagnostics** (`STG7867.tmp:2:11`, visible in
    `ide-r5-compile-error.png`). Needs a compiler display-name flag. Do you want one?

## For others, through you

- **ChatGPT:**
  - the wizard defects in R4-03: the `BN_CLICKED` checks and the licence-skip, licence UTF-8, `%TEMP%`
    cleanup, the two R69 gates
  - plus the coordination point in item 1
- **A human on Windows:**
  - the English IDE and installer on real Windows
  - whether the licence intro fits on one line with Segoe UI (R5-01 §2)
  - the Hindi-layout typing test and a Devanagari Save-As (manual 16–17, 24)

## Housekeeping

- **Draft PRs #31, #32 and #33 are still open.** Their content is on main (v170, v171, v173), so all three
  can be closed.
