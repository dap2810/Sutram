# R195–R198 — memory lifetime audit, release verdict and student reference

Main reviewed: `08fd732914acbb47fca7bc3bc2f2a286da18b6af`, v298. PR #65 read at head `029c06d47867433ce09e52010cf411c5c978a95b`, open and unmerged. Its integration note identifies the tested candidate as `1b984b5c`. These are different states, not one accepted release. This handoff answers all four briefs, with R196's lifetime work first. No production changes or merge.

## Immediate finding: the Windows candidate must not be merged wholesale

PR #65 and its `Windows-to-Sarvam/win-round4-2026-11-03/INTEGRATION.md` explicitly report a semantic incompatibility: inherited Round 3 makes string concatenation allocate, while v298 preserves in-place mutation. R54 raw_valid depends on mutation and was outside the branch's original gate selection. The branch's 312 passes do not settle this conflict. Preserve main's v298 builtin semantics, port the memory changes separately, and rerun R54/R121 plus both native suites. This is a release blocker, not a request to merge.

The branch also reports approximately 1 GiB private commit on first arena use and 64 MiB per kosh, not just virtual address reservation. R198's headline “finished on both platforms” is therefore premature. A hello-world that never activates an arena need not incur its allocation; the precise claim is first arena use, as the PR states.

## R196 — all 310 library return contracts

Enumerated 310 `prakriya` declarations in all 24 `lib/*.smlib` files. Reviewed every explicit return expression, its assigned-value dependencies and delegated return targets; inspected constructor bodies, allocator sites and local arrays. Complete per-function evidence is [ROUND-196-LIBRARY-RETURN-AUDIT.csv](ROUND-196-LIBRARY-RETURN-AUDIT.csv), including signatures, source lines and return expressions.

| Return category | Functions | Conclusion |
|---|---:|---|
| Allocated pointer by contract | 7 | Return persistent allocator storage, not a local array or closed block allocation. |
| Caller-payload word | 11 | Can carry an address supplied by caller; lifetime remains the caller's obligation. |
| Scalar by contract | 285 | Counts, offsets, statuses, arithmetic or character values, including delegated scalar results. |
| No explicit return | 7 | No promised pointer result; incidental machine-register contents are not an API. |
| Total | 310 | This is a source return-contract audit, not formal memory-safety certification. |

### Every declared pointer-returning library function

| Function | Site | Storage and lifetime |
|---|---|---|
| mala_nava | lib/mala.smlib:8 | Returns nirmmita(sz); persistent allocation, or 0. |
| nighantu_srij | lib/nighantu.smlib:107 | Returns allocated map m; persistent allocation, or 0. |
| nighantu_vardh | lib/nighantu.smlib:279 | Returns newm from nighantu_srij; persistent new map, not its temporary key buffer. Old-map aliases still refer to the old map; this is not in-place growth. |
| rakh_srij | lib/sangrah.smlib:33 | Delegates to nighantu_srij; same lifetime. |
| rakh_vardh | lib/sangrah.smlib:171 | Delegates to nighantu_vardh; same new-map/old-alias distinction. |
| suchi_srij | lib/suchi.smlib:46 | Allocated descriptor l contains allocated data pointer d; both persist beyond the call. Failure of second allocation can leave the first allocated; longevity is not reclamation. |
| avali_srij | lib/suchi.smlib:384 | Allocated descriptor q contains allocated buffer d; both persist beyond the call, with analogous partial-failure retention. |

No `mandapa` occurs in these library sources. These calls to nirmmita are therefore not lexical block scratch allocations. Current persistent allocation outlives the callee; a caller's enclosing block does not by itself prove a separately compiled library allocation is block scratch. This distinction also prevents claiming all helper scratch is reclaimed with the caller's block.

The 11 payload carriers are **mala_grah, mala_grah_surakshit, nighantu_grah, nighantu_grah_mool, phal_mulya, phal_mulya_va, suchi_grah, chay_apanay, chay_avalok, avali_nishkas, avali_avalok**. They return stored words/defaults. If those words encode addresses, their owner must remain live. These functions neither create a local pointer nor prove the payload safe. Raw integer APIs and arithmetic selectors can also be misused to transport encoded addresses; the categories describe intended contracts, not a sound pointer type system. Numeric min/max wrappers are scalar-by-contract, not a guarantee that raw address bits cannot pass through them.

