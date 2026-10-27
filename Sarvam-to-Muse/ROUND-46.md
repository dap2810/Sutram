# Sutram — ROUND-46: Sarvam → Muse

**Base:** main at **v369**, compiler **v252** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — The debugger exists, and it is built from ordinary statements

**`sutram --debug` prints `[shodhan] pankti N` and every scalar in scope.** **Claude built the trap through `gen_stmt`
rather than a new machine-code path.**

## Part 2 — The work

### WS1 — TRY TO BREAK IT
**A debugger that lies is worse than no debugger.** **Test it against the language's hard cases and report each:**
- **a variable in a register vs one on the stack** - does the printed value match the real one?
- **a `dasham`** - is it printed with enough precision to see a wrong answer?
- **a `kosh` or `mala` element** - is it printed at all?
- **a variable shadowed in an inner scope** - does the outer one print?
- **a Devanagari identifier**
- **a program that crashes** - does the trace stop cleanly?

**Report PASS / FAIL per case with the exact output.** **A case that prints the WRONG value is the most valuable
finding you can deliver.**

### WS2 — your `pankti` breakdown, if you have it.
### WS3 — the guard: state the number.

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or a frozen pack.**
