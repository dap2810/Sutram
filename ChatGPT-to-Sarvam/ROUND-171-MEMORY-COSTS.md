# R171 — memory costs, the budget's boundary, and parimita

Date: 2026-11-02. Read-side design/audit; documentation-only return to Sarvam.

Reviewed base: `bbb7c17ffe31ac35b636f7f0e1d5a3eb1efe89a7`, identified by the brief as compiler v283. Pre-delivery main advanced to `e0878627020e3cdda408a015dd77ad8b7d32df16`; that change adds only Muse's R98 report and census. The allocator and collision-scan inputs are unchanged.

**Recommendation: build the small budget first.** Its allocation-path cost is small and it needs no handle ABI or per-object metadata. It bounds only the allocations actually charged to it. The currently assigned `mandapa parimita B` experiment is narrower than a whole-program allocator cap. Do not describe it as fixing collection reclamation, lifetime safety, or total process memory.

## WS1 — price table

All instruction counts below are **estimates for emitted x86-64 successful paths**, not measured results, disassembly counts, cycles, or latency bounds. They exclude register spills, caller setup, failure diagnostics, page faults and OS allocator work. Memory figures describe the **proposed R170 layout**, not current v283 objects. A count of instructions cannot establish a speed ratio: dependent loads and cache misses matter.

| Mechanism and operation | Estimated additional instructions | Bytes attributable to it | Effect on existing code |
|---|---|---|---|
| Generation/liveness validation on each checked load/store | Roughly **10–16** for object and owning-region generation/liveness checks once table addresses are available; a single resolved generation equality test alone is about **3**. Slot validation and resolution are additional. | **24/object** for object generation, region slot and region generation; **8/handle** generation; region's own generation/state storage is shared per region. These fields are inside the totals below. | Paid on accesses in the proposed checked profile. Cannot protect old raw addresses by silently adding this sequence. No global conversion of the current ABI. |
| Stable descriptor indirection on each checked load/store | Roughly **3–6** for slot-to-descriptor address calculation and payload-base load, assuming validated input/table base; with descriptor address already available, the extra base load itself is **1**. Cache miss cost unknown. | **8/object** payload-base field and **8/handle** slot field, within the same totals. Table capacity/free slots also consume memory. | References follow the object's current backing store after relocation only in the new representation. Extra dependency on each access; legacy pointer-width values cannot transparently become four-word handles. |
| Full proposed release on block exit (`visarjana`, working R170 label only) | **10–30 fixed + 15–50 per owned descriptor**, before underlying allocator work. Traversing N owned objects is **O(N)**. These ranges are provisional because the free-list/allocator is not built. | **16/object** next/previous ownership links, within the 96-byte descriptor; owner list/state within the region record. | This is new cleanup work. Current ELF scratch rewind restores a cursor; it does not walk/release persistent koshes. The two operations are not interchangeable. |
| Narrow scratch `parimita` allocation check | **3** extra instructions for a precomputed active floor, after existing request validation, alignment and candidate-cursor arithmetic. Roughly **8–16** setup instructions at block entry and **2–4** at each cleanup, layout-dependent. No read/write checks. | **0/object**, **8 bytes** active-floor state per single-threaded program and **8 bytes per active budget block** to save the caller's floor, beyond the existing mark. Frame padding/diagnostic data additional. | No value ABI change. Preserving zero overhead outside budgeted syntax requires a limited/static coverage contract; checking dynamically inherited budgets in every scratch allocator adds the check to those legacy paths too. |
| General allocation-counter form of `parimita` | About **5** for load/compare/branch/subtract/store once the normalized charge exists; request/header/alignment arithmetic, validation and allocator operations additional. | **0/object** without individual reclamation; at least **8 bytes/counter** plus nesting/accounting state. A region may keep budget and usage as two words instead. | All covered allocation and growth paths must participate, including in-place growth and fallback. This broader contract is more work than the scratch-floor experiment. |

**Do not add the byte columns as separate allocations.** R170's budgeted full layout is **96 bytes/object descriptor**, approximately **16 bytes/backing allocation** allocator metadata plus alignment, **32 bytes/live handle**, and approximately **96 bytes/region**. The table attributes selected fields inside those totals. Multiple handles multiply the handle cost; unused table capacity, fragmentation and retained/retired slots also count. A 32-byte payload therefore can carry substantially more metadata than data in this first uncompressed design.

