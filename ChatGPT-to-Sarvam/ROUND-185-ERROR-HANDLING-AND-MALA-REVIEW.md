# R185 — strengthen existing explicit results; do not invent a second exception system

Base: `ff5d9d419976f3f48f37e63ab4aefaa56f41dd9b`, compiler v292. Read-side source/design review, 2026-11-03. R184 inventory is delivered separately and remains the priority vocabulary workstream.

## Findings that change the assignment

1. **Programs already can return, propagate and handle explicit failures.** `src/r25_phal.inc` implements `nivartanam siddhi(v)`, `nivartanam dosh(c)`, `prasar f(...)`, and R26's `yadi dosh (q = f(...)) { ... } anya { ... }`. This does not catch fatal compiler-generated traps.
2. **The named, recognized mala store already converts dasham numerically.** `src/sutram_compiler.asm:19252–19290` calls `emit_f64_to_i64_rax`; the helper at 26979–27065 checks an exact integer round trip. The assignment describes the older raw-bits behavior. This source finding is not a native rerun or proof about aliases/untyped parameters.
3. **The arena wrong answer has a recorded diagnosis.** Claude R109 identifies the retaining-chain/fixed-point cutoff on the unmerged arena branch. It should not be described as an unexplained failure.
4. **55 is not a demonstrated count of live native diagnostic codes.** The attached source inventory finds 47 tokens in src assembly/includes (excluding the generated translated-message include). Broader tools/tests/docs scans mix in reference-tool codes and placeholders. Code presence alone does not prove an unconditional reachable diagnostic.

## Existing mechanism and its limits

The native calling convention carries payload/code in RAX and status in RDX (0 success, 1 failure). A phal procedure returns explicit status; ordinary direct calls must handle or propagate it. `prasar` propagates by an ordinary early return; in `mukhya` it exits with the failure code (OS exit status has a narrower observable range). The R26 handler binds the code in its failure branch and the value in its success branch, allowing execution to continue.

The integration is active: main parser `r26_parse_handler` at line 14793, code generator `r26_gen_handle` at 18544, return status emission at 20490, and include at 30627. `examples/250_r26_dosh_handler.sm` demonstrates invalid-digit/empty-input failures and handled continuation. `docs/LANGUAGE-REFERENCE.md` section 18 describes the feature and limitations. These references are pinned to the base above; line numbers can drift later.

This is not a first-class generic `phal<T>` type: indirect/function-value phal calls and dasham result payloads are not supported by the documented native interface. It is also distinct from `lib/phal.smlib`: that library uses caller-owned two-cell mala storage `[ok,value]`, with failure `[0,0]`, zero-allocation producers and checked arithmetic. Its result can be ignored and its mutable storage aliased. Do not confuse the two conventions or claim the library carries arbitrary error codes.

Earlier statements in `docs/ERROR-CONVENTION.md`, PROJECT-MASTER and the design charter that there is no propagation are stale beside the current compiler/reference. Reconcile those descriptions in a separately accepted documentation change. No source/reference files are changed by this handoff.

## Three options and decision

| Option | Behavior and cost | Decision |
|---|---|---|
| No language handling; explicit checks/status conventions only | Small implementation, but callers must inspect actual operation status. Prechecking free memory cannot guarantee a later allocation. Discarding the existing native result syntax would lose useful functionality. | Reject as the full design; preconditions remain useful. |
| Minimal explicit raise/handle without nonlocal unwinding | Already largely implemented by siddhi/dosh, prasar and yadi dosh. Two result registers, status-setting instructions and a conditional branch on handling/propagation; no heap exception object. Costs need benchmarks before numeric performance claims. | **Choose this existing mechanism.** Specify and extend it coherently. |
| Full exceptions with nonlocal unwinding | Requires cleanup semantics, emitted unwind/search support, stack/FFI rules and verification of resource lifetimes across nonlocal exits. No GC or external runtime dependency does not make this impossible; support could be emitted into native code. | Defer: complexity is not justified by this diagnostic inventory. |

Keep recoverable operation failures as explicit results and invalid-program/safety violations as fail-stop diagnostics. New fallible allocation, parsing or conversion operations should return `dosh` before publishing partial state. They must specify code meanings, ownership on failure and rollback/cleanup obligations. Do not parse printed E_ tags as a runtime protocol or implicitly make every existing fatal trap catchable.

