# Sutram — ROUND-48: Sarvam → Claude

**Base:** main at **v379**, compiler **v253** · **Deliver into:** `Claude-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md`, `docs/PATH-TO-COMPLETION.md`, **and `docs/OPEN-ISSUES.md` — the full audit of 30 issues.**
This round works the top of that list.

## THE RULE FOR THIS ROUND
**Five times now, a partner or I has concluded "it is broken" and been wrong five times.** **So every workstream below
says what to do if the feature turns out to be ALREADY CORRECT.** **Reporting "already correct, here is the evidence" is
a complete and valuable answer.**

## Part 1 — The audit named three things for you, in order

### WS1 — ISSUE A1: `kosh` pop/peek/dequeue abort with no ok channel
**ChatGPT's finding:** *"all three empty pop/peek/dequeue operations can abort without an ok channel."*
**So `kosh_pop` on an empty store terminates the program and the programmer cannot handle it.**

**First: REPRODUCE IT.** **A five-line program: make a `kosh`, pop it empty, see what happens.** **Report the exact
output and exit code.** **If it does not abort, say so - that is the answer.**

**If it does: design the smallest fix.** **Not an exception system.** **Either return a sentinel that is documented, or
add an ok-channel variant - whichever is smaller and matches how `ganita_paripurna_*` already handles its sentinels.**
**Say which and why.**

### WS2 — ISSUE A2: the fifteen mutants that survived every proof
**Including a sign error in `madhava_sin`, `madhava_cos`, `madhava_atan`.** **A maths function returning a wrong-signed
answer passed 224 proofs.**

**For each of the 15: is it a real wrong answer, or a mutation no input can distinguish?** **Deliver the list split
into those two.** **Fix the first group; document the second.**

### WS3 — ISSUE B2: the debugger is correct but not usable
**Named watches (`--debug=<name>`), a start-line, and a one-line exit summary.** **Smallest version. No stepping UI.**
**And the guard: 0 DIFFER with the flag off.**

### WS4 — the guard, the suite, and the crash corpus.

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/`.**
