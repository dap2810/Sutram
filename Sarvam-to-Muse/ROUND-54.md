# Sutram — ROUND-54: finish `nivartanam` everywhere - `tests/` and `docs/`

**Base:** main at **v399**, compiler **v257** · **Deliver into:** `Muse-to-Sarvam/`

**Read first:** your own `ROUND-53-NIVARTANAM.md` - **this is the half you did not cover.**

## Where we are
**Your R53 patches cover `lib/` (677) and `examples/` (122).** **Claude is applying them in R54.**
**You counted 389 more in `tests/` and 146 in `docs/`.** **Those are still `prati`.**

**The compiler speaks `nivartanam`, the library and examples will speak `nivartanam`, and the tests and docs still say
`prati`.** **That is the last inconsistency.**

## WS1 - the danger, stated first
**`tests/negative/` has 108 files with `prati`.** **Some of those tests assert on an ERROR MESSAGE, and if the message
contains the word `prati`, renaming it changes what the test expects.**

**So: before you change anything, find every test whose EXPECTED OUTPUT contains `prati`.** **List them separately.**
**Those are the ones where the rename changes a golden - and each one needs a decision, not a blind rename.**

**The same applies to `tests/r53/`** - **Claude added `tests/r53/test_nivartanam.py` in R53, and it may assert on the spelling.**

## WS2 - migrate `tests/`, carefully
**Every `prati` in `tests/` that is CODE becomes `nivartanam`.**
**Every `prati` that is part of an EXPECTED ERROR STRING stays until the error message itself changes** - **and the error
message does not change in this round, because `prati` is still accepted.**

**So: a test that feeds `prati` as input should keep feeding `prati` - that is a test of the alias, and it should stay.**
**A test that writes a program using `prati` as a statement should become `nivartanam`.**
**Say which is which, and how many of each.**

## WS3 - migrate `docs/`
**83 in `.md`, 63 in `.html`.** **Same rule: a historical changelog entry stays as it is.** **A live reference or guide
becomes `nivartanam`.**

**Mark every historical file you deliberately left alone, so I can see the decision was made and not missed.**

## WS4 - deliver as a patch, and prove it
**Same as R53: patches that apply cleanly in order on a fresh HEAD.** **Then the suite must still be PASS=225.**
**Any test whose expected output changed must be listed with the before and after.**

## Return
`ROUND-54-NIVARTANAM-TESTS-DOCS.md` with: the danger list from WS1 · the code-vs-error-string split with counts ·
**every test left alone and why** · the docs list with KEEP_HISTORICAL marked · the patch names · the suite result.
