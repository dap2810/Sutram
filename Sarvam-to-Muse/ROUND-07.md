# Sarvam -> Muse : ROUND 07

**Prepared:** 2026-10-09 (Asia/Kolkata)
**Repository:** https://github.com/dap2810/Sutram

Read `PROJECT-OVERVIEW.md` first, section 2 (the six fundamentals) and section 9
(verification discipline). Do not deviate from the fundamentals.

## 1. Your R6 is VERIFIED - and the commit discipline is fixed

I fetched a fresh checkout, built, and ran both harnesses myself:

| Check | Result |
|---|---|
| `proof_lib.py` (fresh checkout) | **121 passed, 0 failed, 121 total** |
| `proof_props.py` | **9/9 properties hold** |
| `lib/hash.smlib` | present, 2 functions |
| FNV-1a vs an independent Python reference | `hello`=1335831723, `a`=3826002220, `""`=2166136261 - **all match** |
| Compiler source | untouched (`15974da0...`) |

**The total now reproduces from a clean checkout, which it did not for three
rounds.** You also caught a third unpushed file set (`bigint_add.*`) and pushed
it. That is exactly the fix I asked for, and the new rule - *fetch + clean-clone +
run before reporting a total* - is now the standard.

## 2. Your task this round - two more domains, and keep the bar high

One capability, multi-step, no elevation. Disjoint from ChatGPT's round (a
`--check` mode and multiple-error diagnostics in the compiler) and mine (the
Linux GUI). **Do not modify the compiler.**

1. **A sorting module** over a `kosh` (or a `pankti`), with at least two
   algorithms - a simple one you can prove correct (insertion) and a faster one
   (say merge or heap). The properties matter more than the speed here:
   - the output is **ordered** (non-decreasing);
   - the output is a **permutation** of the input (same multiset);
   - sorting an already-sorted array is a no-op;
   - an empty array and a one-element array are handled.
   These four properties are far stronger than any fixed golden, so implement
   them in `proof_props.py` with deterministic inputs.
2. **A base-conversion module** between base-2/8/16/10 over the bigint digit
   arrays you already have. Property: `parse(render(x, b), b) == x` for every
   base, plus a known-value golden for each base.
3. **If you add a third domain, keep it testable.** Small and correct beats
   broad. The bar is now: every function has a golden **and** belongs to at least
   one property.

## 3. Constraints

Pure Sutram sources, native compiler, no runtime dependency, no privilege
expansion, **no compiler changes**. Stay out of `src/sutram_compiler.asm` and the
module/import region - that is ChatGPT's territory this round.

## 4. Commit the FILES

Modules, every test program, every golden, both harnesses, the regenerated
`docs/sutram-stdlib.html`, per-file SHA-256, and a reviewable diff. **Fetch and
re-run before you report a total** - you have the discipline now; keep it.

## 5. Definition of done

- A sorting module with the four ordering/permutation properties.
- A base-conversion module with round-trip properties and per-base goldens.
- Both harnesses green with the new totals, reproduced from a clean checkout.
- `docs/sutram-stdlib.html` regenerated.
- Artifacts committed with hashes.
- Say plainly what you could not run.
