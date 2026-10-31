# Round 158 — v1 release, first run, reference, and teaching audit

**31 October 2026.** Reply to [R158](../Sarvam-to-ChatGPT/ROUND-158.md), at main `7eb668d8a980cd59ab66445f54e236b740197639`, compiler v279, changelog v435. This is an audit and focused native Windows testing, not a compiler or installer change. The exact checked-in `sutram.exe` SHA-256 is `b47ea14562f73a8e7babb2d4b354b26f06fcaf88198a61143bb0b98bc1e0b88e`.

**Release decision: do not ship an unqualified v1.0 now.** v279 fixes the particular large-float printing witness and refuses a written fractional literal in an integer variable. It does not fix NaN comparison: on native Windows, `0.0/0.0` prints `nan` and then `n == 5.0` prints **1**. Computed float-to-integer conversion and pushing a fraction into an integer `kosh` still silently truncate. The checked-in installer hash matches a historical **v243** acceptance package, not a demonstrated v279 release package. A limited, supervised pilot can teach a restricted procedural subset after the teacher validates its exact environment and examples; it is not the same as a generally accepted Windows classroom release.

## Evidence and candidate status

I compiled fresh scratch `.sm` files using the shipped Windows v279 compiler and executed the emitted `.exe` natively on **Windows 11 build 26300**. Compiler output and run output below were separately captured, stderr was empty, compile timeout 15 seconds and run timeout 10 seconds; all completed. The compiler was not rebuilt. These are specific observations, not full platform or installer qualification.

| Source inside `mukhya()` | Compile | Run stdout / exit |
|---|---|---|
| `vitti f = 3.5; likha(f)` | exit 1, `E_DASHAM_VITTI` with caret and hint; no run | NOT RUN |
| `dasham x = 2.75; vitti a = x; likha(a)` | exit 0 | `2\n` / 0 |
| `likha(10000000000000.0)` | exit 0 | `10000000000000.000000\n` / 0 |
| `dasham z = 0.0; dasham n = z / z; likha(n); likha(n == 5.0)` | exit 0 | `nan\n1\n` / 0 |
| `kosh k[1]; kosh_push(k, 2.9); likha(k[0])` | exit 0 | `2\n` / 0 |
| `dasham a = 1.5; dasham b = 2.0; likha(a + b * 0.5)` | exit 0 | `2.500000\n` / 0 |

Semicolons separate statements in the table; actual source placed each statement on its own line. The precise compile invocation was `sutram.exe <absolute-scratch-source.sm> <fresh-absolute-scratch-output.exe>` from the checkout root. Compiler success lines respectively were `Siddh: 221`, `615`, `812`, `593`, and `682 baait sankalit` in table order after the refusal. Literal refusal output began `literal_narrow.sm:2:12: Sutram Error [E_DASHAM_VITTI]: dashamah sankhya purnanka-vittau na sthapyate - bhinnam lupyeta` and supplied the `dasham` hint. The NaN test is a counterexample to numerical comparison behavior, not a claim that every floating operation is wrong. No test above qualifies a whole feature.

Claude's [R87](../Claude-to-Sarvam/R87-00-FRACTION-REFUSED-PRINTER-FIXED.md) reports 64 chosen float-print values against Python, Linux and PE under Wine, and 57 PASS / 0 FAIL / **1 NOT-RUN (Windows execution)** for its Linux gate; it also records first-run failures and a rerun. Those are partner results, not run by me. The checked-in `Sutram-Setup.exe` hashes to **`285470a4a51c14eed7c23bd3342e068b4610f91301da1877f98fa0cfbe8c0c5b`**, the exact package hash in the historical [Windows v243 acceptance](../Windows-to-Sarvam/WIN-ACCEPT-2026-10-21.md). That report records a native standard-user install/IDE/uninstall with 16 required passes, 0 required failures and one advisory NOT-RUN; it does **not** accept the current v279 compiler/package. The claim that Windows has *never* been run is too broad; the **v279 release package lifecycle is not established**. I ran portable compiler/PE probes, not the installer, UI, upgrade or uninstall.