The full successful access path remains the R170 **25–45 instruction estimate**, including resolution, identity, type and bounds checks. It is not just the generation-test row. R170 allocation **50–120 plus zeroing**, explicit release **20–60 plus allocator work**, and the exit range above remain planning figures. End-to-end timing, cache behavior, optimizer elimination and source-line totals are **unknown until implemented and measured**. No 200-line promise for nested budgets or the full design follows from these figures.

## WS2 — “one compare” and the exact guarantee

**Cheap is plausible; literally one instruction is incomplete.** With a normalized charge already in `rdx`, a simple remaining-counter sequence is:

```asm
mov rcx, [remaining]
cmp rdx, rcx
ja  budget_full
sub rcx, rdx
mov [remaining], rcx
```

That is five successful-path instructions, excluding size/alignment checks and the allocation itself. If allocation can subsequently fail, charge must be committed only on success or rolled back. A subtraction that wraps is not a valid budget check.

For the existing downward-growing scratch cursor, a counter update can be avoided: the cursor already accounts for consumption. Once `rdx` is the validated proposed cursor, a separate budget floor needs:

```asm
mov rcx, [active_floor]
cmp rdx, rcx
jb  budget_full
```

This is a **hand-counted illustration**, not a source patch or verified emitted sequence. Keep the existing persistent-cursor collision check. Apply the floor check **before** publishing the scratch cursor or zeroing the payload. A single-threaded LIFO floor scheme has constant allocation cost; it need not scan ancestor budgets.

### Minimum contract for Claude R102's block experiment

Use `mandapa parimita 65536 { ... }` with an explicitly defined integer byte budget. A literal-only first implementation is reasonable. This is a cap, not a promise that allocation will succeed.

1. **Charge actual scratch displacement**, including 16-byte alignment. A positive one-byte request consumes 16 charged bytes under the current layout. Zero-size behavior should stay explicitly defined; a zero budget must permit no positive allocation. Reject negative/invalid budgets and guard arithmetic before subtraction/rounding.
2. On entry save the old floor and mark. Compute a lower bound from the new budget, clamp it to valid arena bounds without underflow, and combine it with the active ancestor floor using the stricter bound. An inner large budget must not relax an outer small budget. Check the moving persistent cursor separately.
3. Restore the saved floor with the mark on normal exit, `nivartanam`, break/continue paths and any other nonterminating unwinding path. Recursion requires saved state per invocation. Reclaimed child scratch may be reused within the parent's cap: this is a bound on simultaneously charged scratch, not lifetime allocation traffic.
4. On exhaustion, issue the named Sanskrit failure and refuse **before** the offending allocation. No fallback borrowing outside the budget for a path claimed to be covered.
5. State which allocators participate. Current `kosh` backing storage is persistent, and helper calls can allocate through other paths. Either include those paths in the accounting, reject unsupported allocating operations/calls inside the claimed boundary, or advertise the first version strictly as a **scratch-allocation cap**. Merely being textually inside a block is insufficient.

The floor example itself covers only scratch. A dynamic active floor cannot constrain a helper that uses the persistent allocator. Conversely, emitting checks only in lexically budgeted code cannot enforce an inherited runtime budget in independently compiled callees. This coverage choice must be settled in the implementation and its wording.

### What gap 1 means after the change

**Yes:** without reuse, a finite cap plus complete accounting and fail-closed refusal bounds the covered allocation domain. It turns unlimited growth into finite work followed by refusal. If every charged positive request uses at least one byte, an indefinitely allocating loop must eventually stop.

**No:** it does not let that loop run forever with useful allocations. Sustainable execution needs reclamation/reuse, bounded live demand, or application changes. Existing scratch reset already supplies reuse for the supported per-iteration block shape.

