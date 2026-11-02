# R170 — bounded regions, stable objects, and generation-checked references

**Design review, not implementation. 2026-11-02.**
Repository base: `cee703cb156764c2771cc5ebec73c2dfa9eab60f` (incoming brief identifies compiler v283).
Deliverable for Sarvam; Sanskrit is the sole active language. This round changes only this report and its checksum under `ChatGPT-to-Sarvam/`.

## Decision in one paragraph

Use **lexically owned, budgeted regions containing stable object descriptors and typed generation-checked handles**. Regions own storage; handles are non-owning references. A collection grows by replacing its private backing storage behind its stable descriptor, so aliases follow the same object. Free/reset invalidates identities before storage can be reused. Every safe access validates identity, lifetime, type and bounds; stores of references enforce an outlives rule. This closes the four *safety and reclamation mechanisms* within a new checked subset. It does not collect unreachable objects in a still-live region, make infinite live data fit finite memory, or make existing raw-pointer programs safe. Start with the much smaller fail-closed budget experiment; do not promise the full design in 200 lines.

## 0. Evidence and corrections before designing

### What was and was not executed here

- Read the current allocator include, relevant parser/emitter/lifetime code, language reference §19, memory decision documents, known escape fixture, R170 assignment, and vocabulary rule.
- `command -v nasm` returned exit 1 and no path in this environment.
- **Compiler build, emitted-program tests, full suite, allocator benchmarks, RSS measurement, Windows execution, installer and GUI: NOT RUN — no toolchain/native test environment established here.**
- The brief's 164 ms versus 40 ms is **Sarvam-reported timing**: ratio 4.1 for those runs. I did not reproduce it; no distribution, fairness analysis or RSS result follows from two timings.
- All costs and source-line estimates below are **design estimates**, not disassembly counts, performance results or implementation commitments.
- The latest changes since our R169 return are three assignment documents, not a memory implementation.

### Four distinctions that prevent another false conclusion

1. **No external runtime dependency is feasible; literally no runtime work is not.** Allocation, zeroing, descriptor lookup and generation checks execute when the program runs. Emit them into the native executable or include project-owned NASM helpers. No tracing collector, VM, background service, C library or separately installed runtime is required. Calling this “no runtime code” would be false. It fits PROJECT-MASTER's clarified *no runtime dependency* rule.

2. **“No reuse” is not a description of every current path.** In `src/r65_arena.inc`, `r73_gen_rewind` restores the saved scratch cursor; scratch allocation explicitly zeros reused bytes. The distinction is:
   - one mandapa surrounding an allocating loop: the mark is restored only after the whole loop;
   - a mandapa entered/exited each iteration: the scratch cursor is restored each iteration.
   `tests/r72_mandapa/loop_with.sm` is the first shape, not evidence for the second.
   This is source evidence, not a new RSS measurement.

3. **A 1 GiB reservation is not a whole-program hard limit.** The persistent path in `r65_emit_nirm` falls back to `r38_nirm_mmap` on insufficient arena space or failed reservation. The fallback can allocate outside the field. `r65_active` excludes PE and GUARD_PAGES; its actual implementation allows ELF object/separate mode despite older comments at the top of the include. Do not infer Windows behavior from ELF.

4. **Existing docs disagree on what was measured.** Reference §19 records historical v270/v271 RSS values, while R170 explicitly says its new RSS attempt failed. Keep the old values labelled historical/unreproduced; do not promote them to current acceptance or erase them. A zero from failed sampling is not zero RSS. `MEMORY-DECISION.md` also retains an old K0 “no kosh” table, while current §19 and R82 code allow some kosh-in-block behavior. Source and dated evidence must take precedence over stale scope summaries.

Current R82 code retains collection headers, uses a stack liveness slot and an `rdtsc | 1` generation, and checks typed kosh parameters. It is not a universal checked-handle system. A timestamp is not a proof of unique generations, and reading metadata through an address into freed storage would not become safe merely by adding a comparison. The proposal below changes both facts.

## WS1. One coherent model

### 1. Safety boundary and migration

Introduce a **versioned checked-memory profile**, initially opt-in. Keep the accepted legacy raw-address ABI unchanged until a deliberate migration is approved. In the new profile:

