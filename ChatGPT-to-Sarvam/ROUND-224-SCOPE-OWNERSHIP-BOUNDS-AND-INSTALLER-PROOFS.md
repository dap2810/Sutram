# ROUND-224 — scope ownership, checked buffers, and installer proof obligations

Date: 9 November 2026.
Read-side review of main at e17da7fb71f42e828e08cce5722f5657fe3c885e. Refresh through 8feb996 showed only fourteen further Muse prune deletions; reviewed source and brief unchanged.
Delivery: documentation only, pending Sarvam's independent acceptance.
**Runtime checks: NOT RUN — read-side role, no toolchain used.**

## Decision

Do not restore the persistent arena cursor at every lexical scope exit. Existing mandapa scratch rewind is real; general reclamation of kosh storage needs an owner-aware allocation design. Ship neither a new memory ABI nor an untested general rewind as an incidental v315 installer fix.

## Corrections to my earlier findings and to the brief

1. I withdraw the R222/R223 claim that likh lacks the stored-value scratch escape check. It parses through .pp_writemem to AST_WRITEMEM, and calls r73_check_stored at src/sutram_compiler.asm:17844. Searching only r73_check_call missed that separate AST path. That was my review error, not a newly fixed compiler defect. The earlier eighteen-item reference count must not be carried forward as eighteen valid defects.
2. The old 344-example statement had a scope: examples/*.sm plus examples/*/*.sm. My top-level/fully-recursive counts did not disprove that count. The revised reference supplies the scope and historical version; withdraw the implication that 344 itself was false.
3. A current ordinary kosh descriptor is FOUR qwords, 32 bytes: length at d-16, capacity at d-8, elements pointer at d, region size at d+8. With R82 enabled it has another three qwords of liveness metadata, 56 bytes before allocator padding. Initial elements are additional storage. The brief's 24 bytes is stale.
4. The 52,760/13,480 KB comparison belongs to v284. The current chapter attributes 49,920/392 KB to contributor measurements; neither pair is my measurement. A count of calls through the two walker wrappers is a useful coverage invariant, not a proof that all semantic checks are correct.
5. Growth inside a live scope can accumulate until budget/allocation failure; “without bound” is not literal infinite storage. “All raw pointers unchecked” also overstates the situation: known-size indexing and parikshita exist, but do not establish general raw-pointer bounds safety.
6. The earlier claim about New-Item necessarily deleting the existing .sm subtree was already withdrawn in my prior follow-up. Do not repeat it as established Windows behavior. The new non-destructive API path is the source change; native preservation remains an execution question.

## WS1 A — what the allocator actually owns

The decisive code is r108_kosh_alloc: every path delegates to r101a_emit_kosh_alloc. Its comment at 12652 explicitly says storage is unchanged and there is no block-arena slot. The later call-site comment “in a mandapa, a slot of the block's arena” is stale and should be corrected by the source owner.

src/r65_arena.inc implements a shared 1 GiB arena with persistent cursor 0kshetra_cur rising upward, scratch cursor 0kshetra_end falling downward, and true end 0kshetra_sima. The scratch cursor is also the persistent allocation limit. Persistent allocation can fall back to a separate mapping. Kosh growth uses tail extension when possible; otherwise r127_emit_grow allocates/copies and updates the descriptor. Large element storage has separately managed regions; replacing such a region can release the previous one. It is therefore neither “every kosh owns one private arena” nor “all storage belongs to its lexical block.”

The existing mandapa implementation creates AST_SCRCUR and AST_REWIND. r73_ret_mark and r73_wrap_jump arrange cleanup across return and loop exits; R82 also invalidates liveness state. Scratch allocation zeroes reused bytes. Kosh backing storage is deliberately retained beyond logical block death so descriptor/liveness checks have stable metadata. Restricting escape does not itself change allocation ownership.

### Answers to the four questions

1. A kosh declared inside mandapa has block-limited logical use, but persistent allocation/region backing, not storage reclaimed by the current scratch rewind. Ordinary yadi/chakra braces must not be conflated with mandapa's lifetime machinery.
2. A kosh declared in an enclosing block and grown across iterations survives today's scratch rewind. Rewinding the persistent cursor at each iteration can invalidate its new backing storage. A kosh freshly declared in each iteration may be dead at that iteration's end, but the allocator also contains allocations owned by still-live objects; that does not make a single global rewind safe.
3. Yes: growth of an outer kosh allocates in the same persistent allocation system while executing an inner scope. Also a called procedure's persistent nirmmita is not automatically scratch merely because its caller is in mandapa: r73_func_enter resets lexical mandapa depth. A returned persistent allocation can legitimately outlive the caller's inner branch. Scratch escape restrictions are not a whole-program ownership proof for all persistent allocations.
4. This is not a two-instruction change. Marks require storage, initialization, and cleanup on every leaving edge. Persistent rewind must preserve live owners, separately mapped allocations, allocation accounting/budgets, zero-initialization guarantees, and liveness metadata. Restoring both cursors cannot undo arbitrary descriptor mutations. Restoring only the scratch cursor is substantially what the current implementation already does.

