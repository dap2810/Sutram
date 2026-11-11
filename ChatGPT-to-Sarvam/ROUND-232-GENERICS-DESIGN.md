# ROUND-232 — Generics fit the compiler; they do not belong on the 1.0 critical path

11 November 2026. Base: main `cb132a77a99e0a6b80e8bdeef8ae28405613f938`, compiler v315. Return to `Sarvam-to-ChatGPT/ROUND-232.md`. Source paths and line numbers below refer to that commit. The source/library files used by this review are unchanged from the previous v315 review; new staged versions are not silently substituted.

**NOT RUN — read-side role, no toolchain used.** No NASM, compiler, generated program, tests, gates, Windows or installer was executed. This return contains a design and a static inventory, not an implementation or performance result. Only files in `ChatGPT-to-Sarvam/` are delivered.

## Decision

**Ship 1.0 without new generics. For 1.1, use explicit generic declarations, inferred call-site types, and a bounded specialization worklist over the existing AST. Do not add runtime type tags to every kosh.** First make the existing compile-time type information coherent across generic boundaries; then prototype a small numeric-kosh subset. Expand to representation-aware sequence templates only if their measured maintenance benefit warrants it.

Three premises in the brief need correction:

1. **This compiler does not emit user code while it reads source text.** It expands imports, lexes, parses the program, analyzes it, generates main, generates function bodies, and backpatches calls. It already retains the bodies needed for specialization.
2. **Eight-byte storage does not mean the compiler knows no type.** `kosh` and `kosh dasham` already have different compile-time element kinds, typed parameter checks and different arithmetic interpretation. Neither requires a runtime type field.
3. **310 functions is not evidence for 160 type duplicates.** The attached inventory enumerates 310 definitions in 24 modules. A focused body comparison identifies 34 bodies in 15 candidate algorithm families: 19 additional bodies beyond one per family, conditional on representation and policy abstraction. That is not 160 removable functions, and several apparent list duplicates are already wrappers around shared algorithms.

The R231 audit is delivered, but that does not mean its corrections are all implemented. The negative-digit guard remains an identified source defect; Windows acceptance remains a release activity. “95%” is not a measured estimate of the implementation effort left.

## WS1 — What “one pass” can honestly mean

Let **C** mean `src/sutram_compiler.asm`.

| Current step | Source evidence | Consequence for generics |
|---|---|---|
| Expand imports, lex, parse | C:3150–3196 calls `expand_imports`, `lex`, `parse_program`, then `gen_code` | The source is not streamed straight into final instructions. Imported generic bodies can be retained like ordinary bodies. |
| Retain function ASTs | C:1635–1641 parameter/type/definition tables; C:7993 and C:19010 onward collect definitions | A body can be available independently of when its machine code is emitted. |
| Classify return types before main emission | C:18035–18042 calls `classify_float_functions` | There is already a semantic phase before call-site code generation. |
| Repeat return classification until stable | C:27250–27295 iterates functions while information changes | “Exactly one visit to every AST node” is already not a property of v315. |
| Emit bodies after main; patch calls | C:18209–18216; `gen_all_functions` at C:18426 onward | Forward machine-code addresses are already handled. New specializations can use symbols and relocations rather than being emitted in the middle of a caller. |

**Yes, monomorphization is compatible with one source parse.** It requires retaining a representation of each template and instantiating that representation for concrete arguments. If “single pass” instead forbids retaining/revisiting bodies, then arbitrary later specialization is impossible without relaxing another condition: restrict all instantiations to an explicit list, require earlier definitions and retained templates, or use shared runtime-dispatched code. Even “emit on first call” revisits a retained body; it is not literally one visit to everything.

Suggested constraint wording: **“The compiler parses each expanded compilation unit once, retains a bounded AST, performs bounded semantic analysis, and emits native code directly without an external optimizer or language runtime dependency.”** This is a proposed clarification of what the source already does, not unilateral permission to change a project constraint. Imports and existing preflight scans also make a literal one-read claim unsuitable.