- A reference has a distinct type and cannot be silently stored in a numeric `vitti`, cast to an integer, reconstructed from an integer, or hidden by untyped byte copying.
- Function arguments/results, struct fields and collections preserve reference types. A collection of references has reference-width cells; it is not the existing eight-byte numeric kosh with extra assumptions.
- Typed reference copies copy identity, not ownership and not data.
- Raw-address operations, `yantra`, unverified FFI and untyped legacy calls are outside this guarantee. Initially reject these crossings in the checked profile. A later explicit unsafe bridge must specify copy-in/out or a pinned non-escaping borrow.
- No moving/releasing an object while an unsafe pinned borrow is active. Reentrant callbacks and foreign retention must be forbidden unless separately designed.
- One execution thread initially. Concurrency, signal-handler reentry and atomic reclamation are not covered.

Without these representation and call-boundary changes, a function can launder a scratch address through an integer and defeat any local escape checker. A generation field appended to today's raw buffer alone does not close gap 4.

### 2. Identity, ownership and data

**Region ownership:** every region has one lexical owner. Nested region owners form a tree. Explicit reset/release is rejected while a child owner remains active; structured exit closes children first. Normal exit, return, break, continue and propagated language errors close exactly the regions crossed, innermost first. An explicit release is an operation on the owner and must leave the lexical cleanup idempotent; a second explicit release is diagnosed. Fatal process termination need not unwind; the OS cleans process mappings. External resources such as files are not automatically handled by this memory design.

**Reference:** four 64-bit words, **32 bytes**:
`(object_slot, object_generation, byte_offset, view_extent)`.
These are a proposed representation, not a public ABI. Handles can be copied but not constructed by user arithmetic. A slice derives a narrower offset/extent through a checked operation.

**Stable object descriptor:** proposed **96 bytes** = twelve qwords:
generation, region slot, region generation, data base, allocated bytes, logical length, logical capacity, element/type tag, flags/state, allocator class, next-owned slot, previous-owned slot.
Two linkage fields support deterministic region cleanup; unused fields in scalar buffers are the explicit cost of a simple first implementation.

**Region descriptor:** budget **96 bytes initially** for generation/state, parent identity, budget/accounting, ownership and allocator bookkeeping. Final layout needs a separate ABI review. Object/region tables are trusted metadata, outside user-accessible buffers. Metadata is charged to the memory budget.

Use fixed-capacity or bounded segmented tables. Validate a slot index before indexing; do not treat the handle's slot as a pointer. Table storage stays allocated while stale handles could exist. Reuse slots with changed generations rather than append a descriptor for every historical allocation forever. A bounded table can fill and must fail cleanly. Metadata high-water retention is a documented bound, not zero overhead.

Both object and region generations are monotonically advanced for new lifetimes. At the maximum representable generation, **retire the slot rather than wrap**; inability to allocate another slot is an ordinary bounded failure. Use no random generation and no clock uniqueness assumption. Recreating a lexical block, recursive entry and reusing the same table slot all receive different live identities. Never put the only validation metadata in the reclaimed payload or a vanished stack frame.

### 3. Access and reference-store rules

For each safe read/write:

1. Check object slot range, live state and object generation.
2. Check region slot range, live state and its generation against the descriptor.
3. Check expected type, alignment and permissions. The checker must also prevent reads of uninitialized handle fields; zero-filled handle slots represent a defined null handle, never a live object.
4. Check view offset/extent within the *current* logical object bounds and operation offset/width within the view. Use subtraction-based checks after nonnegative validation; never unchecked `offset + length` or `index * stride`.
5. Resolve the current data base from the descriptor, then perform the access.

An object handle resolves current length/capacity. A saved slice additionally has its original view limit: later growth does not widen it implicitly; shrinking invalidates access beyond the new logical end. Arbitrary deletion/reordering means an index view follows the index, not a historical element identity. Do not promise stable element identity without element-level handles.

For storing a reference into another object or an outer binding, require the referenced region to be the **same as or a live ancestor of the destination region**. Regions in unrelated branches fail this test. An ancestor walk is O(depth), unless a checked identity/ancestry optimization is later proved. Equal lexical depth is not enough.

Apply the same rule at function return and assignment boundaries. A caller-region borrow may be returned to that caller; a reference to a callee-local region may not. Known valid cases can be proved statically; ambiguous cases need emitted validation, not an undocumented assumption. Closed handles fail before use/store. Nested typed containers repeat this rule on each reference-field write, including library calls.

