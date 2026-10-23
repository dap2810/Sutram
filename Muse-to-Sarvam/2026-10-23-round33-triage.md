# Triage of `tools/doc_stale_claims.py` output — 163 hits on main (fd486195, v322)

Run 2026-10-23. For each hit: the file:line, bucket, short claim, evidence/note.
Buckets: **FALSE** (doc says absent/never, but it exists/was done) · **TRUE** (real limit, policy, or design proposal) ·
**HISTORICAL** (versioned history or old snapshot) · **AMBIGUOUS** (definition question / unverifiable).

| File:Line | Bucket | Claim (short) | Evidence / note |
|---|---|---|---|
| F8-PACK-WARNING-FALSE-ALARM.md:36 | TRUE | False "language not available" msg is worst error | Value judgment / design principle, not an absence claim |
| PROJECT-MASTER.md:107 | FALSE | "Windows never executed" | 16 required checks passed on real Windows 11 (CHANGELOG v318) |
| PROJECT-MASTER.md:226 | TRUE | Ten packs never exercised by a human | Stated fact, still true per MUSE-CONTEXT |
| PROJECT-MASTER.md:305 | TRUE | No ownership model | Real language limit |
| PROJECT-MASTER.md:335 | TRUE | Not on list ⇒ not on critical path | Project policy/rule, not an absence claim |
| PROJECT-MASTER.md:364 | FALSE | "Windows execution… never performed by anyone" | Windows part false (16 checks); freestanding-boot part true — mixed claim, bucketed FALSE |
| PROJECT-OVERVIEW.md:13 | TRUE | No C backend / Python / LLVM / interpreter / runtime | By design (native compiler) |
| README.md:22 | TRUE | No C backend / Python / LLVM / runtime | By design |
| README.md:148 | TRUE | No concurrency | Real limit |
| README.md:149 | TRUE | No GC, no ownership, no borrow checker | Real limits |
| ROADMAP-TO-V1.0.md:4 | TRUE | Not on list ⇒ not on critical path | Project policy |
| ROADMAP-TO-V1.0.md:129 | TRUE | Ten packs never exercised by a human | Stated fact |
| ROADMAP.md:54 | TRUE | No address-of / dereference | Language design |
| SECURITY-AUDIT.md:68 | TRUE | Network code "never been exercised" | True — no test opens a socket |
| sutram-completion-roadmap.html:292 | HISTORICAL | (old snapshot) | Embedded stamp: compiler d0fe190c, 19 modules / 186 functions — predates FFI, Windows run |
| sutram-completion-roadmap.html:342 | HISTORICAL | (old snapshot, incl. "no FFI") | Same old snapshot; "no FFI" false today but doc is historical |
| sutram-completion-roadmap.html:343 | HISTORICAL | (old snapshot, "no FFI" ×2) | Same |
| sutram-completion-roadmap.html:343 | HISTORICAL | (old snapshot, duplicate) | Same |
| sutram-progress-report.html:153 | HISTORICAL | (old snapshot, "Windows acceptance never executed") | Old snapshot; false today but doc is historical |
| sutram-progress-report.html:186 | HISTORICAL | (old snapshot) | Same |
| sutram-progress-report.html:187 | HISTORICAL | (old snapshot) | Same |
| sutram-progress-report.html:210 | HISTORICAL | (old snapshot) | Same |
| compiler/MODULE_NAMESPACES_R33.md:18 | TRUE | "no new keyword" for R33 namespaces | Design statement about that feature's scope |
| compiler/MODULE_SYSTEM_R40_DESIGN.md:11 | TRUE | "NOT implemented": separate compilation etc. | Design doc for UNBUILT proposal — true as proposal |
| compiler/MODULE_SYSTEM_R40_DESIGN.md:73 | TRUE | "Real separate compilation (not implemented)" | Same — unbuilt proposal doc |
| compiler/XMM_REGISTER_RESIDENCY_DESIGN_R30.md:3 | TRUE | "Status: REVIEW DESIGN, NOT IMPLEMENTED" | Explicitly a design proposal |
| compiler/XMM_STAGE1_EXPERIMENT_R31.md:15 | TRUE | "No delayed spills…" | Describes that experiment's state |
| compiler/XMM_STAGE2_CALL_SURVIVAL_DESIGN_R32.md:33 | TRUE | "Candidate mechanisms (not implemented)" | Design doc |
| compiler/XMM_STAGE2_CALL_SURVIVAL_DESIGN_R32.md:108 | TRUE | Stage 2 "intentionally NOT shipped" | Documented decision |
| docs/ERROR-CONVENTION.md:6 | TRUE | No phal type / propagation op / exhaustiveness | Accurate description of the convention |
| docs/ERROR-CONVENTION.md:116 | TRUE | "no separate cell to forget" | Design rationale |
| docs/ERROR-CONVENTION.md:123 | TRUE | No exhaustiveness checking | Real limit |
| docs/ERROR-CONVENTION.md:125 | TRUE | No `?` operator | Real limit |
| docs/ERROR-CONVENTION.md:136 | TRUE | No `?` operator (early-return chain) | Real limit |
| docs/ERROR-CONVENTION.md:161 | TRUE | "later steps never run" | Describes chain semantics |
| docs/ERROR-CONVENTION.md:162 | TRUE | "No error value to inspect" | Real limit |
| docs/ERROR-CONVENTION.md:166 | TRUE | "no exhaustiveness check" | Real limit |
| docs/FAIL-ALLOC.md:14 | TRUE | "before this switch… never run" | Historical statement about the feature's motivation |
| docs/INDIC-COVERAGE.md:17 | TRUE | Malayalam digits "Not implemented in locked R68 helper" | Specific verified gap |
| docs/KOSH-BUILTINS.md:83 | TRUE | No "peek front" builtin | API design decision |
| docs/KOSH-REUSE.md:38 | TRUE | "no fill-helper function" | True — compiler rejects kosh_push on params |
| docs/KOSH-REUSE.md:74 | TRUE | "there is no free" | True — no free primitive |
| docs/LANGUAGE-REFERENCE.md:360 | TRUE | "no background services unless…" | Requirements spec, not an absence claim |
| docs/LIBRARY-BOUNDARY.md:18 | TRUE | FS ops "deliberately absent" | Deliberate boundary |
| docs/LIBRARY-BOUNDARY.md:34 | TRUE | "no concurrency model yet" | Real limit |
| docs/LIBRARY-BOUNDARY.md:41 | FALSE | "there is no FFI yet (not started)" | C FFI shipped R32–R34; gates "R32 FFI / R33 FFI kinds / R34 FFI v2" PASS |
| docs/LIBRARY-BOUNDARY.md:41 | FALSE | (same, second pattern hit) | Same |
| docs/LIBRARY-BOUNDARY.md:44 | TRUE | "no event or async facility" | Real limit |
| docs/LIBRARY-BOUNDARY.md:59 | TRUE | "no propagation operator / exhaustiveness" | Real limit |
| docs/LIBRARY-BOUNDARY.md:61 | FALSE | "No first-class functions… no methods" | First-class functions + methods exist (R23, tests/r23, gate PASS); "no generic collections" part true — mixed, bucketed FALSE |
| docs/LIBRARY-BOUNDARY.md:72 | TRUE | "no ownership, no borrow checking, no unsafe boundary" | Real limits |
| docs/LIBRARY-BOUNDARY.md:81 | TRUE | "no exhaustiveness checking" | Real limit |
| docs/LIBRARY-BOUNDARY.md:84 | TRUE | "no formal type-contract system" | Real limit |
| docs/LIBRARY-BOUNDARY.md:87 | TRUE | "no formal written specification yet" | Real limit |
| docs/LIBRARY-BOUNDARY.md:114 | TRUE | "not a missing feature to be padded in" | Policy statement |
| docs/MEMORY-MODEL.md:81 | TRUE | "no concurrency memory model…" | Real limit |
| docs/MEMORY-MODEL.md:89 | TRUE | "never been designed" (optimizer assumptions) | True |
| docs/MEMORY-MODEL.md:100 | TRUE | "DESIGN ONLY, NOT IMPLEMENTED" | Explicit proposal |
| docs/MEMORY-MODEL.md:180 | TRUE | "no primitive to call" (no free) | True |
| docs/NEGATIVE-CORPUS.md:120 | TRUE | "never executed" (negative outputs) | Harness policy |
| docs/R58-CONSTANT-FOLDING.md:28 | TRUE | "Not implemented in this partial" | About that partial implementation |
| docs/R62-WINDOWS-ACCEPTANCE.md:3 | TRUE | "Workstreams 4–5 remain not implemented" | About that doc's own scope |
| docs/R63-KOSH-BUILTINS.md:54 | TRUE | Peepholes "NOT IMPLEMENTED" | True |
| docs/R63-KOSH-BUILTINS.md:56 | TRUE | Overflow traps "NOT IMPLEMENTED" | True |
| docs/R64-KOSH-DIAGNOSTICS.md:58 | TRUE | Deferred peepholes "NOT IMPLEMENTED" | True |
| docs/R64-KOSH-DIAGNOSTICS.md:61 | TRUE | Overflow trapping "NOT IMPLEMENTED" | True |
| docs/R68-INDIC-DEVICES.md:35 | TRUE | "no global text replacement" | Design statement |
| docs/R68-WINDOWS-GUI-CHECKLIST.md:24 | TRUE | "There is no timer" | GUI implementation detail |
| docs/R69-PURE-PAIR-MEASUREMENT.md:21 | TRUE | Control "never executed" | Intentional control |
| docs/R71-BOOT-PATH.md:24 | TRUE | "no second stage, relocation loader…" | About that boot experiment |
| docs/R71-CANONICAL-BUILD.md:68 | TRUE | "no new expanded-core or binary hash" | About that build |
| docs/R71-MEMORY-BOUNDARY.md:25 | TRUE | "no new pack spellings… yet" | About that experimental marker |
| docs/R71-MEMORY-BOUNDARY.md:77 | TRUE | Provenance "not implemented by this extension" | About that extension |
| docs/R71-MODULES.md:6 | TRUE | "no second parser or Python compiler" | About the R71 supplement's scope |
| docs/R71-MODULES.md:9 | TRUE | ".sm to object emitter… NOT implemented by this supplement" | Supplement scope (main compiler HAS it via R28/R29) |
| docs/R71-MODULES.md:44 | TRUE | "Proposed minimum… not implemented" | Proposal |
| docs/R71-SPECIFICATION-EVIDENCE.md:45 | TRUE | "never executed" (rejected programs) | Harness policy |
| docs/R72-BASELINE-OBSERVED.md:21 | TRUE | "remain NOT IMPLEMENTED" | R71 workstream tracking (supplement scope) |
| docs/SANDESH.md:4 | TRUE | "There is no English" | Sanskrit-only policy |
| docs/SPECIFICATION.md:69 | TRUE | "no claim here of first-class functions…" | Scope statement — what the SPEC covers, not what exists |
| docs/_newchapter_en.html:53 | TRUE | "not a missing feature" | Policy statement |
| docs/_newchapter_en.html:83 | TRUE | "IDE not yet available on Windows" | True (Windows IDE status) |
| docs/sutram-book-english.html:83 | TRUE | "no interpreter, VM, runtime library" | By design |
| docs/sutram-book-english.html:435 | TRUE | "no runtime dependency" | By design (static linking) |
| docs/sutram-book-english.html:712 | TRUE | "not a missing feature" | Policy statement |
| docs/sutram-book-english.html:742 | TRUE | "IDE not yet available on Windows" | True |
| docs/sutram-design-parameters.html:159 | FALSE | "there are no function values" | First-class functions exist (R23) |
| docs/sutram-design-parameters.html:179 | FALSE | "There are no methods" | Methods exist (R23) |
| docs/sutram-design-parameters.html:191 | FALSE | "no slices…" | Slices exist (PROJECT-OVERVIEW: "methods and slices exist"); alignment/SIMD part true — mixed, bucketed FALSE |
| docs/sutram-design-parameters.html:211 | TRUE | "no event or async facility" | Real limit |
| docs/sutram-design-parameters.html:240 | TRUE | Unicode normalisation "not implemented" | Real gap |
| docs/sutram-design-parameters.html:257 | TRUE | "no formal type-contract system" | Real limit |
| docs/sutram-design-parameters.html:267 | TRUE | "no ownership, no borrow checking, no unsafe boundary" | Real limits |
| docs/sutram-design-parameters.html:279 | TRUE | "no phal type, no propagation operator, no exhaustiveness" | Real limits |
| docs/sutram-design-parameters.html:316 | FALSE | Windows sources "never been executed by this project" | 16 checks on real Windows 11 (CHANGELOG v318) |
| docs/sutram-design-parameters.html:329 | FALSE | "There is no separate compilation" | Exists via --separate + sutram-link (R28/R29); "no package manager, no lockfile" part true — mixed, bucketed FALSE |
| docs/sutram-design-parameters.html:329 | FALSE | (same, second pattern hit) | Same |
| docs/sutram-design-parameters.html:341 | TRUE | Unicode normalisation "not implemented" | Real gap |
| docs/sutram-design-parameters.html:365 | FALSE | "there is no FFI" | C FFI shipped R32–R34 |
| docs/sutram-design-parameters.html:365 | FALSE | (same, second pattern hit) | Same |
| docs/sutram-performance.html:129 | TRUE | "no runtime to call into" | By design |
| docs/sutram-project-status.html:147 | FALSE | Windows compiler "Never executed by this project" | 16 checks on real Windows 11 |
| docs/sutram-project-status.html:186 | TRUE | "No generics, no threads…" | Real limits |
| docs/sutram-project-status.html:186 | TRUE | (same, second pattern hit) | Same |
| docs/sutram-project-status.html:225 | TRUE | "no ownership model" | Real limit |
| docs/sutram-scorecard.html:150 | FALSE | "there is no C FFI" | C FFI shipped R32–R34 |
| docs/sutram-scorecard.html:198 | TRUE | "No generics, closures or metaprogramming" | Real limits |
| docs/sutram-stdlib.html:72 | TRUE | "no bit-cast primitive" | Language limitation |
| docs/sutram-stdlib.html:129 | TRUE | "no entropy source" | Language limitation |
| docs/sutram-stdlib.html:167 | FALSE | "Sutram has no first-class functions" | First-class functions exist (R23) |
| docs/sutram-stdlib.html:228 | TRUE | 'no "deleted" state and no tombstones' | Hash-map design decision |
| docs/sutram-stdlib.html:258 | TRUE | "no propagation operator… no callbacks" | Real language limits |
| docs/sutram-stdlib.html:391 | TRUE | "dasham elements are NOT supported" | API limitation |
| windows/gui/README-WINDOWS-GUI.md:118 | TRUE | "no nonblocking output loop or native Windows CI" | GUI limitations |
| docs/CHANGELOG.md | HISTORICAL | 49 hits, all in versioned history | Dated entries; leave alone per instructions (not listed individually) |

## Counts

| Bucket | Rows | Hits represented |
|---|---|---|
| FALSE | 16 | 16 |
| TRUE | 90 | 90 |
| HISTORICAL | 9 | 57 (49 CHANGELOG + 4 progress-report + 4 completion-roadmap) |
| AMBIGUOUS | 0 | 0 |
| **Total** | **115** | **163** |

No files were modified. The 49 CHANGELOG hits are grouped into one HISTORICAL row per the task instructions.