### The alternatives

| Shape | Feasibility and cost | Recommendation |
|---|---|---|
| Deferred specialization | Keep templates, discover concrete calls, check each instance, emit instances and patch calls. Discovery must continue until the queue is empty because one instance may call another. It is not always exactly “two AST passes.” | **Best eventual fit.** Reuses the present architecture and avoids runtime dispatch for built-in operations. |
| Immediate emission at first call | Possible with a retained body, but emitted callee bytes must not become fall-through instructions in the caller. It needs an out-of-line buffer or a jump around the callee, plus save/restore of extensive code-generator state. | Do not interleave bodies. “First call registers an instance; later queue emission” is the useful part, and is the deferred design. No new blanket definition-before-use rule is needed merely for this mechanism. |
| One implementation with callbacks/dictionaries | A comparator supplies the ordering while a shared routine moves fixed-width elements. Dynamic calls cost instructions, but an arbitrary slowdown cannot be claimed without measurement. Static checking and shared code are compatible; type erasure does not logically require no type checking. | Useful for user-defined ordering and existing integer/raw-word sequences. Current indirect-call typing is not sufficient to promise arbitrary safe float/text callbacks. |
| **Fourth: finite static overload families** | A single public name resolves to a small set of already-written integer/float implementations at compile time. No template-body instantiation or runtime dispatch is necessary. | Small facade if discoverability is the only requirement; it does **not** remove duplicated bodies. Prefer library-level exposure over many compiler-name special cases. |
| Explicit instantiation lists / closed templates | The library author enumerates allowed types or representations; the compiler creates that finite set, optionally lazily. | A useful restriction for a first prototype, not a reason to generate every unused instance. |
| Representation sharing | Copy/swap/reverse can sometimes share machine code for equal-sized elements while arithmetic/order still specializes. | Later optimization. Begin with correct specialization identities; identical storage width is not sufficient proof that two complete bodies are interchangeable. |

For comparison, the Rust compiler documents collection of concrete instances before code generation, with code-size and compile-time costs. Zig documents both explicit compile-time type parameters and call-site inference. These are feasibility examples, not instructions to import either compiler's complexity. Primary references: [Rust monomorphization](https://rustc-dev-guide.rust-lang.org/backend/monomorph.html), [Zig parameter inference](https://ziglang.org/documentation/master/#Function-Parameter-Type-Inference), [Zig compile-time parameters](https://ziglang.org/documentation/master/#Compile-Time-Parameters).

### A bounded implementation plan

1. Parse a new, explicitly marked generic declaration into an immutable template. Preserve the old path for every ordinary declaration. Bind a type variable by identity, not by textual search-and-replace; do not reinterpret existing untyped functions as generic.
2. At a direct call, infer concrete arguments from the caller's established type environment. Create a canonical key containing template identity, concrete type identities, representation and any permitted compile-time policy arguments. Integer, binary64, a pointer and a slice are not interchangeable keys merely because their payload is one qword.
3. Register the instance and its symbol **before** following its dependencies. Cache `queued/checking/checked/emitted` states so ordinary same-instance recursion reuses the same entry. For the first slice, reject type-changing polymorphic recursion and unbounded type construction.
4. Check the specialized signature and return type before emitting callers that need conversions. Start with a declared result type (`T` or a fixed scalar), not a new general return-type inference problem. Check non-dependent errors at declaration; report dependent errors with both the call location and the failing template operation.
5. Use isolated specialization environments or bounded cloned ASTs. Do not mutate the shared template's `[FUNCDEF+40]` return classification, parameter bytes or global inference caches and then reuse it for another type. Cache string/kosh/escape/return summaries per instance rather than only by original function name/index.
6. Append checked instances in a deterministic order, emit each once, and patch calls with specialization symbols. Generic-to-generic calls extend the worklist. Every pending dependency must be resolved or refused before writing a successful output.
7. Cap instance count, nesting, AST growth, generated code and patch entries independently. Report the exhausted limit and instantiation chain. Reuse the existing failure discipline; do not silently truncate or fall back to an untyped call.

