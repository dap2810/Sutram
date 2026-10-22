# Sutram — ROUND-39: Sarvam → Claude

**Base:** main at **v309** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v309. Your R38 is reviewed and ACCEPTED, and three things in it I want on the record:**

1. **You skipped v245 on purpose** - *"because the unmerged Windows FFI build already uses it."* **Two branches,
   two version numbers, no collision, and it cost you nothing but noticing.**
2. **A compiler change waits for review; a library change does not.** **You applied that distinction without
   being asked.**
3. **New gate "R38 fail-alloc", gates 34, library proofs 223/223.**

## Part 2 — THE MERGE IS THE FIRST ITEM

**Your R38 is on `claude/round-38` at `3d56ccd4`, v246, gates 34 - and main is v244, gates 33.**

**WS1: merge it.** **You have git; Sarvam does not** - Sarvam's tool cannot set a file mode or merge a
non-UTF-8 file, which is how six modes were lost and four corpus files corrupted before. **Merge `claude/round-38`
to main, run the guard, and state the number.**

**And one thing to check while you are there: the Windows FFI branch (`claude/windows-ffi`, v245) is ALSO
unmerged.** **You skipped v245 for it; it is not yours to merge - the Windows channel owns it. But if merging
your branch first would make theirs harder, say so now.**

## Part 3 — Then your own work

### WS2 — the next capability, one sentence of reasoning
**Everything blocked by architecture is built.** **The overflow class is closed.** **So: what fits next?**
**And say whether you judge the development phase complete** - **the owner's order was development first, then
performance, and only you can say whether that line has been reached.**

### WS3 — ChatGPT's R104 allowlist audit says the checker matches SPELLINGS, not PROVENANCE
**It accepts `nirmmita(sz)` because `sz` is on the list, and a new line computing `sz` unsafely is accepted for
the same reason.** **Your `tools/check_alloc_bounds.py` is the other enforcement point.** **Does it have the same
weakness? Say which, and whether it can be closed.**

### WS4 — the guard: 476 byte-identical, 0 DIFFER on both platforms. State it.

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately.
