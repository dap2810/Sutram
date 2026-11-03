# R191 — where to start, counts, and program responses

Request reviewed at main `4bad4318b90be28ac053d9bd7efa4a032818f278` (v296). Documentation-only handoff. Vocabulary classification below deliberately partitions the requested R190 inventory, pinned to v295 `613515c5ca3c1009b1b0593b5f340adf7a75422f`; it is not a new v296 census.

## WS1 — prioritize the public surface, not a 531-word rewrite

| Bucket | Distinct words assigned once | Occurrences classified by their own location |
|---|---:|---:|
| 1: student-facing keyword/builtin, diagnostic/help, library callable/output | 33 | 288 |
| 2: source-only wording in the audited scope | 135 | 782 |
| 3: example-local identifiers/output | 357 | 1,143 |
| 4: preserved identity/unit/filename/CLI spelling | 6 | 39 |
| Total | 531 | 2,252 |

Full word list and every location: [ROUND-191-BUCKETS.csv](ROUND-191-BUCKETS.csv). Classification uses the R190-generated inventory and pinned checkout, with the rules below. The CSV includes each word's per-occurrence bucket counts.

**33 is a triage count of vocabulary components, not 33 new renames or a complete count of the language's English surface.** Several are retained aliases, several are parts of longer identifiers, and several require contextual linguistic review. The original inventory uses a bounded lexical heuristic, not a complete output-reachability or Sanskrit-fluency audit. It excludes documentation, most compiler internal identifiers, example comments and library local variables/comments. Consequently bucket 2 is not a census of all source-only English. New v296 contract messages are outside this frozen denominator.

A word can occur in several buckets. For the distinct-word column it is assigned by visibility precedence **1, then 3, then 2, then 4**. Each occurrence is classified independently; these columns measure different things and both sum correctly. Function declarations are conservatively treated as callable/public; library parameter names are source-only for this pass, though they may also appear in documentation. Example occurrences of a builtin retain bucket 1. Pack mapping entries are language surface; pack comments are source-only except preserved spelling identities. Diagnostic/help candidates inherit R190's limited heuristic.

Bucket 1 words: **arr, bit, cap, cat, char, clear, dequeue, diff, dot, empty, enqueue, enter, fd, fmt, from, len, lib, lower, netbind, netlisten, netsock, pad, path, peek, pop, pre, push, root, sign, sorted, space, tab, upper.**

Bucket 4 exclusively assigned words: **bin, kilograms, kilometers, miles, pounds, version.** Other preserved occurrences belong to words assigned a higher-priority bucket elsewhere. “Preserve” is the operational meaning here: physical unit names and published filename/CLI identities must retain their exact meaning or compatibility. They are not linguistically impossible to translate. Already recognized Sanskrit names and proper nouns were excluded by the original inventory, so this partition cannot supply a new count of them. `path` and `pad` especially need context; an English-looking substring is not proof that a Sanskrit name needs replacement.

### Where to start

1. Review the 33-word bucket against its locations. Separate approved compatibility aliases and literal names quoted by diagnostics from active preferred public spellings. Keep compatibility identities stable unless an explicit migration is approved. The withdrawal message mentioning `dot` is not a live integer-dot API.
2. Fix genuinely student-facing explanatory prose and any agreed active API names in a small reviewed patch. Existing examples include `rakh_samroop_diff`, `bit_gan`, `asti_sorted` and `suchi_asti_sorted`; this is a review queue, not an approved translation list. Exact machine codes, units, format strings and external symbols need separate compatibility treatment. Frozen pack constraints still apply.
3. Translate teaching examples in coherent topics after the public terminology is agreed. The 357 example-dominant words explain most of the scale; preserve outputs and negative-test intent or explicitly migrate their expectations. Do not bulk-replace identifier substrings.
4. Defer source-only comments/parameter wording. They do not justify delaying the public-language work. Preserve bucket 4 identities; offer Sanskrit explanation around them when useful.

**Recommendation:** a bounded public-surface review is worth doing now; a promise to remove all 531 words in one round is not. The counts support that priority, not a time estimate or a guarantee that the public surface has only 33 English terms. Retain a written policy distinguishing preferred Sanskrit spelling, compatibility spelling and external identity.

## WS2 — one rule for all public count-taking functions

**Treat a caller's count as a request, never as proof of accessible storage. Verify it against trustworthy length/capacity and liveness metadata before access. Where a raw pointer has no trustworthy extent metadata, state the caller's storage obligation explicitly; do not call that interface bounds checked.**

Apply this convention to every public library function, including the stated 306-function inventory, without pretending that each currently has metadata:

- Reads require `0 <= n <= logical_length`; unused capacity is not readable initialized data. Slices use their own accessible extent.
- Writes require writable extent, initialization/growth semantics and terminator/header room as applicable. An input length cannot establish destination capacity.
- Multiple inputs must each satisfy the count and the documented shape relation. Do not silently use the shorter length unless the API explicitly defines prefix semantics.
- Validate before arithmetic: require `n <= MAX/stride` before multiplication; use `n <= length-start` after validating start, rather than overflowing `start+n` first.
- Validate all regions before mutation when failure promises unchanged output. Specify overlap behavior separately.
- Define zero explicitly; reject negative requests in new checked interfaces. Preserve documented legacy conventions until an explicit migration. Zero need not make an invalid typed handle valid.
- Raw pointer plus count can check arithmetic/domain but cannot discover allocation extent. A caller-supplied capacity is still a caller assertion unless provenance/lifetime enforcement makes it trustworthy. Never probe hidden headers on arbitrary pointers.
- Use the function's agreed status/result channel for recoverable failure, or its explicitly approved fatal refusal. Do not overload a legitimate zero result with indistinguishable failure.