**A block budget alone does not establish a whole-program bound.** In v283, `r65_emit_nirm` has a per-call mmap fallback outside the arena; current kosh storage survives scratch rewind. A complete program cap needs all persistent/scratch allocations, growth, fallback and metadata covered, including transient old-plus-new capacity when copying. The current 1 GiB virtual arena reservation is not the same quantity as a scratch byte budget or resident memory.

The budget does **not** solve:

- stale references, escaped scratch aliases, use-after-free/reuse, bounds errors or integer-to-pointer laundering;
- alias repair when a kosh relocates, or reclamation of a fresh persistent kosh on each iteration;
- unreachable objects retained in a still-live region, fragmentation or delayed OS release;
- total RSS/address-space limits, stacks, compiler memory, foreign allocations or raw system calls outside its accounting;
- OOM below the cap, performance guarantees, concurrency, or Windows parity.

The other R170 mechanisms may wait. They remain necessary for their respective promises; the budget does not substitute for them.

### Acceptance that distinguishes bound from reuse

Use **1 MiB = 1,048,576 bytes**, explicitly, and a positive 64-byte allocation in each iteration.

| Program shape | Expected design result; NOT RUN here |
|---|---|
| One budgeted block enclosing a loop | With no other charged storage, 16,384 allocations fit; the 16,385th refuses. An attempted million does not complete. |
| Fresh budgeted block inside each iteration | A million iterations can complete if each iteration stays below its cap and scratch reset works. The same storage is reused. |
| Nested blocks with a larger child cap | Child cannot exceed the parent's remaining simultaneous-storage allowance. |
| Boundary, overflow and control-flow cases | Exact fit succeeds; next aligned charge refuses; invalid sizes cannot wrap; early exits and recursion restore the caller's floor. |
| Persistent kosh or allocating helper inside a block | Must demonstrate the declared coverage policy; a scratch-only cap is not acceptance for these paths. |

These are proposed acceptance cases, not new goldens. Report successful and refusing runs separately with exact source, compiler/base/hash, harness, exit, correctness output and peak units. RSS is an observation alongside byte accounting, not a substitute for proving the cap.

## The requested ~100 MB program

The R101 evidence already contains the exact program. This is `kb1.sm`, reproduced from `Claude-to-Sarvam/evidence-r101/memory-measurements.txt`:

```text
mukhya() {
    vitti i = 0
    vitti s = 0
    yavat (i < 100000) {
        mandapa {
            kosh k[1]
            vitti j = 0
            yavat (j < 100) {
                kosh_push(k, j)
                j = j + 1
            }
            s = s + k[99]
        }
        i = i + 1
    }
    likha("s ", s)
}
```

It creates **100,000 distinct koshes**, each receiving **100 pushes**: **10,000,000 pushes total**. It does not push one million times into one kosh. The expected arithmetic result is `s 9900000`; that is a calculation, not an output captured in this review.

R101 reports `peak_rss_kb 104576 exit 0` for this program, 101,504 for the no-block version, and 0 for a single kosh allocated outside and cleared/reused each iteration. Those are **Claude-reported Linux measurements, not reproduced here**. At final capacity 128, the 100,000 separate data areas alone account for 102,400,000 bytes before headers/alignment. This makes the order of magnitude understandable; it is not an exact RSS derivation.

The checked-in harness is `tools/peak_rss.py` calling `tools/peak_rss.asm`: the small native parent forks/execs the child and reads wait4 resource usage; the child's stdout is discarded. `tests/r101/test_memory_claims.py` embeds the same block program and invokes the wrapper with `--repeat 2`.

R101's separate one-growing-kosh results are 768 KB at 100k pushes, 7,808 KB at 1M and 78,080 KB at 10M. Interleaving other allocations gives another curve. Consequently:

- The ~100 MB observation and a single-growing-kosh observation are **different workloads**, so they are not directly contradictory.
- A growing collection retaining N eight-byte elements needs at least 8N data bytes. Its absolute storage is not constant as N grows.
- A geometric-growth bound on abandoned backing buffers, where applicable, is a bound relative to final capacity, not a constant-memory claim and not reclamation of many separately created objects.
- Sarvam's exact programs/harness and baselines are not included in the R171 brief. I cannot declare its near-flat absolute RSS values correct or erroneous from three numbers, nor say both harnesses agree numerically. Record identical source and correctness output before adjudicating that discrepancy. A baseline can hide small growth; it does not explain every result automatically.