Initial scope: one type parameter with a finite set `{signed integer, binary64}`; homogeneous named kosh arguments; direct calls; built-in operations; no generic structs, traits, implicit heterogeneous containers, generic function values, foreign generic ABI, or arbitrary compile-time execution. Generic state must also work in `--check`. Initially refuse generic declarations in object/separate/FFI modes with a clear message rather than emitting incomplete objects; maintain the existing behavior for all non-generic programs in those modes. A later object design needs template availability or explicit monomorphic exports, canonical symbol names and duplicate-instantiation ownership.

## WS2 — The duplication, with names rather than a guessed percentage

### Counting method

`ROUND-232-LIBRARY-CANDIDATES.json` includes all 310 definition names, signatures, source lines, module counts and hashes, plus the selected disjoint candidate families. I enumerated all declarations, then read the selected bodies and relevant wrappers. This is a **focused estimate**, not an exhaustive semantic clone detector or a claim that all 310 bodies were proved equivalent/non-equivalent.

“Same algorithm” is weaker than “same contract.” The count excludes wrappers from duplicated algorithm bodies and does not count different sorting algorithms as type variants. The candidate estimate assumes a future shared algorithm can parameterize representation and preserve every API's failure, output and aliasing rules.

### Ten leading candidates

The first three have three or more independent implementations; the remaining rows are paired representation variants. Ranking is by usefulness/amount of repeated algorithm, not a measured engineering-hours saving.

| # | Algorithm | Independent bodies and definition lines | What must differ |
|---|---|---|---|
| 1 | Sum | `shreni.yog`:66; `mala.mala_yog`:62; `sankhyiki.purna_yoga`:131; `sankhyiki.yoga`:16 | Raw pointer/array versus kosh length, integer addition versus binary64 addition, and accumulator initialization. Four bodies; `suchi_yog` is already a wrapper. |
| 2 | Minimum | `shreni.laghu`:39; `sankhyiki.purna_laghutama`:148; `sankhyiki.laghutama`:34 | Integer/float comparison, empty-result type and representation. `suchi_laghu` delegates and adds an `ok` result. |
| 3 | Maximum | `shreni.adhik`:53; `sankhyiki.purna_adhikatama`:161; `sankhyiki.adhikatama`:47 | Same distinctions as minimum; `suchi_adhik` is a policy wrapper. |
| 4 | Replace substrings | `varna_pratisthap`:189; `khand_pratisthap`:142 | Cell versus byte loads/stores, replacement termination and output capacity. |
| 5 | Split | `varna_bhed`:251; `khand_bhed`:206 | Input layout, packing/unpacking, and **different extra-terminator capacity requirements**; not just substitute the element type. |
| 6 | Join | `varna_yuj`:338; `khand_yuj`:289 | Both read length-prefixed cell segments; output/separator representation differs. A single stride for every buffer would be wrong. |
| 7 | Substring search | `varna_anwesh`:155; `khand_anwesh`:105 | Cell versus byte element access; same negative/empty-needle cases must be retained. |
| 8 | Trim ASCII spaces | `varna_chhid`:373; `khand_chhid`:327 | Element/output width and terminator width; neither is a generic Unicode whitespace trimmer. |
| 9 | Uppercase ASCII copy | `varna_unnat`:409; `khand_unnat`:365 | Cell versus byte storage and truncation; only ASCII case conversion. |
| 10 | Lowercase ASCII copy | `varna_avanat`:431; `khand_avanat`:388 | Same representation distinction as uppercase, with the opposite operation. |

