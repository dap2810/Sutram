# ROUND-02 / WS5 — what I need, round two

**Date:** 2026-10-18

Of the nine ROUND-01 items, Sarvam took two (`gates.sh`, the build location). Of the remaining seven:

| R1 item | Still matters? | Why |
|---|---|---|
| 3 — register decision for diagnostics | **Done** (ROUND-02 Part 3 WS4). Thank you; it made WS4 a one-pass job. | — |
| 4 — un-doubling script + golden for F1 | **Done** by me (R2-01a). | — |
| 5 — a one-page diagnostics spec (stream, exit code, one location format) | **Still matters, now more.** Two of its four points are fixed (exit code, line numbers); the other two — **stdout vs stderr** and **one location format** (`file:L:C: Sutram Error [E_…]` in `--check` vs `Sutram Error: vyakaran dosh, pankti L:C` in normal mode, and `file:L:Sutram Error` with no column from `mg_print_loc`) — are design decisions I should not make silently. | translation is done; unifying the *shape* now costs little, later it costs a golden sweep |
| 6 — reserved-word diagnostic | Still matters, small. | `vitti band = 1` still says only `vyakaran dosh`. |
| 7 — one place for library signatures | Still matters, unchanged. | `LANGUAGE-REFERENCE.md` §4b is still 60 of 303. |
| 8 — environment | Nothing needed. | — |
| 9 — volunteered follow-ups | Two of four done (F1 golden, module-graph fixtures). The **documentation fixes** (`to`→`tak`, `.vardh`→`.inc`, the quoted messages — now also the new Sanskrit ones) and the **Devanagari-spelling decision table** remain on offer. | — |

## New this round

1. **Re-pin or release the source locks.** `tools/r68_review.lock.json`, `tools/r69_build.lock.json` and
   `docs/NEGATIVE-CORPUS.md` pin Git blobs of the compiler and its `.inc` files. The compiler's pin has
   been stale since v157; my `r66_indic_lexer.inc` change adds one more. Either the locks are re-pinned
   after each accepted change (and `tests/r68` becomes meaningful again), or they are declared
   historical. As it stands, a test fails on main for a reason nobody acts on.

2. **A rule for `\n`-adjacent renames.** Two people (Sarvam in v167, me ten minutes earlier) applied
   `\bayojan\b` to a Python test file and both left the seven occurrences after `\n` untouched. Any
   future rename sweep over Python/JSON fixtures should grep for the old name *without* word boundaries
   afterwards and expect zero. One line in `AGENTS.md` would do.

3. **`gates.sh`'s suite gate** needs to parse `PASS=/FAIL=` before trusting the exit code (R2-02, last
   section) — otherwise it reports FAIL on every run and the one gate meant to end drift starts it.

4. **A decision on `--version`'s number.** `msg_version` says `v160`; main is v167. If the string
   should track the changelog, say who bumps it; if not, drop the number from the banner.

5. **Which round tools are live.** Eleven `tools/r*_*.py` scripts match on English diagnostic text and
   will now disagree with the compiler. If none of them is a gate, a line in `PROJECT-MASTER.md` saying
   "round tools are frozen to their round's compiler" would save the next person an afternoon.

## What would make the next round faster

Sarvam's rule — read the current file from main before changing it — is the right one, and it cuts both
ways: while I worked, main moved three times (v165, v166, v167), and v167 touched the same test file I
was fixing. A short note in `Sarvam-to-Claude/` saying "I am about to touch X" (or simply not touching
a file assigned in an open brief) would avoid the next merge conflict. Everything else about the channel
works.
