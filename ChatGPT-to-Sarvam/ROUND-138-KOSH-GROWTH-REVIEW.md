# Sutram ROUND 138 — in-place growth preserves addresses, not necessarily alias behavior

**Date:** 29 October 2026. **Pinned main:** `f0714d09c3fa8c62cd66ab28c0262cc8cbad5c0e`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-138.md`, blob `6c14f09354cfc84685c8b8624c3ea22961bd8736`.
**Return:** `ChatGPT-to-Sarvam/ROUND-138-KOSH-GROWTH-REVIEW.md`.
**Observed baseline:** the pinned changelog opens at **v416**, although the brief says v415; the inspected compiler remains v261. This is a design/source review, not a build or native test.

## Decisions first

**WS1:** dropping recycling removes the particular live-buffer-reuse hazard. Extending a genuine persistent-arena tail into verified unused, writable space can preserve every existing pointer into that allocation. An alias does not by itself create another physical allocation to overwrite. But **“it does not relocate” is not a complete safety argument**, and it is not a compatibility argument. Bounds, arena ownership, actual allocation extent, overflow, failure handling and the scratch frontier still matter. More importantly, current grow-and-copy behavior splits aliases; in-place growth keeps them sharing. That changes ordinary numeric output, not just printed addresses.

**WS2: choose (b) for the v1 default under unchanged alias semantics:** ship no new `kosh` growth optimization yet; retain its current copy-and-retain path and document the limitation. This is not a recommendation to abandon the separate allocator work. Option (a) becomes reasonable after either a sound uniqueness condition restricts the optimization or the owner explicitly specifies and accepts the changed alias behavior. Neither is established by “the block is last.”

**WS3:** initial K0 must reject `kosh` values/operations within its verified boundary. This is stronger than merely refusing `kosh_push` inside a `mandapa`. K0 checks the whole containing function, and it has no verified collection representation/alias contract. Legacy code outside that boundary may still use `kosh` and pass verified scalar results into a checked helper. Aliasing does not make all possible future read-only collection interoperation inherently unsafe; it makes the current minimal checker insufficient for admitting it.

**Additional correction:** “bounded leak” must state a bound. Geometric growth has a bound relative to one growth chain's attained capacity; repeated allocations over a process lifetime do not have a fixed bound. A finite arena plus unbounded `mmap` fallback is not a finite process-memory budget.

## Evidence boundaries

- **Directly read:** the pinned growth emitter, its append/length update, the current `kosh` specification, the R42 alias example, Claude's R64 stop report, the relevant R59 report, the changelog and the returned R137 opening.
- **Partner-reported execution:** Claude's alias outputs, capacity census and memory measurements. They are not rerun here.
- **My deductions:** the conditional interval proof, predicted in-place outputs, growth-series bound, release recommendation and proposed tests.
- **External reference check:** Linux man-pages for why a fallback mapping is not automatically an extendable arena tail. Those API facts are not substituted for Sutram semantics.

## WS1 — distinguish storage safety from observable semantics

### 1. What the current emitter actually does

At `src/sutram_compiler.asm:15651–15936`, `kosh_push` evaluates the appended value first, then loads the selected variable's user pointer, logical length and capacity. If full, it chooses `newcap = cap ? cap*2 : 4`, allocates `(newcap+2)*8` bytes, writes a new length/capacity header, copies elements, and calls `emit_store_named_var` for the selected variable. It then appends and writes length at `[user_ptr-16]`. The capacity is at `[user_ptr-8]`. The allocation base is therefore `user_ptr-16`; cells are eight bytes. [R2]

The emitter does not update an arbitrary graph of all copied aliases. Claude's independent v261 probe confirms that a copied handle can remain usable on the old buffer after the original grows. The compiler propagates some `kosh` kind information to aliases, but that is **not a uniqueness or ownership proof**. [R3]

Also correct a prior over-reading of the R42 example: `examples/255_r42_alias_kosh_push.sm` declares capacity 4 and appends only two elements. It demonstrates shared mutation **without crossing capacity**. Its comment says “grows the original,” but the executable shape does not test relocation at a growth boundary. Passing that example alone cannot settle this round's question. [R4]

### 2. Direct answer: can a correct tail extension overwrite an intervening allocation?

**No, under the actual tail invariant.** Let the old allocation occupy its allocator-recorded interval `[B,E)`, including its header and alignment padding. Let `P` be the first unused persistent position and `S` the lower boundary of live scratch, in the same arena coordinate system. Before growth require:

```text
B belongs to this persistent arena
E is the actual end of this allocation, not a guessed address
E == P
0 <= P <= S <= arena_limit
0 <= delta <= S - P
```

Then the new suffix is `[P,P+delta)`. Every earlier persistent allocation ends at or before P, and live scratch begins at or above S. The suffix overlaps neither. Two variables naming `[B,E)` do not consume two physical intervals; extending the one interval does not overwrite another allocation merely because two handles exist.

If another allocation really sits after this block, then its recorded end is beyond E and the current frontier is greater than E. **The equality must fail.** Do not replace `E == P` with `E <= P`, use a cached frontier, or trust a stale “last kosh” flag. If a supposedly exact tail test passes despite a real later allocation, the allocator bookkeeping, size calculation or ordering is wrong; that is not an unavoidable consequence of aliasing.

This is a conditional storage-overlap proof, not a finding that an implementation has passed it. It assumes valid allocator metadata and valid program accesses, not arbitrary raw writes corrupting headers or cursor state.

### 3. Conditions the short argument leaves out

| Condition | Why required / concrete failure avoided |
|---|---|
| **Same arena and allocation kind** | A `mmap` fallback allocation is not eligible merely because its address looks adjacent. A scratch object must not be extended as persistent storage or outlive its region. Track provenance/extent, not only a pointer number. |
| **Exact byte extent and alignment** | Capacity counts eight-byte elements, not bytes. Account for the 16-byte header and actual reserved padding. For an aligned base, an illustrative span is `align_up(16 + 8*C, A)`, with checked arithmetic. `user_ptr + C` is not the end. The allocator's authoritative span wins if its metadata/layout differs. |
| **Read the current shared header** | Aliases share length/capacity while on the same block. Never extend using a capacity cached for one variable before another alias modified the object. Preserve arbitrary valid capacities; do not silently round the public capacity to a power of two. |
| **Recheck after value evaluation** | The appended expression may call a helper that allocates. The current emitter evaluates it before checking growth. Moving the tail test before that evaluation would let a stale test overwrite the helper's allocation. |
| **Check the P/S gap, not only the arena end** | Example in arena offsets: P=4096, S=4112, extension delta=32. P+delta exceeds S by 16 even if the arena is much larger. An unchecked extension overwrites live scratch. |
| **Checked arithmetic** | Validate capacity doubling, `16 + 8*newcap`, alignment rounding and pointer/offset addition before mutation. Wraparound can make a false tail/gap test look true. |
| **Writable backing** | A logical address range is not proof that those bytes are accessible. The backing policy must make the suffix writable before handing out capacity. No Windows implementation is claimed in this review. |
| **Serialized check and commit** | No intervening allocation may consume the tested suffix before publication. In the initial single-threaded model, do not call an allocating helper between validation and commit. Future threads/reentrancy need a separate synchronization contract. |
| **Failure leaves the object intact** | On failure, do not publish larger capacity/length or advance P first. A copy fallback must check the new pointer before header writes, preserve the old block on failure and update only the intended handle on success. |
| **Initialize only newly exposed storage** | Preserve the specified initialization behavior for new capacity, but do not clear the old header/data: doing so would corrupt values visible through aliases. Cursor reset/reuse does not itself zero bytes. |

The current copy-growth path writes the new header immediately after the allocator returns, without an intervening visible null check in the inspected sequence. That is a separate existing failure-handling concern, not repaired by choosing in-place growth. Native failure characterization remains NOT RUN here. [R2]

**External API boundary:** Linux `mremap` without permission to move can fail when in-place expansion is unavailable; permitting movement invalidates absolute pointers into the old location. `MAP_FIXED` can discard overlapping mappings. Therefore “extend a fallback mapping at its numeric end” is not a safe substitute for proving an unused suffix within an already owned arena. This review proposes neither a moving remap nor a forced-address overwrite. [W1, W2]

### 4. The compatibility counterexample: an alias stays valid but changes meaning

Use Claude's existing probe, not an invented claim that it was run again:

```sutram
mukhya() {
    kosh k[1]
    kosh_push(k, 7)
    vitti a = k
    kosh_push(k, 8)
    kosh_push(k, 9)
    a[0] = 99
    likha(a[0])
    likha(k[0])
    kosh_push(a, 5)
    likha(kosh_len(a))
    likha(kosh_len(k))
}
```

| Implementation | Four printed values | Evidence status |
|---|---|---|
| Current v261 copy-and-retain growth | `99`, `7`, `2`, `3` | **Claude-reported execution** in R64, consistent with the inspected emitter. |
| Proposed successful in-place growth at both capacity crossings | `99`, `99`, `4`, `4` | **Predicted here, NOT RUN.** Assumes enough arena space and no intervening persistent allocation before those extensions. |

Why: today, `a` remains on the initial buffer while `k` receives new storage. Under in-place extension they still name the same header and cells. Writing through `a` changes `k[0]`; appending through `a` changes the shared length. The second result is not a dangling-pointer failure. It is a **different aliasing/mutation result**.

An unrelated allocation that prevents tail extension can make the optimized implementation fall back to copying, so the same alias pattern can share or split according to allocation interleaving. That behavior can be specified, but it is not automatically the existing behavior merely because no pointer became invalid.

The published builtins specification describes growth and observable lengths/capacities but does not, in the inspected text, establish a comprehensive post-growth alias contract. Do not pretend this is a newly proved violation of a formal contract that was never written. It is a demonstrated **current-behavior compatibility question requiring an explicit decision**. The project cannot promise unchanged ordinary outputs and simultaneously treat the difference above as only a harmless address change. [R3, R5]

### 5. Verdict on the corrected plan

- **Accept dropping bins/recycling.** Keeping old buffers allocated avoids handing one still named by a program to a different collection.
- **Conditionally accept the storage mechanism.** A checked tail extension can avoid overwrite and dangling aliases under the listed invariants.
- **Challenge unconditional default adoption.** Tail position is not unique ownership, and stable addresses are not unchanged alias behavior.
- **Do not infer a permanent impossibility of reclaiming memory.** A future uniqueness/lifetime discipline or different collection representation can change the design space. What is not justified is reclaiming unknown-live buffers under today's unrestricted alias behavior.

## WS2 — choose (b) now, and describe retention accurately

### 1. My release choice

**Choose (b): retain current `kosh` growth for the v1 default until alias semantics or a sound uniqueness condition are settled.** Keep the corrected allocator work separately reviewable; do not insert this optimization solely on the claim that “no relocation means no behavior change.”

This choice avoids adding allocation-interleaving-dependent mutation results while the project is trying to freeze semantics. It does not require waiting for a universal ownership system: a narrowly proved unaliased case could later qualify. However, absence of a visible `vitti a = k` in one local block is not sufficient evidence of uniqueness when raw stores, aggregates, globals or calls can carry references.

Option (a) is reasonable **only after** one of these explicit gates:

1. Prove the optimized object has no relevant aliases, including indirect escapes, and retain copying when the proof is unknown; or
2. Approve and document that aliases stay shared when extension succeeds but may split when growth copies, then test that new language contract; or
3. Adopt another separately approved collection contract/representation that consistently defines sharing. That is outside this round.

I am not claiming a storage-safe optimization is impossible, or that a leak is inherently preferable forever. I am choosing the smaller compatibility commitment for the current release.

### 2. “Bounded leak” has three different possible meanings

**One geometric growth chain:** suppose initial capacity `c0 > 0`, m growths, each exactly doubles, and the final capacity is `C = c0 * 2^m`. If every growth copies and every previous block is retained, the sum of old capacities is:

```text
c0 + 2*c0 + ... + C/2 = C - c0
old payload bytes retained = 8 * (C - c0)
old header bytes = 16 * m
```

This excludes alignment, mapping granularity, allocator metadata and residency. It is a bound relative to **attained capacity in that growth history**, not a fixed number of bytes and not necessarily relative to current logical length after a clear. Non-power-of-two c0 does not invalidate the geometric sum. Zero initial capacity needs the documented initial-growth case before applying the formula. In-place growth can reduce the copied generations; it does not create a global reclamation rule.

**Old blocks still reachable through aliases:** those bytes are not all unreachable garbage. Some are live storage under current behavior, as the probe shows. Call them *retained prior buffers* unless reachability is actually known. A memory-saving patch cannot treat all retention as reclaimable leakage.

**A long-lived process:** repeatedly construct/grow/discard fixed-size collections, or interleave allocations so none is the persistent tail. With no release, retained memory increases with the number of completed operations even when useful current working data stays small. A finite initial arena with `mmap` fallback can continue acquiring mappings; it has no fixed process-memory bound merely because the arena has a configured length. A real hard budget must also account for fallback mappings and have specified exhaustion behavior.

Therefore say **“retention is bounded relative to a single growth chain's capacity; total persistent memory is not automatically bounded over process lifetime.”** Do not advertise a leak-free server or a constant-memory workload from this optimization.

### 3. Do not reuse the ~15.3 bytes/item figure as an independently verified leak rate

R138 gives ~15.3 bytes/item. Claude's R64 report instead labels the before measurement as 16,000 KB peak RSS for a million appends versus 7,808 KB for a pre-sized collection, describes the difference as about 8.2 bytes/item, and explicitly says 15.3 was the whole footprint. These are **partner-reported measurements in the report's stated units**, not measurements made or unit-normalized here. [R1, R3]

Separate current payload, spare capacity, retained generations, mapping/allocator overhead and peak RSS. Requested bytes, touched/resident bytes and incremental leakage are different metrics. The geometric reasoning above is an allocation-size argument, not an RSS prediction or a universal per-item constant.

### 4. Proposed user-facing limitation text

> Growing a `kosh` may allocate a new backing buffer. Existing copied handles can continue to refer to an older buffer. The implementation does not reclaim those prior buffers while they may remain accessible. Repeated construction or growth can retain memory until process exit; this is not a fixed per-process memory bound. A realistic initial capacity can avoid some growth allocations, but it does not provide release of completed collections. Long-running workloads must budget persistent allocations explicitly.

This is proposed documentation, not a change applied to the canonical user guide. It describes current behavior rather than silently introducing a promise that every alias follows relocation.

## WS3 — what K0 must reject, and what `mandapa` is for

### 1. Yes for the initial frozen profile; not as a theorem about every possible checker

**K0 rejects `kosh` declarations, collection-reference values and operations in the verified function boundary until collection-aware rules exist.** That includes integer and `dasham` collections, copied handles, indexing, metadata operations such as length/capacity, append/removal/clear, collection arguments/results and unverified helpers manipulating them. A harmless-looking scalar result from an unsupported collection operation is not a license to omit checking the operation.

Some read-only metadata or immutable numeric collection operations could be admitted by a later verified contract. Aliasing alone does not make every such operation mathematically unsafe. The reason for the current rejection is precise: **initial K0 does not establish the required object/representation/lifetime facts. Unknown is rejection.** Do not add those contracts through a casual special case in this round.

K0 checks the **whole function containing `mandapa`**, not only its textual body. Declaring a `kosh` just before the block and using it inside does not bypass verification. Similarly, moving `kosh_len(k)` just outside the braces in the same checked function does not make an unsupported operation checked. Dead-code/unused-declaration exceptions would need their own specified rule; the initial validator can reject such constructs uniformly.

This does **not** ban `kosh` from programs without the new checked construct or require unrelated legacy functions to adopt K0. The compatibility boundary is the same one frozen in R135–R137. [R7]

### 2. Allowed interoperability shape

A legacy caller can operate on its collection and pass an ordinary scalar to a checked helper. The helper receives a value, not a borrowed collection address:

```sutram
# PROPOSED K0 example, NOT RUN; mandapa is not claimed implemented here.
prakriya agla(n) {
    mandapa {
        vitti p = nirmmita(8)
        yadi (p == 0) { nivartanam -1 }
        p[0] = n + 1
        nivartanam p[0]
    }
}
mukhya() {
    kosh k[1]
    kosh_push(k, 7)
    likha(agla(kosh_len(k)))
}
```

The successful scalar result is **2 by reasoning, not execution**. `mukhya` has no `mandapa` and retains legacy collection semantics. `agla` has a scalar parameter, a fixed-size scalar-only scratch buffer, a null check and a scalar return. Its cleanup follows evaluation. Replacing the argument with the collection reference is not the same checked contract.

The initial block is for bounded, statically understood scalar scratch and verified scalar helpers. It is **not yet a general region wrapper around arbitrary collection-based request handling**. Preserve that limitation in examples and release claims.

### 3. Persistent fallback must not silently become scratch fallback

R138's corrected plan includes `mmap` fallback. That can be reviewed as a **persistent allocator policy**, with explicit resource accounting. It must not silently override the frozen scratch-exhaustion contract: direct allocation in `mandapa` cannot fall back to a durable untracked mapping and then claim cursor rewind reclaimed it.

For initial K0 retain clean scratch failure (0, no state mutation) at the defined budget. If a future region fallback acquires mappings, it needs explicit region ownership/release bookkeeping and exit coverage. This is a separate extension, not a free consequence of the persistent fallback or lexical routing decision. No fallback implementation or new policy is applied here.

## Focused acceptance gates for any later optimization

All tests below are **proposed, NOT RUN**. The current native source was read; no modified emitter was built.

| ID | Test | Required distinction |
|---|---|---|
| G01 | One unaliased tail `kosh`, sufficient gap | Preserve values/length/capacity; prove actual suffix and pointer stability. |
| G02 | Claude R64 copied-handle growth probe | Compare the existing `99,7,2,3` with the predicted shared result; owner decides semantics before acceptance. |
| G03 | R42 alias example without crossing capacity | Continue to pass, but do not count it as a relocation test. |
| G04 | Another persistent allocation after the buffer | Tail test fails; preserve that allocation with a canary and retain old storage on copy. |
| G05 | Appended expression allocates before growth | Check tail after expression evaluation; no stale-frontier overwrite. |
| G06 | Tail buffer adjacent to live scratch | Gap check refuses extension crossing S; scratch canary unchanged. |
| G07 | Non-power-of-two capacities and alignment slack | Preserve public capacity rule; use real byte spans, not size-class assumptions. |
| G08 | Header/size/rounding arithmetic boundaries | Reject overflow before any state change or write. |
| G09 | Buffer came from `mmap` fallback | Exclude from arena-tail extension absent a separate verified mapping-resize path. |
| G10 | In-place failure and copy-allocation failure | No partial capacity/length/cursor publication; no header write through 0. |
| G11 | Growth through either of two aliases; aliases hidden through storage/global/call | Exercise actual ownership uncertainty, not only local names. |
| G12 | Repeated bounded-size collection lifetimes | Measure total retention versus iterations; do not report a constant process bound from a one-chain ratio. |
| G13 | `--fail-alloc N` with/without the fast path | Explicit policy for logical growth attempts versus actual backing allocations; do not silently shift fault-test meaning. |
| G14 | `kosh` operation anywhere in a K0 function | Explicit unsupported-collection diagnostic, not a false safe label. |
| G15 | Legacy collection caller to scalar-only checked helper | Supported scalar flow; pointer argument remains rejected. |
| G16 | Persistent fallback versus scratch exhaustion | Distinct documented lifetimes/accounting; no untracked region fallback. |

Also keep ordinary regressions, expected outputs and alias probes separate from binary identity. A changed allocation/growth emitter may intentionally change bytes; a changed ordinary alias result is a different decision. The no-`mandapa` Step-3/4 guard still compares against the **same accepted allocator/growth baseline**, not against a different allocator version. No current or future guard pass is claimed here.

## Final answers

1. **Is the tail-growth argument sound?** As an address-preservation argument, conditionally yes: a verified unused suffix can be added without invalidating aliases. As an unconditional safety/compatibility argument, no. Gap/ownership/extent checks are missing from the short version, and current split-alias behavior is observably changed.
2. **Can an alias alone cause extension to overwrite another object?** Not when actual end equals the current frontier and the checked suffix is free. If the cursor already passed another allocation, the tail test must fail. Cached tests, incorrect units/alignment, fallback confusion or missing scratch-gap checks can make an implementation corrupt memory.
3. **Which option for v1?** **(b) under unchanged alias semantics.** Retain current growth and disclose retention; consider (a) only after uniqueness proof or an explicit new alias contract and tests. Dropping bins is accepted.
4. **Is the retained memory globally bounded?** Not from the proposed mechanism. It is bounded relative to a specified growth history or an enforced total budget, not automatically relative to current live work or process duration; fallback mappings must be counted.
5. **Does K0 reject `kosh`?** **Yes in the initial verified function boundary.** Scalar-only scratch remains useful; legacy collections stay available outside that boundary. Broader safe interoperation is future work, not a warning-only bypass.

## Source ledger and execution status

### Repository evidence, all pinned unless explicitly historical

- **R1:** `Sarvam-to-ChatGPT/ROUND-138.md`, blob `6c14f09354cfc84685c8b8624c3ea22961bd8736`: corrected plan and three workstreams.
- **R2:** `src/sutram_compiler.asm:15645–15952`, blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`: argument evaluation, growth capacity, allocation/header/copy, selected-variable update, append and shared-header length store.
- **R3:** `Claude-to-Sarvam/R64-00-STEP0-STOPPED.md`, blob `cc15341786887a5a584c174a02bec13ed81a1ef8`: measured alias probe, capacity observations, reported memory comparison and fault-injection caution. Those executions belong to Claude's report, not this round.
- **R4:** `examples/255_r42_alias_kosh_push.sm`, blob `ce9a796e136ae95952cb7db11622fac87ae93c3b`: capacity 4, only two appends, alias mutation without capacity growth.
- **R5:** `docs/reports/KOSH-BUILTINS.md:1–155`, blob `2b1143d14d0bff9153d6092ab12c80dfb2a637d9`: public growth/length/capacity and operation contracts, with its own historical test attribution.
- **R6:** `docs/CHANGELOG.md:1–72`, blob `9f7dfdaa3c6fde5ec3293504374f326d8f4a2f1c`: v416 plan and bounded-leak claim; older performance figures are reported history, not evidence of the new design.
- **R7:** `ChatGPT-to-Sarvam/ROUND-137-VOCABULARY-K0-FREEZE.md`, blob `7d8c53cb2557a65465b08811b76d24690c4eb3b3`: opening re-read at this pin; complete earlier report is in the conversation. Its frozen scalar-only/K0 and baseline boundaries are retained, not silently broadened.
- **R8:** `Claude-to-Sarvam/R59-00-MEMORY-COST.md:1–160`, blob `1e56e39f3df95075e66a0c6166b7510ab2642e94`: prior allocator measurements and zeroing observations, not remeasured here.
- Instructions read: `AGENTS.md`, the current `PROJECT-MASTER.md` opening, relevant design-charter material and `LANGUAGE-PRIORITY.md`. Documentation-only/Sanskrit-only scope retained; Windows remains the owner's work.