Here `shreni`, `mala`, `sankhyiki`, `varna` and `khand` mean their respective `lib/<module>.smlib` files, not a new namespace syntax.

These ten groups contain **24 bodies**, or **14 additional bodies beyond ten shared algorithm definitions**. Five further paired families are recorded in the JSON: prefix (`varna_aadi`/`khand_aadi`), suffix (`varna_ant`/`khand_ant`), lexical comparison (`varna_tul`/`khand_tul`), reverse-copy (`varna_viparyay`/`khand_viparyay`), and non-overlapping substring count (`varna_gan`/`khand_gan`). They add ten bodies and five potential consolidations.

**Total for this inspected candidate set: 34 bodies, 15 algorithm families, 19 potential body consolidations.** Of these, twelve paired text algorithms account for twelve consolidations; the three numeric families account for seven. This is an upper bound **within this selected set under the stated abstraction**, not an upper bound on all duplication in the library. Compatibility wrappers and new helpers may keep or increase the public definition count. Even the artificial arithmetic `310 − 19 = 291` assumes deleting old definitions and adding only one replacement per family; it is not a proposed library size. There is no evidence here for `310 → 150`.

Strictly per numeric type, the obvious statistics counterparts are sum, minimum, maximum, mean, range and variance. Their float functions are `yoga`, `laghutama`, `adhikatama`, `madhya`, `vyapti`, `prasaran`; their integer counterparts are the corresponding `purna_*` functions. **Do not collapse all six as type substitutions:** integer mean truncates; integer variance uses a truncated mean and guarded integer arithmetic; float variants have floating-point rounding/NaN behavior. Mean/range/variance are therefore not included in the 19 estimate. The three-way repetition in sum/min/max also includes same-type representation overlap, not three distinct element types.

### Sort is not thirty copies, or three copies per type

`lib/shreni.smlib` has four public sorting algorithms: bubble (`budbud_shreni`:13), shell (`shankh_shreni`:120), insertion (`nivesh_shreni`:148), and merge (`mil_shreni`:223, with recursive helper `mil_shreni_punar`:174). `lib/suchi.smlib`:214–219 adapts list storage and failure status by calling the existing merge sort. These are **four algorithms, one recursive helper and one adapter**, not six type-specialized copies. A single beginner-facing sorting entry point would improve discoverability, but does not require deleting the educational algorithms or inventing a generic system.

Other exclusions matter:

- `suchi_yog`, `suchi_gan`, `suchi_anwesh`, `suchi_asti_kramabaddha` and `suchi_dwi_anwesh` already delegate (`lib/suchi.smlib`:249–280). They are API adapters, not duplicated loops.
- `varg` and `vargit` are the same integer square algorithm (`lib/ganit.smlib`:7–20). Ordinary delegation could share it; no generics needed.
- `adish_gunan` and `bindu_gunan` are both binary64 dot products (`lib/samanvaya.smlib`:136; `lib/sankhyiki.smlib`:100). Their diagnostic function names differ. Shared implementation is a same-type refactor, not a generic-type win.
- Checked, saturating, sentinel-returning and `phal`-packaging arithmetic are different contracts. `phal_janchit_*` wrappers do not establish type duplication.
- NUL-terminated and explicit-length string scanners have different boundaries. Replacing both with the NUL scanner makes slices wrong; replacement by a counted core needs boundary adapters.

### Smallest useful feature

**For immediate usability:** expose a well-documented default sorting operation using the existing integer algorithm, and use ordinary helpers/adapters where semantics already match. Existing function values can support a comparator-taking integer sort without general type parameters, though implementing it is another code round and current callback typing limits its safety claims.

**For removing the largest identified duplication:** the missing abstraction is a **sequence access/representation policy**: byte versus qword read/write, explicit length, separate output representation, and termination/capacity policy. A restricted compiler-time template over those policies would address the twelve paired text algorithms. Merely adding `kosh T` for integer/float does not solve them, because they mostly accept raw pointers whose layout is not inferable. Adding one runtime stride argument to every function is not free either: several already use all six argument slots, and split/join use different layouts for different buffers.

