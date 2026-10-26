# Sutram — ROUND-37: Sarvam → Muse

**Base:** main at **v338** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — R36 was clean, and the guard sentence is the reason

**47 comment lines, 0 code lines, 20 files.** **And: *"before/after compile, all 551 programs: 0 differ - a comment
change altered not a single compiled byte."*** **That is what makes a cosmetic sweep trustworthy.**

**And you left the R7/R8 historical notes alone, because a changelog naming a module as it was then is correct, not
stale.** **Second time you have made that distinction without being told.**

## Part 2 — The work

### WS1 — RUN THE WHOLE SUITE, and the three NEW checks
**The project now has checks that did not exist last week. Run them all and report each:**

```
sh tools/gates.sh                          -> state the count, environment named
python3 tests/run_tests.py                 -> expect NO-EXPECTATION=4 PASS=218
python3 tools/crash_corpus.py --compiler ./sutram_compiler
python3 tools/proof_lib.py --compiler ./sutram_compiler
python3 tools/proof_props.py --compiler ./sutram_compiler
python3 tools/check_layers.py
python3 tools/check_alloc_bounds.py
python3 tools/doc_counts_gate.py
python3 tools/doc_stale_claims.py          -> the count, and how many are FALSE
python3 tools/check_doc_signatures.py      -> NEW: must report 305 / 305, 0 mismatches
```
**Name the environment per check. PASS / FAIL / NOT-RUN separately.**

### WS2 — THE GUARD
**476 byte-identical, 0 DIFFER on both platforms. State this round's number.**

### WS3 — the one thing nobody has measured
**`docs/sutram-stdlib.html` was regenerated to 305. Is every function's DOCUMENTED DESCRIPTION still accurate?**
**The signature check compares names and arity; it does not read the prose.** **Deliver: how many descriptions you
sampled, how many were wrong, and the worst one.**

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/` or a frozen pack.**
