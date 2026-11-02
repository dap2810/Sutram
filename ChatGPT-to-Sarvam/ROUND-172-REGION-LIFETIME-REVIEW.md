# R172 — regions reduce indirection; they do not erase lifetime identity

**Read-side audit and revised design costs — 2026-11-02.**
Pinned main: `4ef00a432a2f9f8ee1490a1e9092514ebb1b709d` (compiler v284).
Deliverable: documentation only in `ChatGPT-to-Sarvam/`. No source, test, pack, Windows or CI changes.

**Answer:** a genuinely nonmoving, collectively reclaimed design can drop the per-object payload indirection and reduce a simple region-epoch test to roughly three instructions under stated assumptions. **Current v284 does not yet satisfy that premise:** it still relocates, and its existing stale-reference check reads metadata inside the storage that would be unmapped. Block exit does not make that check redundant. Accept `samskara` as the internal/documentation name for the saved incarnation mark; there is no need to make programmers supply it.

## 1. Correct the v284 premise before deleting mechanisms

The R172 preamble says every kosh never moves and aliases can no longer diverge. The implementation and R101A's own qualifications do not establish that.

In `src/sutram_compiler.asm`:

- `R101A_REGION = 0x04000000`: **64 MiB**, not 64 decimal MB.
- `R101A_MAXCAP = (R101A_REGION - 40) / 8 = 8,388,603`.
- The push path computes `newcap = cap ? cap * 2 : 4`.
- `r101a_emit_kosh_extend` emits `cmp r11, R101A_MAXCAP; ja relocate`.
- The relocating path allocates through `emit_nirmmita_from_rax`, copies the old elements, and updates **the pushed variable** using `emit_store_named_var`. Other aliases are not updated.
- Region mode is off for PE, GUARD_PAGES and `--fail-alloc`.

**The limit is compared with proposed capacity, not element count.** Starting at `kosh k[1]`, capacity doubles up to 4,194,304. Push **4,194,305** proposes capacity 8,388,608, which exceeds 8,388,603, and therefore relocates. It can happen much earlier than the documented “past 8,388,603 elements.”

It is also **not a one-time relocation**. On push **8,388,609**, proposed capacity is 16,777,216 and the same comparison again selects relocation. Region-enabled code bypasses the old arena-extension attempt at code generation, including on these later growths. Thus the reported 9-million-push sum test crosses two relocation points from initial capacity one. Checking the sum through `k` tests value preservation; it does not test an alias saved before a move.

A larger reservation delays this boundary; it does not remove the semantic problem.

### Proposed reproducer for the implementation owner — NOT RUN

```text
mukhya() {
    kosh k[1]
    vitti i = 0
    yavat (i < 4194304) {
        kosh_push(k, i)
        i = i + 1
    }
    vitti a = k
    kosh_push(k, 4194304)
    k[0] = 99
    likha("a[0]=", a[0], " k[0]=", k[0])
}
```

Source-derived prediction on the reviewed region-enabled ELF path: `a[0]=0 k[0]=99`. **No executable was produced or run here.** Test immediately before/after the boundary and again at 8,388,609, keeping aliases across both transitions.

**Implementation choice:** if “never moves” is the contract, refuse growth that cannot remain in the reservation, before changing length/data/identity. Optionally clamp the last capacity increase to the actual reservation limit; that changes capacity-doubling behavior and needs an explicit test. If relocating fallback remains, retain an indirection/handle mechanism for aliases or document the restricted guarantee. An attempted in-place OS extension may fail; it still needs a nonmoving failure policy.

The 86-program comparison is useful evidence for those programs. It does not prove the universal claim or cover the boundary above.

## WS1 — what the descriptor still buys, and the revised price

Separate three jobs that R170 combined:

1. **Payload address indirection:** lets all aliases find a replacement buffer.
2. **Persistent identity metadata:** lets a reference be validated without touching freed payload or an expired stack frame.
3. **Ownership/accounting metadata:** identifies what cleanup must release and what the budget charges.