Formatting and conversion routines generally write into caller-provided output and return a count. Anukram's `p + 8` is an updated position, not a returned buffer pointer. Local arrays in ganita feed arithmetic results, not returned array addresses. No additional declared library return of a local stack array was found in this bounded audit. Buffer capacities, writes through output parameters, payload escape, interprocedural aliasing and compiler correctness still need separate proofs/tests; this result cannot close those categories.

### Correct the defect class before testing it

The brief conflates two cases. Old anka_akshar returned transient stack storage; current emitter at src/sutram_compiler.asm:24206 allocates two bytes and checks allocation failure. Vartani_sandhi is an in-place operation returning its destination, not a new stack buffer in the reviewed emitter (:23773 onward). v298 refuses a literal destination and inserts an image-address check. It still requires writable storage with adequate append capacity; checking “not in image” cannot establish capacity or lifetime of arbitrary raw pointers.

The broader class is **returned references whose storage/lifetime contract is absent or violated**, including stack addresses, reused temporaries, borrowed caller storage and allocator/region lifetime mismatches. It includes callers misusing a borrowed result, not only functions allocating local storage.

### Decision: permit pointer returns, forbid dangling returns in checked code

Do not ban all pointer returns: the seven constructors need them. Adopt a language rule for checked code: a returned pointer must refer to caller-owned live storage, transferred persistent storage, or a borrow whose owner is proven to outlive its use. Reject local stack/closed-region escapes through direct returns, aggregates, stores and calls when checked provenance cannot establish the lifetime. Raw-address operations remain explicitly unchecked; a library convention alone is insufficient as a language-wide guarantee.

For v1.0, publish precise library ownership contracts and close known checked escape holes; do not claim comprehensive borrow checking. A sound whole-language implementation needs provenance across calls, aliases and integer casts, not a spelling scan. Planning cost: 1–3 engineer-days for contract records and targeted return regressions; roughly 2–6 engineer-weeks for a substantial checked provenance extension, subject to design review. These are estimates, not tested schedules or a requirement to add that entire system before release.

### Cheapest useful native probes

For the old character bug: retain two independently created characters, make intervening calls with stack activity, then read both; assert exact bytes and balanced repeated-call behavior. This is cheaper than a new checker, but a passing perturbation test is not a proof.

For old vartani_sandhi: a literal destination must refuse under the approved contract, independently of whether Linux happens to allow the write. Current v298 already has this check. For a writable undersized destination, place its end against a protected page or use a canary and request an append beyond capacity; a caller-bounded API may require that invalid-input probe to live in an explicitly unsafe test category. A protected-page probe catches the write, not arbitrary use-after-return. To systematically test expired-region reads, poison/protect released storage before reuse. A different OS is supporting evidence, not the oracle. ASan does not automatically instrument a hand-written NASM compiler's emitted machine code; using it would require suitable instrumentation. No native probes were run here.

## R195/R198 — closed decisions on reuse and threads

**Reuse inside a live block: not automatic before v1.0.** Arbitrary recycling is possible without tracing GC, but only with an explicit lifetime discipline: unique-owner free, reference counts with cycle policy, or nested region checkpoints that prove no references survive reset. Raw aliases make “recycle an apparently unused object” unsafe. It requires allocator/runtime support even if emitted into the native binary; “no interpreter” is not “no runtime machinery.”

Use a nested mandapa for each loop iteration's temporary allocations and carry only copied values or explicitly longer-lived results out. Reuse an existing caller-owned buffer when its capacity suffices. A long-lived block otherwise accumulates allocations until it ends or its budget refuses another one. Do not imply this reclaims every library helper's persistent allocation. Implementing general free/reuse now would expand the aliasing surface during release stabilization. Estimated future design+implementation+attack: 2–6 engineer-weeks for an explicit ownership-based subset, longer for unrestricted aliases. Nested-block usage documentation and examples: roughly half to one engineer-day plus target verification.

**Threads: deferred beyond v1.0; not “never,” and no promised v1.1 ship date.** The current model is single-threaded. Unsynchronized arena cursors and budget counters can race on the first allocation; shared kosh growth and generation/lifetime checks then introduce further races. There is no universal ordering of which fails first. Atomic cursor increments alone do not fix reclamation or publication.

