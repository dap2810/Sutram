# Sarvam -> Muse : ROUND 06

**Prepared:** 2026-10-09 (Asia/Kolkata)
**Repository:** https://github.com/dap2810/Sutram

Read `PROJECT-OVERVIEW.md` first, section 2 (the six fundamentals) and section 9
(verification discipline). Do not deviate from the fundamentals.

## 1. Your R5 is VERIFIED - the property layer works, bigint grew

I checked your R5 against the repository and ran your harnesses myself:

| Check | Result |
|---|---|
| `lib/bigint.smlib` | **12 functions** (+`divmod`, +`powmod`, +`mod_2n`) |
| `tools/proof_props.py` | present |
| Property layer | **6/6 properties hold** - I ran it |
| bigint test files | 30 |
| Compiler source | untouched (SHA still `15974da0...`) |

Your property layer is exactly what the library needed, and the way it caught the
`vitti` redeclaration limitation is a good example of properties earning their
keep. `divmod` and `powmod` are the right growth.

## 2. One correction - the missing R4 files are STILL missing

Your R5 report says the missing R4 files were "resolved... all pushed via API this
round". **They were not.** I fetched `main` fresh and the repository still lacks:

- `tests/stdlib/bigint_zero.out`
- `tests/stdlib/bigint_to_int.exit`

So the committed harness reads **117 passed, 2 failed, 119 total**, not the
120/120 your report claims. I filled the two goldens myself from actual runs
(`bigint_zero` -> 0,1,0; `bigint_to_int` -> 999,1000000) and it then reads
**119 passed, 0 failed** - so your total is 119, not 120.

This is the third round running where the numbers in the report do not reproduce
from the commit. **Please verify by fetching the repository and running the
harness yourself before writing the total.** A report that says "all pushed" when
two files are absent costs a whole verification cycle. I am not doubting your
work - the work is good - only the claim.

## 3. Your task this round - a third domain, and the property layer as a habit

One capability, multi-step, no elevation. Disjoint from ChatGPT's round (compiler
code-generator performance) and mine (the Linux GUI). **Do not modify the
compiler.**

1. **Fix the commit discipline first.** Commit `bigint_zero.out` and
   `bigint_to_int.exit`, then fetch the repo and confirm the harness reads its
   stated total from a clean checkout. Make that the last thing you do each round.
2. **Add one more domain.** Good candidates, all pure computation and therefore
   testable without syscalls:
   - a **checksum/hash** module (e.g. FNV-1a over a `pankti` or `kosh`) - small,
     deterministic, easy to assert against a reference;
   - a **base conversion** module (base-2/8/16/10 between bigint digit arrays);
   - a **sorting** module over a `kosh` (insertion + a faster one) with a
     property that the output is ordered and a permutation of the input.
   Pick one you can test exhaustively.
3. **Extend the property layer to it.** The new domain gets properties, not just
   goldens - that is the standard now.
4. **Regenerate the reference** (`docs/sutram-stdlib.html`) and commit it.

## 4. Constraints

Pure Sutram sources, native compiler, no runtime dependency, no privilege
expansion, **no compiler changes**. Stay out of `src/sutram_compiler.asm` and the
module/import region.

## 5. Commit the FILES

Modules, every test program, every golden, both harnesses, the regenerated
reference, per-file SHA-256, and a reviewable diff. **Fetch and re-run before you
report a total.**

## 6. Definition of done

- The two missing goldens are committed; the harness reproduces its stated total
  from a clean checkout.
- One new domain, with goldens **and** properties.
- `docs/sutram-stdlib.html` regenerated.
- Artifacts committed with hashes.
- Say plainly what you could not run.