If addresses truly never change, job 1 can disappear. Jobs 2 and 3 remain when escaped references must be diagnosed and storage can be recycled. A compact lifetime table is enough for some designs; it need not be R170's full 96-byte object descriptor.

### A narrower design that earns the lower cost

Assumptions: single-threaded execution; enforced nonmoving allocations; objects in a lifetime group all die together; no independent object free/reset or ownership transfer; typed references cannot be forged or laundered through integers; all relevant aliases/calls preserve the reference identity.

Use:

- A reference containing **payload pointer + lifetime-slot index + saved generation**: **24 bytes** on x86-64.
- A stable, separately allocated epoch table. A slot is zero when dead; live generations are nonzero and never repeated. Retire/refuse on counter exhaustion rather than wrap. Slot reuse gives the slot a different generation.
- One epoch per owning **block invocation/lifetime group**, not necessarily per OS mapping. A block can own many independently mapped koshes. “Each kosh has an mmap region” and “each kosh needs its own generation” are different decisions.
- A cleanup record for each owned mapping, independent of any moving variable.

For a trusted, nonnull typed reference with validated slot and values already in registers, the lifetime test can be:

```asm
mov rax, [epoch_table + slot*8]
cmp rax, saved_generation
jne stale_reference
```

**Three illustrative instructions.** No payload header has been read. This works because zero cannot be a live saved generation. Slot range checks, null handling and loading the reference fields must happen where required; the three-instruction figure excludes them.

| Operation/design | Revised estimated cost | Qualification |
|---|---|---|
| Payload-base indirection with true nonmovement | **0 extra base loads** | Pointer is in the reference. v284's relocating fallback prevents applying this universally today. |
| Single owning-lifetime generation check | **3 instructions** with resolved/validated operands; roughly **6–10** including ordinary field loads, slot/null validation, depending on representation | Replaces the earlier 10–16 estimate only when both object and owner identity are no longer independently necessary. |
| Reference statically proven unable to outlive owner | **0 dynamic generation checks** at that access | Requires an actual escape/borrow proof and invalidation rules across calls; current R82 is not that proof. |
| Independent object free/reuse while the owner remains live | Retain object identity and owner validation; **no general reduction established** | A shared block epoch cannot distinguish two incarnations within one still-live block. |
| Current v284 legacy representation | **No automatic cost reduction** | Removing checks or metadata now changes guarantees; it does not implement the narrowed design. |

These are **design estimates**, not measured timings or emitted-code counts. Type/bounds checks are still separate. I do not claim a newly measured total-access cost or an unchanged ABI.

The 24-byte reference is three times the current eight-byte address. If an exact old block line must survive slot reuse through arbitrary polymorphic calls, carry an immutable origin/site ID as well (**32 bytes/reference**), or provide an equally sound provenance mechanism. Reading the current occupant's line from a reused slot is wrong. Slices and additional bounds may need more fields.

Estimated minimal cleanup record: `next, mapping_base, mapping_length` = **24 bytes/mapping**; allocator-kind/owner bookkeeping can make it **32 bytes or more**. A simple lifetime record can budget **32–48 bytes/slot**, plus table/free-list storage. These are **layout proposals**, not commitments or measured memory use. The existing payload length/capacity header remains; do not count removed R82 header fields as savings before the replacement ABI exists.

**Decision:** the full general descriptor design can be deferred for a deliberately narrower model. Stable lifetime metadata cannot be dropped merely because a payload normally stays put.

## WS2 — returning regions at block exit

**Prefer eventual deterministic reclamation of owned regions at block exit, with safe reference validation installed first. Do not add unconditional munmap to the existing R82 representation.**

The current check deliberately depends on retained storage:

- `r82_emit_check` reads `[payload-32]` to find the stack liveness slot.
- It then compares the slot generation with `[payload-24]`.
- On failure it reads `[payload-40]` for the block line.
- `r82_param_checks` applies this at typed kosh parameter entry; it is not a universal check on every raw-address access.
- `examples/287_r82_kosh_after_mandapa.sm` explicitly stores `bahar = k` and calls `padh(bahar, 0)` after the block. Existing tests also cover sibling blocks, nested blocks and loop reentry.