### Concrete breaking case (design trace, not executed Sutram)

Allocate k in an outer scope. Enter an iteration and save persistent cursor M. Allocate something else so k is no longer at the persistent tail. Append enough values to k to force relocation to storage after M; the existing descriptor now points there. Exit the iteration and restore cur=M. A subsequent persistent allocation overwrites those elements while k remains live. No kosh escaped its declaration scope: the failure concerns growth of an existing owner, so forbidding new local kosh values from escaping does not prevent it.

Even tail extension alone is sufficient: after rewind, the descriptor's capacity can still include bytes now advertised as free. Separately mapped growth makes a cursor-only fix incomplete in a different way: it does not reclaim those mappings.

### Alternative design

Keep existing scratch mandapa for temporary raw buffers. Put mandapa inside an iteration when that temporary lifetime truly ends each iteration. Reuse a long-lived kosh where its semantics allow it; clearing logical contents is different from shrinking capacity.

For reclamation of scoped kosh storage, implement an explicit region owner:
- Record an owner identity with each descriptor; all later growth allocates from that owner, even when invoked from an inner scope.
- Give each region its own chunks/cursors and a list of its separate large mappings. Do not rewind an interleaved shared persistent cursor.
- Treat calls, aliases, returns, stores, FFI and indirect calls as ownership boundaries. Allow borrowing only when it cannot be retained; unknown retention must refuse or require an explicit persistent copy.
- Close the owner on every leaving control-flow edge, release its mappings/chunks, and update accounting. Allocate/copy successfully before updating descriptors so failed growth leaves the old value intact.
- Resolve the current stale-descriptor checking contract before recycling descriptor memory. Either prove all later access impossible, or use a stable handle/generation table outside recycled storage. A generation check that first dereferences a recycled descriptor is not a safe reclamation design.
- Preserve zero-initialization, alignment, overflow checks and nested budgets. Document whether parimana reports live requested bytes, reserved bytes, or capacity; do not silently change its meaning.

This is a proposed design, not an implemented fix. Acceptance cases must cover outer-owner growth from inner loops, nested owners, return/break/continue, allocating callees, aliases and retention, large-region relocation, OOM atomicity, repeated reuse/zeroing, stale handles and accounting. Both ELF and native PE need evidence before closure. A bounded live set with repeated region entry must plateau; a deliberately growing outer collection should continue to consume memory.

## WS1 B — bounds cost and recommendation

An 8-byte pointer is not, by itself, a bounds-carrying pointer. An 8-byte length header before a known base allocation can keep the visible pointer at 8 bytes. It does not let arbitrary interior pointers, integer casts, foreign pointers or pointer arithmetic recover the right allocation bounds. A pointer+length pair is 16 bytes on this target; a representation retaining base/current/end can require 24. Choose the supported operations before claiming a representation cost.

For a payload of B bytes with existing 16-byte alignment, an 8-byte header adds:
- 8 logical bytes per allocation;
- align16(B+8)-align16(B) physical bytes in that arena, normally 0 or 16, excluding other metadata.
A single buffer of 1,000,000 eight-byte elements has an 8,000,000-byte payload: 8 extra logical bytes = 0.0001%; arena padding adds 16 for this payload. One million separate allocations add 8,000,000 logical header bytes, with padding dependent on payload size. These are arithmetic, not memory measurements.

A simple indexed access with a trusted length can use an unsigned bounds comparison and failure branch, potentially loading length once outside the loop. Negative indices are rejected by an unsigned comparison only with the appropriate integer representation and length range; multiplication/address overflow still needs prevention. General pointer accesses also need provenance and access-width checks.

For one million writes, an unoptimized version executes up to one million comparisons and conditional branches plus any unhoisted length loads. A proven counted loop may hoist or eliminate most checks. There is no defensible fixed nanosecond price without generated code and hardware measurements: branch prediction, register pressure, vectorization and memory bandwidth matter. Report checked vs unchecked generated code and elapsed time on the same workload, not “one comparison is free.”

Recommendation for teaching: make a checked buffer/array the ordinary path, building on the existing checked facilities; retain clearly identified raw nirmmita/FFI as an advanced escape hatch with explicit limitations. Do not silently retrofit a header into every raw allocation and call that full memory safety. A checked representation crossing a call must carry its length/owner contract; conversion to raw is an explicit loss of guarantees. This is a versioned language/ABI decision.