This makes the known `adr(buf)` escape into an outer kosh either a type error or an outlives error, even through a helper. If an explicit early object release leaves copies behind, subsequent access still traps by generation; this is dynamic prevention of use-after-free, not a promise that all stale values are impossible.

Same-region cycles are allowed. Region exit frees the region's owned descriptors/buffers irrespective of reference cycles; it need not trace a reference graph. Unreachable objects in a long-lived open region remain until explicit object release/reset/exit. That is intentional region retention, and is why “nothing can leak” is not a valid claim.

### 4. Allocation, growth, release and reset

**Allocation:** validate size and alignment without overflow; charge data plus metadata and fragmentation to the region and its ancestors; acquire storage; zero user-visible bytes; initialize descriptor; publish the handle last. A zero-byte request returns a defined null handle; dereferencing it is diagnosed. Allocation failure must leave all counters, free lists and descriptors consistent. For the first version use a named fatal allocation diagnostic; recoverable allocation can follow only after an explicit failure-result contract exists.

**kosh growth:** preserve arbitrary logical capacities, including 3, 5 and 1,000,000. Internal allocator size classes may round physical storage, but must not silently change observable kosh capacity.

1. Validate the object handle and checked new-capacity arithmetic.
2. Reserve budget for old and new buffers to coexist.
3. Allocate/zero new backing storage, copy initialized elements.
4. Publish new base/capacity in the same stable descriptor.
5. Return old backing storage to this region's allocator.

All aliases resolve through that descriptor and immediately see the new object state. No raw data pointer is retained across the operation. Relocation does not increment object generation because the logical object still exists. Actual destruction/reuse does. OOM before publication preserves the old object and all aliases.

Use bounded segregated slabs or another specified free-block allocator for persistent/growable storage. Freed buffer bytes become allocatable again; a bare bump cursor would simply reintroduce the leak. Track actual block size/classes, not an assumed power-of-two kosh capacity. Fragmentation can still cause OOM despite enough aggregate free bytes; document it. Large mappings can be released separately. Count temporarily coexisting old/new storage and cached free blocks against the budget.

**Individual release:** only the region owner or an explicitly authorized owning operation may release an object; copied handles do not carry that authority. Mark descriptor dead and advance its generation before reclaiming payload. Invalidate any children owned by the operation under a defined order; ordinary reference elements are non-owning and do not recursively free their targets. Aliases become stale and deterministically fail.

**Region reset/exit:** invalidate region generation first; dispose of owned descriptors/buffers and unlink them; reset arena/slab state; mark closed or begin a fresh generation. Do not lazily reset only the data cursor while the descriptor table keeps growing. A straightforward implementation is O(number of owned objects + mapped chunks), not “two instructions” and not always constant time. A cached scratch slab can reset cheaply, but zeroing and metadata reclamation are still work.

Separate reuse from return-to-OS. Caching a bounded slab gives reuse without immediate RSS reduction. Releasing physical pages or mappings is a separate policy and needs separate Windows/Linux tests.

### 5. What closes each gap

| Gap | Mechanism | Remaining limit |
|---|---|---|
| Loop allocation grows with iteration count | Explicit finite budget, and per-work-unit reset/exit or explicit release for continuing work | A fixed budget without recycling must eventually refuse. All-live data cannot be kept in constant space. |
| Old kosh backing buffers retained after relocation | Descriptor-based identity plus return of old private backing storage to a bounded allocator | Growth has temporary old+new peak, zero/copy cost and fragmentation. |
| Aliases point at obsolete moved buffers | Every alias holds stable object identity and resolves the descriptor | Legacy raw aliases are incompatible; they cannot be retroactively repaired without representation changes. |
| Lexical escape check misses dynamic lifetime | Typed handles across calls/containers, runtime region identity/outlives barriers, generation check at access | Unsafe/raw/FFI paths are excluded; concurrency and complete ownership inference are deferred. |

### 6. Budget invariant

Let B include backing storage, descriptors, allocator metadata, retained free storage and temporary relocation storage for the selected region tree. At each operation maintain:

`charged_live + charged_cached_free + charged_metadata + charged_temporary <= B`.