Unmapping the payload makes the first header access invalid. If the same virtual address later holds another object, a raw address alone cannot distinguish the old reference from the new one. **A table keyed only by address does not solve that ambiguity.** The reference must retain its expected identity, or static rules must prevent it from surviving.

A liveness table “owned by the block” must therefore mean the block updates it, **not that its storage is freed with the block**. Validation metadata must remain safely addressable across dead references and slot reuse. Never relocate the only expected-generation copy into memory that cleanup destroys.

### Is the generation check redundant?

**Only where nonescape is proved.** A statically restricted subset can reject escaped block references and use zero dynamic lifetime checks for proven local accesses. That would change acceptance of programs such as example 287 from runtime diagnosis to compile-time rejection and needs a deliberate compatibility policy.

For today's permitted escape-and-diagnose behavior, the check remains necessary; reclamation makes checking **before any payload access** more important. “The object dies” is a lifetime rule. It is not proof that all copies of its address disappear.

Keeping mappings for the whole process avoids use-after-unmap but still requires enforcement if use after a block is a language error. Region liveness and object relocation are independent concerns.

### Entry/exit cost

All new costs below are **estimates for userspace instructions**, excluding register spills, allocator slow paths and kernel work. Syscall counts are structural; syscall latency is **unknown here**.

| Path | Block entry | Allocation-time bookkeeping | Block exit |
|---|---|---|---|
| Existing scratch-only mark/rewind | Save mark; arena reservation may occur on first use | Existing downward allocation/zeroing | Restore cursor, no per-object unmap. This already exists. |
| Mapping cleanup with statically proved nonescape | Roughly **2–6** to initialize/save list state | Roughly **4–8** stores/loads to link a preallocated record; record allocation extra | Roughly **4–8 fixed + 8–16 per mapping**, plus **one munmap syscall per owned mapping** |
| Cleanup plus shared dynamic lifetime identity | Roughly **8–20** for slot acquisition/initialization and list state on an available-slot fast path | Same list cost; attaching reference identity additional | Roughly **6–12 fixed + 8–16 per mapping**, plus **one munmap syscall per mapping**; invalidate epoch before release |

Costs are illustrative for different implementations, not additive with every earlier R170 row. Empty blocks can be optimized; dynamic registration still needs a clear policy. A block with N independent owned mappings has **O(N)** cleanup, plus kernel work dependent on mappings/pages. It is not one cursor store. No millisecond or percentage regression for the 86 programs can be estimated responsibly from the current evidence.

A mapping record must save the **actual base and length**, including initially oversized regions. Do not derive the release length from a later logical capacity. Ownership logs must survive until cleanup has finished; read/link the next record before freeing memory that could contain it.

The present fallback is an additional trap: post-region growth allocates through the ordinary allocator, potentially into the shared arena. **Do not munmap an arbitrary buffer as if it were an independently owned mapping.** Either enforce nonmoving refusal or record allocator provenance and provide a matching release operation. Tracking only the latest kosh variable also misses prior buffers and aliases.

### Required behavior around blocks and calls

- A child block releases only mappings it owns. Borrowing an outer kosh must not transfer ownership.
- Growth of an outer-owned kosh inside a child must remain charged/owned by the outer lifetime, or be rejected under the initial narrow policy.
- Normal exit, return, break/continue, error propagation and recursion must unwind exactly the intended owners, once.
- Invalidate identity before storage reuse; retain enough independent provenance to diagnose an old reference after slot reuse.
- Reuse control records so a million one-object block iterations do not leave a million “small” tombstones behind. A finite generation counter must fail closed on exhaustion.
- Handle partial initialization and allocation failure before publishing a usable object; do not report released budget for a failed release. Failure policy must be explicit.

