# Sutram ROUND 134 — keep the region block; reject the one-scope-check safety claim

**Date:** 29 October 2026. **Pinned source:** `2553ee4354a6a965c4390d615f441a6fb6eb122b`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-134.md`, blob `d4eee603c50767c3083e7fd3856ab4af7678b9a7`.
**Returned here:** `ChatGPT-to-Sarvam/ROUND-134-KSHETRA-REVIEW.md`. Documentation only; no compiler/library edits.

## Verdict

**The explicit `kshetra` block is a defensible lifetime construct. Its proposed safety rule is not complete. None of the three escape families in the brief is generally caught by checking the declaration scope of an assignment's variable.** A direct store whose base is visibly an outer variable can be rejected, but a local alias defeats that syntactic shortcut.

A block can remove the obligation to remember mark/rewind calls. It cannot remove the obligation to prove that no usable reference survives reclamation. The repair is a deliberately restricted, conservative region-provenance and call-effect check, plus cleanup on every control-flow edge leaving a region. That is escape analysis, even if considerably smaller than a full ownership/borrow checker.

**Correction/clarification to my Round 133:** automatic cleanup is not inherently unsafe. Automatic reclamation of arbitrary existing function allocations is unsafe without an escape/lifetime contract. An explicit opt-in block with an enforced contract and correct exit lowering is a materially better proposal. Its specified cleanup is the visible construct's semantics, not an undisclosed source-level action. I do not insist on manual mark calls when the compiler can enforce that contract. [R1, R2]

### Evidence boundaries

- **Repository evidence:** pinned source excerpts listed in section 10, including actual retaining stores in `suchi`, raw stores in `mala`, indirect-call dispatch, and the direct return emitted by `prasar`.
- **Brief-reported measurements:** the five-party timing results, 313/322 allocation-site classification, 16 TiB reservation experiment, and executable-size comparison. I did not rerun or independently establish those numbers.
- **External verification:** Linux kernel/man-pages documentation, Microsoft API documentation, and an original Sanskrit dictionary scan, cited separately as W1–W6.
- **Proposals/inferences:** all revised rules, code sketches, instruction estimates and tests below. None is an implemented or executed `kshetra` feature.

## 1. The three known escapes — exactly what the rule misses

| Escape in the brief | Caught by the rule as written? | Missing information |
|---|---|---|
| Pass a region pointer to a function that stores it | **Not generally.** The call is not an assignment to an outer variable in the caller's AST. A scalar return does not imply non-retention. | A verified effect summary: which argument may be retained, returned, or stored through another argument. |
| Store through a pointer that refers outside | **Not generally.** `outer[0] = p` might be caught by special-casing its visible base, but `vitti local = outer; local[0] = p` has an inner-declared base. | Provenance and lifetime of the destination storage, not the local variable holding its address. |
| Return a region pointer from the enclosing function | **No.** `nivartanam p` has no assignment to an outer variable. | Return-value provenance, including slices, wrappers and aggregate fields. |

**Score: 0/3 escape families are generally prevented by the proposed declaration-scope rule.** This does not mean every spelling of every store evades it; it means each family has a counterexample the rule does not cover.

### A. The retaining call already exists in the library

`lib/suchi.smlib:87–96` copies its second argument into `val`, obtains the backing array through `lst[2]`, and performs `d[lst[0]] = val`. `suchi_khip` returns an integer success flag, but the passed value remains in the caller-owned list. This is direct body evidence, not speculation about a foreign library. [R3]

```sutram
# PROPOSED negative test; kshetra syntax is under review, NOT RUN.
yoj suchi
mukhya() {
    vitti l = suchi_srij(2)
    kshetra {
        vitti p = nirmmita(64)
        suchi_khip(l, p)   # Must be rejected: l retains p after this block.
    }
}
```

The compiler must distinguish this from a verified synchronous consumer that reads bytes and retains no address. Rejecting every pointer argument is conservative, but would reject many useful programs; accepting every call is unsound.

### B. The variable's scope is not the allocation's lifetime

```sutram
# PROPOSED negative test, NOT RUN.
mukhya() {
    vitti dst = nirmmita(8)
    kshetra {
        vitti local = dst
        vitti p = nirmmita(64)
        local[0] = p       # local is inner; its destination storage is outer.
    }
}
```

The same hole exists for fields and aliases of arrays. `lib/mala.smlib:20–25` demonstrates a real wrapper around the raw write primitive: `likh8(a + j * 8, v)`. Looking only for `AST_ASSIGN` would miss a retaining write expressed as a builtin call. [R4]

### C. Return is an escape without assignment

```sutram
# PROPOSED negative test, NOT RUN.
prakriya nava() {
    kshetra {
        nivartanam nirmmita(64)   # Must be rejected.
    }
}
```

Evaluate-and-return of an ordinary numeric value copied from the region is different: it may be valid, provided evaluation finishes before cleanup. A returned address, or an aggregate containing it, is not valid.

### Additional channels beyond the simple examples

**Derived scalar representations:** `p + 8`, arithmetic/bit transformations of an address, and bytewise copying can erase a naive 'this variable was initialized by nirmmita' marker. **Aggregate carriers:** a slice or header can hide a region pointer even when the outer container itself is older. **Opaque effects:** an indirect call, foreign call, callback registration, or `yantra` can retain or reconstruct an address without an ordinary checked assignment. The compiler already has both indirect and foreign call paths. [R5]

These are not all mathematically distinct escape mechanisms; they are additional language forms a real checker must handle. A fourth spelling is not the important result: the rule must cover all ways of retaining access, not an enumerated list of three syntax patterns.

## 2. A replacement rule small enough to stage, but accurately named

**Proposed invariant:** a reference to an allocation owned by region R may be stored only in a place whose usable lifetime is contained within R. No result, retained argument, stored pointer, slice or other reachable carrier may give access to that allocation after R exits.

The allocation's owning region and the destination object's lifetime matter. Lexical declaration scope is only one source of evidence.

A conservative first implementation should carry compile-time region provenance through values and aliases, track destination storage origins, merge possible origins at branches, and reject a use when the necessary relation cannot be established. Loop-carried values require a sound join/fixed-point rule or a deliberately restrictive rejection rule; a single recursive AST visit is not automatically sufficient.

| Operation | Proposed checked-region rule |
|---|---|
| Copy a region pointer into a same-region/deeper local | Allow, retaining the region identity. |
| Use an outer pointer inside an inner region | Allow a borrow of the existing storage; do not transfer ownership. |
| Store an inner pointer in an outer variable, field, array or collection | Reject, including through aliases. |
| Return a pointer owned by a region being exited | Reject; propagate provenance through returned carriers. |
| Pass a region pointer to a direct function | Allow only with a verified non-retention/effect contract appropriate to that argument and the destination arguments. |
| Call an unknown indirect/foreign target with a region pointer | Reject in the checked subset until an enforceable/trusted contract exists. |
| Convert a region pointer into an ordinary integer or forge a pointer from integers | Reject in the checked subset; merely dropping a provenance label is not an escape check. |
| Use a raw memory write/copy or inline assembly whose effect cannot be proved | Reject in the checked subset, rather than silently treating it as safe. |

**No full Rust-style ownership system is implied:** multiple aliases within the permitted lifetime can be allowed. But provenance, retention effects and lifetime containment are still required. In this raw-cell language, unknown contents must remain unknown; a copied cell cannot be declared harmless merely because its source variable is called an integer.

A restricted safe subset can coexist with unchanged legacy code outside the block. Its guarantee is not language-wide memory safety, not a sandbox against arbitrary raw-memory corruption, and not proof of array bounds. Existing unchecked code must not be accepted as a safe region consumer just because it compiles today.

**Diagnostic proposal:** report both the region allocation/origin and the retaining use, with source lines. Distinguish 'proven escaping reference' from 'callee effect unknown; not permitted in checked region'. A parser error on the new keyword does not count as passing an escape-rejection test.

## 3. Nested blocks, non-local exits, and emitted-code placement

### Nested access is not itself the problem

Outer storage can be read or updated with ordinary scalar data while an inner region is live. Ending the inner region rewinds to its own entry mark and must leave outer allocations intact. Assigning an inner allocation into an outer-owned object is different and must be rejected.

With a single shared bump arena, allocate only into the innermost active region in the first version. Allocating something notionally owned by the outer region *after the inner mark* and then rewinding that mark would reclaim it anyway. Supporting that operation requires separate region storage or another explicit mechanism, not just a different tag.

Lexically nested blocks are properly nested lifetimes. Truly interleaved lifetimes are not represented by a single LIFO cursor. The new block construct should not promise arbitrary interleaving, promotion or a second independent allocation stream.

### `nivartanam` is allowed only with cleanup and a valid result

A function return from inside a region is not inherently a leak. It becomes a leak when the compiler emits the return without the specified cleanup. Evaluate the return expression first, reject escaping references, preserve the result/status registers, rewind the regions actually exited, then return. Do not read the returned value through reclaimed storage afterward.

The compiler must identify the scopes crossed by every control-flow edge:

| Edge | Cleanup required |
|---|---|
| Ordinary end of region block | Its own mark. |
| `nivartanam` from the enclosing function | All active regions owned by that function activation, not caller-owned regions. |
| `krama` to a loop exit outside the region | Every region crossed before reaching that target. |
| `agrim` to a loop continuation outside the region | Every region crossed before reaching that target. |
| Break/continue of a loop wholly inside the same region | **Do not rewind the surrounding still-live region.** |
| Failure propagation returning from a function | Same cleanup as an early return; preserve failure value/status. |
| Handled failure that remains inside the region | No premature rewind of that region; clean up only scopes actually exited. |
| Actual process termination | OS reclamation ends the process lifetime; this is not a reusable-region continuation. |

**Concrete extra exit found in the source:** `src/r25_phal.inc`, label `r25_gen_prasar`, emits its own function epilogue and `ret` on failure. It does not merely delegate to the ordinary `AST_RETURN` statement. It uses RAX for the result/error and RDX for status. Updating only ordinary `nivartanam` emission would miss this route. The same include implements `yadi dosh` handling, which may continue instead of exiting. [R6]

**Patch-width consequence:** the existing `prasar` path patches a short conditional branch and checks its distance against 127. Adding cleanup can exceed that displacement. Either retain the bound and diagnose it, or widen/re-encode the branch; do not truncate the offset. The no-region path should retain its old encoding where byte-identical output is required. [R6]

### Lowering algorithm — proposal, not implemented code

1. Give each active region a unique identity and a mark slot in the current function's generated stack frame. A single global saved mark is insufficient for nesting or recursion.
2. Record the region-stack identities at branch destinations and at the function boundary. Depth alone is not enough for unrelated sibling scopes.
3. On an edge from scope stack S to target stack T, require T to be the appropriate enclosing prefix; never permit a jump into a region without its initialization.
4. Emit cleanup for the suffix of S being exited, inner to outer. Then emit the existing jump/return.
5. Allocate frame slots and patch branch destinations using the final layout. Preserve live return values, RAX/RDX status pairs, and the applicable float/ABI registers.

With one arena and only cursor restoration, a proven optimization can collapse several rewinds to the outermost exited mark. Do not generalize that optimization to independent arenas, clearing, decommit, or other cleanup actions.

### Cost is not universally 'two instructions'

For a memory-resident cursor and a frame-resident mark, a straightforward sequence is:

```asm
; CONCEPTUAL emitted code; scratch register/frame allocation not specified here.
; Entry:
mov r11, [rel arena_cursor]
mov [rbp - mark_slot], r11
; Exit:
mov r11, [rbp - mark_slot]
mov [rel arena_cursor], r11
```

That is two instructions at entry and two at exit, excluding frame setup, spills and control transfer. A dedicated cursor register can reduce some operations, but imposes ABI/register-pressure costs. This is a count of the shown sketch, not measured performance or a completed emitter.

Checked allocation separately needs size/overflow/alignment/capacity checks and cursor update. Zero initialization adds work proportional to bytes cleared. Page faults and Windows commitment are not part of a four-instruction bump. Runtime checkpoint stacks are unnecessary for syntactically nested regions if marks are activation-local and exits are compiled correctly; compile-time nesting limits must still be checked.

## 4. Define which allocations the block owns before implementing it

The brief says both 'where the allocation is written is its lifetime' and '`nirmmita` never changes'. These can coexist only as an explicit opt-in contextual rule, not as a claim that every invocation of the same spelling has identical semantics.

**Recommended first policy:** a direct `nirmmita` written within a checked `kshetra` uses that lexical region; a call written outside any region retains its existing backend and lifetime. Ordinary called functions do not silently inherit a different allocator from a global ambient variable.

Under that policy, calling existing `mala_nava` from a region still invokes the legacy allocation written in `lib/mala.smlib:8–16`. It does not become scratch merely because the caller is in a block. Likewise, `suchi_srij` creates a returned header with a separately allocated backing store, and `suchi_vardh` stores new storage into caller-held metadata. [R3, R4]

This lexical policy preserves understandable call contracts but means that wrapping arbitrary request handling in a region does **not** prove the whole request leaks nothing. Legacy allocations made by helpers, growing persistent containers, file handles and other resources are not reclaimed by resetting one cursor. The 313/322 classification in the brief is not proof of all call effects; its 'released inside one function' wording must not be mistaken for observed deallocation in the existing allocator.

If allocator-aware helpers are needed, add an explicit destination/workspace parameter or a specified separately compiled region-aware variant. This is a later interface decision; it must not be hidden dynamic rebinding of existing functions.

**Implicit allocations require a decision too:** `mala`, `kosh`, growth operations and helpers synthesize allocations. In a minimal first checked subset, reject allocating forms without specified region-aware lowering/effects. Do not quietly send them to a fallback heap and then claim bounded request memory. Later support must preserve their layouts, bounds, alias and OOM behavior.

**Zeroing:** resetting the cursor does not erase bytes. Reusing the spelling `nirmmita` while returning uncleared scratch would change its current fresh-zeroed behavior. Preserve zero initialization, or introduce a separately specified uninitialized operation; do not silently change this contract to reach a benchmark number. The cost belongs in the measurements. [R2, W1, W3]

**Compatibility gates:** programs containing no region constructs should keep the old allocator/code-generation path. Do not reserve `kshetra` globally in a way that breaks an existing identifier of that name; prefer an unambiguous contextual construct and test it. Emit new image state only where required by the new feature if exact legacy binary identity is the gate. Separate/object mode needs compatible region/effect metadata or an explicit unsupported-mode diagnostic.

The existing `kosh` abandoned-growth-block problem is not automatically fixed by this change. Do not insert `munmap(old)` solely because a scope exists; surviving aliases and backing-store ownership remain relevant. Region-scoped collections can eventually reclaim all their obsolete blocks at region exit, but only with complete provenance and a documented policy, not by relabeling existing allocations. [R2, R3]

## 5. Capacity, exhaustion, and Windows — one language contract, different OS mechanisms

### 5.1 Choose a budget, not '16 TiB because it mapped once'

A successful huge reservation on one host is not a portable resource guarantee. Use a configurable bounded arena, report its actual limit, and distinguish virtual reservation, committed backing, resident pages and allocator-used bytes. A fixed `.bss` pool remains viable for a bounded profile; the measured small file size does not establish zero loader, address-space or first-touch cost. [R1]

Do not make 16 TiB the v1 default. Its suitability depends on the target's address space, resource limits, fragmentation, process layout and policy. The important language property is checked exhaustion and an explicit budget, not the largest reservation a demonstration can obtain.

### 5.2 Exhaustion must not silently change lifetime or allocation policy

**Recommendation:** for a raw region allocation that exceeds its budget or has invalid/overflowing size, return 0 without changing the cursor. Require declaration/growth lowering to check that result before writing any header. A trap-on-failure variant would need its own specified contract. Never silently fall back to a durable `mmap` allocation: that defeats bounded memory, predictable costs and uniform lifetime semantics.

For an aligned bump, validate positive size and overflow before rounding; compare against remaining bytes before pointer addition. Failure must leave region state intact. Decide zero-byte behavior explicitly instead of inheriting an accidental cursor alias. These are implementation requirements, not tests already passed.

### 5.3 Linux facts versus policy inference

For Linux writable anonymous mappings, `MAP_NORESERVE` omits swap reservation and may defer failure until a write; the man-page warns of a possible SIGSEGV and of OOM process termination. Kernel overcommit mode 2 ignores the flag. Thus a successful reservation is not a guarantee that all later touches can be converted into a clean allocator error. [W1, W2]

**Inference for this design:** prefer a modest explicit budget and state the OS-pressure limitation. Optional initialization/pre-touch can move some faults and latency earlier, but is not a general promise against later system OOM. No universal cycle guarantee follows from a warmed bump benchmark.

### 5.4 Windows is not the same contract at the API level

`MEM_RESERVE` reserves addresses, not accessible storage. A reserved page cannot be read or written until committed. `MEM_COMMIT` accounts backing resources; physical pages are ordinarily supplied on first access, and `VirtualAlloc` can return NULL on failure. [W3, W4]

Therefore reserve-only Windows memory resembles an inaccessible address reservation, not Linux **writable** anonymous memory with `MAP_NORESERVE`. Using `MEM_RESERVE` and then treating a bump pointer as writable would fault before the intended workload works. Similar-looking reservations do not have identical failure semantics under memory pressure.

**Proposed bounded Windows profile:** reserve and commit a configurable finite budget during explicit initialization, then allocate within it without per-object API calls. Alternatively, track a committed frontier and explicitly commit page-aligned chunks before handing out pointers; that adds a documented slow path and must roll back allocation state on failure. Do not silently describe the second profile as syscall-free. Choose and benchmark a profile rather than mixing the two.

A cursor rewind alone returns no commit charge to Windows. Decommit and release are separate operations: decommit returns pages to the reserved state; full release requires the original reservation base and zero length for `MEM_RELEASE`. Keep page-reclaim policy separate from per-block cursor rewind. [W5]

### 5.5 What can honestly fail cleanly?

| Condition | Proposed outcome / limitation |
|---|---|
| Logical arena budget exhausted | Synchronous 0 result; cursor unchanged. |
| Invalid size or arithmetic overflow | Reject/return 0 before cursor mutation or header writes. |
| Explicit Windows commit fails | Synchronous failure; do not return an uncommitted pointer. |
| Initial OS reservation fails | Initialization failure before entering usable region code. |
| Linux deferred backing failure/global OOM | May be a signal or process kill; not covered by a promise of clean region-allocation failure. |
| Use of a stale pointer after rewind | Must be prevented in the checked subset; rewind alone neither detects it nor reliably traps. |

## 6. Is another existing construct a better lifetime boundary?

| Construct | Fit for Sutram |
|---|---|
| **Explicit block** | Best default for local/request/iteration scratch: narrow, nestable, and chosen by the programmer. Still requires the checks above. |
| Function call | Good for a verified non-escaping scratch helper, but wrong as an implicit lifetime for constructors returning memory or mutating caller-owned storage. `mala_nava` and `suchi_vardh` are concrete counterexamples. [R3, R4] |
| Loop iteration | Useful placement of an explicit block; unsuitable as a universal implicit reset because values and collections can intentionally survive iterations. |
| Struct/object | Represents an owning object graph only after ownership of fields and aliases is specified; today's raw fields do not supply that contract. |
| Module/process | Useful for caches or pools, but far too long-lived to reclaim per-request scratch. |

**Different structural alternative using existing functions:** caller-owned workspace plus output parameters. Allocate a bounded workspace once, pass it to helpers that neither retain it nor return references into expired portions, and reuse it at a visibly controlled point. This suits formatting/sorting work and avoids ambient allocator changes. It is not a magical safety substitute: helper effects and retained references still need a contract.

**My choice:** keep `kshetra` as the surface construct, and use explicit workspaces for interoperation where a region-safe call contract cannot yet be expressed. Do not make every function, loop, struct or module implicitly own everything allocated while it executes.

## 7. The two deciding tests need exact shapes and a larger rejection suite

All tests below are **proposed and NOT RUN**. They are acceptance criteria for a future implementation, not claims about today's compiler.

### Test A: put the block INSIDE the loop

```sutram
# PROPOSED test shape; check each pointer before touching it.
mukhya() {
    vitti i = 0
    yavat (i < 1000000) {
        kshetra {
            vitti p = nirmmita(64)
            # fail explicitly if p == 0; then write/read allocated bytes
            p[0] = i
            # accumulate an ordinary scalar checksum before region exit
        }
        i = i + 1
    }
}
```

The expected allocator-used high-water is bounded by the maximum simultaneously live iteration allocations, including alignment/metadata, not by the iteration count. Record the cursor before and after every exit and check a value-dependent checksum so the work cannot disappear. Measure mapped/reserved bytes, committed bytes where available, RSS/working set, faults and allocation-call counts separately.

**Opposite nesting is different:** one `kshetra` surrounding a loop of one million allocations has one lifetime and retains all those allocations until that block exits. A bump allocator cannot infer that each allocation has become dead merely because the loop advanced. This test should accumulate or hit its configured capacity, not pretend to have iteration-scoped reclamation.

The brief's approximately 4 GB baseline is consistent with one million independently touched 4 KiB pages: 4,096,000,000 bytes. That is a conditional arithmetic explanation, not a measurement here or a universal RSS figure for untouched mappings. A region implementation with a fixed 64 MiB reservation may show that reserved size while touching much less; 'a few megabytes' must specify which metric. [W1, R1]

### Test B: reject the retaining use, not just the new syntax

The outer-variable assignment test needs a successful positive region test first. Then verify an escape-specific diagnostic and source line. A compiler that rejects every `kshetra` token has not implemented a safe region construct.

### Additional acceptance matrix

| ID | Case | Required result |
|---|---|---|
| K01 | Direct region pointer assigned to outer variable | Compile-time escape diagnostic. |
| K02 | `suchi_khip(outer_list, region_pointer)` | Reject retained pointer or reject unsupported effect; never silently accept. |
| K03 | Local alias of outer storage receives region pointer | Reject based on storage origin. |
| K04 | `nivartanam` returns region pointer | Reject. |
| K05 | Returned/stored slice or wrapper carries region pointer | Reject transitively. |
| K06 | `likh8(outer_address, region_pointer)` | Reject retaining raw write or unsupported operation. |
| K07 | Arithmetic/bitwise disguise of pointer | Preserve dependency or reject operation; no provenance laundering. |
| K08 | Unknown indirect/FFI/assembly consumer | Reject in checked subset unless contract is established. |
| K09 | Read scalar from region, copy scalar outward | Accept when it is an actual value, not a disguised pointer. |
| K10 | Outer allocation used in inner block | Accept; remains valid after inner rewind. |
| K11 | Inner pointer stored in outer region allocation | Reject. |
| K12 | Nested normal exits | Rewind inner then outer; correct activation-local marks. |
| K13 | Early scalar return from nested regions | Correct result and complete cleanup. |
| K14 | Break to outside region | Cleanup exactly the exited scopes. |
| K15 | Continue to outside region | Cleanup before next iteration. |
| K16 | Break/continue in inner loop that stays in region | Do not reset the still-live outer region. |
| K17 | `prasar` propagates failure | Cleanup and preserved RAX/RDX result/status; valid branch encoding. |
| K18 | Locally handled `dosh` continues inside region | No premature cleanup. |
| K19 | Recursion/reentrant nested calls in supported model | Distinct mark storage per activation; no global saved-mark overwrite. |
| K20 | Exact capacity, oversize, negative and wrapping sizes | Correct boundary behavior; failure leaves cursor unchanged. |
| K21 | Reset and reallocate | Zeroing matches specified `nirmmita` contract; stale-reference uses rejected. |
| K22 | One region per iteration, one million iterations | Bounded allocator high-water and correct checksum. |
| K23 | One region outside the allocation loop | Accumulation/capacity failure, not fictitious per-iteration cleanup. |
| K24 | Windows reserve-only/commit-failure probes | No pointer returned for inaccessible/uncommitted memory. |
| K25 | Legacy source, including identifier `kshetra` | Existing accepted programs preserved; default guard unchanged. |
| K26 | Implicit `mala`/`kosh` and allocating helpers | Documented lowering/effects or explicit unsupported diagnostic, no silent heap fallback. |
| K27 | Object/separate compilation and opaque callees | Verified effect metadata or explicit rejection; no duplicate ambient arenas. |
| K28 | Region nested beneath a caller-owned region | Callee cleanup preserves caller allocations and result registers. |

Also retain the project's existing regression/proof/guard gates. Their historical counts are not results produced in this round.

## 8. Is `kshetra` the right Sanskrit word for a block?

**Keep it for a memory-region block.** The original Benfey dictionary entry on page 240 gives `kṣetra` senses including field, place and extent. That supports the region metaphor; it does not assert compiler visibility, automatic cleanup or no-escape semantics. I inspected the page image, not only extracted text. [W6]

The construct can be a *block syntactically* and a *region semantically*. It need not rename every generic block or lexical scope in the language. A normal conditional block can delimit variable visibility without owning storage. Teach that distinction explicitly.

I have not established a uniquely better single Sanskrit technical word for all compiler scope meanings in this round. There is no reason to replace the already-reviewed region term merely because braces or indentation delimit its lifetime. Spelling and lexer compatibility still need tests; linguistic approval is not implementation approval.

## 9. Final answers to the seven questions

1. **Scope completeness:** incomplete; none of the three escape families is generally prevented by the stated rule. Destination-storage provenance, returns and retaining calls must be covered.
2. **Nesting/returns:** outer borrowing is valid; inner-to-outer retention is not. Allow returns only with valid results and cleanup of the scopes actually exited.
3. **Code cost:** mark/restore is cheap but not necessarily one instruction each. Cleanup belongs on control-flow edges, including the source's separate `prasar` epilogue; preserve status and patch ranges.
4. **Range/exhaustion:** bounded configurable budget; no default 16 TiB bet and no silent `mmap` fallback. Logical OOM can be clean; arbitrary OS pressure cannot be universally promised clean.
5. **Windows:** reserve-only is not writable. Commit before use, handle commit failure, and distinguish rewind from decommit/release.
6. **Other structure:** explicit blocks remain the best fit; caller-supplied workspace is a useful existing-construct alternative, not a substitute for retention contracts.
7. **Framing:** the block idea is not wrong. The claim that lexical assignment checking alone proves lifetime safety is wrong. Structural cleanup and reference escape prevention are two different obligations.

**Integration recommendation: conditional design approval, implementation HOLD until the restricted safe subset, call effects, allocation routing, zeroing and exit policy are written down.** This report supplies a candidate policy and test matrix, not evidence that those gates already pass.

## 10. Sources, readback and execution status

### Pinned repository sources

All paths below were read at `2553ee4354a6a965c4390d615f441a6fb6eb122b`.

- **R1:** `Sarvam-to-ChatGPT/ROUND-134.md`, blob `d4eee603c50767c3083e7fd3856ab4af7678b9a7`: proposed block, scope rule, seven questions and reported measurements.
- **R2:** `ChatGPT-to-Sarvam/ROUND-133-MEMORY-DESIGN.md`, blob `a67a16df09bd454f6699c6e35e55131ebec6d0fa`: previous returned design; its opening was re-read to clarify the earlier automatic-release objection.
- **R3:** `lib/suchi.smlib:46–100`, blob `a6834561bf086f163c933bf18afe9e7d310eaec3`: returned list graph, replacement backing pointer stored into caller-held header, and retaining append.
- **R4:** `lib/mala.smlib:1–33`, blob `de4e247aeb862e0f8986ce04de47b08aac417fe4`: raw allocation factory and raw memory store/load wrappers.
- **R5:** `src/sutram_compiler.asm:12400–12665,12670–12815`, blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`: statement dispatch, return/break/continue/handler/assembly kinds, direct/indirect/foreign call handling.
- **R6:** `src/r25_phal.inc:1–330`, blob `a36bd286aa6beea0b854576945e6874ba8835af0`: return status, direct failure-return epilogue, short-branch limit, and handled failure machinery. Its historical comments use the legacy spelling `prati`; this report uses canonical `nivartanam` for new examples.
- Repository instructions: `AGENTS.md`, `Sarvam-to-ChatGPT/READ-FIRST.md`, the current Project Master opening and design-charter material. Sanskrit-only scope and documentation-only return path retained.