Child reservation is charged to its parent; reject attempts to bypass a parent cap by opening more children. Separate root limits bound table slots and nesting. Stack, program image, OS page tables, foreign allocations and compiler process memory are outside a region-only B. Therefore B is not a promise that process RSS is exactly B. A process-wide bound needs separate controls on those components.

Reuse bounds memory by live/high-water demand, not by total historical operations. With no reference-count or tracing system, an open owner that never releases anything retains it until its budget is exhausted.

## Costs — estimates, not measurements

Assumptions: single-threaded x86-64, warm metadata, bounded tables already present, no static elimination, no OS slow path. Counts are rough emitted machine instructions, not cycles; an instruction such as REP can do size-dependent work. Cache misses and dependent loads can dominate.

| Operation | Estimated added work | Size-dependent/slow work |
|---|---|---|
| Scalar numeric local read/write | 0 memory-model checks | Normal generated code only |
| Checked object read | ~25–45 instructions for slot/liveness/generation/type/view checks and address resolution, then the load | Several dependent metadata loads; cache misses. |
| Checked scalar object write | ~25–45, then store | Same as read; no reference barrier for a number. |
| Store a handle in a container | ~45–80 fixed instructions plus ~5–10 per ancestry level | Validate both identities; copy four words. O(depth), not an unbounded scan of the heap. |
| Copy an already typed handle locally | Four word loads/stores, roughly ~8 if not kept in registers | No allocation and no reference counting. An outward assignment may also need an outlives check. |
| Allocate from a prepared free block/bump slab | ~50–120 control/bookkeeping instructions | Zero O(bytes); refill, table expansion and OS allocation are separate paths. |
| Grow a collection | ~60–150 control instructions beyond validation/allocation | Allocate + zero + copy O(length), release old block; transient old+new memory. |
| Release one object | ~20–60 fast-path instructions | Allocator coalescing or OS release may add work. |
| Exit/reset a region | ~10–30 fixed, then ~15–50 per descriptor/chunk | O(objects + chunks); potential OS calls. |

These ranges are a design budget to challenge by assembly inspection, not a benchmark prediction. Exact “instructions per allocation” is impossible without specifying size, fast/slow path and generated register allocation.

**Storage estimate:** 96 bytes per object descriptor + approximately 16 bytes allocator block metadata + 0–15 bytes alignment padding + payload capacity; **32 bytes per retained handle copy**; approximately 96 bytes per active/reusable region descriptor; plus bounded table/slab bookkeeping. For one 64-byte payload, one descriptor, one 16-byte allocator header and one stored handle, the subtotal is **208 bytes**, before padding/slab overhead. This is deliberately expensive for tiny objects. Descriptor slots are charged at metadata high-water, including free and retired slots. Reference-valued elements need 32 bytes each rather than today's 8-byte numeric cell. Do not advertise “only one generation word per object.”

Bounds/generation checks can be hoisted only across a proven no-release/no-reset/no-relocation interval. An unknown call breaks that proof. No fast “unchecked” option inside the advertised safe profile.

## WS2. Sanskrit naming — proposals, not added syntax

The actual rule is at `docs/vocabulary/VOCABULARY-RULE.md`, not the older top-level path quoted by the decision file. Retain kshetra as documentation terminology and mandapa as the existing block opener. Do not turn every implementation field into a keyword. Prefer existing constructs and diagnostics; any proposed new spelling needs owner/native-speaker review and collision checks.

The code fragments below are **illustrative future .sm syntax only, NOT accepted by v283 and NOT instructions for users to run**. `r` denotes an owned region and `h` a checked handle.

| Concept / proposed word | Literal basis and why it fits | One illustrative line |
|---|---|---|
| Epoch: **kalpa — कल्प** | An attested long period/cosmic age. Use it for one validity period between resets, not elapsed clock time. It removes “same address means same lifetime.” | `vitti janma = kalpa(h)` |
| Release for later reuse: **visarjana — विसर्जन** | Sending forth/dismissal, also giving up. Names the ending of this ownership, not a promise to return pages to the OS. Reuse is what the allocator may do afterwards. | `visarjana(r)` |
| Finite budget: **parimita — परिमित** | Measured, limited. Describes an actual enforced byte budget. It must fail closed, not fall back beyond the limit. | `mandapa parimita(65536)` |
| Unbounded: **ananta — अनन्त** | Endless, infinite. **Reject as a shipped allocator mode**: physical resources and counters are finite. At most a documentation label for “no user-specified cap,” still subject to machine limits. | `mandapa ananta  # REJECTED proposal: no infinite-memory promise` |
| Generation-bearing handle: **kalpasmriti — कल्पस्मृति** | A **proposed compound**, kalpa + smriti (“recollection/memory of an epoch”). Not claimed as an attested ancient technical noun or a full history log. The object identity remembers the validity period in which it was issued. | `kalpasmriti h = nirmmita(64)` |

