# Sutram — ROUND-45: Sarvam → Claude

**Base:** main at **v364**, compiler **v250** · **Deliver into:** `Claude-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — The rename landed cleanly, and your guard was the right shape

**One commit, revertible whole. 574 programs: 480 byte-identical, 93 refused identically, 0 DIFFER, 1 new.** **And it
held on all three paths.** **And you checked against Muse's independent caller list** - its 9 program sites and 9
`lib/` sites were exactly the ones renamed.

**The suite is now PASS=224 and gates 41 / 0 / 1.**

## Part 2 — The work: the next real capability

**The owner has set the next phase. The first item is the one that changes what the language IS.**

### WS1 — A DEBUGGER. The smallest useful version.
**Not gdb. A compile flag - `--debug` or `SUTRAM_DEBUG` - that:**
- **emits a trap on each statement**
- **prints the LINE and the live variables**
- **and lets the program continue**

**Design it as small as possible.** **A developer who cannot see why a wrong answer happened leaves the language.**
**That is the single biggest gap and the owner named it first.**

**And it must not touch normal builds: the guard is 0 DIFFER with the flag off.**

### WS2 — the guard, and the suite.

### WS3 — your own capability choice, one sentence.

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/`.**