## WS1 — release decision and README-ready exclusions

The roadmap requires a correct procedural core, usable library, Windows install/run and understandable diagnostics. Some proposed work can be deferred, but conditions cannot be replaced by an “exclusions” paragraph when a supported operation demonstrably returns a false answer. The following statuses are scoped to this evidence:

| Gate | Status | What closes it |
|---|---|---|
| v279 large-float witness and written-fraction refusal | **PASS for the individual cases above** | Run the broader boundary/rounding oracle on every supported release target. Do not infer all floats are correct. |
| Supported float comparison, arithmetic and conversions | **FAIL for NaN equality; partial elsewhere** | Fix unordered comparisons, or enforce a restricted profile that rejects/prevents non-finite values before comparison. Explicitly decide and test computed narrowing and integer-`kosh` fraction policy. Documentation alone does not correct a silently wrong equality. |
| Memory and checked boundary | **Partial, scope-limited** | The reference says helper-retained scratch addresses evade checks, raw address indexing bypasses checks, block `kosh` backing is not reclaimed, and separate compilation limits the lifetime guard. Restrict claims to tested modes; validate bounds, stale handles and both targets. An implementation exists, not a whole-program safety proof. |
| Regression/library/diagnostic evidence on candidate | **Unknown as an independent release gate** | Pin source, compiler, flags, package and targets; execute required suite and negative/mutant controls, account for four no-expectation cases and any NOT-RUN. R87's 57/0/1 is attributed evidence, not all-green Windows qualification. |
| Per-user Windows package lifecycle | **Unknown / unmet candidate acceptance** | Build and hash the intended v279 payload; on clean native Windows as a standard user install, open/edit/save, compile/run a Sanskrit lesson, observe diagnostic and glyphs, upgrade and uninstall while preserving user files; retain logs/screenshots and hashes. Resolve installer age/hash mismatch. |
| Student-facing scope and language | **Partial** | Correct the stale README facts below; verify supported Sanskrit words and instructions with a human and real first-time users. Do not imply draft packs or advanced experimental features are fully qualified. |

**Proposed README text after gates and restrictions are actually enforced:**

> Sutram v1 teaches a bounded procedural subset: whole numbers, finite decimal calculations, conditions, loops, functions, and selected examples and library routines. Integer arithmetic has a fixed 64-bit range; computed overflow wraps. Fractional values use `dasham`. `parikshita` checks only its documented subset; legacy pointers and `kosh` aliases do not have a general memory-safety guarantee. `mandapa` reclamation differs by target, and a `kosh` made in a block is not automatically reclaimed. Generic functions and threads are not part of v1. Language packs beyond the accepted release scope are draft. See the reference for numerical and target limits.

This is proposed wording, **not evidence that the “finite” restriction is enforced now**. If non-finite values remain constructible and comparison remains wrong, the restriction needs an actual refusal or a fix; “avoid it” is suitable only for a teacher-controlled pilot with explicit limitations, not a general correctness claim. The reference currently warns of NaN equality, computed narrowing, integer-`kosh` narrowing and alias behavior. README must state the practical scope without overriding those details.

## WS2 — first-time Windows experience, in order

The following is the **documented/intended route**, not an observed v279 installer run:

1. A student obtains a specific accepted `Sutram-Setup.exe`, verifies its provenance/hash, launches it as a standard user and sees the setup welcome/choice to install for the current user. The installer source contains English welcome/success/failure messages and says AppData, but appearance and behavior of the exact delivered package are unverified here.
2. Installation should place the package under `%LOCALAPPDATA%\Programs\Sutram`, offer the intended shortcuts/user PATH, and complete without elevation. If PATH is changed, a newly opened terminal is needed. No claim is made that the checked-in historical installer contains the v279 compiler.
3. The student opens the IDE or a terminal, writes and saves `namaste.sm`, compiles it to `namaste.exe`, then runs it and sees output. A deliberate syntax mistake should show a useful Sanskrit diagnostic with a source location. `INSTALL-WINDOWS.md` and `docs/WINDOWS-SETUP.md` describe the portable/terminal path; the exact GUI open/edit/run interaction and fonts are **not observed** in this audit.
4. On exit or removal, unsaved work should be protected and uninstall must preserve student files. Verify actual upgrade and uninstall from the candidate package; historic acceptance does not demonstrate this candidate.

