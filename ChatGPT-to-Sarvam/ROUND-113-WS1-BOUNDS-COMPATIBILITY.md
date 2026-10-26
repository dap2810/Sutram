# Sutram ROUND-113 WS1 — Universal bounds guard: source-based compatibility forecast

**Read pin**: main `1ccec720dccc53ae8ed344e4f58f87fba727682a` (26 October 2026, changelog v341). This is a *forecast*, not evidence that a universal guard has shipped. Do not edit `src/`, `lib/`, `tests/`, `tools/`, golden output or `backups/`.

## Direct compiler finding: typed arrays already checked; raw pointers intentionally not

- `src/sutram_compiler.asm:12851-12858`: declared `mala` has a runtime count header, and the comment states that raw `nirmmita` pointers keep the historical unchecked index path.
- `src/sutram_compiler.asm:13183-13238`: assignment `a[i] = ...` distinguishes slice/fixed mala/typed kosh; kosh index checks logical length `[ptr-16]`, not capacity `[ptr-8]`; unrecognized/raw pointer skips the check.
- `src/sutram_compiler.asm:15027-15035`: expression/read indexing likewise calls `emit_array_bounds_check` for recognized arrays only.
- `src/sutram_compiler.asm:14444-14475`: unsigned `index < length` check rejects negative indices and prints a bounds diagnostic, exit 1.

**Therefore**: first specify whether "universal" means all *typed* `mala`/`kosh` reads/writes (much of this already exists) or extends to *raw pointers*. Arbitrary pointers do not inherently carry trustworthy allocation bounds. Do not assume a raw `nirmmita` pointer can use `[ptr-8]`/`[ptr-16]`: those fields belong to recognized typed array layouts, not the raw buffer. The scope choice determines what could break.

## A. EXISTING INTENTIONAL FAILURES — preserve failure, not success

| Fixture | Direct source line(s) | Committed expectation | Guard consequence |
|---|---|---|---|
| `examples/68_array_oob.sm` | 2-4: `mala a[3]; a[3] = 99; likha(999)` | `tests/expect/68_array_oob.exit`: 1; `.out`: `Sutram Error: mala ank seema atikram` | Already rejects one-past-end write. Passing and reaching `999` would be a regression. |
| `examples/71_array_negative_index.sm` | 2-4: `mala a[3]; a[-1]=99` | `tests/expect/71_array_negative_index.exit`: 1; same bounds-error output | Negative index rejection already expected. |
| `examples/100_t18_kosh_bounds.sm` | 3-6: `kosh a[1]; push 42; pop; likha(a[0])` | `tests/expect/100_t18_kosh_bounds.exit`: 1; same bounds-error output | Capacity remains while logical length becomes zero: indexing must reject. |
| `tests/r23/test_capabilities.py` | CASES entries "a slice index past its length", "slice write past", "hi past", "lo after hi", negative lo and sub-slice past | Each is an explicit `run-fail` or `compile-fail` case | Existing rejection semantics and diagnostic must be maintained, not converted silently to a returned zero. |

**Confirmed existing programs relying on out-of-bounds success in this inspected set: NONE.** This does *not* prove there is no other one in the entire repo: no native suite was run and no whole-tree semantic execution census was performed.

## B. VALID GUARD-SENTINEL USES — not out of the allocated memory

- `tests/stdlib/r8_array_guard.sm:5-23` allocates **four** qword cells but calls `shreni` routines with logical n=3, deliberately placing a sentinel at index 3. Reading/writing index 3 in *this raw 4-cell allocation* is physically within the allocation; the sorting/searching functions correctly must ignore it when n=3. Do not label this an out-of-allocation success.
- `tests/stdlib/r10_roop_suchi_edges.sm` allocates four qword cells as `o` and writes/reads `o[2]` as a sentinel after two queue entries. This is still inside the allocated four-cell buffer. The test checks algorithms do not overwrite the extra cell.

## C. LIBRARY PRECONDITIONS — likely RED only for invalid callers, not proven failing tests

1. `lib/samanvaya.smlib:32-41` `pehchan` writes `out[i*n+j]`; `:50-60` `vivartana` reads/writes; `:91-107` `matrika_gunana` reads/writes; `:111-157` `nishan`, `nirnaya2/3`, `rekha_manak` index flat `kosh dasham`. Its header explicitly requires **`kosh_push` m*n output entries first**. Capacity alone does not suffice. `matrika_yoga` and `skalar` already have `samanvaya_akar_na` length guards; do not report those as missing.
2. `lib/kalana.smlib:115-141` `bahu_mula` uses `ok[0]`, explicitly requires caller `kosh_push(ok, 0.0)` first. `tests/stdlib/kalana_bahu_mula.sm` does perform this push for both `ok` and `ok2`; valid current fixture is safe.
3. `lib/ganita.smlib:76-84,151-152,160-167` `chakravala` and `samasa` write two cells of caller-provided **raw pointer** `out`. `ganita_janchit_*` write `okp[0]` on a raw-pointer argument (e.g. `:269-300`). These functions require caller allocation, but a guard only recognizing typed arrays cannot infer raw-pointer extent. `tests/stdlib/ganita_checked.sm` explicitly allocates `ok=nirmmita(8)` and is valid.
4. `lib/mala.smlib:20-64` `mala_sangrah`, `mala_grah`, `mala_purn`, `mala_pratilip`, `mala_yog` use raw `likh8/pad8` and caller-supplied lengths. `mala_*_surakshit` bounds-check a caller-provided count, **not actual allocation provenance**. Adding the compiler's typed index guard does not make these raw-pointer helpers universally safe.
5. `lib/suchi.smlib:128-149` inserts at `idx == length` after capacity validation: this is valid within allocated capacity and should keep working. `lib/sangrah.smlib:239-274` indexes allocated scratch arrays using its own lengths/capacities; require allocation provenance and arithmetic checks before any instrumentation that assumes a typed header.

## D. Concrete routing to Muse

1. Define two separate contracts: typed `mala/kosh/vibhag` access (current logical-length checks) versus raw pointer + explicit extent API (not solved by old typed header).
2. Build/test exact success fixtures: zero/one/full-length indexing, `kosh` grow/pop/clear, float `kosh` param, slices, boundary read/write, side-effectful index (`examples/140_r30_index_side_effect.sm`), and valid `samanvaya/kalana` callers. Detect changed stdout/exits/binary bytes.
3. Preserve exact failure fixtures above; compare old/new error text and exit status. Do not rewrite negative goldens to accept a regression.
4. Add separately labeled invalid-caller probes for under-filled matrix output and empty `ok` **in an isolated native harness**, never call such probes already-passing tests.
5. Run guard byte-parity on exact candidate and revert if owner-mandated parity fails; a desired changed invalid-input behavior needs an explicit owner decision on parity-scope exceptions, not an unreported difference.

**Static source reading PASS. Native execution: NOT RUN - no toolchain. Confirmed OOB-success reliance in inspected existing examples/tests: none. Whole-repo absence: CANNOT CHECK.**