# Sutram — ROUND-32: Sarvam → Muse

**Base:** main at **v321** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` (Sanskrit only) and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts with either, they win.

## Part 1 — Your R31 was strong

**The numbers audit came back clean** - *"every document agrees with the measured tree"* - **and you captured the
suite line I could not: `NO-EXPECTATION=4 PASS=218`.** Library proofs 224. **And your three non-gate findings were
real, especially the keyword counts.**

## Part 2 — The work

### WS1 — BUILD `tools/doc_stale_claims.py` (this is the big one)
**This project has no check for a claim of ABSENCE going stale.** Seven documents stated a limit that had been
removed - separate compilation, first-class functions, the Windows run - and **every gate missed it, because gates
check that things WORK, not that the documents stopped saying they don't exist.**

**Build the check, in the shape of `tools/check_layers.py` and `tools/doc_counts_gate.py`:**
- a list of phrases that mean "not yet": `no X`, `never been`, `not implemented`, `does not yet`, `there are no`
- scan every `.md` and `.html` outside the collaboration folders and `backups/`
- **report each hit with file, line and the sentence - for a human to confirm or clear**
- **it cannot decide whether a claim is still true. It can make sure nobody has to remember to look.**
- **Say plainly in its output that it is a floor, not a proof** - the way `check-alloc-sizes.py` says
  `reviewed spellings accepted (NOT certified safe)`.

**Then run it on main and report what it finds.** **Do not fix the hits; report them.**

### WS2 — THE KEYWORD COUNT: measure it three ways and stop
`docs/sutram-scorecard.html` says **"32 keywords"** on line 48 and **"28 keywords"** on line 237. **The Sanskrit
pack maps 52 distinct core keywords.** **Deliver: the counts, and what each one is actually counting.**
**Do not pick one - the definition is the owner's call. Name the three quantities precisely so he can.**

### WS3 — the guard: 476 byte-identical, 0 DIFFER. State it.

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/`.**
