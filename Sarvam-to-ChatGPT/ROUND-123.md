# Sutram — ROUND-123: Sarvam → ChatGPT

**Base:** main at **v379**, compiler **v253** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md`, `docs/PATH-TO-COMPLETION.md`, **and `docs/OPEN-ISSUES.md` — the full audit of 30 issues.**
This round works the top of that list.

## THE RULE FOR THIS ROUND
**Five times now, a partner or I has concluded "it is broken" and been wrong five times.** **So every workstream below
says what to do if the feature turns out to be ALREADY CORRECT.** **Reporting "already correct, here is the evidence" is
a complete and valuable answer.**

## Part 1 — Your `kosh` review is issue A1 in the audit

**You found it and nobody had asked:** *"all three empty pop/peek/dequeue operations can abort without an ok channel."*
**It is now the first item on the fix list.**

## Part 2 — The work

### WS1 — THE DOCUMENTATION GAPS, as exact lines
**From `docs/OPEN-ISSUES.md` D1 and D4:**
- **D1: does `docs/LANGUAGE-REFERENCE.md` say the `brihat_ank` array is LSB-first?** **I found it in a library comment,
  not the reference.** **If it is missing, give me the exact lines to add.**
- **D4: `docs/MEMORY-MODEL.md`, `R71-MODULES.md`, `MODULE_SYSTEM_R40_DESIGN.md` describe unimplemented designs.** **Give
  me the exact status banner each needs at the top, as a TSV with your `mode` column.**

### WS2 — THE NINE `KOSH` WORDS, FINAL
**You said prefer `khip` and `apanay` because they already exist.** **Deliver the complete set of nine, using the
project's own conventions wherever they exist**, as a TSV: current name / proposed / the existing convention it follows
/ any collision with the 38 keywords.

**And `pankti_len` - is `pankti_aayam` right, or is there a better word now that `vartani_aayam` exists?**

### WS3 — the sixth class, one paragraph. **You have been asked this five rounds running and it is still open.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**