This is a targeted audit, not a fresh exhaustive re-audit of all library functions or allocation sites. Search returning no indexed hit was not treated as proof of absence.

### External primary references checked 29 October 2026

- **W1 — Linux man-pages, mmap(2):** https://man7.org/linux/man-pages/man2/mmap.2.html — anonymous mappings, page alignment, MAP_NORESERVE, deferred faults and OOM limitations.
- **W2 — Linux kernel, Overcommit Accounting:** https://www.kernel.org/doc/html/latest/mm/overcommit-accounting.html — policy modes, accounting, MAP_NORESERVE ignored in mode 2.
- **W3 — Microsoft, VirtualAlloc:** https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc — reserve/commit distinction, initial zero contents, page sizing and NULL failure.
- **W4 — Microsoft, Page State:** https://learn.microsoft.com/en-us/windows/win32/memory/page-state — reserved memory is inaccessible; committed memory and first access.
- **W5 — Microsoft, VirtualFree:** https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualfree — decommit versus release and base/size requirements.
- **W6 — Benfey Sanskrit-English Dictionary, original page 240, Cologne scan:** https://www.sanskrit-lexicon.uni-koeln.de/scans/BENScan/BENScanpdf/ben-0240.pdf — `kṣetra`; page image inspected.

### Status

- **Completed:** source-grounded critique, three-case verdict, nested-exit lowering proposal, platform distinctions, terminology answer, and 28 proposed acceptance cases.
- **NOT RUN:** Sutram compilation, Linux/Windows execution, region escape tests, million-iteration benchmark, regression suite and binary-identity guard. This was a read-side round; no toolchain was invoked.
- **Not claimed:** a sound checker has been implemented; exact instruction/cycle results have been measured; the brief's census/benchmarks were independently reproduced.
- **NOT APPLIED:** compiler/library/test/doc-source edits, new language keywords, frozen pack changes, workflow changes, or changes to `Windows-to-Sarvam/` or backups.
- **Delivery:** one new Markdown handoff under `ChatGPT-to-Sarvam/`. Verify the uploaded file/commit by readback before reporting return completion, then stop after this round.
