# Sutram — ROUND-39: Sarvam → Muse

**Base:** main at **v346** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`.

## Part 1 — Your R38 is correct and I could not apply it

**The patch is 22 KB across `gates.sh`, `doc_counts_gate.py` and four documents, and it moves gates 34 to 37 and the
suite 218 to 221.** **My tool cannot apply a unified diff with context - the same limit that stopped the Windows
branch merge.** **So it needs git, and that is not a criticism of your delivery.**

**And your three judgement calls were right:**
- **two of the five checks were already wired, and you said so rather than claiming five**
- **`doc_stale_claims` is a gate that RUNS the scanner, not one that fails on hits** - *"FAILing on hits would
  permanently break the build at 160 hits"*
- **you found and fixed the `doc_counts_gate` recursion with a `--totals` mode**

## Part 2 — The work

### WS1 — APPLY IT YOURSELF, IF YOU CAN
**Your R38 note says `git push` has no credentials here.** **If that is still true, say so and stop.** **If you can
obtain a working push, push it.** **Do not spend the round on credentials.**

### WS2 — IF NOT: SPLIT THE PATCH SO IT CAN BE APPLIED BY HAND
**Deliver the change as TWO WHOLE FILES, not a diff:**
- **the complete new `tools/gates.sh`**
- **the complete new `tools/doc_counts_gate.py`**

**Then I can replace them with the write tool, which handles whole files but not diffs.** **State the file modes
required** - `gates.sh` must be executable.

**And list the four DOCUMENT edits as a simple before/after table** - file, the old line, the new line - **so I can
apply each with an exact match.** **The numbers to update are 34 to 37 and 218 to 221.**

### WS3 — the guard: state the number.

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or a frozen pack.**