### External primary references checked 29 October 2026

- **W1:** Linux man-pages, `mremap(2)`: https://man7.org/linux/man-pages/man2/mremap.2.html — in-place failure and the consequences of permitting movement.
- **W2:** Linux man-pages, `mmap(2)`: https://man7.org/linux/man-pages/man2/mmap.2.html — fixed-address overlap behavior. Used only for the fallback-mapping boundary, not as Sutram's language contract.

### Status

**Completed:** corrected-plan critique; conditional no-overlap reasoning; concrete alias-behavior counterexample with separate observed/predicted columns; explicit option-(b) recommendation; retention-bound qualification; K0 collection boundary; 16 proposed acceptance gates.

**NOT RUN — no native toolchain invoked:** Sutram compiler, modified allocator, alias reproduction, tail-growth/OOM/fault-injection probes, memory benchmarks, regression/proof suite, Linux/Windows execution and byte-identity guard. No measured post-change output, performance, memory bound or safety certification is claimed.

**NOT APPLIED:** compiler/library/test/tool/canonical-document edits, diagnostic renames, language-pack updates, workflow changes, Windows changes or backups. This return does not independently close R137's full-corpus vocabulary-search gate; acceptance of its scoped report was not a claim that the missing census ran.

**Delivery:** one new Markdown file under `ChatGPT-to-Sarvam/`; read back the complete report and verify the commit diff before reporting return completion. Stop after Round 138.
