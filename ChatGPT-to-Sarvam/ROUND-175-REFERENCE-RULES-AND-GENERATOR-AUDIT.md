# R175 — reference operators, printing, and the trap generator

Read-side audit and proposed rules, 2026-11-02. Base: `dc09dc02a32c51edb3361152f9b6125f1c79efb8` (v287). Documentation-only return; Claude owns implementation and Muse owns generator changes.

**Verdict:** v287 improves string operations substantially, but does not establish a general reference-type system. Container pairs still reach machine-word operations. Muse's generator is useful as a behavior recorder, but it is not yet an automatic trap detector or acceptance gate. Identity comparison is not inherently wrong; an undocumented choice between identity, contents and raw bits is the defect to eliminate.

## WS1 — what v287 actually does

In `rfx_kind`, a definite string is kind 1, a sometimes-string is kind 3, and everything else defaults to kind 2. `rfx_check_str_binop` passes a kind-2/kind-2 pair onward unchanged. `.ge_binop` then uses ordinary numeric lowering. This includes ordinary kosh/kosh and mala/mala operands: **`==` and `!=` compare address words, and ordering compares those words numerically**. `+` likewise performs word addition. There is no container-content comparator on this path. This is a source-derived finding, **NOT RUN — no toolchain**.

An expression `a == a` returning 1 does not distinguish identity equality from content equality: both can return 1. A decisive probe uses distinct containers with equal contents, an alias, unequal contents, and mutation of one distinct object. Muse's saved v286 matrix uses two separate koshes each holding 7 and records equality 0. That is historical evidence, not a v287 execution here. Do not use an address's particular magnitude or ordering as a stable golden.

The R174 specification was not implemented in full. R105 explicitly retains string-plus-integer pointer arithmetic, mixed assignments, unknown-as-number paths, persistent allocations outside `parimita`, and gaps for globals/elements/indirect calls. It adds text ordering, which R174 had proposed initially refusing. These are distinct implementation decisions and must remain visible. R105's old-program guard is 551 identical binaries, 132 identical refusals and six new cases, across 689 total inputs; “0 DIFFER” is not evidence that all newly supported combinations are correct.

The new whole-function/call analysis addresses the demonstrated R173 cases according to Claude's probes. I do not carry their exact failures forward as if unchanged. But `rfx_check_str_binop` still explicitly allows a sometimes-string beside kind 2 to retain numeric meaning. Therefore printing is **not the last text defect**: unresolved types can still select the wrong operation, and raw pointer offsets and budget/lifetime boundaries remain.

### Recommended operator policy

The table applies when **both operands have the same established type**. These are recommended rules for integration, not a claim that v287 has them all.

| Type | `==` | `!=` | `<` | `<=` | `>` | `>=` | `+` |
|---|---|---|---|---|---|---|---|
| string/Text | Byte-content equal | Complement of equal | Byte lexicographic less | Less or equal | Greater | Greater or equal | Fresh concatenated Text |
| kosh | Refuse implicit comparison | Refuse | Refuse | Refuse | Refuse | Refuse | Refuse |
| mala | Refuse implicit comparison | Refuse | Refuse | Refuse | Refuse | Refuse | Refuse |
| rachana | Refuse implicit comparison | Refuse | Refuse | Refuse | Refuse | Refuse | Refuse |

**Why string differs:** it has a defined sequential byte-content contract. Ordering uses unsigned byte values, first difference decides, and a proper prefix sorts first; no locale collation or Unicode normalization. Equality returns 1/0, without allocation, while concatenation creates owned storage. Keep the existing explicit builtin comparison convention unchanged. Compare live, terminated values; raw pointers are not automatically Text.

**Why refuse the other three for now:** they are mutable composites without a general element/field-type and ownership contract. Address equality can legitimately mean identity, but users must be told that, and identity must survive legitimate movement/aliasing or have an explicit invalidation rule. Blind byte comparison is worse: it compares padding, capacity, allocator headers and pointer representations. Automatically recursive equality introduces cycle handling and ambiguous nested-reference semantics. `+` adds further copying, capacity and ownership choices. A compiler should not invent any of these from an eight-byte representation.

Provide explicit operations separately when implemented: sequence content equality compares logical length and each typed element, ignoring capacity; record equality compares declared fields of the same nominal type, ignoring padding; identity comparison compares a stable live object identity, not an undocumented relocatable storage address. A first content-equality API can support only acyclic, known comparable element/field types and reject the rest. Nested reference fields must have an explicit identity/content choice. Float fields follow the declared numeric equality, including NaN behavior; do not promise reflexivity for every possible composite. No new API spelling is prescribed here.

