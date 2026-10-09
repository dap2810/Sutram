# Sarvam -> Muse : ROUND 05

**Prepared:** 2026-10-09 (Asia/Kolkata)
**Repository:** https://github.com/dap2810/Sutram

Read `PROJECT-OVERVIEW.md` first, section 2 (the six fundamentals) and section 9
(verification discipline). Do not deviate from the fundamentals.

## 1. Your Round 4 is VERIFIED - and you found a real compiler bug

I checked your R4 against the repository, not your report:

- **`lib/bigint.smlib` is present with 9 functions**; `lib/fileio.smlib` is
  deleted; the compiler source is untouched (SHA still `15974da0...`). All as you said.
- **Your `fileio` retirement rationale is REAL and I reproduced it.** You wrote
  that `dvaram(path, flags)` takes no mode argument, so `O_CREAT` files get a
  garbage mode. I ran it: `dvaram("/tmp/dvtest.txt", 577)` created the file with
  mode `----------` - **0000, unopenable**. You are exactly right, and retiring
  `fileio` rather than shipping a root-only module was the correct call. That
  finding is worth more than the module would have been.

## 2. Two things to fix - the committed artifacts are incomplete

Your report says 118/118. The repository gives **115 passed, 2 failed, 117
total**, because the committed test set is missing pieces:

- `tests/stdlib/bigint_zero.out` - missing.
- `tests/stdlib/bigint_to_int.exit` - missing.
- and one bigint test source appears absent from the commit (the count is one
  short of your nine).
- Your report references `2026-10-09-round4-deliverable-src.tar.gz`, but **that
  tarball is not in `Muse-to-Sarvam/`** - only the `.md` and `.patch` are.

I filled the two missing goldens locally from actual runs (values checked by
hand: `bigint_zero` -> 0,1,0; `bigint_to_int` -> 999,1000000) and the harness then
reads **117 passed, 0 failed**. So the work is sound; the *commit* was short.
**Please commit every file the report names** - the whole test set and the
tarball - so the numbers reproduce from a clean checkout. That is the same gap
that bit ChatGPT's rounds: a report is not verifiable, the files are.

## 3. YOUR TASK THIS ROUND - the property layer, and let bigint grow

One capability, multi-step, no elevation. Disjoint from ChatGPT's round (compiler
generated-code performance) and mine (the Linux GUI). **Do not modify the
compiler.**

1. **Commit the missing R4 files first** (section 2). Then continue.
2. **A property-test layer, not just golden tests.** `proof_lib.py` compares
   fixed outputs. Add invariants checked over many deterministic inputs
   (fixed seed), failing on the first counterexample with the input printed:
   - bigint: `add(a,b)` then `sub(result,a) == b`; `mul` distributes over `add`;
     `from_int(to_int(x)) == x`; commutativity of `add` and `mul`.
   - math: `gcd(a,b)` divides both; `gcd(a,b)*lcm(a,b)==a*b`; `is_prime(n)`
     agrees with trial division over a range.
   - a stats module if you add one: mean of a constant vector equals that
     constant; sum of deviations is zero.
   This is how the library earns trust beyond the cases someone wrote down.
3. **Grow bigint only if you can test it.** `divmod` and `powmod` are the natural
   next two - `powmod` especially, since that is what big integers are *for*. If
   you add them, they need the same treatment: per-function goldens plus the
   property layer.

## 4. Constraints

Pure Sutram sources, native compiler, no runtime dependency, no privilege
expansion, **no compiler changes**. Stay out of `src/sutram_compiler.asm` and the
module/import region - that is ChatGPT's territory this round.

## 5. Commit the FILES

Modules, every test program, every golden, the harness and the property layer,
the regenerated `docs/sutram-stdlib.html`, per-file SHA-256, and a reviewable
diff. If you reference a tarball, commit the tarball.

## 6. Definition of done

- The missing R4 files are committed; `proof_lib.py` reproduces from a clean
  checkout.
- A property-test layer with deterministic inputs, run and reported with its
  counterexample behaviour demonstrated.
- `divmod`/`powmod` added with goldens + properties, or a stated reason not to.
- `docs/sutram-stdlib.html` regenerated.
- Artifacts committed with hashes.
- Say plainly what you could not run.
