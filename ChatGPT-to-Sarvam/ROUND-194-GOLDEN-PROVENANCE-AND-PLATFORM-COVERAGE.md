# R194 — independent oracles, platform coverage and error response

Read-side review at `c803cc07327b3e4452f7854015d80d8c7a5c9409`. Sanskrit target; no production changes.

## WS1: rule for producing evidence

**Derive expected behavior from an approved contract independently of the implementation under test. Recording may capture a candidate; it must not approve that candidate.** Use a combination: hand-derived small examples, independent reference computation for complex values, and properties for invariants that printed output cannot establish. A second implementation is useful only to the extent that its algorithm, dependencies and assumptions are independent.

Important qualification to the brief: tests/expect/322_r111_new_names.out expects `B42` and `abcd`, as does the Windows evidence. That is sensible visible output. R193 identified unsafe character-buffer lifetime and in-place concatenation as source candidates. The supplied evidence does not prove those goldens recorded visibly wrong Linux output, or establish their original authorship. A program can print the right text while writing outside storage or returning a transient pointer. Thus **an independently correct golden alone would not fix this testing gap**. Preserve the distinction between wrong expected values and insufficient observation of unsafe implementation.

### Required provenance record per test

Record test ID, input hash, contract/version and target assumptions; oracle type and derivation/reference version; expected output/exit/channel; allowed normalization; reviewer; and the change reason. Preserve the implementation version used for observations separately from the source of truth. Code and expectation changes may share a review only when the reviewer explicitly checks the independent derivation; never bulk re-record to turn failures green.

| Test kind | Chosen oracle | Cost per test (planning estimate, not measured) |
|---|---|---|
| Small deterministic arithmetic/collection operation | Hand calculation and short derivation; boundary and invariant check | 5–15 minutes for a simple case; more if contract unclear. |
| Complex numeric result | Independent high-precision/reference implementation plus hand-checkable anchor cases | 30–120 minutes initial case/family setup; 5–15 minutes per additional fixture. Specify rounding, overflow, NaN and tolerance. |
| Mutation, ownership, strings and aliases | Hand-derived observable result plus lifetime/capacity/alias properties and guarded native probes | 30–120 minutes per family for a harness; 10–30 minutes per boundary case. Native availability is extra. |
| Parser/refusal diagnostic | Independently written invalid input and contract-based code/location/exit; separately reviewed editorial message snapshot | 10–30 minutes; translation review separately. |
| ABI/OS interaction | Small independent foreign caller/callee or OS oracle, plus platform-specific semantic assertions | 1–4 hours family setup; 15–45 minutes per case, excluding platform setup. |
| Timing, addresses, OS allocation details | Relational/property oracle; bounded resource behavior rather than arbitrary fixed bytes/numbers | 30–120 minutes per family; do not invent one universal numeric golden. |

These ranges overlap and depend on reuse. Do not multiply the highest estimate by 315 or promise a fixed completion date. First inventory the reported 315 goldens; their count is supplied by the brief, not independently recounted here. Keep legacy snapshots as regression evidence while labelling their oracle provenance unreviewed. They must not be counted as independent correctness proofs.

### Conversion order

1. New/changed tests immediately need provenance. For the exposed strings: define whether concatenation allocates or mutates; validate source preservation or destination capacity accordingly; test character results across subsequent calls and distinct live results. Require exact bytes and no invalid access, not only `B42`/`abcd`.
2. Convert high-risk families first: allocation/lifetime/aliasing, budget enforcement, strings, integer overflow, indexing, FFI and PE emission. Group fixtures around shared derivations and native safety probes.
3. Convert numeric/library families using independent reference models and explicit domains. Metamorphic identities need anchor cases: a function that always returns zero can satisfy some algebraic identities.
4. Review diagnostic wording and low-risk display snapshots incrementally. Keep separate totals for snapshot-only, independently reviewed, property-covered, platform-verified and unsupported; these dimensions overlap and are not a single PASS count.

Existing tests/run_tests.py:78–140 shows why this matters: --record writes observed stdout/exit directly (even TIMEOUT can be stored); stderr is checked only when an .err file exists. Proposed acceptance must forbid approving a timeout/crash as an ordinary success expectation, require explicit expected channels, and review candidate changes. Existing deliberate crash fixtures need separate classification. No harness edit is made here.

### What cannot be converted to an independent exact-output calculation?

An editorial diagnostic sentence has no unique mathematical result. Its wording golden remains a reviewed presentation contract; independently check the error category, phase, source span, exit status and lack of partial output. It can gain provenance without a second compiler. Runtime timestamps, addresses, scheduler order and performance measurements usually require properties/distributions rather than fixed text. External-service outcomes require controlled fixtures and separate integration tests. GUI appearance needs an approved visual specification and human/native observation. None is exempt from review; they simply need a different oracle. A second implementation agreeing with identical undefined behavior is not proof.

## WS2: second-platform defect classes and actual evidence

