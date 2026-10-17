# Sutram: foundations, comparative positioning and development priorities

**To:** Sarvam  
**From:** ChatGPT, at the owner's explicit request  
**Date:** 2026-10-17  
**Status:** Advisory handoff; source/document review and proposed acceptance gates.  
**Inspected main:** `ca53eab710059eb574f1f19c64018b5eaedec1a8`  
**Scope of this delivery:** documentation only. No compiler, library, installer, workflow or accepted expectation is changed by this advisory.

**Companion catalogue:** [Projects and methods to study for Sutram](SUTRAM-PROJECT-METHODS-CATALOGUE-2026-10-17.md). It lists the earlier Sanskrit-related projects, their evidence status and concrete lessons, with additional systems references kept separate.

## 1. Read this first

The owner asked what Sutram is built on, how it can be better than other languages, and what we should do to achieve its goals. The owner then explicitly requested that this advice be uploaded to `ChatGPT-to-Sarvam/` for Sarvam.

**Recommendation:** develop Sutram as a dependable native language with a Sanskrit-centered, multilingual procedural core. Make it easy to begin and possible to grow into substantial systems and application programming. The immediate work is to integrate and validate the existing foundation: one reproducible compiler baseline, precise semantics, resource behavior, real modules and verified platform releases.

The charter's goals of Python-like ease, Rust-inspired safety and C-level control remain useful. They are not current guarantees. This advisory does not replace the charter, issue a new numbered round, approve pending compiler changes, or claim an implemented feature.

Before assigning implementation, reconcile this review with live main and the relevant PRs. The evidence below is pinned to the inspected snapshot; later source or execution evidence can change the assessment.

**Publication concurrency:** after the source review, main received separate keyword-renaming commits. The findings and source links below intentionally retain the inspected snapshot. Reconcile current spellings, documentation and compiler behavior before implementation. Publish this handoff on top of the latest main while preserving those concurrent changes.

### Recommended next concrete outcome

Deliver one independently reproducible Linux compiler baseline, complete the staged `kosh` growth-reclamation acceptance with an explicit alias contract, and demonstrate two actual Sutram modules compiled independently and linked into a working program. Specify the affected language rules alongside implementation. Windows and freestanding work have separate gates below.

Suggested positioning for future user-facing material:

> A native programming language that people can learn and use through Sanskrit and other Indian languages, with a simple starting point and progressively available systems capabilities.

This is a recommended direction, not a measured superiority claim.

## 2. What the implementation is built on

| Layer | Observed foundation | Precise interpretation |
|---|---|---|
| Source language | Procedural core: variables, expressions, functions, conditions, loops, numeric and indexed-storage operations | A useful implemented core; nine finished programming paradigms are not established. |
| Vocabulary | Canonical Sanskrit keywords with language packs | Different keyword spellings map to the same intended programming operations. |
| Compiler implementation | Handwritten NASM/x86-64 assembly | Its own parsing and machine-code generation; no C, Python or LLVM shipping backend was found in the inspected path. |
| Supported build entry | `src/r68_compiler_entry.asm` | This includes the principal compiler plus accepted R68 diagnostics. Bare-core builds omit that profile. |
| Instruction target | x86-64 | Architecture portability must be implemented and tested separately. |
| Executable formats | Linux ELF and Windows PE32+ | Format generation is distinct from full native target acceptance. |
| Library mechanism | `.smlib` source imports with graph/visibility-related machinery | Ordinary compilation still expands imports textually into one translation unit. |
| Compiler source build | NASM and a linker; Python tools for validation/reporting | Developer tooling is distinct from dependencies of generated applications. |
| Program execution | Native instructions with generated support and OS services as needed | No separately installed language interpreter/runtime does not mean no support code or no OS dependency. |

Sources: [build guide][build], [compiler][core], [default entry][r68], [specification][spec], [freestanding assessment][free].

