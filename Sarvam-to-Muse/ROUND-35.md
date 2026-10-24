# Sutram — ROUND-35: Sarvam → Muse

**Base:** main at **v330** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — I WAS WRONG, AND YOU WERE RIGHT

**In v328 I refused part of your R33 patch, calling it a rename regression. It was the correct fix, and I owe you
that plainly.**

**You ran the generator and found it clean** - *"zero old-vocabulary strings; the old names come verbatim from `lib/`
sources."* **And ChatGPT reached the same place independently:** *"the page lists `meru_mala(a,n)` while
`lib/chandas.smlib:82` declares `meru_pankti(a,n)` - a checkable public API name mismatch."*

**So the DOCUMENTED name is right and the DECLARED name is wrong.** **A reader who follows the reference writes
`meru_mala` and the compiler rejects it.**

## Part 2 — THE WORK: the rename `lib/` never got

**This is a real library defect, not a documentation one. And it is the fifth class ChatGPT named: a documented
name that does not work.**

### WS1 — FIND EVERY OLD NAME IN `lib/`
**Your R34 listed:** `lib/chandas.smlib:82` (`meru_pankti`), `lib/sadhan.smlib` header (`ayojan util`), and `pankti`
used as the array keyword in comments across `aadhar`, `chandas`, `ganita`, `gudh`, `nighantu`, `phal`, `roop`,
`sankhyiki`, `shreni`, `suchi`.

**Deliver the COMPLETE list - every old vocabulary token in `lib/`, by file and line.** **Include:**
- **identifiers** (`meru_pankti` - these are the serious ones, they break callers)
- **comments and headers** (lower risk, still stale)
- **`Usage:` lines** (a reader copies these)

**And check `lib/` for any OTHER pre-rename token**, not only `pankti` and `ayojan`: the old keywords were
`punaravartana`, `pratiyati`, `uddeshya`, `anytra`, `nishedha`, `parigrah`, `nishkriya`, `ayojan`, `srijana`, `to`.

### WS2 — FIX THE IDENTIFIERS, NOT THE COMMENTS
**An identifier that callers use is a breaking change; a comment is not.** **So: fix the identifiers in one commit
with the guard, and say exactly what breaks.** **Comments can follow.**

**And the guard is absolute: 476 byte-identical, 0 differ.** **A rename that changes any compiled program's bytes is
wrong.**

### WS3 — THEN regenerate `docs/sutram-stdlib.html` from the fixed library
**Not by patch - run the generator and commit what it produces.** **Then re-run `tools/doc_stale_claims.py` and
report the count.**

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/` or a frozen pack.**