`prasar` already calls mandapa return-rewind support (`r73_gen_ret_rewind`) on the early-return path while preserving payload/status. That does not establish general cleanup of files, locks, FFI objects or arbitrary resources. Any extension must test those contracts separately. Preserve existing non-phal ABI; define future float/FFI result representation before extending it.

For arithmetic, checking the divisor prevents zero division, but signed MIN/-1 overflow also needs handling. Prefer checked operations with explicit status over duplicating incomplete guards at every caller. A bounds/lifetime trap is not permission to retry with a dead reference.

## Code phases: what a running program can respond to

47 source tokens: **40 compile/tool pre-execution, 4 mixed compile/runtime, 2 runtime fatal, 1 conditional runtime fatal**. The JSON supplies file/line/text evidence for every token. E_ABBREVIATION_VALUE and E_UNSAFE_BOUNDARY include optional diagnostic machinery; presence is not proof of default-build emission. None of the fatal paths below is automatically caught by `yadi dosh`; prevention or a fallible API is a different operation.

| Code | Phase | Program response / required action |
|---|---|---|
| `E_ABBREVIATION_VALUE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_AMBIGUOUS_FIELD` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_ANTARAL_MISHRA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_APARIKSHITA_AHVAN` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_APARIKSHITA_KARYA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_APARIKSHITA_SMRITI` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_ARITY` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_ATIPRAVAH` | compile/tool pre-execution | Literal/constant-expression overflow detected during compilation; use representable constants. Runtime checked arithmetic has its separate result/trap paths. |
| `E_CHAKRA_DASHAM` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_DASHAM_KRIYA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_DASHAM_VITTI` | compile + runtime | Literal/type checks or exact float-to-integer conversion failure. Validate/convert through an explicitly fallible API; no current trap catch. |
| `E_DUPLICATE_NAME` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_EXPORT_UNDEFINED` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_FFI_KIND` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_GAHANATA` | runtime fatal | Recursion-depth protection. Bound recursion/use iteration; do not resume the trapped operation. |
| `E_INTEGER_TRAP` | conditional runtime fatal | R65 checked-integer build path. Use checked arithmetic results to branch; not an ordinary handler event. |
| `E_KOSH_GANIT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_KOSH_MANDAPA` | compile + runtime | Static escape refusal and runtime lifetime/generation check. Repair ownership; never continue using a dead reference. |
| `E_LIKHA_TRAYA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MALA_GANIT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_ALIAS_REUSE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_CYCLE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_DEPTH` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_DUP_EXPORT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_INVALID` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_LIMIT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_MISSING` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_NOT_EXPORTED` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_V1_ALIAS` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MULYA_VINA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_NIRMMITA_RNA` | compile/tool pre-execution | Negative literal allocation size refuses at compile time; validate dynamic input in a fallible allocation contract, not by catching this code. |
| `E_NIRMMITA_SEEMA` | compile/tool pre-execution | Known raw allocation + constant out-of-range index refuses at compile time. Dynamic analogous bounds use another trap path; validate index before access. |
| `E_PARIKSHITA_STHAN` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_PARIMITA` | compile + runtime | Invalid budget refuses; dynamic budget exhaustion terminates. Bound work; a future fallible allocation must check before mutation. |
| `E_PARSE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_SCRATCH_ESCAPE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_SHUNYA_BHAJAN` | compile + runtime | Constant zero can refuse at compile time; dynamic zero stops. Check divisor or use checked phal division before the trap. |
| `E_UNDEFINED_FUNCTION` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_UNDEFINED_NAME` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_UNKNOWN_FIELD` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_UNSAFE_BOUNDARY` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_UTF8` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_VARTANI_CAT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_VARTANI_GANIT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_VARTANI_SATYA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_VARTANI_SMRITI` | runtime fatal | String allocation failure. A future fallible allocator could report failure before publication; checking available memory beforehand is insufficient. |
| `E_VARTANI_TUL` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |

### Why broad token counts can reach 55

These eight additional tokens make 55 when added to the 47 source tokens, but that arithmetic does not establish the handoff author's original counting method:

| Additional token | Evidence/category | Running-program response |
|---|---|---|
| E_EXPORT_COLLISION | tools/module_graph_reference.py and tests | Build/module input correction; reference-tool diagnostic |
| E_EXPORT_DUPLICATE | tools/module_graph_reference.py and tests | Build/module input correction; reference-tool diagnostic |
| E_IMPORT_ALIAS | tools/module_graph_reference.py and tests | Build/module input correction; reference-tool diagnostic |
| E_PRIVATE_SYMBOL | tools/module_graph_reference.py and tests | Build/module input correction; reference-tool diagnostic |
| E_BAD | tests/r83 diagnostic fixture | No real operation to recover from |
| E_CODE | documentation/template placeholder | No real operation to recover from |
| E_OTHER | tests/r83 diagnostic fixture | No real operation to recover from |
| E_TEST | tools X11 test fixture | No real operation to recover from |

Also exclude E_APARIKSHITA_ (prefix), E_DASHAM_VITTII (changelog typo), E_MOS (malformed negative fixture). The broader scan includes these too, hence naive token counting can yield 58. The source JSON is the reproducible bounded inventory; request the original 55-item list if exact reconciliation with its author is required. English machine identifiers and messages without position text also refute the blanket assertion that every code is Sanskrit with a line number.

Notable distinction: E_NIRMMITA_SEEMA is a compile-time known-allocation/constant-index refusal. Analogous dynamic bounds faults take a different path; they are not evidence that this particular tag is catchable at runtime. Similarly, literal E_ATIPRAVAH differs from runtime checked arithmetic.

## dasham into mala: preserve numerical meaning at the store

Equal byte width only preserves a representation, not a type. Untagged whole-number cells cannot tell whether eight bytes mean integer 3 or the encoding of floating-point 3.0. Changing every read to a floating-point interpretation would corrupt existing integer programs. There is no correct universal read-side guess.

For the existing whole-number mala contract, the smallest correct semantics are: accept exactly representable integral dasham values by numeric conversion; reject fractional, non-finite and out-of-range values; retain integer reads. Use typed dasham kosh for floating-point collections. Any raw bit reinterpretation belongs to a separately explicit low-level contract.

This is already the intent of the recognized-array store path. The helper emits movq, cvttsd2si, cvtsi2sd and ucomisd, then rejects unordered/non-equal round trips using E_DASHAM_VITTI and termination. Thus source predicts 3.0 -> integer 3, -3.0 -> -3, signed zero -> 0, fractional/NaN/infinity/out-of-range -> rejection. Signed zero's sign is deliberately not preserved by numeric conversion. A nearby older comment about truncation is weaker than the actual exact-round-trip sequence.

Remaining verification work is specific: direct local/global mala, aliased mala, field-held references, untyped procedure parameters, computed dasham expressions, boundary values including -2^63 and +2^63, and integer/float kosh controls. Ensure source type and target collection provenance survive every path. If an alias bypasses `is_array_var`, fix provenance/type propagation rather than converting all raw-pointer stores or rewriting all loads. These are proposed cases, NOT RUN here. A graceful conversion API can later return dosh without changing the fail-stop assignment contract silently.

## Arena status: already diagnosed, still unmerged

`Claude-to-Sarvam/R109-00-ARENA-STAYS-UNMERGED-TWO-HOLES-CLOSED-PAYLOAD-NAMED.md` records a 40-step retaining chain escaping on `claude/r108-arena-review` at 0e71e54, followed by reuse producing 99 instead of 11. The fixed 32-round analysis cutoff is not convergence; sufficiently long chains escape classification. The report also separates main alias-provenance repairs and convergence-until-unchanged work from the unchanged arena branch.

Do not merge that branch based on main's scratch-reclamation measurements. Main's block-kosh retention policy and the experimental arena reuse policy are different. Require the long-chain and alias cases against the actual arena head after integrating the relevant analysis fixes, including preservation of payload/lifetime checks. This review neither reproduces the failure natively nor certifies a fix.

## Acceptance boundary

Delivered: source-backed correction of the assignment's premises, three design options and a selection, 47-code phase inventory with extra-token reconciliation, numeric-store semantics and focused verification obligations. R184 report/table/evidence accompany this handoff.

No production files changed. No native build, suite, guard, CI or Windows execution run. Existing repository evidence is attributed to its authors; it is not presented as a new measurement. The next implementation decision should be based on this current-source baseline, not a new exception feature built to fill a gap that is already partly implemented.
