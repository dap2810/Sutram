# R192 — count semantics, error response, and boundary probes

Read-only source review at `bce540597e6e25dd655ff61649761f1277dc72a4`, v296. Sanskrit target. No production edits.

## WS1: verify the contract, not merely the upper bound

**A count is a request, never proof of storage. Verify both its semantic meaning and its bounds before access.** The deciding test is: does the documented operation consume whole inputs, or an explicitly requested prefix?

- Whole-vector dot: require `n == length(a) == length(b)` (or remove redundant n). `[1,2,3]·[4,5,6]` must give 32. Supplying n=2 must refuse; merely checking n<=3 would still permit the wrong operation.
- Explicit prefix dot: n=2 legitimately gives 14, provided `0<=n<=length(a)` and `n<=length(b)` and the name/contract clearly promises prefix semantics.
- Raw pointer without trustworthy extent: arithmetic checks cannot establish bounds. Mark caller-bounded, with an explicit live-storage obligation; introduce a metadata-bearing checked interface for enforced bounds. Never infer allocation size by reading an arbitrary hidden header.

This rule applies to all count-taking functions in the 306-function library. Read bounds use initialized logical length, write bounds use writable capacity plus initialization/terminator requirements. Validate liveness and every participating region before writes if failure promises unchanged output. Check n<=MAX/stride before multiplication and n<=length-start after checking start. Define zero; reject negative counts in new checked contracts, migrate legacy conventions explicitly. Preserve each API's agreed status channel.

The missing distinction in a short slogan is **shape correctness versus memory safety**: an in-bounds prefix can still violate whole-operation semantics. Record whole/prefix/caller-bounded in each contract; a parameter called length is not evidence.

## WS2: all 55 names and whether the program can respond

This is the R185 reconstruction: 40 compile-time, 4 mixed, 2 fatal runtime, 1 conditional fatal runtime, 4 reference-tool codes, 4 placeholders = 55. It is not a fresh v296 census or proof of the original author's unspecified counting method. R190 added E_RACHANA_GANIT and E_PRATYAHRITA as compile refusals. Library messages are another surface.

**Compile refusals cannot be handled by a program that has not started. Runtime fatal diagnostics are not catchable today. Expected failures can be prevented or returned through explicit results before the trap.** Existing siddhi/dosh/prasar/yadi dosh already support recovery. The sort is worth doing; it supports expanding fallible APIs, not inferring a need for full exception unwinding from a diagnostic count.

| Code | Phase | Response |
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
| `E_EXPORT_COLLISION` | reference tool | Correct module/build inputs; not a native runtime event. |
| `E_EXPORT_DUPLICATE` | reference tool | Correct module/build inputs; not a native runtime event. |
| `E_IMPORT_ALIAS` | reference tool | Correct module/build inputs; not a native runtime event. |
| `E_PRIVATE_SYMBOL` | reference tool | Correct module/build inputs; not a native runtime event. |
| `E_BAD` | placeholder/fixture | No production operation to recover from. |
| `E_CODE` | placeholder/fixture | No production operation to recover from. |
| `E_OTHER` | placeholder/fixture | No production operation to recover from. |
| `E_TEST` | placeholder/fixture | No production operation to recover from. |

Runtime response is not always a preliminary check: memory allocation can fail despite an earlier availability check; it needs a fallible allocator. Lifetime failures must not resume use of a dead reference. Division can check a stable divisor first or use checked division. Float-result and indirect phal-call limitations remain. Full unwinding would additionally need cleanup/ownership/FFI semantics.

## WS3: boundary candidates and known coverage

These are source-grounded candidates, **not confirmed crashes or a claim that no test exists**. Focused source/test searches establish the evidence below; generated fuzz cases and other gates may cover some boundaries. Require an explicit test identifier for each edge before declaring coverage complete.

Constants are in src/sutram_compiler.asm:26–57 unless otherwise stated. For each capacity C, probe C-1/C/C+1, including failure followed by another valid compilation in the same relevant invocation mode.