The last compound is a naming candidate, not linguistic sign-off. The dictionary also attests **smritimat / smṛtimat — स्मृतिमत्**, “having recollection/good memory”; it is a complete adjective, not merely the suffix -mat, but kalpasmriti identifies *what* is remembered more precisely. Do not romanticize it as a record of all past lives or all allocation history: only identity and validity data are stored.

Among the brief's alternatives:
- kalpa and yuga are full words; choose **one** epoch label, not both. kalpa is the selected metaphor, not the only linguistically possible one.
- samskara is not a fresh synonym for a generation counter merely because impressions/history are associated with the word. Reserve judgment on a new technical use; it removes less ambiguity than an explicit epoch-memory compound.
- punaravritti names recurrence/return rather than termination of ownership and risks confusion with loop repetition. No second keyword for allocator reuse is necessary.
- mukti is broad liberation/release; visarjana better labels dismissing a particular live region/object in this proposal. Neither word proves safe reclamation.
- maryada/seema emphasize a boundary; parimita describes the resource as actually limited. Keep existing diagnostic seema spellings rather than adding synonyms.
- Reject standalone fragments such as **punar-**, **pari-**, **sam-**, or **-mat** as names. Full dictionary lemmas/complete compounds are distinct from an isolated prefix or suffix.

Lexical checks used Monier-Williams/Apte entries as reproduced by the University of Hyderabad dictionary and Sanskrit Dictionary; the design metaphor is my inference, not the dictionaries' claim about programming. ASCII spellings follow the project's existing transliteration convention, not scholarly IAST. Dictionary evidence does not substitute for native-speaker review. No pack edits, keyword reservation or all-repository collision certification is claimed here.

## WS3. Comparison: potential axes, not overall superiority

The comparison is between this **unimplemented proposal** and existing language mechanisms. Classroom ease has not been tested with students.

| Language | Axis where the proposal could improve the ordinary baseline | Axis where it loses | Equal or available in both |
|---|---|---|---|
| C | Checked-subset stale access and bounds errors are defined diagnostics rather than relying on raw malloc/free discipline | Wider handles, descriptor traffic, less direct ABI/hardware interoperability | No tracing GC is necessary; C can implement the same arena/handle design in a library. No unique algorithm claim. |
| Rust | Shared mutable graphs within one region may need less borrow-lifetime annotation; this is a teaching hypothesis | Rust can reject many lifetime errors at compile time without per-access epoch checks; this proposal often detects at runtime and has more metadata | Both can use deterministic region cleanup and avoid tracing GC; Rust can also implement generational arenas. |
| Go | Explicit hard regional budgets and cleanup points without tracing-GC work | Requires lifetime/budget choices and can reject cross-region references that Go handles automatically; less mature ergonomic/safety coverage | Safe code should not silently access freed objects; Go's GC memory limit is soft and is not this region budget. Both still face resource exhaustion. |
| Zig | Uniform checked-handle lifetime enforcement rather than relying on allocator-lifetime discipline | Larger references, dependent loads, compiler/ABI complexity and reduced low-level transparency | Both support explicit allocators and arena-style bulk reclamation without requiring tracing GC; bounded allocators are not a Sutram invention. |

C can pair explicit allocation/deallocation; Rust's ownership checking, Go's GC and Zig's allocator guidance are different policies, not proof that one wins all workloads. No throughput, latency, memory-footprint or teaching superiority is established. The credible candidate advantage is **a consistent Sanskrit-facing diagnostic and budget model for a deliberately restricted teaching subset**, conditional on implementation and tests.

## WS4. Smallest useful version

### A. Literal request: bounded memory without reuse