The observed pipeline is source read, module preflight, import expansion, lexing, parsing/program-tree construction, code generation and image output. The emitter writes instruction bytes directly. Some semantic checks occur during code generation; `--check` therefore still invokes generation in memory without publishing an executable. Do not draw an architecture diagram that pretends a fully independent type-checking pass or mature portable IR already exists. [Compiler pipeline][pipeline], [emitter][emitter]

### Important distinctions for explanations

1. **NASM builds the compiler.** An ordinary user with a prebuilt Sutram compiler does not need to invoke NASM for each `.sm` program.
2. **The compiler is not currently self-hosted.** It is implemented in assembly, not in Sutram.
3. **C, Rust and Python are design references in the charter.** Do not invent a historical fork or implementation dependency on them.
4. **Sanskrit supplies the keyword core and project identity.** The reviewed evidence does not establish implementation of the full Paninian grammar or unrestricted natural-language programming.
5. **Describe the current source layout accurately.** It has one principal pure-NASM implementation with reviewed entry/include files. This observation does not authorize changing the one-pure-NASM constraint.
6. **Use “no separately installed language runtime” precisely.** PE output contains embedded support and normal programs use OS services. Native output alone does not establish kernel readiness.

## 3. Evidence status at the inspected snapshot

### 3.1 Source and branch identities

| Item | Observed value |
|---|---|
| Main commit inspected for this advisory | `ca53eab710059eb574f1f19c64018b5eaedec1a8` |
| Main tree | `dd9502ecee8bcfddfc4f299feaacc443738f93e5` |
| Principal compiler Git blob | `64ea028a5ccf56117c132a7efd0673cbe2df3fc6` |
| Canonical R68 entry Git blob | `42389aaf73179726d91e23359aee2199734036e1` |
| Experimental R71 entry Git blob | `6ba05e206556d9b18349b633ac1bda73ac89aab1` |
| PR #30 state on 2026-10-17 | Open, draft, not merged |
| PR #30 head | `b08c74630d3f7aa460acceb5eb6864a9a4fd822a` |
| PR #30 base branch | `feature/r69-canonical-build-return-20261016` |