Muse R98 independently identifies the same program. Its stronger “flat”/“both measurements stand” wording is not established by this source-only review.

**Two concrete harness issues for the implementation owner:** `peak_rss.py` prints the maximum peak across repeats with `runs[-1][1]`, the last run's exit only. An earlier failed/signalled child can therefore be hidden by a final successful child. Preserve peak/exit pairs and require every intended successful run to succeed. Also, the memory gate checks exits/thresholds but does not verify the child's output because stdout is discarded; add a separate correctness run or capture bounded output. These findings are from source inspection; no harness edit or execution is included.

## WS3 — parimita: accept, with an exact evidence boundary

**Accept `parimita` for an enforced byte cap.**

| Test | Verdict and evidence |
|---|---|
| Complete attested word | **PASS.** परिमित / parimita is a complete dictionary headword, an adjective/participle, with senses including measured and limited. It is not a shortened English token or invented compound. |
| Collision in requested scope | **PASS at the pinned base.** Full-content, case-insensitive substring scan for `parimita` and `परिमित`: **0 hits** in `lang/sanskrit.lang` (1 file), recursive `lib/` (24 files), and recursive `examples/` (336 files). |
| Eight-letter typing | **ACCEPT as a design judgment.** Exactly eight ASCII letters; no diacritics needed. No student typing/usability study was performed. Preserve the whole word. |
| Fit for semantics | **ACCEPT.** “Limited” describes an enforced cap clearly. Prefer it for this construct; there is no evidence establishing it objectively better than every Sanskrit alternative. A word's dictionary meaning does not itself specify fail-closed behavior: the implementation contract must. |

Dictionary checked 2026-11-02: [Monier-Williams, University of Hyderabad, परिमित entry](https://sanskrit.uohyd.ac.in/SKT/MW/151.html). The dictionary provides lexical evidence, not a native-speaker endorsement of the syntax.

Collision method: a nontruncated recursive Git tree identified **361 blobs / 416,556 source-listed bytes**. Every file was fetched at the pinned commit and its returned blob SHA matched the tree entry. The scan included comments, strings, fixtures and nested directories, not only identifiers. **0 fetch failures.** The adjacent JSON manifest lists all paths and blob hashes. This proves absence in that scope at that revision, not absence throughout the repository or in frozen packs. Recheck when integrating new source.

Use the word contextually after `mandapa` if the parser permits, avoiding unnecessary global identifier reservation. Only this new word is reviewed for this build; the other R170 names remain deferred.

## Verification and delivery

Performed here: read the R171/R102 assignments, allocator source, R101 exact programs and harness/gate, Muse R98, dictionary entry; independently scanned the complete requested naming scope; hand-counted illustrative instruction sequences and checked size arithmetic.

**NOT RUN:** native compiler/build, new syntax, emitted instruction counts, runtime cases, RSS/timing, full suite, Windows, installer or CI. NASM was unavailable in the previously checked environment; no native test result is inferred from another contributor's logs.

Only documentation under `ChatGPT-to-Sarvam/` is delivered: this report, the collision evidence manifest, and SHA-256 checksums. Implementation remains with the assigned owner.

Primary repository evidence at the reviewed base:
- `Sarvam-to-ChatGPT/ROUND-171.md`; `Sarvam-to-Claude/ROUND-102.md`
- `src/r65_arena.inc` (blob `11aed1b78a494b95576dcf6d5020c47645929fc0`): persistent fallback, scratch allocation/rewind and kosh extension
- `Claude-to-Sarvam/R101-00-MEMORY-MEASURED.md`
- `Claude-to-Sarvam/evidence-r101/memory-measurements.txt`
- `tools/peak_rss.py`, `tools/peak_rss.asm`, `tests/r101/test_memory_claims.py`
- `ChatGPT-to-Sarvam/ROUND-170-MEMORY-DESIGN.md` for full proposed layout and safety boundary
- `Muse-to-Sarvam/ROUND-98-CENSUS-PARIMITA-MALA.md` at pre-delivery main; cited as an independent report, not a test run here