For N retained allocations of s positive bytes, storage is at least N*s (more after metadata/alignment). A fixed cap independent of N cannot admit arbitrarily many such allocations without reuse, release, compression with suitable data assumptions, or refusal. “One million” is finite: a sufficiently large cap can admit one million requests, but that does not demonstrate constant memory as N increases.

**Small candidate: opt-in bounded Linux ELF allocation mode.** Keep the existing reservation but choose a finite B. At every allocation/extension compare the aligned charged size to remaining space; on failed reservation or exhaustion, issue a named error and stop. **Disable the per-call mmap fallback in that mode.** Preserve existing zero-size behavior and validate negative/overflowing sizes before rounding. Check new-capacity arithmetic in in-place kosh extension as well as the copy path. Scratch and persistent cursors must share the cap. Reject unsupported PE/GUARD_PAGES combinations instead of claiming they are bounded.

This closes uncontrolled allocator growth by **refusal**, not by freeing anything. It can finish a million 64-byte allocations when B is at least the required roughly 64,000,000 data bytes plus accounting (alignment does not add to size 64), but fails for sufficiently larger N. It does not fix old-buffer retention, alias divergence or escape safety.

**Estimate: 80–180 added/changed NASM source lines for a narrow ELF-only fixed-budget candidate**, using existing diagnostics and reservation/emission machinery; unimplemented and not a verified diff. Flag parsing, regression cases, documentation, complete separate-module enforcement and cross-platform support are additional. If the actual reviewed diff exceeds 200 lines, report that fact rather than hide work in a helper or count byte-array lines as if they were instructions. All modules must share the same budget policy; reject a bounded/unbounded link mixture. Fault-injection paths also need a deliberate check.

### B. Finish arbitrarily many iterations with bounded temporary demand

This **requires reuse/release**. For the existing scalar-only Linux scratch use case the essential shape is already expressible:

```sutram
mukhya()
    vitti yoga = 0
    chakra i = 0 tak 999999
        mandapa
            vitti p = nirmmita(64)
            p[0] = i
            yoga = yoga + p[0]
    likha(yoga)
```

Expected arithmetic total: **499999500000** (calculated, NOT an observed Sutram run here). The compiler implementation restores the mark each iteration in this shape. By contrast, moving mandapa outside chakra holds all per-iteration allocations until the loop ends.

No new compiler feature is needed to *express* the existing Linux pattern; whether the exact program passes the current checker and meets an RSS bound must be measured. This does not reclaim library allocations chosen lexically elsewhere, any persistent kosh backing storage, or Windows allocations. It retains the documented escape-check limitation and is not the full safe model.

If the requirement is “make arbitrary existing loops recycle dead allocations automatically, preserving escaping values, with the same behavior on Linux and Windows,” **under 200 lines is not credible**. Liveness/provenance, cleanup and representation changes are needed. For the full typed-handle/allocator/ABI design, budget **several thousand lines (2,000+ plausible before tests and platform coverage)**; an exact estimate needs a prototype. Do not promise a 2,000-line ceiling.

### The experiment that decides the next step

Use actual generated binaries pinned to source and compiler hashes. Run:
1. no block;
2. one block around the loop;
3. one block inside each iteration;
4. a preallocated buffer reused manually as a control;
5. bounded mode with deliberate exhaustion.

For N = 10^4, 10^5, 10^6, 10^7, touch every requested page, preserve equivalent arithmetic/checksums, record compile exit and runtime exit separately, and impose a timeout. The two unbounded/no-reset shapes should not be labelled failures solely because their memory grows; they are the controls.

On Linux, prefer a parent collecting per-child peak resource usage via wait4, or GNU time's maximum resident-set measurement if available, rather than a polling loop that can miss the entire child. Keep harness high-water inheritance/noise in mind: use a tiny parent, subtract an empty-program baseline, and cross-check larger touched workloads with /proc measurements. Record units and distinguish maximum RSS, current RSS and virtual reservation. The current arena reserves 1 GiB of address space; constant RSS does not mean a 64-byte address-space reservation.

On Windows, separately use process memory counters or job-object peak accounting on the actual native executable. No Linux result substitutes for that run.

