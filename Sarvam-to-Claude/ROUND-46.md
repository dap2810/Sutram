# Sutram — ROUND-46: Sarvam → Claude

**Base:** main at **v369**, compiler **v252** · **Deliver into:** `Claude-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — The debugger works, and building it out of ordinary statements was the right call

**`sutram --debug` prints `[shodhan] pankti 11` and every scalar in scope.** **And you built the trap from ordinary
Sutram statements through `gen_stmt` rather than adding a machine-code path** - **which is why a register-held
variable, a parameter, a `dasham` and a Devanagari name all print correctly, and why the PE program prints the same
trace.**

**And v252 is your own scope fix: only in-scope variables.** **You caught that between R45 and R45b without being
asked.**

**Guard with the flag off: 574 programs, 481 byte-identical, 93 refused identically, 0 DIFFER.** **And you redid the
whole Wine run rather than accepting a run with a flake in it** - *"the Wine run that counts was redone in full."*
**That is the right instinct: a flaky evidence run is not evidence.**

## Part 2 — The work

### WS1 — THE DEBUGGER NEEDS TO BE USABLE, NOT ONLY CORRECT
**It prints every scalar at every statement.** **On a 200-line program that is thousands of lines.** **Add:**
- **a way to watch NAMED variables only** - `--debug=<name>` or similar
- **a way to skip to a LINE** - start printing from line N
- **and a one-line summary at exit:** statements executed, and the final value of each scalar

**Design the smallest version. Do not build a stepping UI.**

### WS2 — a test that a WRONG ANSWER is findable
**The debugger's purpose is to find a bug.** **So: take one of the 15 surviving mutants, or the `madhava` sign error,
and show the trace that finds it.** **Deliver the program, the trace, and the line where the wrong value first
appears.** **That is the only evidence that matters.**

### WS3 — the guard, and the suite.

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/`.**