Sources: [reviewed commit][snapshot], [source][core], [R68 entry][r68], [R71 entry][r71], [PR #30][pr30].

The API state was rechecked for the advisory upload. **PR state alone does not determine integration:** original R71 files are present on main, but the ordinary build still selects R68. Source presence, publication, compilation and accepted behavior must remain separate states.

### 3.2 Current R71 integration boundary

| Workstream | What exists | What remains |
|---|---|---|
| Modules/linker | Native qualified-symbol resolution and relative-call relocation groundwork | Production `.sm` object emission, module driver and import/export integration. The executed linker example joined authored machine-code fixtures, not independently compiled Sutram units. |
| Unsafe boundary | Experimental `asurakshit` token pass and conditional R71 entry | Full compiler/profile acceptance and generated positive/negative programs. No ownership or borrow checking follows from this pass. |
| Kosh growth reclamation | Staged Linux emitter work on the PR follow-up, with isolated native-helper evidence | Full production staging/build, generated `.sm` A/B tests, alias compatibility, regression acceptance and Windows reclamation. |
| Boot path | Assembly BIOS-sector source and image construction evidence | Recorded image not booted and not generated by Sutram; no demonstrated Sutram kernel. |
| Semantics | Two narrowly scoped clauses based on pre-existing fixtures, plus new probes | New full-compiler order, associativity, conversion and pack-resolution observations still need execution. |

Sources: [module report][modules], [experimental entry][r71], [reclamation handoff][reclaimhandoff], [combined handoff][combined], [specification][spec].

At the inspected main, the principal compiler retained its inherited blob and the growth path lacked the new reclamation hooks. The follow-up document `docs/R71-KOSH-RECLAMATION.md` was available at the PR head but returned not-found at the inspected main. The handoff on main records the staged work and its remaining acceptance. Treat that branch document as branch-specific evidence. [Branch reclamation document][reclaim]

### 3.3 Recorded tests are not this advisory's executions

- The README reports 187 Linux regression passes, four no-expectation cases and 12/12 code-generation shape gates.
- The original R71 record reports 66 helper/developer test methods.
- The reclamation follow-up reports 44 local methods and an isolated probe releasing 16 old mappings with 527 successful old-page checks.
- The two R71 totals were not rerun here and must not be combined into a fresh integrated test result.
- Hash verification, a compiled helper, a valid PE header and a golden file are different evidence from running the actual compiler and generated program.

Sources: [README][readme], [original R71 observations][r71observed], [reclamation handoff][reclaimhandoff].

**Compiler builds, Sutram execution, full regression reruns, Windows GUI/installer runs, emulator/firmware runs and comparative benchmarks performed for this advisory: NONE.** This is an advisory based on inspected source, documents and explicitly attributed historical records. Document packaging and readback do not change that status.

## 4. Where Sutram can become a better choice

“Better” should identify a user, task and measurement. The clearest opportunity is a complete Indian-language learning and development experience combined with reliable native compilation.

| Comparator | Useful lesson and opportunity | Claim that is not established |
|---|---|---|
| C | Keep direct systems control while improving the intended audience's workflow, diagnostics and eventual resource protections. C already specifies separate translation/linkage. [WG14 draft][cstandard] | Sutram has not demonstrated a stronger complete systems foundation or safer lifetimes. |
| Rust | Study ownership, borrowing and cleanup, while designing a procedural-first curriculum and comprehensible native-language diagnostics. [Rust ownership][rust] | Rust-equivalent safety or a simpler learning experience is not proven by new keywords. |
| Python | Native executable deployment can serve suitable tasks; high-level collections, clear errors and useful libraries are essential for everyday productivity. [Python tutorial][python] | Native output alone does not establish faster applications or greater productivity across Python workloads. |
| Vedic | Direct native compilation is an architectural distinction from Vedic's documented Rust interpreter. Vedic already offers a standalone binary. [Vedic repository][vedic] | Sanskrit programming and single-binary distribution are not exclusive to Sutram. |
| Vak | Its documented role checking, several engines, native C/GCC route and self-hosting work provide useful language-design/testing comparisons. [Vak repository][vak] | Do not describe Vak as merely a Python interpreter or infer Sutram superiority without equivalent tests. |
| Smrti and OM Lang | Smrti advertises Sanskrit vocabulary and NASM/x86-64 output; OM advertises multilingual programming. [Smrti][smrti], [OM Lang][om] | Native output or multilingual keywords alone do not establish uniqueness. Their advertised performance/safety was not independently validated in this review. |

External project statements above are attributed documentation, not execution audits of those projects. Check their current implementations before a future benchmark publication.

### Three product hypotheses to test

1. **Accessibility throughout the workflow:** supported-language diagnostics, tutorials, documentation and editing, beyond keyword substitution.
2. **A simple core that grows coherently:** ordinary functions and data first; memory annotations, foreign interfaces and hardware features only where the task needs them.
3. **Dependable native distribution:** a declared target, a working package, predictable compilation and reproducible output.

Sanskrit spelling itself does not prove efficiency, safety or beginner comprehension. Likewise, an assembly-written compiler does not automatically emit better code. Optimization algorithms and program representation determine generated-code quality. GCC documents tradeoffs among optimization, compilation time and code size. [GCC optimization documentation][gcc]

## 5. Development order and acceptance gates

These are recommended milestones, not new assignments, fixed schedules, completed features or authority to merge unreviewed code. Define the affected semantics and compatibility before activation. Independent workstreams can progress together when file ownership and interfaces are explicit.

### Gate 1 — One reproducible baseline and accurate current documentation

**Problem:** current-looking documents disagree about the entry to build, supported behavior and inventory counts.

**Deliver:**

- One release manifest identifying source commit, all required inputs/includes, entry, flags, output hashes, host and target.
- Current instructions selecting the canonical entry.
- Explicit feature labels: default-integrated, experimental, source-only, planned; include the execution evidence for each.
- Generated current inventories and a clearly separated historical record.

**Accept when:** a clean checkout builds the intended compiler; existing accepted gates run against that exact executable; failures, skips, no-expectation and not-run cases remain separate.

Do not rewrite accepted goldens to make a new binary pass. Inspect how each runner selects its compiler; a positional argument is not universally supported.

Sources: [build guide][build], [master][master], [overview][overview].

### Gate 2 — Integrated kosh reclamation with reviewed alias behavior

**Deliver:** full integration of the staged Linux growth change in an appropriate review branch, with capacity arithmetic and allocation-failure handling, preserved generated-register/stack behavior and an explicit invalidation contract.

**Accept when:**

- The full NASM compiler builds with the intended inputs.
- Actual integer and floating `.sm` growth programs preserve their required output.
- An unaffected scalar control retains the required behavior/byte parity.
- Old mappings are absent after completed growth and the live buffer remains correct.
- Allocation failures, capacity overflow and relevant parameter/alias cases behave according to the declared contract.
- The accepted regression, code-generation, pack and library checks run on that actual compiler.
- Windows behavior is explicitly tested or excluded for this profile; Linux syscall emission is not substituted for Windows deallocation.

**Memory caution:** freeing old storage invalidates raw aliases into it. Define whether borrows prevent growth, stable handles are used, or unsafe callers accept explicit invalidation. Do not silently change a copied raw value into an owner.

**Measurement caution:** old and new buffers overlap during allocate-copy-free. Peak RSS can remain high after a correct fix. Measure retained mappings/current state at defined barriers; do not promise an 8-bytes/item peak just from adding unmapping.

This gate fixes superseded growth storage only. Final-buffer disposal, raw allocations, file handles, cleanup on return/errors and a general ownership model require additional design and implementation. [Memory inventory][memory], [reclamation contract][reclaim]

### Gate 3 — Real separate compilation and project scale

**Deliver:** a documented object/interface representation, public/private symbols, relocations, a native compilation/link driver and source-located errors. Reuse the existing parser/emitter; do not introduce a substitute shipping compiler.

**Accept when:**

- Two actual `.sm` units independently define a private `init`, compile separately, link once and execute correctly.
- Private, missing, duplicate and incompatible imported symbols fail deliberately.
- Interface types, argument counts, resolution order and supported relocation kinds are documented.
- Rebuilding one changed module behaves predictably.
- Cross-pack use follows the documented source-file/pack rules.
- Capacity stress cases fail clearly or compile successfully within declared limits.

The current compiler constants include 65,536 bytes for expanded imports/source capacity, 128 function slots, 256 variable-table entries, six parameters, and a 262,144-byte emitted-code buffer. Treat these as implementation capacities, not universal language semantics; avoid misrepresenting scope-specific tables. [Capacity definitions][capacities]

Prefer an intentionally versioned, reviewed object contract; the existing in-memory linker record is not already a public `.smo` file ABI. [Module work][modules]

### Gate 4 — Executed and specified foundational semantics

**Deliver:** precise supported rules for grammar/scoping, evaluation order, integer behavior, conversions, strings/indexing, source locations and pack selection.

**Accept when:** the actual compiler runs discriminating positive and negative programs for the declared rules, including the pending R71 probes. Record input and output identities, flags, exits, stdout/stderr and diagnostic locations. Keep unsupported or unsettled behavior explicitly identified.

Do not promote one positive conversion example into a universal numeric rule. Do not infer all argument evaluation orders from one indexed-mutation example. Compiler crashes, timeouts and failed startup are not successful rejection tests.

Add reproducible randomized/fuzz cases where they expose meaningful lexer/parser/emitter risks. Preserve failure cases as regressions. [Current specification][spec]

### Gate 5 — Unsafe boundary and resource model

**Deliver first:** end-to-end acceptance of the optional R71 boundary through the actual frontend and generated programs.

**Accept the boundary when:** valid and invalid `.sm` programs cover raw-operation aliases, nested blocks, imported locations, diagnostics and recovery interactions. Check compatibility of the default profile separately. List exactly which operations are governed.

**Then design/implement ownership where intended:** owning values, move/copy behavior, shared/exclusive access, escape rules, reallocation, partial initialization, cleanup order and failure paths. Define how raw operations and foreign calls interact with safe values.

**Accept a stated safety property only within its declared scope:** valid use must work, and forbidden use-after-move, conflicting mutation, dangling-reference and repeated-release cases must be prevented as specified. Resource counters and failure injection are useful complements to output tests. Passing tests improve confidence; they are not automatically a formal proof.

An unsafe marker neither validates arbitrary addresses nor proves that operations outside its checked set are safe. [Memory model][memory], [experimental entry][r71]

### Gate 6 — Verified Windows release and multilingual workflow

**Deliver:** one accepted native package chain and a consistent language-pack experience.

**Accept when:**

- The exact compiler and generated PE execute on Windows.
- Non-ASCII console output is verified.
- GUI open/edit/build/run/close and the intended per-user install/cancel/uninstall paths are exercised.
- Every advertised pack is checked for intended semantics and diagnostic behavior.
- Native-script typing, cursor movement, shaping, copy/paste and source locations work in the supported editor path.
- Identifier normalization/confusable-name policy is explicit. Keyword translation does not silently rewrite strings, comments or identifier identities.
- Windows reclamation has a reviewed allocator-specific implementation and execution evidence before it is advertised.

Implement formatter/language-server support from the real language model as it stabilizes. Keep compiler host support and generated target support as separate matrix axes. PE structure checks and mocked X11 traffic do not establish a working GUI session. [Build acceptance][build], [charter][charter]

### Gate 7 — Sutram-generated freestanding demonstration

**Deliver:** one documented x86-64 loader/firmware interface, entry ABI, stack, memory layout, startup responsibilities, OS-free core and observable output/failure behavior.

**Accept when:** a Sutram-generated program body boots as part of the declared image, produces an expected captured marker, and has reproducible commands, image hashes and environment/tool versions. Identify assembly startup/loader components separately.

Audit implicit syscalls, allocation, process exit and Windows support out of this profile. Add volatile/hardware access, inline-assembly effects and interrupt contracts as required by subsequent systems demonstrations.

An unbooted 512-byte BIOS sector or an ordinary native application does not satisfy this gate. A minimal demonstration is the first proof; a complete OS is a separate project. [Freestanding assessment][free], [R71 limits][reclaimhandoff]

## 6. Architecture and ecosystem after the foundation

Preserve the pure-NASM compiler constraint. Make boundaries between lexing/parsing, program representation, typing, code generation, executable layout and host services clearer within that implementation. This does not require adopting LLVM or a C/Python replacement.

Add abstractions in response to real program needs: result/optional-value handling, reusable generics, composition through methods/traits, first-class functions and closures. Define the resource model before advertising safe concurrency.

Develop the library layers as one language with the same type/resource rules: an OS/allocator-free core, allocation-dependent collections, and application services. Audit transitive dependencies rather than trusting layer names.

A C-compatible FFI can later connect selected existing libraries. Define layout, register/stack conventions, ownership and error behavior for each supported ABI. Keep such integrations optional so ordinary standalone programs retain the project's deployment goal. [Charter][charter]

Adding an ARM code-generation target and running the compiler itself on ARM are different engineering tasks. Preserve that distinction when planning portability; current x86-64 code emission is not a general portability guarantee.

## 7. How to measure an advantage

| Goal | Evidence to publish |
|---|---|
| Easier for the intended audience | Installation success, time to first program, novice task completion, diagnostic comprehension and support needed |
| Consistent multilingual behavior | Equivalent meaning/results across packs, deliberately localized diagnostics and correct source locations |
| Compiler reliability | Positive/negative coverage, reproducible fuzz failures, preserved regressions and exact release identity |
| Resource correctness | Declared invariants, rejection of forbidden programs, cleanup counters and failure-path observations |
| Execution efficiency | Repeated elapsed-time results for equivalent algorithms, inputs and semantics |
| Memory efficiency | Retained/live memory and peak memory reported separately with the observation method |
| Build efficiency | Full compile and incremental rebuild time, separate from execution time |
| Deployment efficiency | Executable size, startup behavior, actual dependencies and verified target installation |
| Systems capability | A documented generated-image boot test with observable output |

Use correct equivalent programs, optimized C configurations and Rust release builds. State the Python implementation and native-library use. Keep integer/float precision, overflow requirements, input sizes and I/O work comparable. Record hardware, OS, toolchain versions, flags, source hashes and repeated measurements with variability.

Avoid global percentages such as “X% complete,” “Y% safer,” or “faster than every language.” Publish scoped claims that the observations actually support.

For a first real application, consider a local file/data-summary utility with multiple modules, collections, error handling and tutorials in a few supported packs. This is a proposed acceptance vehicle, not an existing delivered application.

## 8. Documentation corrections to reconcile

The following are discrepancies observed during review, not permission to overwrite current work:

1. `PROJECT-MASTER.md` and `PROJECT-OVERVIEW.md` still show bare-core build commands; `docs/BUILDING.md` specifies R68.
2. The master/README/reference differ in library/function/test counts. Generate current counts and retain historical records as historical.
3. Older reference text says floating parameters/returns are unsupported, while the source contains scalar binary64 parameter/return handling.
4. The roadmap's broad “no raw pointers/no Windows IDE” descriptions do not match the newer raw-address builtins and GUI source. Replace broad statements with the actual missing contracts and execution limits.
5. The master sample uses `samapt`, which the source review did not find in the compiler. Use a compiled sample before publishing it as valid syntax.
6. Claims that Sanskrit programming is unique to Sutram conflict with the other public projects in section 4.
7. A “synced/verified” label must be reconciled with actual default integration and execution evidence. Do not use a changelog heading to override a precise R71 limitation.
8. Do not claim no SIMD instructions whatsoever: some vector emission exists. Distinguish instructions from a documented general data-layout/vector abstraction.
9. “No runtime” should be explained as no separately installed language runtime where supported; generated helpers and OS services remain relevant.

Sources: [master][master], [overview][overview], [README][readme], [language reference][reference], [roadmap][roadmap], [compiler][core], [R71 handoff][reclaimhandoff].

## 9. Proposed division of work and expected reply

Keep workstreams disjoint and assign ownership before parallel source edits.

| Owner/workstream | Deliverable |
|---|---|
| Compiler work | Reviewed frontend/emitter/module/resource changes and exact semantics |
| Library/language work | Compatible APIs, contracts, pack examples and a real application |
| Independent verification/release work | Clean builds, exact-binary execution, observations and synchronized current documentation |

For each accepted milestone, return:

- Base and final source commits; compiler entry, includes and flags.
- A reviewable source diff and changed-file identities.
- Exact commands and actual exit/stdout/stderr observations.
- Separate PASS, FAIL, SKIP, NO_EXPECTATION and NOT_RUN outcomes.
- Declared target/host, compatibility impact and remaining limits.
- Current user-facing claims supported by those observations.
- The next bounded task and its acceptance criteria.

Please read this advisory alongside the current charter and the R71 reclamation handoff. Complete the acceptance of existing work before expanding the corresponding capability claims. Keep future compiler changes on appropriate review branches until independently accepted.

## 10. What this advisory delivery actually did

**Read operations:** GitHub source/document inspection, folder instructions, live branch/PR metadata, and primary external documentation for the comparison. No repository implementation script or compiler test was run for this advisory.

Selected API requests and returned observations from advisory preparation (before the concurrent keyword-renaming commits):

| Request | Returned observation |
|---|---|
| `GET /repos/dap2810/Sutram/git/ref/heads/main` | `object.sha = ca53eab710059eb574f1f19c64018b5eaedec1a8` |
| `GET /repos/dap2810/Sutram/git/commits/ca53eab710059eb574f1f19c64018b5eaedec1a8` | `tree.sha = dd9502ecee8bcfddfc4f299feaacc443738f93e5` |
| PR #30 metadata | `state = open; draft = true; merged = false; head_sha = b08c74630d3f7aa460acceb5eb6864a9a4fd822a` |
| `ChatGPT-to-Sarvam/` listing | 95 existing entries; no conflicting dated advisory name |
| Contributor instructions | Root `AGENTS.md`, folder `README.md`, master/charter and overview read |

**Not run:** NASM build, Sutram program execution, regression suite, performance benchmark, Windows session, emulator or firmware. No new performance, correctness or safety result is claimed.

**Packaging:** the companion `.patch` represents the new advisory and project-methods catalogue. It is a review aid, not a compiler patch. The companion SHA-256 file covers both Markdown documents and that patch; the manifest does not hash itself. The publication history records SHA-256 values for all four files, including the manifest, and supplies the complete publication diff.

**Source archive:** none, because no compiler source changes are delivered. The inspected source is identified by the immutable commit above.

**Publication verification:** the sender will read the committed files back through the GitHub API and compare their exact contents and blob identities before reporting upload success to the owner. This document itself does not claim that Sarvam has read or accepted the advice.

## Sources

Repository evidence is pinned to the reviewed snapshot, except the explicitly identified reclamation review branch and live PR metadata. External pages were consulted on 2026-10-17.

[snapshot]: https://github.com/dap2810/Sutram/commit/ca53eab710059eb574f1f19c64018b5eaedec1a8
[core]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/src/sutram_compiler.asm
[pipeline]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/src/sutram_compiler.asm#L1946-L2031
[emitter]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/src/sutram_compiler.asm#L9966-L10040
[capacities]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/src/sutram_compiler.asm#L21-L53
[r68]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/src/r68_compiler_entry.asm
[r71]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/src/r71_compiler_entry.asm
[build]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/docs/BUILDING.md
[readme]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/README.md
[master]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/PROJECT-MASTER.md
[overview]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/PROJECT-OVERVIEW.md
[charter]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/docs/sutram-design-parameters.html
[spec]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/docs/SPECIFICATION.md
[memory]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/docs/MEMORY-MODEL.md
[free]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/docs/FREESTANDING.md
[modules]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/docs/R71-MODULES.md
[reclaimhandoff]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/ChatGPT-to-Sarvam/ROUND-71-RECLAIM-HANDOFF.md
[reclaim]: https://github.com/dap2810/Sutram/blob/b08c74630d3f7aa460acceb5eb6864a9a4fd822a/docs/R71-KOSH-RECLAMATION.md
[combined]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/ChatGPT-to-Sarvam/ROUND-69-71-COMBINED-HANDOFF.md
[r71observed]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/ChatGPT-to-Sarvam/ROUND-71-OBSERVED.txt
[reference]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/docs/LANGUAGE-REFERENCE.md
[roadmap]: https://github.com/dap2810/Sutram/blob/ca53eab710059eb574f1f19c64018b5eaedec1a8/ROADMAP.md
[pr30]: https://github.com/dap2810/Sutram/pull/30
[cstandard]: https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3096.pdf
[rust]: https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html
[python]: https://docs.python.org/3/tutorial/
[gcc]: https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html
[vedic]: https://github.com/vedic-lang/vedic
[vak]: https://github.com/vidyadheeshp/vak
[smrti]: https://revanthnemtoor.me/smrti_docs.github.io/index.html
[om]: https://omlang.com/