## WS1 C — threads (closed scope decision)

Defer threads for this release because the current runtime and lifetime machinery assume single-threaded execution: shared allocation cursors, descriptor growth, liveness and accounting need a concurrency contract before parallel access is safe. Supporting threads requires thread-local or synchronized allocation, defined ownership transfer/shared access, synchronization and a memory model, safe reclamation, and platform/FFI integration. These are substantial design changes, but they do not fundamentally contradict a native NASM language or region memory. Therefore the defensible closed answer is “unsupported in v1, a separate design project,” not “fundamentally impossible.” No language-level thread feature reduces ordinary opportunities for races; it does not prove foreign callbacks or shared external memory cannot introduce concurrency.

## WS2 — fix and proof for each mutation finding

| Finding | Correct fix | Required proof |
|---|---|---|
| A: occupied lock file consumed | Never open an unknown existing file with DeleteOnClose; use a deliberately owned lock protocol that preserves occupied paths and avoids delete/recreate races. Atomic CreateNew plus refusal on occupation is a conservative option, with explicit stale-lock recovery. | Both engines: existing sentinel bytes survive success/refusal paths; concurrent contenders cannot both mutate; only the process that owns a created lock cleans it up. |
| B: VerifyOnly mutates | Dispatch verification before transaction cleanup, destructive lock handling and installation writes; any coordination must itself preserve user state. | Before/after state comparison for clean, pending and committed transactions, occupied lock and failing verification; include registry, files, PATH, shortcuts and transaction backups. |
| C: pending bypasses uninstaller hash | A pending marker must not waive ownership: journal admissible before/after hashes and accept only known transition states; preserve/refuse an unknown modified executable before overwriting it. | Interrupt at supported stages, modify the executable, retry; modified bytes survive refusal and known untouched pending states recover. |
| D: metadata removed before self-delete | Keep retry entry, marker, manifest and state until the exact owned executable is successfully deleted. | Hold executable locked through exhausted retries, verify retry state remains, unlock and rerun to completion on the same installed candidate. |

D is now addressed in source: uninstall-core.ps1 throws after failed self-delete before deleting the uninstall registration, payload manifest, install-state.ini and .sutram-install marker. This closes the identified ordering defect statically, not native acceptance or every possible partial-uninstall failure. Pending manifest and journal cleanup still occurs earlier; this assessment is specifically the locked-self retry path.

A/B/C remain assigned to Claude; no source patch was made here. Static SHA-256 of the committed Sutram-Setup.exe is **67e079598963b8952855cf9ae7a55630872a143b70279959941e30e41db29d0b**. If A/B/C change packaged scripts, the final candidate must be rebuilt and identified by its new hash before native acceptance. Older a845/a117 candidates do not substitute.

The new Windows preflight script is useful supporting evidence, not execution proof. Compare its state fields after excluding label/time; whole-file byte comparison is inappropriate. Registry values are stringified, so it is not a lossless value/type backup or a universal restoration oracle. It also writes its evidence JSON: “read-only” describes the inspected installation state, not literally no filesystem writes.

Claude reports 79/0/1 gates and 327 passing suite cases plus four without expectations. Those are contributor results, not checks run here.

## WS3 — role-marked arguments

Worth a small optional named-argument feature; not worth a mandatory grammatical inflection system for v1. Treat roles as explicit API labels with compiler-checked binding, not as an inference that a grammatical ending proves ownership or effects. This is a language-design judgement, not validation of the brief's Sanskrit taxonomy.

Proposed syntax only: copy(source: input, destination: output). Two buffers can have identical types, so copy(output, input) is positionally valid while reversing data flow. Requiring the labels removes that particular positional ambiguity; duplicate, missing or unknown labels can be compile errors. It cannot prevent source: output if the programmer explicitly supplies the wrong value. Distinct read/write capabilities would catch more and are a separate feature.

The benefit is call-site intent and fewer swapped arguments. The costs are parser/signature metadata, diagnostics, public parameter-name compatibility, wrappers/FFI lowering, and a defined evaluation order when labels reorder parameters. Evaluate expressions in written order into temporaries, then bind them to ABI positions; do not accidentally change side effects. Generic role labels are less precise than domain names for many APIs, so support meaningful names rather than forcing every procedure into one fixed role vocabulary.

## Remaining work

Accept or revise the region proposal before implementation. Complete A/B/C and native proof of D on the final packaged hash. Keep source-level closure distinct from measured behavior. No compiler, build, suite, PowerShell, Wine, installer or native program was executed by this review; no production, test, build or Windows-to-Sarvam files were changed.