This policy intentionally replaces implicit container identity comparisons with a diagnostic. Audit existing users and migrate deliberate identity checks before integration. If the owner instead chooses identity for container `==`, that can be coherent, but label it explicitly and test alias growth, block death and reuse; “reference type” alone does not dictate content equality. The proposal here chooses refusal until that contract is delivered.

Mixed reference types, reference-versus-number, and unknown/mixed operands refuse rather than auto-format or fall back to address arithmetic. Text-plus-integer is a **versioned compatibility exception in v287**, not a general reference rule. R174's future uniform decimal-formatting proposal is not shipped and needs raw-offset migration before adoption. Keep numeric-only operations unchanged. Preserve deliberate low-level pointer arithmetic through explicit raw/view operations; do not ban it by misclassifying all pointers as text.

## WS2 — `likha` dispatch and `shabda`

The current `.ge_lk_str` checks AST tag 14 (literal), not semantic Text kind. Nonliteral Text therefore reaches numeric printing. There is a second defect site: for three to six values `.r52_lk_next` sends every nonfinal nonliteral argument to `BN_LKHB`, whose emitter checks only float versus integer. Fixing single-argument `likha` alone leaves text in those positions wrong.

**Dispatch by resolved semantic type, before argument lowering, for every position and supported arity.** Evaluate each argument once in source order, emit its output, then proceed to the next argument, matching the existing interleaved evaluation/output model. A later operand failure can leave earlier output visible; this is not atomic printing. Preserve earlier values across nested calls where lowering requires them. Do not infer Text from address magnitude, AST literal shape, or a memory probe.

| Argument kind | Required behavior |
|---|---|
| Definite Text: literal, local, concatenation, typed return, typed parameter | Print its bytes through the first NUL, without quotes; empty Text emits zero payload bytes. All forms use the same semantics. |
| Integer | Existing signed numeric formatter; comparisons currently produce normalized integer 0/1 and print that way. |
| dasham | Existing specified float formatter, not its IEEE bits. Preserve its precision and special-value policy in this change. |
| Enum/character code represented as integer | Existing numeric representation unless a separate typed formatting contract is introduced; no guessing that a number is a glyph. |
| kosh, mala, rachana | Compile-time refusal until container/record display is specified and implemented. Future formatters need element/field types, cycle/depth limits and deterministic delimiters. |
| Raw buffer, pointer, byte view, function value, opaque resource handle | Refuse implicit content/address printing; require explicit byte output, address formatting or a defined formatter. A file descriptor currently represented as an ordinary integer remains numeric; the compiler cannot distinguish an undeclared nominal handle type. |
| Unknown, sometimes-Text, unresolved global/field/index/call result | Refuse or resolve the type first. Never choose integer merely because definite Text inference failed. |
| No value / void | Compile-time refusal; do not print a stale return register. |

Compile-time validation must cover all arguments even if an earlier runtime expression would terminate. New diagnostics should identify the argument position/type and a valid explicit operation. Preserve raw-byte output in `dvaram_likha`; it must not regain an arity-based overload in `likha`.

**Compatibility on separators/newlines:** do not silently redesign them in the Text-dispatch fix. Current source lowers two arguments as two single-value calls; three to six values suppress numeric newlines except on the last argument. Text literals add none. Preserve those arity rules initially, making a Text variable behave exactly like the equivalent literal in each position. Thus one Text argument has no automatic newline; one numeric argument retains its numeric newline; with two arguments each follows its single-value rule; with three to six only a final numeric argument adds its existing newline. A future uniform print/println design would be cleaner but is a separate migration. Add exact-byte expectations rather than using `.strip()`.

**Keep `shabda` as the explicit text-only form.** It remains useful for compatibility and for making a text-only API intention clear. Its typed path should share the same payload emitter as Text in `likha`, add no separator/newline, and reject known non-Text values. Today's `shabda` also accepts caller-supplied NUL pointers; preserve that only as a documented legacy low-level contract, not a way to cast arbitrary integers into safe Text. A bounded conversion/byte-output API is the appropriate migration for raw buffers. Do not remove `shabda` or break raw callers without a census.

## WS3 — audit of Muse's actual generator

Reviewed `Muse-to-Sarvam/trap_matrix.py` and its saved JSON at this base. The JSON has **112 unique ordered cells**, four kinds, seven operators (`==`, `!=`, `<`, `+`, `-`, `*`, `/`), 19 REFUSED entries and no CRASH entries. The remaining 93 record output/exit. The 28 numeric cells have expected-looking recorded outputs for their fixed inputs, but the script does not compute an oracle or validate them. This is a v286 record, not a rerun on v287.