The smallest first **language** experiment is still finite integer/binary64 kosh specialization because that metadata already exists. Be honest about its smaller payoff: it establishes a sound mechanism rather than halving the library. Validate it before attempting byte/cell views. Prefer explicit layout adapters at legacy raw-pointer boundaries; never guess a buffer's stride from its bytes.

## WS3 — The type information exists, but it is not yet one general type system

| Question | Source-backed answer |
|---|---|
| Does kosh have a runtime type field? | No element-type tag in the descriptor emitted at C:19279–19367. The ordinary descriptor has length, capacity, elements pointer and region size; block-liveness mode adds metadata, so “always exactly four qwords” is too broad. |
| Does the compiler distinguish element types? | Yes. Declaration marker 2 versus 3 at C:15006–15057; `float_kosh_vars` at C:1560; `mark_float_kosh_var` / `is_float_kosh_var` at C:27676–27719. |
| Are function parameters typed? | Five current parameter codes: raw/integer, scalar dasham, kosh, kosh dasham, vibhag (C:69–73). The parser stores one byte per parameter slot at C:15335–15344. |
| Are wrong kosh types rejected? | `gen_typed_call_arg` at C:27311–27393 checks a named kosh and rejects integer/float mismatch. Both pass the same pointer-sized value without converting the pointer as a scalar. |
| Does aliasing discard the kind immediately? | No: alias-kind propagation tracks float kosh before plain kosh at C:27779–27809. It is not safe to characterize all metadata as erased at the first copy. |
| Is every variable a fully typed symbol entry? | No. The main variable table stores name and offset (C:1535); float names, string flags, array/kosh/slice markers and structure-use metadata are parallel structures. `vitti s = "ab"` illustrates why “every vitti is semantically only an integer” is too broad. |
| Can existing slices carry every element type? | No. `src/r23_capabilities.inc`:574–596 explicitly refuses a float-kosh slice. A universal typed `vibhag T` is additional work, not existing capability. |
| Are calls overloaded by argument type today? | Ordinary function lookup is by name, then declared parameter kinds control checking/conversion (C:26997–27038). There is no general “find the sort overload from element type” facility. |
| Are callbacks already fully typed? | No. `src/r23_capabilities.inc`:174–194 emits `call rax`; C:28962 onward notes that function-value calls have no known parameter kinds. A typed callback API needs signature and effect rules. |

**Inference:** `kramit(k)` can infer integer or binary64 if `k` is a known named kosh or an appropriately typed parameter. The declaration supplies the type even when the collection is empty. It cannot infer “text elements” or a particular record from an opaque integer/raw pointer, nor infer a return-only type parameter from no arguments without an additional rule. Refuse an unresolved type and request an annotation or typed adapter; do not inspect runtime values or choose integer silently.

**Runtime cost of the proposed homogeneous static model:** 0 extra bytes per kosh descriptor, 0 extra bytes per element, and no per-element runtime type test. Compilation needs canonical type IDs and per-instantiation environments; specialize arithmetic, loads/stores and comparisons. Existing bounds and lifetime checks remain. This is a design cost claim, not an implemented measurement.

If a different design adds one qword type tag to a four-qword descriptor, that is a nominal **8-byte header increase**, before alignment and block metadata effects; all descriptor producers/consumers must agree. It does not provide static type safety by itself. Per-element tags instead describe a heterogeneous container, with tag storage and dispatch costs, which is outside the recommended feature. Neither approach follows from the need for generics.

**Already generic in a limited sense:** qword copy (`mala_pratilip`), cell swap (`vinimay`) and list reverse (`suchi_viparyay`) rearrange stored bits without arithmetic on the payload. Their public APIs still have raw/integer and representation restrictions; this is representation-independent movement, not proof that arbitrary typed kosh/float/record arguments can be passed safely. Lifetime is separate from type: `kosh T` does not prevent storing dangling pointers when `T` is a pointer-like value.

