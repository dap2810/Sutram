# Sutram — ROUND-53: migrate the library and the examples to `nivartan`

**Base:** main at **v395** · **Deliver into:** `Muse-to-Sarvam/`

**Read first:** `docs/WHATS-LEFT.md`, and **finish R52 first if it is still open** - this round comes after it.

## The owner's decision
**`nivartan` becomes the keyword. `prati` stays accepted as a legacy alias.**

**Why the alias and not a clean removal:** **`prati` is in every program written for this language, including the ones the
owner has tested on Windows.** **The alias means `nivartan` IS the keyword - it is what the reference says and what new code
writes - while no existing file stops compiling.** **The guard then proves it: 0 DIFFER.**

## The fact that makes this safe
**`prati` is a statement keyword. It never appears in program output.** **So renaming it changes NOTHING observable: every
golden file stays byte-identical, and the crash corpus behaves identically.** **The only thing that can go wrong is a file
that fails to COMPILE - and the alias prevents that.**

**Devanagari: `निवर्तन` (nivartana) for `nivartan`.** **`प्रति` stays as the Devanagari alias.**

---

## WS1 — count it first

**Before changing anything, count every `prati` in the tree:** **how many in `lib/` (functions and statements), how many in
`examples/`, how many in `tests/`, how many in `docs/`.** **Give the numbers by directory.** **That is the change surface,
and it is the first thing to report.**

## WS2 — migrate `lib/`

**Every `prakriya` in `lib/` that ends with `prati x` becomes `nivartan x`.**

**Then: the library proofs must still pass 226/226.** **If any fails, that function's body changed in a way it should not
have - revert it and list it.**

## WS3 — migrate `examples/`

**Every `prati` in `examples/` becomes `nivartan`.**

**And here is the test that makes it safe: every golden must stay BYTE-IDENTICAL, because `prati` never prints anything.**
**So: change, compile, run, compare against the unchanged golden.** **A golden that differs means the rename broke something
and that file must be reverted and listed.**

**Report: files changed, and any file where the output changed.**

## WS4 — and the honest check
**After the migration, does any file still use `prati`?** **If yes, list it and say why it was left.**
**Then re-run the counts from WS1 and give the before and after.**

## Return
`ROUND-53-NIVARTAN.md` with: the counts before and after · **every file changed** · **any file reverted with the reason** ·
**the library proof result** · **the suite result**.