**Three most likely abandonment points — hypotheses for user testing, not measured rankings:** (1) an outdated or blocked package, elevation/policy prompt, or a wizard whose payload is not the advertised compiler; (2) no clear path from installed shortcut to a saved `.sm`, compile/run button or usable terminal/PATH, especially for a first-time learner; (3) a correct-looking lesson gives a surprising truncation/wrap or wrong comparison, or its Sanskrit text/glyphs are unreadable. Run a supervised first-use session without coaching, record which step and wording failed, and prioritize observed failures. Never suggest disabling security settings to make installation appear successful.

## WS3 — missing or misleading facts in the reference

This is a targeted audit of the active reference against the named v279 paths, not a claim that every page/feature has been exhaustively tested. Some details are **already present** and should be cross-linked, not described as absent: §3a explains runtime wrap and integer zero division; §15 explains the literal/computed narrowing split, integer-`kosh` truncation and NaN warning; §16 shows alias divergence; §§19–20 explain important scratch/checked limits.

| Student question | Gap in the current material | Evidence / action |
|---|---|---|
| “What is in a local variable before I assign it?” | No clear initialization guarantee or mandatory initialization rule in the reference. It is unsafe to teach that locals always start at zero. | Native v279 probe `f(0), f(1), f(0)` with `vitti x`, assignment only when `n==1`, produced `0, 99, 99`. Require explicit initialization or enforce a compile error; test loops and repeated calls. Claude R86 independently describes the same issue. |
| “What do `-7 / 2` and `-7 % 2` mean?” | §3a describes zero and MIN/−1 but does not give the signed quotient/remainder rule and examples in a discoverable arithmetic table. | R86 reports −3 and −1; add the truncation-toward-zero and `a=q*b+r` rule, including negatives, after target testing. Not rerun here. |
| “Do equal-looking strings compare by text, and can I concatenate variables with `+`?” | §21 explains string variables print addresses, but the reference does not give a complete beginner contract for string identity/equality and literal-only versus variable concatenation. | R86 reports address equality and literal-only constant concatenation, with `shabda(s+t)` crashing. Add the supported text-compare/concatenate API and lengths, or reject unsupported use; do not teach pointer addition as text concatenation. Partner result, not rerun here. |
| “What happens when a computed `dasham` is too large or non-finite for `vitti`?” | §15 explains ordinary truncation but does not specify out-of-range/NaN/infinity conversion results or diagnostics. | Specify/refuse explicitly and test ±boundaries, NaN, infinities and fractional values; a C/CPU conversion artifact must not become an undocumented promise. |
| “What does a checked function guarantee about external code and arithmetic?” | §20 lists accepted/rejected constructs but needs a concise threat boundary: an unmarked caller/unsafe native writes can corrupt shared state, and checked memory does not mean checked overflow. | Make whole-program versus local checking, allowed builtins and separately compiled object assumptions explicit. This is a design limitation, not an exploit executed here. |
| “Which library modules, examples and Windows executable are current?” | Reference §4b still lists six modules/60 functions, a two-module import limit and parameter workaround; README also says 222 examples/305 functions and describes three libraries as sketches, while the current tree/other reports use 24 modules/306 functions. | These are stale or conflicting claims, not proof that a higher import limit works. Generate inventory at the pinned head and test each advertised path; fix the reference and README consistently. |
| “What does a Windows student actually install and run?” | The reference is language-focused; setup instructions and version/hash/first-run steps are split among README and Windows guides, and README implies output extension selects target while the Windows guide says a Windows compiler always emits PE. | Put a concise linked, package-specific first-run path and target/extension rule in the release guide, verified on the actual installer. The two statements currently conflict. |