For contract records label each implementation **metadata-checked**, **arithmetic-checked/caller-bounded**, or **unchecked legacy**. This makes enforcement gaps visible without claiming a blanket safety repair. R189's individual failure channels remain in force. R190's fuller count section remains available in [ROUND-190-AUDIT-REFRESH-ERROR-PHASES-AND-COUNTS.md](ROUND-190-AUDIT-REFRESH-ERROR-PHASES-AND-COUNTS.md).

## WS3 — the 55-item reconstruction, with a direct answer

**A running program cannot respond to a pre-execution compiler refusal. It can branch on explicit fallible results before a runtime trap; existing fatal traps are not catchable exceptions.** Sutram already supports `siddhi`, `dosh`, `prasar` and `yadi dosh`; lack of English `try`/`catch` does not mean lack of recoverable results.

The following is the explicit **R185 55-item reconstruction**, not a claim that the brief supplied an authoritative 55-name list or that this is the current v296 inventory. Its composition is 47 native-source tokens plus four reference-tool diagnostics and four placeholders. R190 found two additional compiler refusals, `E_RACHANA_GANIT` and `E_PRATYAHRITA`, bringing that bounded native-source scan to 49. New library diagnostic strings are a different surface; these historical totals should not be relabeled current.

| Group within the reconstructed 55 | Count | Can the running program respond? |
|---|---:|---|
| Compiler/tool pre-execution | 40 | No; correct source/build inputs before execution. |
| Mixed compile/runtime | 4 | Compile part: no. Runtime: validate or use a fallible operation before the fatal path; no trap catch. |
| Fatal runtime | 2 | Prevention or a separate fallible API, not recovery after the trap. |
| Conditional fatal runtime | 1 | Checked result before trap; optional build path is not universal reachability. |
| Reference-tool diagnostics | 4 | Build-input correction; not native exceptions. |
| Fixtures/placeholders | 4 | No production operation to recover from. |
| Total | 55 | No evidence here requires full exception unwinding. |

All 55 names follow so the answer is self-contained. File/line evidence and original caveats remain in [ROUND-185-CODE-PHASES.json](ROUND-185-CODE-PHASES.json).

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
| `E_EXPORT_COLLISION` | reference tool | Correct build/module inputs; not a native runtime exception. |
| `E_EXPORT_DUPLICATE` | reference tool | Correct build/module inputs; not a native runtime exception. |
| `E_IMPORT_ALIAS` | reference tool | Correct build/module inputs; not a native runtime exception. |
| `E_PRIVATE_SYMBOL` | reference tool | Correct build/module inputs; not a native runtime exception. |
| `E_BAD` | fixture/placeholder | No production operation to recover from. |
| `E_CODE` | fixture/placeholder | No production operation to recover from. |
| `E_OTHER` | fixture/placeholder | No production operation to recover from. |
| `E_TEST` | fixture/placeholder | No production operation to recover from. |

**Design decision:** extend explicit fallible results for expected operational failures; keep memory/lifetime safety failures fail-stop. The number of printed diagnostic tags does not establish a need for nonlocal unwinding. Full exceptions would require separate cleanup, ownership and FFI design. Float result payloads and indirect native phal calls retain the previously documented limitations. This is a design recommendation, not an implementation claim.

## WS4 — patra_asti dependency and next-spec discipline

Acknowledged: row 11 is **blocked**, not implemented. R189 did explicitly call for an OS metadata-query prerequisite, but presenting it alongside immediately implementable library rows made the readiness distinction insufficiently prominent. Future specs should mark every row READY / BLOCKED / DESIGN-ONLY, name the missing primitive, assign its owner and require backend evidence before a library implementation task begins.

For `patra_asti`, opening a file is not an existence query: permissions, directories and other errors make that substitution incorrect. Retain the proposed contract: successful followed-target metadata query returns 1; ENOENT/ENOTDIR returns 0; indeterminate query failure follows the separately specified error channel. Until the required platform primitive exists and is verified, keep the row blocked rather than silently returning absence.

R191 reports 15 implemented contracts, suite 312 and 132 new checks; these are reported results, not runs performed for this review. The reported long-string crash and 167 DIFFER artifacts remain open acceptance concerns. In particular, no vocabulary classification or algebra check explains 167 binary differences. The implementation owner should classify their byte/semantic causes against the approved change set and isolate the string-length repair before claiming compatibility; do not approve changed baselines from the count alone.

## Validation and delivery limits

Reclassified the existing 531 rows and all 2,252 locations; checked distinct-word and occurrence totals and emitted the complete CSV. This is deterministic lexical triage with the qualifications above, not fluent-language certification or exhaustive compiler reachability analysis. Reproduced the historical 55 rows and distinguished the later two additions. No native build, tests, guard, Windows execution or CI run was performed. No production source, library, examples, packs, reference or baseline files changed. Handoff only, pending Sarvam's independent acceptance.