The region allocation sequence returns zero on mmap failure, while the declaration path proceeds to header stores without an intervening null check (both plain and R82 header emission). **Source finding, not an induced runtime failure:** add a fail-closed check before those writes. `--fail-alloc` turns region mode off, so existing injected-failure coverage does not exercise this new allocator path.

### Why releasing only pages is not the same fix

Linux `munmap` removes the mapping; accesses then fault unless another mapping later occupies that address. `MADV_DONTNEED` on private anonymous memory leaves a valid mapping whose discarded pages can return zero-filled on access. It does not provide generation identity or prevent stale writes. In current R82, zeroing the slot-address header can select the “outside a block” success path. Keeping a header page also preserves the minimum page cost for small koshes.

A permanent, never-reused reserved address can help avoid address reuse but consumes virtual address space indefinitely. Reserving 64 MiB for 100,000 objects totals **6.1035 TiB** of address space, distinct from RSS. It is not a bounded lifetime/reclamation solution.

Sources for the OS distinctions: [Linux mmap/munmap manual](https://man7.org/linux/man-pages/man2/munmap.2.html), [Linux madvise manual](https://man7.org/linux/man-pages/man2/madvise.2.html). The architectural conclusions are this review's inferences.

## Measurements: keep the workload and evidence labels

R101A `evidence-r101a/cost.txt` already provides the exact 100,000-fresh-kosh programs:

| Workload | Reported v283 peak | Reported v284 peak |
|---|---:|---:|
| 100,000 distinct koshes, each filled with 100 values, in per-iteration blocks | 104,576 KB | 400,000 KB |
| Same fresh-object pattern without blocks | 101,504 KB | 400,000 KB |
| One kosh cleared/reused each iteration | 0 KB reported | 0 KB reported |
| One kosh grown alone to 10 million | 78,080 KB | 176,384 KB |

These are **Claude-reported measurements, not rerun here**. Linux harness units are KiB despite the printed “KB” label. The fresh-object result is consistent in scale with 100,000 touched 4-KiB pages. A reported zero is not literal zero program memory.

The 100 MB question is again a workload mismatch: **100,000 separate objects / 10 million total pushes**, not one object receiving a million pushes. R171 already reproduced `kb1.sm`; R101A repeats it and supplies the changed result. The larger single-object result is also compatible with retained buffers across the two source-derived relocation points; exact RSS attribution still needs measurement.

R101A's approximately 4 microseconds per mmap is not isolated by the saved aggregate best-of-three program timings. Those include creation, page/header work, pushes and loop work. **No munmap timing is provided.** Do not carry 4 microseconds over as a release cost.

Sarvam's 200,000 function calls with/without a block are separately reported evidence; they do not measure kosh-region cleanup. Nor does increasing allocation traffic alone prove every allocation remained semantically live.

The R171 repeat-exit-status issue remains open: `tools/peak_rss.py` is unchanged in this diff. Validate each run's exit and correctness output, not just its peak. The new large-kosh check tests output but does not check that child's runtime return code; require both.

For a budget on top of regions, choose the accounted quantity explicitly: logical payload/capacity, allocated/touched storage, and virtual reservation are different. A 1-MiB cap on virtual reservation cannot admit a default 64-MiB reservation; a 1-MiB payload cap does not bound virtual space. Check in-place growth too. Scratch-floor accounting alone does not cover these independent kosh mappings.

## WS3 — samskara

**Yes: accept `samskara` (संस्कार; scholarly transliteration saṃskāra) as the replacement internal/design term.** It is an attested word; dictionary senses include preparation/refinement and an impression retained in memory. It is not literally the Sanskrit technical term “allocation generation counter.” Using the impression sense for a saved incarnation mark is a stated programming analogy, not a philological fact.

[Monier-Williams and Apte entries reproduced by Kosha](https://kosha.sanskrit.today/word/sa/saMskAra), checked 2026-11-02, support the attestation. I see no sufficient benefit in introducing another candidate this round.

**Engineering definition:** the reference carries the samskara of the lifetime incarnation in which it was created; access is allowed only while that saved value matches the live, independently stored identity. A timestamp or merely the current contents of reused payload is not that guarantee. Current `rdtsc | 1` is not a proof of nonrepeating generations; a checked counter with an explicit exhaustion policy is easier to specify.

**Vocabulary-rule application:** replace rejected `kalpasmriti` in design terminology, while keeping the mechanism compiler-managed. No new keyword or programmer-chosen generation number is needed. Rule 3 says the compiler should handle what the programmer need not name. Acceptance of the word does not certify an unbuilt runtime mechanism or native-speaker review.

Fresh full-content collision scan at this pinned revision: `samskara`, `saṃskāra` and `संस्कार`, case-insensitive substring search, **0 hits** in `lang/sanskrit.lang` (1), recursive `lib/` (24), and recursive `examples/` (336). **361 files, 416,531 source-listed bytes; every returned blob SHA matched the nontruncated Git tree; zero fetch failures.** The adjacent evidence JSON identifies each file. This is a scoped result, not a whole-repository or future-integration guarantee.

## Late cross-review: Muse R99

Before delivery, main advanced to `f60aa677144496796bed7f39f0f8cbe8111bec8b`, adding only Muse's R99 report and census; all audited source and naming-scan inputs are unchanged. I read its WS2 verdict. We agree to save a programmer-facing keyword. Its rationale needs two corrections before being used to remove machinery:

- Example 287 is a **runtime generation/liveness refusal**, not a lexical refusal. `r82_emit_check` performs the comparison that makes the reported refusal happen. Its success is evidence that the existing mechanism is doing work, not that generations have nothing to check. Avoiding a new handle system does not authorize removing R82.
- Generation identity and relocation indirection have different jobs. Stable descriptors solve following a moved buffer; an epoch distinguishes lifetime incarnations. Region retention can prevent a physical use-after-free while post-block use still violates the language's declared lifetime. Current relocation exceptions also remain real, with the earlier capacity-doubling boundary derived above.

Keep the narrower conclusion: a new exposed builtin is unnecessary now; a future reclamation path still needs proved nonescape or sound independent identity. Muse's illustrative `samskara(k)` is explicitly unimplemented and is not proposed as accepted syntax by this return.

## Handoff order and verification

1. Correct “never moves,” “past 8,388,603 elements” and “moves once” in the owner-maintained documentation; reproduce the boundary alias case.
2. Choose enforced nonmovement or a relocation-aware reference representation before deleting indirection.
3. For reclamation, choose proven nonescape or independent identity-bearing references. Preserve exact R82 diagnostics where promised; do not silently substitute a fault or a zeroed object.
4. Add allocation-failure, relocation-boundary, stale-alias-after-address/slot-reuse, nested-owner and early-exit cases. Measure cleanup and metadata high-water on the fresh-kosh workload.
5. Integrate the declared budget with the allocation paths and quantities it actually covers.

**Executed here:** source/evidence inspection; pinned full-content naming scan; arithmetic and illustrative instruction counting; check for NASM returned no executable.

**Native compiler build: NOT RUN — no toolchain. Boundary reproducer: NOT RUN — no toolchain. R82/new cleanup tests: NOT RUN — no toolchain. RSS/timing: NOT RUN — no toolchain. Full suite/proofs/gates: NOT RUN — no toolchain. Native Windows/installer/CI: NOT RUN.** Reported passes remain attributed to their authors.

This return cannot verify whether the owner requested Option A in Claude's separate session. R103 correctly asks that author to distinguish an actual instruction from an inference; no owner approval is inferred here.

Key source evidence: `src/sutram_compiler.asm` blob `d27f0d8109825361c16686058c31dc640464a533`; `src/r65_arena.inc`; `examples/287_r82_kosh_after_mandapa.sm`; `tests/r82_kosh_mandapa/test_kosh_mandapa.py`; the R101A report and cost/disassembly evidence; R172/R103 briefs; `docs/vocabulary/VOCABULARY-RULE.md`. No implementation is claimed.