| Audit finding | Consequence | Required repair |
|---|---|---|
| No expected-result/type-rule oracle | It records behavior; it cannot automatically label a result correct, an old trap fixed, or a new regression | Add a separately specified rule table plus independent output model and versioned approved migrations. |
| Only executable existence decides compile refusal; compiler return code ignored | Compiler crash, timeout-related absence, output failure or parse error can masquerade as type rejection; a failed compile leaving a partial file can be executed | Record compile status first; distinguish expected diagnostic, unexpected compile error, signal, timeout and missing/invalid artifact. Never execute after failed compilation. |
| Runtime exit 1 is accepted as ordinary output | Resource/error exits can be mistaken for successful value results | Separate successful exit 0 from named runtime refusal and other nonzero exits, according to each case's oracle. |
| External `timeout` plus uncaught subprocess exceptions | Timeout, missing tool and signals are conflated or abort the whole matrix, losing the final JSON | Use explicit per-case exception handling and statuses; save incremental records; ensure child processes are terminated. |
| `.strip()` and text decoding; runtime stderr omitted | Newline/whitespace defects disappear, invalid-byte output can abort decoding, diagnostics are lost | Capture stdout/stderr as bytes; retain exact bytes or lossless encoding, exits and signals. |
| No source/compiler/build hash or seed/target metadata | Runs are hard to reproduce or attribute | Store source text/hash, compiler binary hash, source/build revision, flags, host/target, generator version and case ID. |
| Four kinds and one local shape; seven operators | No mala/rachana; no `<=`, `>`, `>=`; no print-position, storage, call, lifetime or branch coverage | Extend both operand axes, operations and provenance contexts; publish missing cells. |
| Result observed through `likha(a op b)` | A correct text concatenation can look wrong because its printer is wrong | Separate operation tests using an independent byte observer from tests of printing itself. For known valid Text, explicit byte output is an observer candidate; raw invalid addresses must not be dereferenced by the oracle. |
| No alias/equal-distinct/empty/unequal alternatives | Single sample cannot distinguish identity from contents or validate boundary rules | Add discriminating cases and metamorphic transformations. |
| Writes `probes/` and overwrites `trap_matrix.json` beside itself | The “never changes the tree” description is false when run in its checked-out folder | Require a separate output directory and preserve prior reports. It does leave compiler source unchanged. |

The generator uses 4 × 4 × 7 = 112 cells, not merely kinds × use sites. Binary operations need ordered operand pairs; values, provenance and context multiply the space further. One probe per cell does not decide all behaviors. The report's 63 “silent-wrong candidates” are a manual classification, not 63 proven defects, and legitimate identity policies must not be counted automatically as wrong.

### Required next matrix and acceptance rule

Muse already owns extension under R102; do not duplicate it with a second implementation. Add the four reference kinds plus numeric/raw/unknown kinds; all seven requested operators; same-object, alias, equal-distinct, unequal and empty values; then literal/local/parameter/return/global/field/element/branch/loop/module/indirect-call origins. Printing must cover each position at arities 1–6 and literal versus same-valued local/return/concat. Include casts/typed stores separately. Containers with unknown element kinds must not be pretended to be typed by the test harness.

Separate three outcomes: an observed behavior, its contract verdict, and its old/new classification. A compiler refusal is correct only when the intended type diagnostic is expected; a changed output is progress only if it matches the independent oracle. A missing case is NOT RUN, never a pass. Known bugs form a reviewed baseline, not accepted language semantics. Compare the same input corpus across compilers, while separately testing source migrations.

Use metamorphic pairs to force the compiler's alternative paths: add unused locals to cause spills, replace a literal by a same-typed variable, pass through a typed identity function, insert an unreachable assignment, and cross a module boundary. Include side effects to check once-only left-to-right evaluation, and allocation failure/budget checks in a separate resource matrix. Shrink failures and mutation-test omitted type checks, unknown-as-integer fallback, and print-position dispatch. Those tests make the class systematic without pretending finite samples prove complete correctness.

## Delivery boundary

No generator execution, compiler build, probes, suite, guard, proofs or gates were run: **NOT RUN — no toolchain**; `command -v nasm` found none. JSON cell counts and source/control-flow inspection were performed. Native Windows and CI: **NOT RUN**. This round changes only outbox documentation; no source, tests, tools, README, Windows or frozen-pack files.

Primary evidence: R175 assignment; current `src/sutram_compiler.asm` (`rfx_kind`, `rfx_check_str_binop`, `.ge_binop`, `.ge_lk_str`, `.r52_lk_next`, `.ge_call_lkhb`, `.ge_call_shabda`); Claude R105 report; Muse R101 report, generator and JSON; Muse R102 assignment. Exact blob identifiers are in the accompanying evidence file.