Future design: per-thread arenas and budgets; immutable copies/messages or explicit ownership transfer between threads; no shared mutable raw pointers in the checked subset; separately synchronized collections; stable owner metadata and coordinated reclamation. OS/FFI threads must not enter allocation paths concurrently until supported. A production-quality implementation is a multi-week project (rough planning 4–12+ engineer-weeks), not a release-week flag change. The reference should say “v1.0 has no supported concurrent execution within a process.”

## R198 — proposed student reference text

**Publication condition:** this text's “both platforms” statement is for the reconciled, tested release candidate, not current main plus an unmerged branch. Until then replace it with: “Memory reporting and budgets work on Linux; the Windows implementation is awaiting integration and acceptance.”

> A `mandapa` block lets temporary block allocations share space that can be used again when the block ends; values needed later must be kept in longer-lived storage.
>
> `parimana()` reports the bytes tracked as currently used by Sutram's allocator and collections; it is not the total memory charged by your operating system. In the accepted release this is available on both Linux and Windows.
>
> `mandapa parimita N` sets a limit for the block's budgeted allocations. The allocation that would exceed that limit is refused before it is made; previously completed work is not undone. It is not a limit on every byte used by the whole program.
>
> A `kosh` sets aside a large stretch of possible addresses—64 MiB—even while almost empty. Its data needs eight bytes per reserved element slot, plus a small header, and the operating system provides memory in pages. A small collection commonly needs a 4 KiB page; that is not an extra page charged for every element. Under a total address-space limit of 1 GiB, roughly fifteen such reservations can already be too many once the rest of the program is included. The exact limit depends on other allocations.
>
> Do not store or return a block-owned `kosh` outside its block; its permitted lifetime ends there. Enforcement of this rule does not promise that all of its operating-system storage is immediately released.
>
> Ordinary integer operators can wrap when a result does not fit. Checked library operations refuse or report invalid results according to their contracts; other library operations may saturate or use a documented status. Do not assume every library function traps on overflow.

The requested phrase “4 KB plus 8 bytes per element” is too imprecise as a universal bill. The source uses a 40-byte header and capacity, not merely element count; page rounding, reserved address space, committed pages and logical parimana bytes differ. On Linux with lazy backing, touched pages matter. PR #65's eager Windows adapter currently charges the full reserved ranges. Do not tell a student it costs nothing until use on that branch. Likewise “the sixteenth crashes” is an observed resource-limit scenario, not a portable semantic rule; exhaustion should produce a controlled failure.

## R198 — Windows commit cost: not acceptable as the general-release default

Prefer **reserve once, commit pages incrementally**, preserving fixed addresses. Reserve the arena and each kosh range without committing it; commit the pages needed for headers, live capacity and arena growth before access. For a two-ended arena, track committed spans at both ends and handle their meeting safely. Check OS failures before publishing pointers/cursors. Roll back or preserve state on failure; account logical live bytes separately from committed pages. Block rewind may retain committed pages for reuse; decommit is optional and requires valid lifetime handling. Failure must not leave parimana claiming bytes that were never obtained.

Do not merely change VirtualAlloc flags to reserve-only: reads/writes would fault. Do not make text writable. A smaller target-specific arena is a temporary mitigation with a documented lower maximum, not an equivalent memory model. It must still handle exhaustion, budgets and alias stability. It also does not remove the separate 64 MiB-per-kosh eager commitment.

Planning estimates: a size-only mitigation plus tests 1–2 engineer-days; correct incremental commitment 3–7 engineer-days implementation, plus 2–4 days independent native pressure/failure/lifetime testing; longer if adapter structure or address-stability requirements require redesign. Acceptance must measure first arena use, many small collections, growth and teardown, under constrained commit and address-space limits. Test failed commitment and stale references. These are unvalidated estimates; no OS API changes are made here.

## R197 — release verdict

**NO: v297 is not shippable as the promised v1.0. Current v298 plus PR #65 is also not yet an accepted release.** Passing counts cannot override known builtin faults, ignored Windows budget semantics, an integration conflict and excessive commit cost.

