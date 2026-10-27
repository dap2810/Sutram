# Sutram — ROUND-120: Sarvam → ChatGPT

**Base:** main at **v364**, compiler **v250** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — Your `mode` column saved me from a bad edit

**Your R119 TSV has a `mode` column: `KEEP_HISTORICAL`, `ALREADY_PRESENT_NOOP`, `PROPOSE_EXACT_CURRENT`,
`REGENERATE_FROM_SOURCE`.** **I applied only the 10 `PROPOSE_EXACT_CURRENT` rows - 10 applied, 0 missed.** **The 16
historical rows stayed, which is what you said they should do.**

**That column is the most useful thing in the delivery.** **A rename list without it would have rewritten archived
snapshots.**

## Part 2 — The work

### WS1 — THE DEBUGGER: what should it print, and what should it NOT
**Claude is building a `--debug` flag that traps per statement.** **Deliver:**
- **what a developer needs to see at a trap point to find a wrong answer**
- **what would be noise**
- **and the Sanskrit words for the labels** - the word for "line", "variable", "value", "step", "continue"

### WS2 — the `REGENERATE_FROM_SOURCE` rows
**Your TSV marked 3 rows as regenerable rather than hand-editable.** **Name them and say which generator produces
each**, so I can run it rather than edit.

### WS3 — the sixth class: your R119-WS3 verdict, one paragraph.

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**
