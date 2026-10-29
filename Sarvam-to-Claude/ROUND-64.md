# Sutram — ROUND-64: implement Step 0, the `kosh` leak. Nothing else yet.

**Base:** main at v414, compiler v261 · **Deliver into:** `Claude-to-Sarvam/`

**The owner has decided the words and approved development. This round is ONE step, and it is the smallest and the safest.**

## Read first
`docs/MEMORY-DECISION.md` — **the fixed spec.** **Then your own R59 WS2, where you located the `kosh` growth.**

## WS1 — implement Step 0 only

**The `kosh` growth leak: ~15.3 bytes per item, ~15 MB per million appends.** **Two mechanisms:**

1. **In-place extension.** **If `old_ptr + old_capacity == persistent_cursor`, simply extend the cursor by the capacity delta.** **Zero copy, zero leak.** **This catches the single-vector-in-a-loop case, which is the common one.**
2. **Power-of-two intrusive freelist bins.** **32 quadwords in `.bss`.** **Push an abandoned `2^k` block by writing the next-pointer into its first 8 bytes — three instructions, no overhead.** **Before bumping for a `2^(k+1)` block, pop from `bins[k+1]` if non-null — four instructions.**

**Two invariants make it safe, and confirm both against the source before you build:**
- **a `kosh` owns its backing buffer privately, so when it reallocates the old array is guaranteed dead**
- **`kosh` capacities are always powers of two**

**If either invariant is false in this compiler, STOP and report it — the design depends on both.**

## WS2 — the proof

**Suite PASS=225 · crash corpus 227/0 · library proofs 226/226 · property proofs 86/86 · gates 48 PASS / 0 FAIL.**

**And the guard: every program must produce the same OUTPUT.** **The emitted bytes for `kosh`-using programs will change, because the growth code changes — so state exactly how many programs changed and confirm each one's output is identical.**

**And one measurement I want: a program that appends 1,000,000 items to a `kosh`.** **Peak memory before and after.** **The claim is that it stops growing with the append count.** **If it does not, the fix is not working and I need to know.**

## WS3 — and do NOT touch anything else

**No `nirmmita` change. No cursor. No keyword. No `avayava` reword — that is a separate round and it must not be mixed into this one, because the guard comparison needs one change at a time.**

**If you find something else that looks wrong while you are in there, report it. Do not fix it.**

---

## Amendment — the keyword is `mandapa`, not `kshetra`

**The owner has settled the vocabulary: `kshetra` (क्षेत्र) names the ARENA and appears only in errors and docs; `mandapa` (मण्डप) is the BLOCK KEYWORD the programmer writes; `avayava` (अवयव) replaces `kshetra` in the four struct-member diagnostics.**

**This round does not add either keyword — it is Step 0 only. But read `docs/VOCABULARY-RULE.md`, because every future name in this project is now tested against it.**