Acceptance for the scratch shape: correct checksum and natural exit; memory high-water approximately flat across N once warmed for constant live demand, with tolerance declared in advance; cursors/charged-byte high-water support the RSS result; all early-exit and nesting cases restore the intended mark. Timing should use repeated interleaved trials, medians and spread. A truncated output prefix, a zero sample or a shared ulimit failure is not acceptance.

## Full-design rejection/acceptance cases before implementation can be called safe

- Alias before/after forced relocation: both refer to the new collection; old storage is reused without corrupting either.
- Odd logical capacities, zero allocation, negative and near-maximum sizes, multiplication/rounding overflow.
- Inject OOM at every growth step: no partial publication, no lost old buffer, counters restored.
- Direct, helper-returned and container-nested scratch references; caller-owned borrows returned legitimately.
- Same lexical depth on different recursion invocations; reentry at the same address; slot reuse; forced generation exhaustion with tiny test counters.
- Freed handles, sliced references and raw-conversion attempts; slot bounds checked before any table read.
- Exit/return/break/continue/propagated error and partial initialization; no double cleanup.
- Same-region reference cycles reclaimed at region exit; long-lived unreachable data charged until explicitly released.
- Million reset/reuse cycles with fixed live objects: descriptor/table usage stays bounded too.
- Parent/child caps, old+new relocation peaks, free-list corruption guards and allocator fragmentation.
- Separate compilation/module ABI mismatch rejected; PE parity or explicitly unsupported status.
- Linux and native Windows tests, including allocator failure and non-ASCII diagnostics, before a cross-platform claim.

## Handoff and implementation recommendation

Approve the **bounded ELF experiment** first as a narrowly scoped, reviewable candidate. In parallel planning, decide whether to accept the wider checked-reference ABI; without it, do not turn recycling bins back on for legacy kosh aliases. Keep the compiler, lib, tests, tools, README/docs and Windows work with their assigned maintainers. No source patch, CI run or new runtime result is delivered in this round.

### Sources

Repository sources, all at the pinned base:
- `Sarvam-to-ChatGPT/ROUND-170.md`
- `src/r65_arena.inc`: r65_active, r65_emit_nirm, r65_emit_kosh_extend, r73_gen_scrcur, r73_gen_rewind, r73_gen_scratch_nirm
- `src/sutram_compiler.asm`: r72_parse_mandapa, r73_ret_mark, r73_wrap_jump, R82 header/liveness comments and emitter
- `docs/LANGUAGE-REFERENCE.md` §19
- `docs/decisions/MEMORY-DECISION.md`, `docs/decisions/MEMORY-DESIGN.md`, `docs/MEMORY-MODEL.md` (historical claims labelled above)
- `docs/reports/KOSH-REUSE.md`
- `tests/r73_scratch/blind_kosh_via_call.sm`, `tests/r72_mandapa/loop_with.sm`
- `docs/vocabulary/VOCABULARY-RULE.md`, AGENTS.md, PROJECT-MASTER.md, LANGUAGE-PRIORITY.md and design charter (standing rules read in R169; only round briefs changed since).

External references, checked 2026-11-02; dictionary meanings are evidence for words, not for the proposed programming semantics:
- [Rust ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)
- [Go GC guide and soft memory limit](https://go.dev/doc/gc-guide)
- [Zig 0.15.2 allocator guidance](https://ziglang.org/documentation/0.15.2/) (explicitly versioned, not a latest-version claim)
- [WG14 N1570 C draft, lifetime/allocation](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), §§6.2.4, 7.22.3
- [MW visarjana, University of Hyderabad](https://sanskrit.uohyd.ac.in/SKT/MW/246.html)
- [MW/Apte smritimat](https://sanskritdictionary.com/?q=sm%E1%B9%9Btim), [smriti](https://sanskritdictionary.com/?iencoding=slp1&lang=sans&q=sm%E1%B9%9B)
- [parimita dictionary entries](https://sanskritdictionary.com/?iencoding=%2F46856%2F1&lang=&q=mita)
- [kalpa dictionary entries](https://sanskritdictionary.com/?action=Search&lang=&q=kalp)
- [ananta dictionary entries](https://sanskritdictionary.com/?iencoding=sl&lang=&q=ananta)

The remote dictionary search returned some entries for pages that denied direct fetch. Those meanings were checked from indexed dictionary text; no claim of a full Sanskrit philological review is made.

