# Sutram ROUND 146 — composition audit of v270, not a whole-language safety certificate

**Date:** 30 October 2026. **Pinned main:** `b667bd9ebc84adfb38d811ab691e14a520f16273`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-146.md`, blob `7c7e4a1cceb425037cd5822fd8db87d9b54ef5b7`.
**Return:** `ChatGPT-to-Sarvam/ROUND-146-MEMORY-COMPOSITION-AUDIT.md`.
**Role:** independent read-side source/claim audit. No native compiler, fixture, benchmark or release gate was executed here. The source-confirmed omissions below and predicted consequences are deliberately distinguished from partner-reported executions. Sanskrit-only; no source changes.

## Decisions first

1. **The proposed README sentence is NOT true without substantial qualification.** This is a Linux ELF scratch-region facility with partial escape diagnostics, not general scope-based memory reclamation or complete compile-time memory safety. PE and guard-page builds deliberately take the ordinary allocation path. Cursor rewind makes arena space reusable; it is not an OS unmap. Emitted allocation, zeroing and cleanup code still runs at execution time, even without an external managed runtime. [R2-R5]
2. **The composition has unresolved source-level gaps.** I found a root-statement-only store check that misses store calls nested in expressions; a one-pass provenance check that does not establish loop-backedge facts; and an implicit `prasar` failure-return path that bypasses scratch rewind. These are concrete mechanisms, not another request for an arbitrary higher test count. Native acceptance/results of the proposed witnesses remain **NOT RUN**. [R3-R6]
3. **Ordinary positive-size exhaustion has an explicit failure path, but the size-rounding domain is not fully guarded.** For `nirmmita(-1)` inside a live region, the published machine template rounds the request to zero and still executes a zeroing store. This predicts a write at the current scratch boundary. It is an invalid-size handling gap, not evidence that all legitimate positive requests fail. [R4]
4. **Do not treat the intended restrictive K0 contract as already enforced.** R73 explicitly says `kosh` is not refused, and unverified helpers may retain/return addresses. The actual implementation is weaker than the earlier whole-function K0 proposal. Documentation is necessary but cannot turn an accepted bypass into a rejected one. [R2,R3,R7]
5. **Credit the completed work accurately.** The ordinary scratch path, zeroing, explicit return/jump cleanup and reported depth-100 recursion are real evidence. They do not cover the new combinations identified here. My recommendation is to hold the unrestricted safety claim and close the named gaps before qualifying a checked/reclaiming v1 feature.

**Prior return verified:** R145 now exists in GitHub as `ChatGPT-to-Sarvam/ROUND-145-ESCAPE-COVERAGE-AND-K0-CONTRACT.md`, commit `916f74acbe6e97dbedf7d14071a340d64499a942`. It is not the differently named local fallback artifact from the preceding chat response. I did not re-upload or overwrite it. [R9]

## Evidence baseline: what v270 actually implements

The parser rewrites a lexical `mandapa` into a block containing a hidden local mark, its body, and a rewind node. A `nirmmita` lexically inside it is tagged `BN_NIRM_SCRATCH`; an allocation inside an ordinary called function does not inherit that tag merely because the call site is inside a region. `r73_ret_mark` annotates explicit return nodes; `r73_wrap_jump` inserts rewind before a break/continue that exits region scopes. [R3]

In Linux ELF production mode, persistent allocation grows upward and scratch allocation grows downward within the reserved arena. `r73_gen_scratch_nirm` checks the proposed scratch position against the persistent cursor before publishing it, then zeroes the allocated range. `r73_gen_rewind` restores the saved scratch cursor. `r65_active` is false for PE and `GUARD_PAGES`; the expression dispatch also uses the ordinary allocation path under `--fail-alloc`. These alternate modes are not native validation of the production scratch path. [R3,R4]

The check is invoked by `parse_stmt` after each parsed statement. `r73_check_stmt` recognizes assignment, return and selected standalone builtin calls. `r73_taint` recognizes scratch allocation, named variables, binary expressions and ternaries; other expression forms, including ordinary function-call results, are treated as untainted by this function. There is no demonstrated whole-function K0 rejection policy or complete effect-summary pass in these helpers. [R3,R5]

R73 reports 15 scratch checks, a recursion example at depth 100, scalar copy-out, normal/jump cleanup, an oversized-request exit, and flat RSS on its selected repeated-block workload. Those are **partner-reported**, not rerun by this review. The fixture `blind_call.sm` intentionally accepts a helper that retains a scratch address, and observes only a final `1`, not a later stale dereference. Its passing status records a known limitation; it is not a lifetime-safety positive. [R2,R8]

## WS1 — the four requested compositions

| Requested composition | What the inspected implementation supports | What fails or remains unqualified |
|---|---|---|
| A block inside a loop growing an outer `kosh` | For numerical values, representable sizes and no escaping references, scratch moves the upper boundary down while persistent allocation/growth respects that boundary. Rewind restores only the upper cursor, not persistent vector storage. I found no immediate cursor-crossing defect in that ordinary case. | This is not a native combined-case PASS. `kosh` is not hard-refused. A scratch pointer appended through an expression-wrapped `kosh_push` can bypass the standalone-store check; reuse can then make the stored pointer name another iteration's data. See F1. |
| A `prakriya` receives scratch and returns a derived value | Reading initialized, in-bounds numerical cells while the caller's region remains live can legitimately return a scalar. | A helper may instead return an address or retain it while returning a scalar. The caller has no verified non-retention summary; call results are treated as clean. The shipped blind-call fixture acknowledges this. A derived *address* is not equivalent to a derived *number*. |
| Deep recursion with a block in each frame | Hidden marks are ordinary per-invocation locals. The supplied `gahan(100)` example preserves the parent's buffer across a recursive call and reports the expected scalar result. | Depth 100 is not arbitrary-depth qualification. Live scratch and native stack both grow with active frames; lexical nesting limits are not runtime recursion limits. Failure propagation via `prasar` bypasses region cleanup, so a recursive/error variant is not covered by the ordinary-return positive. See F3. |
| A block exhausts the scratch range | For positive, representable requests, emitted bounds checks branch to `kshetra purnam` and exit 1 before publishing a new scratch cursor. The supplied report says a 2 GiB request takes this path. No ordinary scratch fallback to persistent allocation is emitted in this path. | This is process termination, not recoverable `0` for positive exhaustion. Size zero returns `0`. Negative/wrapped size validation has a separate hole, F4. PE, guard mode and fault-injection mode use different paths and must not be cited as testing the Linux scratch-exhaustion mechanism. |

**Answer to “name the composition that fails”:** the strongest source-confirmed cleanup omission is **a scratch-owning function that returns implicitly through failed `prasar`, followed by a caller that catches the failure and continues**. The new escape witness is **a scratch pointer passed to a store builtin nested in an initializer/expression**, including the outer-vector loop requested in the brief. I have not executed either; the following source traces make the predicted failure falsifiable rather than presenting a guessed PASS/FAIL result.

### F1 — a store effect disappears from the check when the call is inside an expression

`r73_check_stmt` checks the value argument of `BN_LIKH8` and `BN_KOSHPUSH` only in its `.call` branch, when the **statement root** is `AST_CALL`. An initializer's root statement is `AST_DECL`, which this checker does not traverse. `r73_note_decl` asks for the initializer's value taint, and `r73_taint` returns zero for a call other than `BN_NIRM_SCRATCH`. Checking the returned length is not checking the pointer stored by `kosh_push`. An assignment containing that call has the same separation between result taint and effects. [R3,R5]

**Proposed witness — NOT COMPILED OR RUN:**

```sutram
mukhya() {
    kosh saved[1]
    vitti i = 0
    yavat (i < 2) {
        mandapa {
            vitti b = nirmmita(8)
            b[0] = i
            vitti count = kosh_push(saved, b)
        }
        i = i + 1
    }
    vitti first = saved[0]
    likha(first[0])
}
```

The ordinary standalone `kosh_push(saved,b)` is intended to be refused. Putting the same effect in the initializer above is predicted to bypass that check. Both block instances reuse the same scratch slot; the persistent vector retains addresses whose region lifetime has ended. A later read may appear to work while observing reused contents. **Do not promise a crash, a unique pointer value, or an exact printed value without running the candidate.** A non-crashing stale read is precisely why an output/lifetime oracle is needed.

A corresponding raw-store witness is `vitti ignored = likh8(out,b)`, with `out` a valid longer-lived cell. `likha(kosh_push(saved,b))` is another expression-composition variant. The fix obligation is to visit effects in every admitted expression position and to inventory all store/copy builtins, not merely add one initializer special case. A complete K0 prohibition would reject unsupported collections independently, but that restriction is not implemented by the inspected helpers.

### F2 — a monotone one-pass update is not a loop fixpoint

The v270 weak update fixes the reported branch-clearing example by never decreasing an existing name's taint. It does not revisit an earlier use in a loop after a later assignment changes the value that reaches that use on the next iteration. The parser's statement hook is one source-order visit; an `AST_WHILE` root is not reanalyzed by `r73_check_stmt`. [R3,R5]

**Proposed witness — NOT COMPILED OR RUN:**

```sutram
mukhya() {
    vitti outside = 0
    mandapa {
        vitti b = nirmmita(8)
        b[0] = 123
        vitti q = 0
        vitti i = 0
        yavat (i < 2) {
            yadi (i == 1) { outside = q }
            q = b
            i = i + 1
        }
    }
    mandapa {
        vitti replacement = nirmmita(8)
        replacement[0] = 777
    }
    likha(outside[0])
}
```

At the source-order check of `outside=q`, `q` has no scratch origin yet. `q=b` is encountered later. At runtime the second iteration can carry `b` through `q` into the outer variable. Weak updates alone do not propagate that backedge fact to the already-checked store. A fresh full-function dataflow pass, iteration to stable loop facts, or conservative refusal of unsupported loop-carried pointer forms is required. This is a **new source-based prediction**, not a claim that Claude's specific v269 branch-join repair failed its existing test.

Even without the final two statements, the outward assignment is the violated lifetime rule. The second block makes reuse observable for a native negative control. Do not call it safe because its address remains mapped.

### F3 — `prasar` returns through an epilogue that does not rewind

The explicit `AST_RETURN` builder receives a mark and its function-return generator invokes `r73_gen_ret_rewind`. By contrast, `.ge_prasar` delegates to `r25_gen_prasar`. On failure inside a function, that helper emits the epilogue directly:

```text
lea rsp,[rbp-8]; pop rbx; pop rbp; ret
```

There is no scratch restore on that branch, and it bypasses the trailing `AST_REWIND` in the enclosing block. The `AST_PRASAR` parser construction retains the call but does not attach the explicit-return mark. The separate R25 include is unchanged in the inspected source. [R3,R4,R6]

**Proposed witness shape — NOT COMPILED OR RUN:**

```sutram
prakriya failure() { nivartanam dosh(1) }
prakriya one_attempt() {
    mandapa {
        vitti b = nirmmita(64)
        b[0] = 1
        vitti x = prasar failure()
        nivartanam siddhi(x)
    }
}
mukhya() {
    vitti attempts = 0
    yavat (attempts < 1000000) {
        yadi dosh (code = one_attempt()) {
            attempts = attempts + 1
        } anya {
            nivartanam dosh(2)
        }
    }
    likha(attempts)
}
```

The caller deliberately catches the failure **without an enclosing region that would later hide the missing rewind by restoring an older mark**. Each attempt is predicted to leave its scratch cursor lower; repeated handled failures consume region capacity instead of reusing it. It can eventually hit the full-range exit even though each attempt logically finishes. This is a retention/cleanup failure, not necessarily an immediate use-after-free.

The correction must preserve the failure value and status while restoring all exited regions. Main's process-exit case is a different lifetime outcome; do not use process termination to claim a returning helper cleaned up correctly. Add propagation success/failure cases, nested regions and recursion, not only explicit `nivartanam` and `krama`/`agrim` cases. The existing `jumps.sm` covers ordinary return at depth 100, not this failure path. [R8]

### F4 — invalid negative requests can wrap the alignment and still zero memory

The live scratch template tests only `size==0` before `aligned=(size+15)&~15`; it does not reject a negative size or detect the addition wrapping first. For the 64-bit value `-1`:

```text
(size + 15) mod 2^64 = 14
aligned = 14 & ~15 = 0
new_end = old_end
(size + 7) mod 2^64 >> 3 = 0
```

The zeroing sequence executes its first qword store **before** comparing its counter with that last zero count. Thus this path predicts one store at `old_end`, despite reserving no bytes. With an outer live scratch allocation, `old_end` is the beginning of that outer object's storage; in a fresh top-level region it is the arena's one-past-end address. [R4]

**Proposed boundary witness — NOT COMPILED OR RUN:**

```sutram
mukhya() {
    mandapa {
        vitti owner = nirmmita(16)
        owner[0] = 123
        mandapa { vitti bad = nirmmita(0 - 1) }
        likha(owner[0])
    }
}
```

This is deliberately an invalid allocation request. It should be rejected or follow a documented fail-closed size-error path, not mutate a valid outer allocation. The predicted overwrite is source/arithmetic evidence, not an observed printed result. Other negative values near zero can also produce a very large zeroing count. Validate the size domain and checked rounding before updating the cursor or zeroing. The positive oversized-request test does not cover signed/wraparound inputs.

I evaluated a small local unsigned-64 arithmetic model of these published operations for 0, 1, 8, 16, 2 GiB and -1/-8/-15/-16. It confirmed the arithmetic distinction; it did not execute the byte template or establish end-to-end compiler acceptance.

### Known helper-call escape remains an actual design limitation

`tests/r73_scratch/blind_call.sm` contains `rakh(m,p) { m[0]=p; nivartanam 0 }`, called with a scratch pointer. The gate expects this to compile/run. A helper returning `p+0`, or retaining `p` while returning a computed number, is the same unverified-call boundary. Returning a numerical result alone is not evidence of non-retention. [R2,R8]

An unsafe address can also be stored through one of these routes and subsequently read from a cell, which the current checker declares untainted. Therefore the claim that all cell reads are clean depends on rejecting **every** pointer-producing store/effect that can populate those cells. F1 and helper effects invalidate that premise unless the accepted domain is restricted and enforced.

## WS2 — audit the proposed public sentence word by word

Proposed: **“Sutram's memory is released by scope, checked at compile time, with no garbage collector and no runtime.”**

| Wording | Verdict at this source snapshot |
|---|---|
| **“Sutram's memory”** | Too broad. Ordinary persistent `nirmmita`, collection backing storage and allocations inside ordinary helpers are not all reclaimed by the caller's block. |
| **“released by scope”** | Only a narrower region-reuse claim is supported on Linux ELF for the implemented exits. Rewind changes the allocator cursor; it does not unmap pages or guarantee an immediate RSS drop. `prasar` cleanup is missing. PE/guard builds deliberately do not use this reclamation path. |
| **“checked at compile time”** | Some escape patterns are diagnosed. The statement falsely suggests a complete lifetime/memory-safety check when admitted calls, nested effects and loop-carried origins can bypass it. Compilation success is not such a certificate. |
| **“no garbage collector”** | Consistent with this region allocator: no tracing/collection mechanism is introduced by the inspected paths. This does not imply safe reclamation by itself. |
| **“no runtime”** | Ambiguous and misleading as an absolute. Allocation, zeroing, checks and rewinds are emitted code executed at runtime; PE uses its native adapter. Prefer **“no external managed runtime”** or **“no VM dependency”**, not “no runtime code.” |

**README wording I would accept now, while the gaps remain:**

> Sutram emits native code without a garbage collector or external managed runtime. On Linux ELF, its experimental `mandapa` facility reuses scratch-arena space on supported block exits; escape checking and cleanup are incomplete, so this is not a general memory-safety or scope-based reclamation guarantee.

**After the named defects are repaired and qualified, a narrower feature sentence could become:**

> On supported Linux ELF builds, `mandapa` reclaims its own scratch-arena space for reuse on every supported exit, with compile-time checks for the documented restricted subset; persistent collections and ordinary callee allocations retain their separate lifetimes.

That second sentence is a **future acceptance target**, not today's certified result. A guarantee requires an enforced accepted subset, not a paragraph asking users never to exercise accepted bypasses.

Lower peak RSS in the reported loop supports reuse for that workload; it is not evidence of an OS deallocation syscall on every exit. Linux's mmap/munmap documentation distinguishes creating mappings from deleting them; the inspected rewind emits only a cursor store. External API context does not validate Sutram's implementation. [R4,W1]

The brief and R73 give different benchmark/RSS summaries. I have not reconstructed their exact environments or timing windows. Preserve their separate provenance; this round neither measures the stated 2–8 ns nor endorses the historical ~62,500 ns baseline or a cross-language speed ranking.

## WS3 — where the limitations belong and the exact sentence

**Both the reference and relevant diagnostics, but not diagnostics alone.** Put the limitation immediately before the first `mandapa` example and before any safety/reclamation promise in §19; summarize its scope next to the README claim. An unsafe program that compiles receives no `E_SCRATCH_ESCAPE`, so a hint printed only on rejected programs cannot inform all affected users. [R7]

**Reference sentence to add now:**

> The current escape check is partial: scratch addresses can escape through unverified function calls, nested store expressions and pointer-containing containers, and loop-carried origins are not fully analyzed; accepted code is not a memory-safety guarantee, and no scratch address may be retained beyond its originating `mandapa`.

**Separate cleanup/platform sentence:**

> Scratch reuse currently applies to Linux ELF, not PE or guard-page builds; failure propagation through `prasar` is not yet covered by the region rewind path, and ordinary `kosh` storage is not reclaimed by the block.

Keep the existing Sanskrit `E_SCRATCH_ESCAPE` diagnostic and its `Sanket` explanation, but update the diagnostic's coverage description during the source fix rather than implying that two named blind spots are an exhaustive list. I have not authored or applied new message-pack translations in this round.

**Correct the blanket `kosh` wording:** direct `kosh_push(k,b)` with a tracked scratch value is checked as a standalone statement; nevertheless `kosh` is not globally forbidden, pointer contents are not followed, and F1 bypasses the direct store check by changing expression context. “Every kosh operation is invisible” and “all kosh is refused” are both inaccurate descriptions of this source. [R2,R3]

For the intended strict K0 v1 contract, unsupported constructs must cause an explicit rejection throughout the containing checked function. If the owner instead releases this weaker advisory mode, name it as such and remove the checked-memory guarantee. A safe subset and an advisory checker are different products; a warning cannot silently substitute for a promised restriction.

## Narrow, actionable acceptance work — proposed, NOT RUN

| ID | Required comparison or control |
|---|---|
| C146-01 | Standalone versus initializer/assignment/argument-position `kosh_push` and `likh8`: every pointer-retaining effect must be rejected in the claimed checked subset; numerical-value positives must retain correct behavior. |
| C146-02 | The two-iteration backedge witness in F2, with a one-iteration control and a scalar-only loop positive. Reject the outward pointer store regardless of its earlier source position. |
| C146-03 | F3 under failed versus successful `prasar`, explicit tagged return, nested regions, caught failure and recursive propagation. Assert scratch cursor restoration and status/value preservation, not merely equal output. |
| C146-04 | Zero, positive exact-room, one-byte-over-room, positive oversized, negative and rounding-overflow requests. Check rejection/termination before any cursor publication or canary mutation. |
| C146-05 | Outer numerical kosh grown during repeated scratch scopes: verify vector contents, persistent/scratch nonoverlap, tail-extension and forced-copy paths; distinguish this legacy composition from a strict K0 positive. |
| C146-06 | Read-only scalar helper versus address-returning/retaining helper, with independent expected effects; a scalar return alone is not the oracle. |
| C146-07 | Recursive regions: parent buffers before/after child return, ordinary and propagation exits, measured frame/scratch limits and defined exhaustion handling. Do not infer arbitrary depth from 100. |
| C146-08 | Linux production, object/separate, PE, guard and fail-allocation configurations: label the allocation/reclamation path actually exercised. No cross-target safety claim from byte parsing or Wine alone. |

These eight named obligations describe families, not eight tests already implemented or a complete release matrix. Keep the prior parser, store/extent, alias, retention and wrapper-status work open unless separately evidenced as closed. Calibrate rejection tests with valid scalar counterparts and run every prospective crash in an isolated, bounded child process. No production patch or new test file is included in this return.

## Evidence ledger

All repository reads were pinned to the main SHA above. Helper names are provided where a whole-file lookup was used; do not mistake this for a complete audit of every line of the compiler.

- **R1:** `Sarvam-to-ChatGPT/ROUND-146.md`, `7c7e4a1cceb425037cd5822fd8db87d9b54ef5b7` — requested four compositions, public sentence and limitation wording.
- **R2:** `Claude-to-Sarvam/R73-00-STEP4-AND-REAL-BLOCK.md`, `b520002d3ecf583208ece01c7efad04cc00dc0fb` — measured claims, explicit acknowledged limitations, v269/v270 branch fix and target scope; all executions attributed.
- **R3:** `src/sutram_compiler.asm`, `d66f4ef81b10f5f55c82183d567f8188d6a6b90d` — inspected 7440–8075 for `r72_parse_mandapa`, region/function state, `r73_taint`, declaration tracking and `r73_check_stmt`; targeted whole-file lookups for scratch dispatch, kosh growth, explicit-return marking, AST_PRASAR construction and `.ge_prasar`. The live source identifies v270.
- **R4:** `src/r65_arena.inc`, `d3415cee577c686b7b1b197500f144c6bb550892` — complete fetched ranges 1–220,221–460,461–end: opposing cursors, target gating, persistent fallback, kosh extension, scratch size/zeroing byte templates, mark/reserve/rewind and explicit-return cleanup. No native disassembly equivalence check was performed.
- **R5:** `src/r45_debug.inc:1–155`, `fea8f9fe5de048b16d3f373772768c7ecdd0aaac` — `parse_stmt` invokes the statement-root checker after parsing, in normal and debug paths.
- **R6:** `src/r25_phal.inc:140–360`, `a36bd286aa6beea0b854576945e6874ba8835af0` — `r25_gen_prasar` direct failure epilogue and handler behavior, without region rewind.
- **R7:** `docs/LANGUAGE-REFERENCE.md:565–800`, `46897f03eb9295ce49c84a2b471121088738ab78` — result/propagation semantics and current §19 promises/limitations, which do not consistently reflect platform and cleanup boundaries.
- **R8:** `tests/r73_scratch/test_scratch.py`, `6498867c6f2efb434700063c106450e7554ec6db`; `jumps.sm`, `258df356f6b55d29799edbbb11b030a7e9723ee5`; `blind_call.sm`, `29545ee6ee7715bde736e2ccbbbeec9528da5c09` — read-only fixture/runner inspection, not a rerun. The runner explicitly expects the blind call to compile and prints no stale read.
- **R9:** `ChatGPT-to-Sarvam/ROUND-145-ESCAPE-COVERAGE-AND-K0-CONTRACT.md:1–22`, `b296e711b63e5dfeda7af868c8736cacad501f0b` — prior return confirmed present under this repository filename.
- **R10:** `LANGUAGE-PRIORITY.md:1–50`, `64682919a70fa1b79e415bc879aee9cad07582ad` — Sanskrit-only review and frozen-pack boundary.
- **W1, external API context only:** Linux man-pages mmap(2)/munmap(2), https://man7.org/linux/man-pages/man2/mmap.2.html, consulted 30 October 2026. Mapping removal is distinct from this implementation's cursor update; the source itself establishes which operations are emitted.

**Performed here:** connected pinned-source reads and a small independent unsigned-64 arithmetic model of the published scratch size/zeroing operations. No repository source/tool was executed. No new native counterexample result is claimed.

**NOT RUN — no native toolchain invoked:** F1–F4 witnesses, helper/recursive compositions, actual exhaustion, allocator canaries, compiler builds, ELF/PE/Windows/Wine execution, proposed acceptance work, regression/proof/guard suites or benchmarks. Source predictions must be independently reproduced at an exact compiler hash before being recorded as native failures or accepted repairs.

**Disposition:** request changes before the broad README guarantee or a completed strict-K0 claim. The findings do not erase the partner's measured ordinary scratch-reuse results; they show why those measurements do not establish the stated whole-system guarantee.

**NOT APPLIED:** compiler, library, examples, tests, tools, canonical documentation, language packs, workflows, Windows and backup changes. Add only this report under `ChatGPT-to-Sarvam/`, verify readback and the single-file commit scope, then stop after Round 146.
