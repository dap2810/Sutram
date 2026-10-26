# Sutram — ROUND-36: Sarvam → Muse

**Base:** main at **v335** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — R35 was exactly right, including the call you did not make

**One identifier, and it is fixed on main: `meru_pankti` to `meru_mala`, with the test updated.** **And the inventory
told me the difference between a defect and a mess - 1 identifier against 18 headers, 2 usage lines and 19 comments.**

**And `util_chinha`: you did not rename it and said why.** **That is the right call and it is now with the owner.**

## Part 2 — The work

### WS1 — THE COSMETIC LAYER, in one pass
**18 headers carrying old file names, 2 `Usage:` lines (`ayojan util`, `ayojan sort`), 19 comment lines using
`pankti` for the array.** **Fix all of them.**

**Rules:**
- **comments and headers only** - no identifier changes this round
- **the guard: 476 byte-identical, 0 DIFFER** - a comment change must not alter a single compiled byte
- **`util_chinha` stays** - it is the owner's decision

### WS2 — THEN regenerate `docs/sutram-stdlib.html` from the fixed library
**Not a patch - run `tools/gen_stdlib_ref.py` and commit what it produces.** **It should now show 305 functions and
`meru_mala`.** **If it still shows 303 or `meru_pankti`, say so - that is a generator defect and it is worth more
than the page.**

### WS3 — re-run `tools/doc_stale_claims.py` and report the count
**163 on v325. How many now?** **And how many are FALSE?**

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/` or a frozen pack.**
