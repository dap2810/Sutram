# Sutram — ROUND-49: Sarvam → Claude

**Base:** main at **v384**, compiler **v253** · **Deliver into:** `Claude-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md`, `docs/PATH-TO-COMPLETION.md`, `docs/OPEN-ISSUES.md`.

## STATE
**Main at v384, compiler v253. Suite 225, corpus 227/0, proofs 226/226, signatures 305/305, gates 43 PASS / 0 FAIL /
1 NOT-RUN.** **A1 is CLOSED - three independent reproductions agreed it is a checked error, not a defect.**
**Windows is out of scope this round.**

## Part 1 — The one thing left that changes what the language is

### WS1 — THE DEBUGGER, USABLE (issue B2)
**It is correct and it prints everything.** **On a 200-line program that is thousands of lines, and nobody reads it.**

**Add, smallest version:**
- **`--debug=<name>` watches only that variable** - and say whether repeated flags work
- **`--debug-from=<line>`** starts printing at that line
- **a one-line summary at exit:** statements executed, and each scalar's final value

**Do NOT build a stepping UI, a REPL, or a breakpoint system.** **Three flags and a summary line.**

**And the guard: 0 DIFFER with the flag off, and state it.**

### WS2 — THE 15 MUTANTS: what you found in R48
**Your R48 handback covered WS1 and the guard but I cannot see the mutant split in the first lines.** **Deliver it as its
own section: which of the 15 are REAL wrong answers, which are indistinguishable, and fix the first group.**

**The `madhava_sin`/`cos`/`atan` sign error is the one that matters - a maths function returning a wrong-signed answer
passed 224 proofs.**

### WS3 — the guard, the suite, the corpus, the proofs.

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/` or `Windows-to-Sarvam/`.**
