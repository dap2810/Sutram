# R190 — post-truti audit, error phases and the count-validation rule

Base: `613515c5ca3c1009b1b0593b5f340adf7a75422f`, v295, 2026-11-03. Read-side review; no production changes.

## WS1: 531 words/abbreviations, 2,252 occurrences

The repeated R184 method yields **531 distinct English surface words/abbreviations and 2,252 occurrences**, across 301 immediate example files, 24 library files, 11 keyword packs and the compiler. The complete refreshed list, replacements and file:line sites are in [ROUND-190-ENGLISH-TABLE.csv](ROUND-190-ENGLISH-TABLE.csv).

| Scope | Occurrences |
|---|---:|
| examples identifiers and strings, excluding comments | 1,386 |
| lib function/parameter names and strings | 330 |
| lang/*.lang entries and comments | 508 |
| compiler diagnostic/help literal candidates | 28 |
| Total | 2,252 |

The earlier total was 2,251. The only counted difference is `dot`, now 8 rather than 7 occurrences. The withdrawal diagnostic mentions the legacy spelling `sankhya_dot`. Newly encountered tokens are Romanized Sanskrit, including truti and pratyahrita; no additional English vocabulary category was added.

This is **the same bounded audit**, not a census of every repository file: docs deliberately written in English, linker source, tests, historical handoffs and many other paths are outside R184's four scopes. Compiler strings still use the documented diagnostic/help-label heuristic, not complete output-reachability analysis. R184 already excluded `Sutram Error`, so subtracting 748 from its count would be wrong. `lang/*.sandesh` and `lang/*.lang` are different inputs; the prefix migration changed the former. The 22 aliases predate R184. “Only one English word remains” is therefore not a whole-project conclusion.

Vocabulary drafts and exact-spelling collision screens retain R184's limitations: they are not approved translations or safe bulk-renaming instructions. The regenerated screen reports zero reserved-name collisions for the concrete candidates. Preserve external symbols, physical units and published compatibility names; do not translate them mechanically.

### Linker prefix

**Yes, align the linker-family prefix with `Sutram truti`, under a separate explicit owner decision.** R114 expressly excluded these tools, so its pack exception is not authority to change them now.

| Source | Literal occurrences |
|---|---:|
| linker/sutram_link.asm | 8 |
| linker/sutram_elf2smo.asm | 15 |
| linker/sutram_coff2smo.asm | 15 |
| Total | 38 |

These are independent NASM diagnostic literals, not the compiler's translated-message lookup. Both `Error` and `truti` are five ASCII bytes, so each replacement is length preserving. That does not prove rebuilt executable identity or eliminate testing: rebuild all three tools and update consumers that match the literal. Preserve message bodies, error/exit behavior and non-prefix bytes. Normal linked program output should not change merely because a host tool's failure text changes, but verify rather than assert that for every artifact.

Scope the patch to active tools and their current matching tests/docs. Do not edit historical reports or frozen language message bodies. Inventory all literal consumers first; validate representative malformed-input refusals, normal link/conversion output and exit statuses on supported targets. No timing estimate or native acceptance is claimed. The cost is a bounded token-and-consumer migration, not translation or a new diagnostic system.

## WS2: the requested sort exists, and is refreshed here

R185's full answer is [ROUND-185-ERROR-HANDLING-AND-MALA-REVIEW.md](ROUND-185-ERROR-HANDLING-AND-MALA-REVIEW.md), section “Code phases”; its file/line evidence is [ROUND-185-CODE-PHASES.json](ROUND-185-CODE-PHASES.json). It sorts 47 source tokens and explains eight additional tool/placeholder tokens that can produce a misleading total of 55. Those eight are not eight more recoverable native runtime exceptions.

At this base, the same bounded src assembly/include scan, excluding generated r11_sandesh.inc, finds **49 distinct E_ tokens**. Added since R185: E_RACHANA_GANIT and E_PRATYAHRITA, both compile-time refusals. The resulting source classification is **42 compile/tool-pre-execution, 4 mixed, 2 fatal-runtime and 1 conditional fatal-runtime**. Token presence is not proof of default-build reachability; optional machinery remains optional.

A running program cannot catch a compiler refusal before it exists. It can validate data or use a checked operation before a runtime trap; that does not make the trap itself catchable. Existing native `nivartanam siddhi(v)`, `nivartanam dosh(c)`, `prasar` and `yadi dosh (...) ... anya ...` already provide explicit result handling. See current LANGUAGE-REFERENCE section 18 and src/r25_phal.inc. The lack of English `try`/`catch` keywords is not the absence of recovery. Fatal printed E_ diagnostics are a separate mechanism.

**Decision remains: build on explicit results, not full nonlocal exceptions.** Use fallible operations for recoverable conditions before unsafe effects; preserve fail-stop safety violations. Float result payloads and indirect native phal calls remain documented limitations. Full unwinding is not made impossible by the lack of GC, but needs resource/FFI/cleanup semantics that this inventory does not justify introducing now.

The full current classification follows. Rows retained from R185 describe phases, not newly executed probes. New rows are marked below.

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
| `E_RACHANA_GANIT` | compile/tool pre-execution (new) | Use supported field operations; the not-yet-running program cannot catch this refusal. |
| `E_PRATYAHRITA` | compile/tool pre-execution (new) | Withdrawn builtin; use an available API with its actual contract. No runtime catch or alias escape. |

The eight extra entries discussed in R185 remain non-runtime: E_EXPORT_COLLISION, E_EXPORT_DUPLICATE, E_IMPORT_ALIAS and E_PRIVATE_SYMBOL belong to reference tooling; E_BAD, E_CODE, E_OTHER and E_TEST are fixtures/placeholders. Do not add these to a native recoverability count. Reconcile any other claimed “55” against its actual enumerated source list.

## WS3: counts are requests, not evidence of capacity

**Every public library operation must validate a requested count against trustworthy accessible length/capacity before access, whenever that metadata is available. A raw pointer plus count alone cannot prove the allocation's extent.** Such a low-level API must state an explicit caller-provided storage obligation and must not be advertised as bounds checked. New safe interfaces should carry a descriptor or typed collection with trustworthy metadata.

| Input form | Required rule |
|---|---|
| Typed kosh | Validate liveness, n>=0 and n<=logical length for reads; writes require existing logical elements unless a specific growth operation reserves/initializes them. Capacity alone is not readable length. |
| Fixed array/slice with preserved metadata | Check count against accessible extent. A slice uses its own extent, not its owner's entire allocation. Do not read a hidden header after provenance has been lost. |
| Raw pointer + n | Check arithmetic/domain constraints, but acknowledge extent cannot be established. Caller must supply live storage for the stated region; prefer a descriptor API for safe public use. |
| Two read sequences | Prefix operation checks n against both lengths; full dot/equality/zip-style exact-shape operation requires its documented length relationship. Never silently choose min unless prefix semantics are explicit. |
| Output pointer/collection | Check writable capacity separately from input length; reserve space for terminators and headers where needed. Source length cannot prove destination size. |
| Mutable/overlapping inputs and outputs | Specify overlap separately; passing bounds checks does not prevent overwrite-before-read bugs. |

### Required arithmetic and behavior

1. Interpret public counts as nonnegative quantities. A new checked interface refuses negative n rather than treating it as empty. Existing documented negative/empty conventions require an explicit versioned migration, not a blanket silent change. n=0 must be defined per API; no element dereference on that path. Do not promise that an invalid typed handle is acceptable merely because n is zero.
2. Validate n before n*stride. For signed-i64 byte arithmetic, require n<=MAX/stride; for start/count require start>=0, start<=length and n<=length-start. Avoid checking `start+n<=length` after addition has wrapped. Check additional headers/terminators separately with subtraction-first bounds.
3. Validate all participating regions and shape constraints before writes when promising failure leaves outputs unchanged. Do not start copying/sorting and then discover capacity failure unless partial output is a documented failure state.
4. Count validation is mandatory at runtime for dynamic data. Static proof may remove a check only when it establishes the same condition. A plain parameter named length is not a proof; aliases, casts and calls must preserve or invalidate provenance honestly.
5. Use existing status channels where present; otherwise define a checked variant or approved fatal refusal. Do not return 0 and claim callers can distinguish failure from an empty legitimate result without a status. R189 specifies particular channels; this round does not override them.
6. Metadata must stay trustworthy through calls and lifetimes. Adding a capacity integer to an unchecked pointer lets the caller lie; it improves a contract but is not independently enforced memory safety. Generation/lifetime checks must not read already-freed headers. Neither a count check nor a current test suite proves escape analysis complete.

For the existing library, classify each function as metadata-checked, arithmetic-checked but caller-bounded, or unchecked legacy. Publish that classification in R187's contract records. Prioritize parsers, copies, sort, matrix operations and conversions; preserve a deliberately explicit low-level path for systems work. Native address probing is not a valid substitute for tracking allocation provenance.

Acceptance witnesses: negative/zero/exact-length/one-too-large count; mismatched paired lengths; capacity larger than logical length; missing terminator room; multiplication/addition boundaries; expired and aliased handles; overlapping output; raw-pointer paths clearly marked caller-bounded. Test rejection before mutation where promised. No blanket reinterpretation of every raw pointer as a kosh/mala header.

## Delivery and limits

R184 and R185 are linked above and remain delivered, with their original source pins and caveats. This refresh does not overwrite historical evidence. Current withdrawal is acknowledged; the earlier integer-dot repair is no longer treated as active functionality.

Executed: fresh checkout of the pinned main, R184 lexical scan/reclassification using its existing glossary, candidate collision screening, linker literal counts and source error-token inventory. New lexical tokens were reviewed: ashuddham, asyah, avayavasya, gunanaya, laghutara, pathyate, pratiksate, pratyahrita, sanshodhanam and truti; none adds an English category under the stated method.

Native build, suite, guard, Windows and CI: **NOT RUN — no toolchain used for this read-side assignment.** Sanskrit fluency review and exhaustive compiler output reachability: NOT RUN. No production code, reference, pack or linker changes; linker migration remains a separately scoped owner decision.
