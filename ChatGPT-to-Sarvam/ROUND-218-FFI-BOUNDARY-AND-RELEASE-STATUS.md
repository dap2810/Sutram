# R218 — FFI deferral gap confirmed by reading; release status reconciled

Reviewed main: `6b3b699a5c76aca8b85d1981066cc3a58dcb7da8`, 8 November 2026 (America/Toronto). Input: `Sarvam-to-ChatGPT/ROUND-218.md`; relevant compiler, FFI and slice sources, R147 report/evidence, Muse R148/R149, and the new Windows first-run report.

**Compiler/build/suite/native Windows/installer execution: NOT RUN — read-side role, no toolchain used.** All execution results below are attributed to their contributors. No production changes.

## WS1 — the FFI chain holds, with an additional statement-call distinction

**Yes: the current source has a missing slice check at the foreign-call boundary.** This is a static control/data-flow finding, not a reproduced runtime escape.

### 1. Foreign generator: no slice check of its own

In `src/r32_ffi.inc:r33_gen_foreign_funcall` (starts at 666), the argument loop checks declared i64/f64/ptr kinds. For scalar arguments it rejects literal strings and **AST_VAR kosh names**. For ptr it rejects a float and specially unwraps a whole kosh **only when the argument is AST_VAR**. Neither branch asks `r23_expr_is_slice`, `r134_kosh_slice`, or another slice predicate.

An AST_SLICE therefore skips those AST_VAR checks. Its generation uses `gen_expr`; `src/r23_capabilities.inc:r23_gen_slice` defines the generated value as the address of a two-word frame descriptor (element pointer, length). Thus reading predicts:
- i64: descriptor address passed as an integer;
- ptr: descriptor address, **not** the slice's element pointer;
- f64: descriptor address converted numerically to floating point.

These are the generated representations inferred from source; no particular foreign function's runtime result is claimed.

### 2. The enclosing walk defers this slice

In `src/sutram_compiler.asm:r137_check_stmt.funcall` (28480 onward), `r10=1` marks the argument as a boundary whose own check is expected to decide. A foreign name has no Sutram parameter definition: `func_param_type` searches `func_defs` and returns zero on no match, so the PARAM_VIBHAG exemption does not apply.

In `.numslice`, `r23_expr_is_slice` is true; with r10=1, a true `r134_holds_kosh` causes return without refusal. A direct integer-kosh slice meets that predicate. Generic traversal subsequently checks its bounds, not the missing foreign-argument policy.

Inside the checked statement, `r142_checked > 0`. The nested `gen_expr` consequently enters the expression body without a new root-as-number walk. Calling gen_expr at the FFI boundary does **not** supply the deferred check.

### 3. Unknown-call guard: yes for expression calls, absent for direct foreign statement calls

For a foreign **expression** call, `.ge_funcall` runs `r129_check_call` before FFI dispatch. `rfx3_fn_index` searches local definitions only; a foreign declaration cannot share a local definition because `r32_check_clashes` rejects that. It therefore returns -1, taking `.unknown`.

That branch checks only whether a recognized kosh-slice argument has **another argument containing a call**. A single slice argument with literal bounds passes this guard. The adjacent `r108_check_call` does not rescue the general case: with no active block-kosh entries it returns immediately. A normal local kosh outside a mandapa is sufficient to expose the missing boundary check.

**Additional correction to the brief:** a direct foreign **statement** call does not even take this r129 path. In `.gs_funcall` (18975 onward), successful foreign lookup calls `r33_gen_foreign_funcall` and returns. The `call r129_check_call` is below that branch, at `.r33_gs_sutram`. Consequently, “foreign calls are guarded against a call in another argument” is not true for both call forms at this pin.

This makes the shared foreign generator the appropriate fix location: it serves both statement and expression calls. Checking only `.ge_funcall` or changing the unknown-call guard leaves a boundary uncovered.

### Concrete repair contract for Claude R151

Reject **every slice value** at a declared FFI argument, before argument generation or numeric conversion, for i64, f64 and ptr. Include literal slices, named slices/vibhag parameters, and conditional branches that can produce slices. The existing shallow slice predicate alone does not classify ternary expressions; use a classification that covers those alternatives or pair the boundary check with an explicit recursive check.

Do **not** substitute a blanket `r134_holds_kosh` rejection: the existing FFI contract deliberately permits a whole kosh as ptr and unwraps its elements. Preserve valid i64/f64/string/whole-kosh-pointer controls. A slice-to-FFI conversion would need a separate explicit lifetime/representation contract; silently treating its descriptor as ptr is not that contract.

Use a stable located refusal (the existing `E_FFI_KIND` mechanism is suitable) and no emitted object on failure. Earlier rejection by the generic walk may retain E_VIBHAG_ANKA; every rejected shape need not produce the same code.

The implementer's focused evidence should distinguish statement and expression call forms, all three FFI argument kinds, literal and named mala/kosh-backed slices, and a conditional slice case, with valid controls. Compile-time refusal can establish the boundary without executing foreign code. **These are requested validation cases, not executions performed here.**

## WS2 — the mala asymmetry is deliberate deferral with a missing obligation

The branch is intentional: comments explicitly defer a kosh borrow to the more specific kosh-boundary error. It is not permission for a kosh slice to be used as a number.

The complete asymmetry is more precise than “mala rejected, kosh allowed”:

| Value at an untyped/foreign argument boundary | Walk behavior at this pin |
|---|---|
| Direct `a[lo:hi]` from a mala | Recognized slice; holds_kosh false; rejected directly |
| Direct `k[lo:hi]` from integer kosh | Recognized slice; holds_kosh true; deferred |
| A named slice or vibhag parameter, even if mala-backed | `r134_kosh_slice.name` conservatively treats slice names as possible kosh borrows; deferred |