A second OS changes ABI, loaders, page protection, allocator behavior, handles, filesystem rules and text I/O; it can expose latent bugs without changing the CPU. Both current Windows and Linux x86-64 targets are little-endian. Testing both does **not** exercise big-endian execution, different pointer width or strict-alignment architectures.

| Class | Evidence located | Honest coverage status / missing proof |
|---|---|---|
| Endianness | Current x86-64 targets share byte order | No big-endian target execution established; not a supported-target promise. Add explicit byte-serialization tests independent of host packing. Focused search did not establish a dedicated cross-endian semantic suite. |
| Syscall availability / OS services | R193 case 29 uses Linux syscall 60; Windows bridge exists | Tests exist, but platform eligibility failed. Enumerate bridge-supported calls and reject/label raw OS-specific examples. |
| Path handling | tools/test_windows_portable.py covers external CWD, imports and spaces; tests/gui/test_win_unicode_installer_source.py checks wide-path APIs | Not “no tests.” Source inspection is not Unicode-path native acceptance; reserved names, case collisions and long paths remain unverified by this review. |
| Memory accounting/budgets | 303/317/318 native failures; PE zero stub/bypass in source | Tested and failing/unsupported, not untested. Platform-correct enforcement and accounting acceptance absent from this evidence. |
| Permissions and file identity | No dedicated ACL/symlink/reparse-point semantic matrix located in focused test/tool search | Coverage unverified; do not infer repository-wide absence from filenames/search alone. Need access-denied versus missing, sharing locks and read-only directory cases. |
| Console encoding | tools/test_windows_console.py checks UTF-8 bytes, Sanskrit output and restoration of code page 437 | Test exists. Captured bytes do not prove interactive glyph rendering; native run status not established here. |
| Calling convention | tests/r35/test_ffi_windows.py covers mixed integer/float positions, shadow space, alignment, volatile clobbers and stack arguments | Substantial Windows-only test exists; it reports NOT-RUN outside Windows. A green Linux process exit is not execution evidence. |
| Memory protection/lifetime | R193 322/323 access violations; RX PE text versus writable data | Output snapshots miss safety. Add independent capacity/lifetime tests and native guarded probes. Exact crash site still requires tracing. |
| Exit/fault representation | Windows exception 3221225477, Linux signal semantics, raw-syscall expectation mismatch | Distinguish normal status, refusal, fault and timeout. Do not normalize all nonzero outcomes together. |

Therefore the blanket claim “never an automated Windows gate” needs qualification: automated Windows test programs exist; execution and integration evidence are separate. This review does not assert they have run. The defensible missing items are **unverified matrices** above and the current absence of a different-endian target, not a proof that every named category has zero tests. No source keyword search can certify universal absence.

## WS3: the requested 55-code response sort

**Worth doing: yes.** Answer directly: compilation failures cannot be handled by a program that never started; runtime hazards can sometimes be prevented or returned as explicit errors, but the existing fatal trap cannot itself be caught. Sutram's siddhi/dosh/prasar/yadi dosh support result-based recovery already. This inventory does not demonstrate a need for full exception unwinding; extend fallible operations for expected failures and preserve fail-stop safety violations.

The historical reconstruction is 40 compile refusals + 4 mixed + 2 runtime fatal + 1 conditional runtime fatal + 4 reference-tool tags + 4 placeholders = 55. It is not a current complete inventory: R190 added E_RACHANA_GANIT and E_PRATYAHRITA as compile refusals. Original evidence is ROUND-185-CODE-PHASES.json. Every reconstructed name follows, not merely a link to the earlier answer.

| Code | Phase | Running-program response / action |
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
| `E_EXPORT_COLLISION` | reference-tool diagnostic | Correct build/module inputs; not a native runtime event. |
| `E_EXPORT_DUPLICATE` | reference-tool diagnostic | Correct build/module inputs; not a native runtime event. |
| `E_IMPORT_ALIAS` | reference-tool diagnostic | Correct build/module inputs; not a native runtime event. |
| `E_PRIVATE_SYMBOL` | reference-tool diagnostic | Correct build/module inputs; not a native runtime event. |
| `E_BAD` | fixture/placeholder | No production operation to recover from. |
| `E_CODE` | fixture/placeholder | No production operation to recover from. |
| `E_OTHER` | fixture/placeholder | No production operation to recover from. |
| `E_TEST` | fixture/placeholder | No production operation to recover from. |

Prevention is not universal recovery: a fallible allocator must report its actual failure, not trust an earlier free-memory check. Lifetime faults do not authorize resuming access. New unwinding would require a separate ownership/cleanup/FFI design; error-code counts alone do not supply it.

## Delivery limits

Source/test reading and historical error-table reuse only. Build, native suite, Windows, guard, fault tracing and CI: **NOT RUN — no toolchain used for this read-side assignment.** No production, test, tool, pack or Windows-folder changes. Time estimates are planning ranges. No conversion of all 315 goldens or global absence-of-tests certification is claimed.