## WS4 — Syntax: simple calls, explicit library-author intent

Sanskrit keywords do not forbid punctuation such as brackets or a user-chosen type variable called `T`. `sort` is an English illustrative identifier, not an unavoidable keyword. The real choice is how to expose polymorphism without changing the meaning of all existing untyped functions.

The following are **proposed syntax sketches, not accepted v315 programs**. `samanya` is a provisional spelling for review, not a newly approved language-pack keyword. Prototype behind an explicit experimental opt-in; preserve legacy identifiers by making the modifier contextual rather than globally reserving a formerly valid name. Any multilingual keyword addition requires the project’s vocabulary review before adoption.

| Shape | Proposed declaration surface | User call / assessment |
|---|---|---|
| A: explicit binder, inferred call | `samanya prakriya vinimaya[T](kosh T xs, i, j)` | `vinimaya(k, 0, 1)`. Recommended author surface: one named type variable can be reused across parameters, locals and result. The beginner sees an ordinary call. |
| B: marked declaration, inferred parameter | `samanya prakriya vinimaya(kosh xs, i, j)` | Same call. Less syntax, but now plain `kosh` means something different inside this form; it also needs a way to name the inferred element type for locals/results and express equal-type arguments. |
| C: no new marker | `prakriya vinimaya(xs, i, j)` inferred as generic from its body/use | Same call, but silently changes existing raw-parameter semantics, diagnostics and conversion behavior. Do not retroactively make this the default. A separate explicit opt-in mechanism would still be needed. |

For A, a complete specification must define typed locals such as a `T` temporary and a result annotation before an exchange/sum body is written; using today's `vitti` temporary as if it preserved binary64 would be a mistake. Start with declaration syntax and typing rules, not a plausible-looking example whose intermediate values silently narrow.

A beginner can learn “call `kramit(k)` to sort” without learning how its author binds `T`. Custom ordering remains a separate advanced option. Define error messages at the call: expected known homogeneous collection, received raw pointer / unsupported slice, with the original declaration shown. Do not expose internal specialization names as the primary error. Generic authors need a small closed set of supported operations initially; a full trait language is not necessary for the first numeric slice.

Sorting needs explicit behavior for duplicate elements, stability, empty input, allocation failure and floating-point NaNs. An integer comparator implemented as `a - b` can overflow, so comparator correctness is not solved by generic syntax. The compiler can check a signature; it cannot generally prove that an arbitrary user comparator defines a consistent order or avoids mutating/growing the container while it is being sorted.

## WS5 — Cost, compatibility and release timing

### Effort estimate, not a promise

These are judgment ranges for additional or substantially changed NASM source lines, not a measured patch or calendar estimate. Tests, proofs, books, language-pack review and native acceptance are additional. Implementation choices can move the ranges materially.

| Work package | Rough NASM lines | Scope |
|---|---:|---|
| Generic declaration/signature parsing and canonical type bindings | 400–900 | One binder, closed numeric types, explicit return rule |
| Per-instance semantic context and existing-analysis integration | 700–1,500 | Return/kind/string/escape analysis isolation; reject unsupported boundaries |
| Instance cache/worklist, symbols and direct-call patches | 400–900 | Deterministic queue, recursion reuse, no inline body emission |
| Limits, diagnostics, check/object/FFI exclusions and compatibility plumbing | 500–1,200 | Guard every unsupported path and preserve legacy defaults |
| **First restricted prototype** | **about 2,000–4,500** | Excludes full typed callbacks, generic records, arbitrary compile-time evaluation and generic object exchange |
| Representation-aware byte/cell views plus legacy adapters | **another 1,000–2,500 or more** | Separate layouts for source/output, capacities, terminators, bounds and alias rules |

