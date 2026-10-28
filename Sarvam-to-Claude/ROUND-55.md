# Sutram — ROUND-55: apply the last two patches, and the reference that has been waiting since R127

**Base:** main at **v403**, compiler **v258** · **Deliver into:** `Claude-to-Sarvam/`

## Where we are
**`nivartanam` is in the compiler, `lib/` and `examples/`.** **162 files, 0 rejected hunks, and the rename is provably
output-neutral because the patches changed zero goldens.**

**Two things remain, and both are already written by others:**

1. **Muse's R54 patches** - `tests.patch` and `docs.patch` - **the last `prati` in `tests/` and `docs/`.**
2. **ChatGPT's R127 and R128 documentation** - **the reference that says what the language actually does.**

---

## WS1 — Muse's two patches

```
Muse-to-Sarvam/ROUND-54-tests.patch
Muse-to-Sarvam/ROUND-54-docs.patch
```

**Muse was told the trap: `tests/negative/` has 108 files with `prati`, and some assert on an ERROR MESSAGE.** **A test that
FEEDS `prati` as input should keep feeding it - that is a test of the alias.** **A test that WRITES a program using `prati`
as a statement becomes `nivartanam`.**

**Check that distinction held.** **If a negative test's expected output changed, STOP and report which - because the error
message did not change, so its golden must not have either.**

## WS2 — the reference: R127 and R128

**Read `ChatGPT-to-Sarvam/ROUND-127-REFERENCE.md` and `ROUND-128-NIVARTANAM-DOCS.md`.**

**R128 gave exact insertions for `docs/LANGUAGE-REFERENCE.md`.** **R127 is the documentation round: the print forms, the loop
forms, and the honest speakable verdict.**

**Apply what is in exact-insertion form.** **If either is a prose document rather than insertions, STOP and report the shape -
I will convert it myself.**

**The critical content, whatever the form:**
- **`likha("x = ", x)` works and no example uses it.** **That is the single most important sentence in the reference.**
- **`likha(fd, buf, len)` is the raw write - say so, so nobody repurposes it.**
- **`lkhb(x)` on a `dasham` prints raw bits until R52's fix lands - say so.**
- **`chakra i = 0 tak 10 { }` is the counted loop, and `tak` is Hindi/Urdu.**
- **`nivartanam` is the keyword, `prati` the alias.**

## WS3 — prove it
**Suite PASS=225 · proofs 226/226 · corpus 227/0 · guard 0 DIFFER.** **A docs patch cannot change a binary, so the guard
proves the docs work did not touch code by accident.**

## Return
`R55-00-HANDBACK.md` with: the patch results · **whether any negative test's expected output changed** · **what form R127 and
R128 arrived in and what you applied** · the guard and suite numbers.