| Candidate | Source evidence | Required probe / current coverage conclusion |
|---|---|---|
| Identifier and rewritten name length | NS_FUNC_NAME_CAP=63, NS_ALIAS_CAP=31; these are rewrite limits, not a universal identifier limit | 62/63/64-byte exported names; 30/31/32-byte aliases; two names differing only after the boundary. Also ordinary local identifiers, qualified alias+name lengths and UTF-8 byte/code-point differences. Complete edge coverage unverified. |
| Parser nesting | BLOCK_NESTING_CAP=128, EXPR_NESTING_CAP=1024 | Boundary blocks, parentheses, unary chains, right-associated expressions and mixed forms; guards must cover every recursive route, not just parentheses. Unverified boundary matrix. |
| Region nesting | R73_MAXDEPTH=32 | 31/32/33 mandapa levels, cleanup on rejected nesting. Separate parser nesting from runtime recursion. |
| Module counts and names | IMPORT_NAMES_CAP=16; NS_FUNC_CAP=128; IMPORT_BUF_CAP=131072 | 15/16/17 distinct imports, duplicate imports, long paths, fan-out versus chains, cycle diagnostics, 127/128/129 exported functions. Different tables can reach different limits first. |
| Expanded source bytes | IMPORT_BUF_CAP=131072; comment says individual input read up to 64 KiB | tests/r54/test_r54.py already tests below/above expanded 128 KiB. Add exact byte edges, single-file read limit, EOF without newline, UTF-8/escape expansion. Do not call this entirely untested. |
| Literal emission | Current R116 regression | tests/r116/test_contracts.py:187–194 exercises 125,126,127,128,255,256,300,1000,5000-byte literals through three output paths. Extend escaped/multibyte literals, embedded zero semantics, empty strings, adjacent literals and aggregate pool exhaustion. Existing test compares output with newlines removed, so add exact-byte assertions when line layout matters. |
| Parameters and call arguments | KOSH_PARAM_VAR_CAP=6; FUNC_PARAMS_CAP=8192 bytes (1024 name slots) | 5/6/7 arguments and parameters, direct/indirect/method/FFI paths with mixed types where supported. Distinguish per-call ABI limit from total name storage; exact coverage unverified. |
| Statements and locals | BLOCK_STMT_CAP=256; VAR_TABLE_CAP=256 | 255/256/257 statements and variables independently, nested scopes, captures and stack offsets across signed-byte displacement boundaries. |
| Functions and records | FUNC_TABLE_CAP=FUNC_DEFS_CAP=128; RACHANA_CAP=16; RACHANA_FIELDS_CAP=15 | Function 127/128/129; records 15/16/17; fields 14/15/16. Ensure excess declaration refuses before a table write. |
| Token/string pools versus imported source | TOKEN_CAP=STR_POOL_CAP=65537 while expanded source capacity=131072 | Many tiny tokens and many distinct short lexemes in imports. Larger source capacity does not imply larger token/string capacity. Guarded refusal is acceptable; corruption is not. Constant comments still describe 64 KiB, requiring path review rather than assuming consistency. |
| AST/code/patch storage | AST_HEAP_CAP=3145728; CODE_BUF_CAP=262144; PATCH_LIST_CAP=512; break/continue caps=1024 | Generate AST-heavy expressions, branch-heavy bodies, many calls and nested exits. Measure which limit is reached; test emitter reservation before multi-byte writes and fixup width transitions. |
| Numeric literals | Integer/float parser paths | Huge digit strings, signed i64 edges, huge positive/negative exponents, leading zeros and malformed trailing input. Distinguish clean domain refusal from overflow, hang or parser desynchronization. |

Prioritize (1) byte-width transitions related to the observed string bug, (2) identifier/namespace copies and pool limits, (3) recursive parser routes, (4) parameter/ABI transitions, (5) table and aggregate capacity exhaustion. Use bounded subprocess timeouts and inspect exit status, exact stdout/stderr, artifact creation and deterministic repeatability. Valid edge cases must compute correct output; rejected cases must produce a diagnostic and no usable partial output. A mere nonzero exit is insufficient because a crash is also nonzero. Cross-platform execution belongs to the build/Windows owners.

## Updated project observations

R192 attributes all 167 differences to library contract changes and reports suite 313 / contract gate 133. Acknowledge that explanation; this review did not reproduce the guard. The long-string defect is reported old, with current regression coverage directly observed above. Neither should be presented as newly discovered by this review.

patra_asti remains blocked. A future access-style primitive must distinguish definite absence from permission/other failures; it must not turn every failed query into false. R189's existence contract and the proposed primitive need an explicit semantic match before implementation. No estimate is independently validated here.

R191's 33 are vocabulary components including aliases/context-sensitive terms, not 33 universally safe renames. Preserve per-name review.

Validation: source reading, focused test searches and historical error-table reuse only. Native build/suite/guard/Windows: **NOT RUN — no toolchain used for this read-side assignment.** No source, library, tests, tools, frozen packs or baselines changed. Documentation handoff pending independent acceptance.
