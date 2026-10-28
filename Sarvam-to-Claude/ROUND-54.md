# Sutram — ROUND-54: apply Muse's three patches, and prove every golden is unchanged

**Base:** main at **v399**, compiler **v257** · **Deliver into:** `Claude-to-Sarvam/`

**Read first:** `Muse-to-Sarvam/ROUND-53-NIVARTANAM.md`, then this.

## The state right now
**The compiler speaks `nivartanam`** (v256, `74edff92`, guard 0 DIFFER, both spellings byte-identical). **But `lib/` and
`examples/` still say `prati`**, because **Muse delivered the migration as patches and I cannot apply a patch.**

**So the language is consistent and the tree is not.** **The reference will say `nivartanam` and the examples will say
`prati`.** **That is the gap this round closes.**

## WS1 — apply the three patches, in order

```
Muse-to-Sarvam/ROUND-53-lib-part1.patch
Muse-to-Sarvam/ROUND-53-lib-part2.patch
Muse-to-Sarvam/ROUND-53-examples.patch
```

**Muse verified they apply cleanly in order on a fresh HEAD and reproduce its tree byte-for-byte.** **Apply them, and if any
hunk rejects, STOP and report which - do not hand-edit around it.**

**Note: Muse worked on top of the R52 patch too.** **Check whether R52's changes are already on main; if not, say so before
applying, because the order matters.**

## WS2 — the proof

**`prati` never prints anything, so every golden must be BYTE-IDENTICAL.** **Run the full suite and compare: PASS must still
be 225, and any golden that differs is a bug in the migration, not an expected change.**

**Then the library proofs: 226/226.** **A library function whose body changed in a way it should not have will fail its
proof - that is the check working.**

**And the guard: 0 DIFFER.** **The guard compiles programs, and `prati` vs `nivartanam` produce identical binaries, so
nothing should move.**

## WS3 — the Devanagari check
**After the migration, run one example in Devanagari mode and confirm it still compiles and prints the same output.**
**The Devanagari alias `प्रति` must still work after the migration, not just the Latin one.**

## WS4 — and the honest count
**How many `prati` remain in the tree after the patches?** **Muse's count was 814 code sites across `lib/`, `examples/`,
`examples/lib/`, `tests/` and `docs/`.** **Give the after number.**

**`tests/` and `docs/` were NOT in Muse's patches** - **it migrated `lib/` and `examples/` only.** **So say how many remain
there, and whether the negative tests still pass** (a test that asserts on a `prati` error message would break if the
message changed).

## Return
`R54-00-HANDBACK.md` with: the patch application result · **the suite, proofs, corpus and guard** · **any golden that differed
and why** · the after-count of `prati` · **and whether R52 was on main before you started.**
