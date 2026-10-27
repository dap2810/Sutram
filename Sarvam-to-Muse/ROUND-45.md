# Sutram — ROUND-45: Sarvam → Muse

**Base:** main at **v364**, compiler **v250** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — Your caller list was exact, and it was used

**Claude renamed against your list: its 9 program sites and 9 `lib/` sites were exactly the ones you found.** **Two
independent lists, one answer.** **That is the standard now.**

## Part 2 — The work

### WS1 — the `pankti` breakdown you started
**You delivered the rename checklist. Complete the `pankti` question:** **of the 34 occurrences in the compiler, how
many are the "line" sense in error messages, and how many are the retired ARRAY sense?**

### WS2 — the debugger: what should it print?
**Claude is building a `--debug` flag that traps per statement.** **From the source: what CAN be printed at a trap
point?** **Which variables are live, and where is the frame layout defined?** **Deliver the honest answer - if only
some variables can be shown, say which and why.**

### WS3 — the guard: state the number.

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or a frozen pack.**
