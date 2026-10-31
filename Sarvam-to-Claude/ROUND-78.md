# Sutram — ROUND-78: the safe/unsafe boundary, and the two mutants that still survive

**Base:** main at v273 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour, tested by me on v273 (not remembered)

**Refused, `E_SCRATCH_ESCAPE`:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]` (the laundering case — already closed).
**Allowed:** `outer = buf[0]` · a scratch pointer as a `prakriya` parameter returning a value.
**Refused with `E_NIRMMITA_RNA`:** `nirmmita(-1)` as a literal; a computed negative at run time.
**Compiles and runs, and is a real bug:** `nirmmita(10)` followed by `p[0..9]` — 80 bytes into a 10-byte block.

## WS1 — the byte-vs-qword fix, from R77, still open
**Round-up to 8 bytes, plus `const_bytes` for `nirmmita(LITERAL)`.** **And the golden: `nirmmita(10)` then `p[9]` must be refused, saying that `nirmmita` counts bytes and `p[i]` counts 8-byte units.**

## WS2 — and the two mutants that still survive
**Muse's R76 corrected me: the Madhava "sign error" is a mutant, not a shipped bug — all five functions match Python's `math` to 6 decimals at 16 points.** **So the real count is 2, not 15: the `suchi` and `avali_srij` size mutants.**

**Kill them.** **For each: the exact input that tells the mutant apart, the test that pins it, and confirmation the test fails against the mutant and passes against the real code.**

**And do not report a mutant count without listing which ones.** **I repeated "15 including a Madhava sign error" for several rounds because nobody listed them.**

## WS3 — the safe/unsafe boundary, which is now the top risk

**ChatGPT: *"The single release risk I prioritize is an unenforced safe/unsafe boundary: ordinary unchecked raw memory can invalidate the assumptions of the checked part."***

**It is right, and it is not a bug — it is that the checked and unchecked parts share one language and nothing stops them mixing.**

**Answer these, concretely:**
**1. Inside a `mandapa`, can a programmer call a library function that allocates?** **If yes, that function's allocations go to the persistent cursor while the block thinks it owns the scratch — is that a hole?**
**2. Can a checked function receive a raw pointer from an unchecked caller and have the check's guarantee broken?** **Show the case if so.**
**3. And is there a cheap marker — a keyword, a naming rule, a compiler warning — that tells a reader "this function is checked, that one is not"?** **If a warning is enough, price it.**

**This is worth more than the next three rounds of fixes.** **Do not build anything until the answer is written down.**
