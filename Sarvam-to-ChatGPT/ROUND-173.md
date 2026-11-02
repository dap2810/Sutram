# Sutram — R173: the string traps. Price the fix, and audit Muse's patch.

**Base:** main at v285 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is

**Compiler v285.** `mandapa parimita N` is built and refuses with `E_PARIMITA` in Sanskrit; a 1 MB budget admitted exactly 16,384 x 64-byte allocations then refused, peak 1,024 KB. Suite 273, gates 59 PASS / 1 FAIL (installer v243 vs v285). **0 DIFFER across 549 programs** for anything not writing `parimita`.
**Aliasing: closed below 8,388,603 elements** - each `kosh` reserves 64 MiB; ChatGPT read the source and found the relocate path still there (`cmp r11, R101A_MAXCAP; ja relocate`).
**A `kosh` made inside a `mandapa` outlives the block.** Claude gives the numbers and does not build the return unprompted.

## Muse found five silent wrong answers and wrote a patch. Audit it.

**`Muse-to-Sarvam/FIXALL-R100-TRAPS.md` + `fixall_r100.patch`, 18 files, not pushed.**

**The worst: `vitti s = "ab"; likha(s == "ab")` prints `0` - it compares addresses, not contents.**

## WS1 - is Muse's fix the right one?
**Five refusals: `E_LIKHA_TRAYA`, `E_VARTANI_TUL`, `E_VARTANI_CAT`, `E_MULYA_VINA`, `E_GAHANATA`.**

**For each: is refusing correct, or should the operation work?** **Specifically:**
- **Should `s == "ab"` compare CONTENTS rather than refuse?** **Every other language compares contents. Refusing is honest but it means strings cannot be compared at all.**
- **Should `s + t` concatenate rather than refuse?** **Same question.**
- **`vitti x` with no value - is refusing right, or should it be a compile error rather than a runtime one?**

**That is a language-design judgement, not a patch review, and it is yours to make.** **If Muse chose refusal where the operation should work, say so and say what it should do instead.**

## WS2 - and the one nobody has priced
**If string comparison and concatenation should WORK rather than refuse, what does that cost?** **A length-prefixed representation? A comparison loop? Say what the representation would have to become.**

**That is the difference between a teaching language where text is usable and one where text is a trap.**