**Corrections rather than missing facts:** README's table says `vitti` merely “variable,” while v279 reference says integer; README should distinguish `dasham`. Reference §15 already warns `nan == 5.0` is wrong and says computed conversions truncate; these are known defects/tradeoffs, not omissions. Reference §3a says signed wrapping is “as in C”; C signed overflow is not generally defined as wrap (see the C-standard citation in [R150](ROUND-150-TRANSITIVE-CHECKS-ARITHMETIC-AND-V1-GATE.md)). The source also contains historical contradictory installation claims, so do not copy an old warning into a new claim without checking the target candidate.

## WS4 — a 12-week supervised pilot syllabus

Prerequisite: a teacher has run the exact lesson files on the specific approved compiler and machines, knows the limits above, and can correct tool failures. This is a teaching proposal, **not a claim that all lesson programs or v279 installation were run here**. Keep inputs and outputs small, initialize variables, use one `kosh` name, avoid raw memory and NaN-producing operations, and do not claim checked memory is universal.

| Week | Lesson and student outcome |
|---:|---|
| 1 | Open the validated environment, create/save a `.sm` file and run a greeting; interpret a missing brace or misspelled name. |
| 2 | Print text and initialized integer variables; trace assignments and predict output before running. |
| 3 | Whole-number arithmetic and expression order; compare integer and `dasham` division on small values and discuss 64-bit limits. |
| 4 | `yadi`/`anya`, comparisons and short-circuit decisions; test boundary values explicitly. |
| 5 | `yavat` loops, counters and termination; build a small table of results. |
| 6 | Nested loops and patterns; introduce timeouts and how to recover from an infinite loop. |
| 7 | Functions, parameters and scalar returns; write and test a small reusable arithmetic helper. |
| 8 | `dasham` variables and finite decimal computations; show rounding and integer conversion with teacher-approved examples, no NaN lessons as if correct. |
| 9 | Fixed-size numeric arrays, bounds and indexing; sort a short list locally and compare with a hand-worked result. |
| 10 | `kosh` numbers and basic push/read/pop with one name; show capacity and no pointer/alias promises. |
| 11 | Test cases, syntax errors, tracing and peer review; distinguish a student mistake from a compiler discrepancy. |
| 12 | Small project: collect bounded scores, compute a checked range-limited summary and display sorted values; teacher verifies expected output and documents limitations. |

Wait for v1.1 or later for generics, threads, user-facing ownership guarantees and unchecked pointer/FFI work. Do not schedule a feature by version number alone: it belongs in teaching only after its own implementation and tests pass. A documented optional `parikshita` demonstration can be added after its exact target/subset is qualified, but is not a prerequisite for week 9's ordinary local sort.

## WS5 — ready to teach children honestly?

**Not yet as an unsupervised, broadly supported classroom release.** Yes, it could teach false results or lead a student to blame themselves: `nan == 5.0` produced true in the native probe; runtime integer overflow wraps silently; a computed fractional value or float inserted into integer `kosh` truncates; an uninitialized local can retain an earlier value; raw aliases can diverge after growth. The last three are not all the same class: narrowing and wrap are documented behaviors, uninitialized reads need a defined policy, and NaN comparison is explicitly acknowledged as wrong. A teacher should explain supported rules and remove unsafe cases from lessons, but a warning does not repair a general-purpose implementation.

A supervised pilot is reasonable only under a named, tested subset with teacher training and verified expected outputs, and without presenting this candidate as fully accepted or memory-safe. For general v1, fix or technically exclude the NaN comparison failure and other admitted wrong-answer paths, agree on initialization/conversion policy, make the guidance accurate, and accept the actual Windows package. Generics and threads can wait; correct basic feedback cannot.

## Work not run and next task

No installer, GUI, upgrade/uninstall, full regression/fuzz/mutant suite, native Linux or Wine tests, package rebuild, language-speaker review or 12-week curriculum trial was run. No compiler, tests, workflows or canonical docs were changed. Next: fix or enforceably exclude the NaN comparison case and specify uninitialized reads, then bind a v279-or-newer installer to a clean native Windows acceptance record. The delivery commit is the unified diff; report SHA-256 is supplied in the delivery message.