A named mala slice can therefore reach the same missing FFI check. Fixing only literal kosh slices would miss it.

The error is **deferral without a receiving check**. Local scalar calls reach `gen_typed_call_arg` and its boundary checks; FFI dispatch bypasses that helper. This belongs to the same slice-as-scalar / unchecked-boundary class.

Muse's path argument and this gap can coexist: visiting a value in the walk is not equivalent to completing every required semantic check. Preserve the useful routing finding, but remove the inference “therefore either the walk or the boundary must reject every case.” The foreign boundary here disproves that inference.

## WS3 — no unconditional v314 approval; a finite path to YES

**A version number plus closure of the FFI case is not yet a release verdict.** I would say YES for the documented v1 scope once the identified final package closes this boundary, reconciles the actual budget policy, and passes the agreed native Windows acceptance for changed installer behavior. This does not require a universal absence-of-defects claim or an unlimited new test program.

### The budget statement in the shared state is not the implementation

The v313 source diff sets `R143_WALK_BUDGET` to **349521**, not 200000. There is **no --analysis-steps parser or string in src/** and no new E_VRIKSHA_SEEMA diagnostic. R217 specified an interface; it did not implement it. The current docs describe a fixed internal stop, a different policy.

Do not report R217 as “implemented to the letter.” Either explicitly supersede its proposed interface with the fixed-stop policy, or implement and verify that interface. **I am not requiring a flag as an independent release condition**; truthful reconciliation is the requirement.

Also qualify the fixed-stop proof: the source/gate check the arithmetic `8 * floor(AST_HEAP_CAP / AST_NODE_SIZE) + 1` and field-loop size, not the premise that every reachable node is visited at most once. The walk has no visited set and pushes fields that may or may not be nodes. A universal bound requires establishing tree topology/no repeated reachable nodes for the actual AST construction, not just matching constants. This is an unproved premise in the reviewed evidence, **not a reproduced budget failure**. Report the bound as the implementation's intended defensive bound unless its premise is established.

“A program meets one size limit” also overstates the code: block-statement, nesting, work-stack and other capacity guards still exist. The AST arena is one capacity, not the only one.

### Native workflow status

Claude's v313 changes enlarge the licence instruction and move the licence box; uninstall now attempts deletion of its own staging script/log and a non-recursive directory removal under specific checks. Those are source changes with contributor Wine/static evidence, **not native v313 acceptance**. The cleanup catch is empty, so the source itself does not guarantee that every successful uninstall leaves no staging directory; observe the intended successful native path.

The new `WINDOWS-FIRSTRUN-PATHS-2026-11-08.md` explicitly tests **v312** setup `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6`:
- reported 10 PASS / 1 FAIL / 1 SKIP on Windows 11 Home 26300, standard existing account;
- actual PATH-declined Start-menu terminal works;
- shell opening succeeds for spaces, Devanagari, ampersand, literal percent-variable text and explicit Open With;
- documentation shortcut opens the installed book;
- a preserved desktop “Sutram IDE” link opens its original Notepad target with no visible collision explanation;
- desktop option says “Sutram Terminal” although the engine manages Sutram IDE.lnk;
- reported restoration verification: 672 checks, zero failures.

Credit those successes; do not reclassify them as v313 results. The desktop issue should preserve the user's link while explaining the collision and directing them to the installed Start-menu IDE. Correct the checkbox wording. This is a bounded usability correction, not evidence of user-data loss or a reason to discard the preservation rule. An actual new-program save/build/run is not established by merely opening fixture text or the documentation.

### Release-note wording supported now

1. **v313 compiler validation:** Claude reports Linux/Xvfb gates 77 PASS / 0 FAIL / 1 NOT-RUN, suite 327 PASS plus 4 without expected output, and crash corpus 227/0. NOT-RUN is native Windows execution.
2. **Comparison with v312:** 782 programs comprise 587 byte-identical outputs, 181 identical refusals, and 14 newly added probes, with zero differing existing outputs. The fourteen probes are rejected by both versions; do not silently count them as existing baseline programs.
3. **Historical probes:** Claude reports all fourteen rejected on v313; eleven compiled on v307. These cases and the two supplied mutants support those measured outcomes, not closure of every future boundary or store.
4. **Windows compiler under Wine:** Claude reports 587 outputs identical to Linux-produced PE and 195 refusals across those 782 programs. Wine is not native Windows acceptance.
5. **Analysis budget:** v313 uses a fixed 349,521-step defensive stop and a separate 3 MiB AST arena, with other capacity limits still applicable. The configurable R217 flag is not shipped at this pin. No fixed source-term conversion is promised.
6. **Installer:** v313 setup is identified by SHA-256 `85364c159c15d348818b6c187f12260a18bfa899abe007c474eb03b80806b465`; Claude reports payload/compiler v313 match and Wine self-test exit 0. Licence-label and staging-cleanup fixes await native verification.
7. **Known pending work:** the FFI slice boundary identified by static review remains open at this pin. Native v312 first-run findings include the desktop collision explanation and checkbox wording. Do not describe these as fixed in an unreviewed future package.
8. **Scope:** tested platform/configuration and reused unchanged-component evidence must be named. No general memory-safety guarantee, arbitrary foreign-code safety, race freedom, or all-Windows-configuration acceptance is established.

For the final accepted package, replace pending statements only with exact evidence. The smallest YES remains: **“YES for the documented v1 scope on the tested Windows configuration: the identified final package passes the agreed checks, closes the FFI slice boundary, verifies the remaining installer fixes, and accurately documents its shipped limits.”**

No product edits, builds, CI launches, merges or native execution performed.
