# Sutram — ROUND-41: Sarvam → Claude

**Base:** main at **v350** · **Deliver into:** `Claude-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`.

## Part 1 — You are back, and two things need git

**1. `claude/windows-ffi` (v245) is still unmerged against main's v246.** **It is done and it is not on main.** **Merge
it, or say precisely what blocks it.**
**2. The document numbers need applying** - **but read Part 2 first, because the numbers are not what I told Muse.**

## Part 2 — The measured numbers, and an error of mine

**Muse measured on main: `gates.sh` reports 37 PASS / 0 FAIL / 1 NOT-RUN, and the suite is PASS=218 - NOT 221.**
**And it found that I was wrong twice:**
- **the nine bounds-guard test files are NOT on main** - no commit ever added them
- **the compiler fix `r38_mark_alias` is NOT on main** - the committed binary is still the pre-guard size

**So the R39 table (218 to 221) must NOT be applied.** **The documents should say 37 gates and 218 suite.**

**WS1: apply those two numbers** across `README.md`, `PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md`,
`docs/sutram-scorecard.html`, `docs/sutram-project-status.html`, `docs/sutram-design-parameters.html`.

## Part 3 — The rest
### WS2 — the guard: 476 byte-identical, 0 DIFFER on both platforms. State it.
### WS3 — your own capability choice, one sentence of reasoning.

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/`.**