The ranges overlap where helpers are shared; they should not be treated as a bid. A 100-line AST-copy trick does not cover the semantic work. Conversely, the compiler does not need a new runtime, GC, borrow checker or second implementation language to support this restricted design.

### Concrete risks in this tree

- **Global compiler state and cache contamination:** return-kind and parameter summaries are currently attached to names/definition indices; specializing twice without isolation can compile one instance using another's facts.
- **Finite tables:** C:50–55 permits 128 definitions, 128 emitted functions, 512 call patches and 256 KiB generated code; C:36–39 sets a 3 MiB AST heap. Keep template count and instance count distinct. Two instances per definition can already exceed the emitted-function table.
- **Representation confusion:** integer versus floating comparison, byte versus qword access, and descriptor versus element pointers must not be chosen from equal width alone.
- **Lifetime regressions:** a specialization or callback must preserve the kosh growth/slice escape checks. A comparator that can grow its input invalidates a borrowed element pointer even if its scalar type is correct.
- **Library migration changes bytes:** replacing old loops with wrappers/shared bodies changes calls, code layout, generated bytes and possibly diagnostics. Calling it a refactor does not exempt it from the guard.
- **Separate compilation and FFI:** an object cannot instantiate an unavailable template body from just a function name. Export concrete instances initially or reject the new feature in that mode; do not change the old non-generic path.
- **Semantic policies:** integer wrapping/sentinels, float NaNs, empty-container statuses, output capacity and termination are part of contracts, not incidental differences to erase.

### Keep the byte-identity requirement concrete

For a feature-only prototype, ordinary old source must still use the old parser/type/emission paths. Do not change library bodies, introduce extra generated globals, reorder old functions, or emit unused generic instances. Compiler executable bytes will change; the invariant concerns its outputs for the **same legacy input, options and target**. It must include refusal behavior and diagnostics, not just successful binaries.

Proposed acceptance for the code owner, **not executed here**:

1. Pin the then-accepted baseline and enumerate its actual guard inputs; do not copy a stale “783” or suite count from a handoff. Compare legacy ELF and PE output bytes plus success/refusal and diagnostics.
2. Confirm one cached instance for repeated equal-type calls; distinct integer/binary64 instances; deterministic output across repeated builds; forward calls; generic-to-generic calls; and ordinary same-instance recursion.
3. Refuse unknown raw layouts, integer/float kosh mismatch, unsupported float slices, generic FFI/function-value use, type-changing recursion and every exhausted table/AST/code budget before reporting success.
4. Exercise integer/float arithmetic and return conversions, empty inputs, NaNs and comparator boundaries under the chosen contract. Cover specialization order reversal to expose shared-cache contamination.
5. For any later library migration, separately authorize its changed-byte list and preserve old behavioral contracts and proof inputs. **Do not rebaseline all goldens to make generics pass.** Identical bytes and reorganized library code are separate milestones.

**Release call: after 1.0.** The existing type metadata and retained AST make a small 1.1 design credible. The evidence does not establish that generics are needed to finish 1.0 or that they remove half the library. Finish the accepted fixes, remaining documentation corrections and native Windows acceptance first. Then gate a deliberately narrow prototype on correctness and measured maintenance benefit, rather than on the claim that it is the last big feature.

## Handoff and audit boundary

- This design answers WS1–WS5. The accompanying JSON makes the 310/24 inventory and 34/15/19 candidate arithmetic inspectable. It does not claim whole-library semantic equivalence or an exhaustive maximum reduction.
- Muse's independent ROUND-170 type/duplication audit remains independent; reconcile its classifications with these named families rather than counting the same wrappers twice. No work was written to another partner's folder.
- No source, tests, tooling, installers, language packs, baselines or production documentation were changed. No source branch was merged.
- Public artifacts contain repository-relative paths only and no owner machine details. **NOT RUN — read-side role, no toolchain used.**