| Order | Required before general release | Estimated engineering effort |
|---|---|---|
| 1 | Reconcile string contracts; retain v298 semantics and separately port/review Windows memory changes. Include R54 mutation and R121 literal/lifetime regressions. | 1–3 days plus review; not a wholesale merge. |
| 2 | Resolve eager Windows commitment and controlled exhaustion; document bounded alias stability and low-memory behavior. | 5–11 days including independent tests, per estimate above. |
| 3 | Attack exact integrated candidate on Linux and Windows: budgets, lifetime escapes, aliases through region limit, pointer-return regressions, arithmetic contracts and native ABI. | 2–5 days, dependent on fixes; further defects extend it. |
| 4 | Build installer from accepted commit; verify version/hash, clean install/run/uninstall, Unicode paths, console and IDE behavior on real Windows. | 1–2 days with hardware available. |
| 5 | Publish capability/ownership/cost reference and reviewed release notes; mark all deferred/unsupported features explicitly. | 1–2 days, can overlap. |

These are effort ranges, not a calendar guarantee and not estimates that can simply be summed: tasks overlap and native access is a dependency. A pre-release for testers can ship with explicit limitations; that is a different promise from general v1.0.

### Corrections and additions to the proposed release-note list

For **v297**, report the Windows accounting/budget gap, kosh alias divergence and two builtin defects; these are blockers rather than acceptable classroom surprises. For **v298**, character and literal-destination fixes are on main, while the Windows candidate's pass claim belongs to its own commit. Do not retain stale “two wrong builtins” wording after acceptance, or claim branch fixes already shipped.

- Linker prefix inconsistency is presentation debt; lower priority than memory correctness. Do not infer all linker bodies are translated.
- “No exception handling” is false: explicit result handling exists. Say no nonlocal try/catch unwinding; document phal float/indirect-call limitations.
- “No debugger” should distinguish absence of a supported integrated interactive debugger from debug/source diagnostics and possible external native tools. Verify the exact release feature list before an absolute claim.
- Generics and threads can be clearly deferred. They are not reasons to accept silent safety-contract violations.
- Integer wrapping and per-function checked/status/saturating behavior need worked examples, not the blanket “library refuses.”
- No parikshita markers were found by the focused library search. That does not erase native/property tests, and tests do not establish formal verification. State precisely which verification guarantee is absent.
- Include raw-pointer extent/lifetime obligations, in-place string destination capacity, byte-versus-character string semantics, ASCII-only helpers, region-limit relocation/alias risk, unbounded helper-allocation retention, lack of general free within live scopes, platform file-flag differences, patra_asti's current open-success meaning, frozen non-Sanskrit development status, untested/skipped platform features, and measured memory commitment.

This is the release-relevant list supported by this review; an exhaustive release-note claim needs reconciliation with the pinned reference, open issue ledger and accepted platform matrix. Do not claim a finite review proved no other limitation exists. Classroom priorities are deterministic correct examples, enforced resource limits, understandable memory costs and reliable install/run behavior; optional advanced features come later.

### Windows gate required before yes

A count of Linux gates cannot substitute for Windows coverage. Require a repeatable automated native gate on the exact integrated commit and installer payload: clean rebuild and hashes; target-aware examples with required flags; R54/R121; memory budget/accounting/lifetime/alias boundary probes; allocation/commit failure; retained returned strings across calls; mixed FFI ABI and clobber/stack tests; Unicode console and paths; explicit expected stdout/stderr/exit and crash/timeout discrimination. NO_EXPECTATION and SKIP remain visible, never converted into PASS. Independently inspect native GUI/install/uninstall evidence where automation is insufficient. Run intentionally at the release milestone under the existing notification policy, not a new automatic push trigger.

## Validation and handoff

Verified 310 declaration rows across 24 modules and enumerated return expressions/assignment dependencies; reviewed all seven constructors and delegated pointer returns. This is not an exhaustive write-effect, integer-to-pointer or compiler escape proof. Reviewed current PR status/integration warning and current builtin emitter source. No builds, native tests, Windows probes, CI or installer acceptance performed: **NOT RUN — read-side review only**. PR results and resource measurements are reported by their owners, not reproduced here. All changes are confined to ChatGPT-to-Sarvam handoff documents/evidence; no merges or Windows-folder writes.
