# Sutram ROUND 140 — library write footprints, a numerical release gate, and the actual K0 scope

**Date:** 30 October 2026. **Pinned main:** `ace0a4e9f5d7f1cdff2dea771f5ffc8cbc9e42a1`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-140.md`, blob `0ee57d15de34d175c0269cfc333a9cca5742ba17`.
**Return:** `ChatGPT-to-Sarvam/ROUND-140-LIBRARY-CAPACITY-SAFETY-BAR.md`.
**Observed baseline:** compiler v263; changelog opens at v418. The library tree is `e674529588a78ef1023d64754725cd5136d32bbb`, unchanged from the preceding audit. Findings below apply to that pin, not to an uninspected concurrent repair.

## Answers first

1. **The class deserves more work than only fixing `pad_vam`.** That function has a false explicit numeric capacity minimum. Two splitters also have contradictory zero-limit behavior. Three segment exporters require attention to a trailing qword outside the length-prefixed representation. Those last three are **capacity-specification gaps, not three additional proved violations of an explicit numeric minimum**: comments already mention termination in some places. The distinction matters.
2. **A practical release gate:** rerun the existing stage-separated corpus and suites; add the **48 named deterministic fixtures** below, plus a reproducible **10-seed × 100,000-operation campaign**. Require **zero unexplained corruption, unexpected failures or unapproved semantic differences**. Also complete a capacity ledger for every library destination write. This qualifies a named release/profile; no finite program count proves unrestricted raw-pointer Sutram memory-safe.
3. **Retention is pass/fail:** zero retired backing bytes in the specified uninterrupted single-tail fixture; for two monotone alternating vectors, `R_payload <= 16*N` and `R_reserved <= 16*N + 32*G`, plus a proposed **64 MiB retired-storage budget per declared finite workload**. Definitions and exact expected counts follow. These are proposed qualification limits, not limits v263 enforces.
4. **K0 is a small, opt-in scalar-scratch feature.** Its checked function cannot contain unsupported `kosh` values or operations. It can hold fixed-size scalar-only buffers with proved accesses; it is **not the general memory model**, not a region around arbitrary vector-heavy code, and not implemented merely because v263 has a bump allocator.

## WS1 — what the source actually writes

### Method and limits

I freshly read all **24 live `lib/*.smlib` source files** at the pin, comparing caller-capacity statements, element units, loop endpoints, terminators and delegated writers. This is a source-level capacity screen, not an exhaustive proof of all integer domains, malformed pointers, aliasing combinations or mathematical algorithms. It did not execute any Sutram program.

Use three classifications:

- **A — numeric contract mismatch:** the stated minimum permits a buffer smaller than the body's write footprint on an ordinary supported path.
- **B — limit-contract inconsistency:** the stated limit is bypassed; resolve the API's zero case before treating a caller's zero-output allocation as safe.
- **C — footprint specification gap:** the implementation writes more than the encoded payload representation, but the public text does not state a numeric minimum falsely. Make the actual requirement explicit; do not manufacture an absent promise.

Unless otherwise stated, counts/lengths below are nonnegative, input buffers valid, arithmetic representable and output aliasing satisfies the routine's contract. A qword cell is eight bytes. Packed-byte buffers are a different representation.

### Findings table

Let `L = sum(1 + segment_length)` over the segments actually exported: one qword length followed by that segment's qword character cells.

| Function | Documented contract | Actual write bound | Gap / disposition |
|---|---|---|---|
| `vakyank.pad_vam` | Caller allocates at least `width` cells; left-pad when `width > count`. | On the padding path, writes content through `dst[width-1]`, then `dst[width]=0`: **width+1 cells**. With width 6/count 2: indices 0..6, **56 bytes**. The no-padding branch returns without writes. | **A, confirmed.** The stated minimum is one qword too short on the padding path. Preserve termination and correct the contract/callers, or deliberately specify a different behavior. Do not claim every generously allocated caller overruns. [R2] |
| `varna.varna_bhed` | Returns a segment count capped at `maxparts`; empty input/empty separator yields one segment. No positive-only minimum for `maxparts` is stated. | `sn==0` writes `parts[0]=0` and returns 1 before checking the limit. Nonempty input with `sepn<=0` writes `sn+1` cells and returns 1, also before checking it. | **B, confirmed contradiction at maxparts=0.** The cap and special-case promises disagree. Prefer zero limit -> zero segments/no writes, or specify and reject unsupported zero. Do not silently write one segment under a zero-limit claim. [R4] |
| `khand.khand_bhed` | Same capped segment-count promise and special cases, with qword length-prefixed parts. | Empty input writes one cell/returns 1 regardless of maxparts. Nonempty empty-separator case writes prefix + `sn` cells + helper terminator: **sn+2 cells**, returning 1 regardless of maxparts. | **B**, same zero-limit inconsistency; also the **C** extra-cell obligation below. A segment-count limit is not an output-byte capacity. [R3] |
| `khand.khand_bhed`, nonempty exported segments | Length-prefixed parts, same shape as `varna_bhed`. Module header says output buffers terminate; inline code mentions the helper's trailing zero. There is no exact public allocation formula. | Each `khand_mukt` writes a zero at the next length position. A final nonempty segment can therefore write `parts[L]`: **L+1 cells**, not just L. A final empty segment can consume that position as its legitimate length, so the extra cell is path-dependent. | **C, explicit formula missing.** Worst-case capacity must include one trailing cell, or replace the terminating copy with an exact cell copy. The terminator is not secret in the source; describing it as always harmless is unjustified without storage. [R3] |
| `nighantu.nighantu_kunjika` | Exports qword length-prefixed keys `[len, byte-cell...]`; returns key count. No numeric caller minimum. Inline comment acknowledges the trailing helper zero. | For a nonempty map, `khand_mukt` finally writes `out[L]=0`. **L+1 cells**; worst case with cap keys of length 32 is **33*cap+1 cells**. Empty map writes none. | **C.** Exact encoded L-cell allocation is insufficient. State the extra-cell requirement or eliminate the redundant terminator. This is NOT the packed-byte exporter. [R5] |
| `sangrah.rakh_tak_mala` | Sorted qword length-prefixed set elements, same shape as the map export; returns element count. No numeric caller minimum. | Nonempty result delegates to `khand_mukt` for each item and can write `out[L]`: **L+1 cells**, worst case **33*actual_map_capacity+1 cells**. Empty set writes none. | **C.** Same extra-cell footprint; sorted order does not change the capacity calculation. [R6] |

**Count honestly:** one explicit numeric minimum mismatch; one zero-limit defect family affecting two functions; three exporter footprints needing precise capacity contracts. `khand_bhed` belongs to two categories. This is not six independently demonstrated new allocator bugs.

### Small witnesses for the extra-cell family

These are source-derived expectations, **NOT RUN**:

- `khand_bhed("ab", 2, ",", 1, parts, 1)` exports one segment. Its representation is `[2,97,98]` (3 cells), but the helper also writes `parts[3]=0` (4 cells total).
- A valid one-slot map with a 32-byte key exports a 33-cell length-prefixed representation through `nighantu_kunjika`, but writes cell 33 as zero: **34 cells / 272 bytes**, not 33 cells / 264 bytes.
- The corresponding one-element set through `rakh_tak_mala` has the same 34-cell footprint.
- `varna_bhed` uses an explicit cell-copy loop rather than the terminating unpack helper. For the analogous nonempty, ordinary one-segment result it writes the L representation cells, not an extra final terminator. Do not mechanically impose one implementation's bound on both splitters.

For `maxparts=0`, exercise both empty-input and nonempty/empty-separator paths separately. The normal separator loop consults `nseg < maxp`; the special paths bypass it. This is why a test of only ordinary splitting would miss the issue.

### A refinement to the proposed `217` repair: respect both callees

R139's **56-byte minimum is correct for `pad_vam(..., width=6, ...)` on its padding path**. It is not the general buffer precondition of the entire example:

```text
ank_tak_varna(scores[i], koshtha)
pad_vam(koshtha, cnt, 6, 32)
```

`ank_tak_varna` explicitly requires **at least 22 cells** for its integer renderer. A repair honoring both published contracts is therefore:

```text
required_cells = max(22, width + 1)
width = 6 -> 22 cells -> 176 bytes
```

For the example's actual two-digit scores, a 56-byte buffer is sufficient for the accesses in those two calls. But it does not meet the renderer's unconditional documented 22-cell precondition. Prefer **176 bytes** for the general contract-respecting example repair, unless the renderer's contract is deliberately refined to a value-dependent bound. This does not reveal an overrun in the renderer: its documented 22 cells are sufficient. The old 32-byte caller and the library's false width-only padding minimum are separate problems. [R2, R11]

### Related gaps to document, without calling them the same proved bug

| Function / family | Actual obligation | What is and is not established |
|---|---|---|
| `ank_tak_aadhar_varna` | For nonnegative int64 and base 2..36, at most 63 digit cells plus one terminator: **64 cells**. Zero needs two cells; failure/invalid base writes one terminator cell. | The comment lacks a clear numeric destination minimum. No smaller numeric minimum was found to contradict. [R2] |
| `anukram_grah_aayam_purva` | `cap` limits the encoded source buffer; decoded `n` bytes need a destination of at least n bytes, plus a separate writable `out_n[0]` cell. No payload terminator. | The source-bound check does not measure destination capacity. State that caller obligation explicitly; do not describe its source `cap` as checking every destination. [R7] |
| Replacement/grouping formatters | Expansion can exceed input length; terminated output needs actual expanded length +1 in the correct unit. | “Allocate generously” is not an executable capacity formula. Absence of such a formula is a documentation gap, not evidence that a function exceeded an explicit numeric promise. [R3,R4,R8] |

### Controls that must NOT become false positives

- `khand_mukt` explicitly documents `out[n]` as a terminator cell. It needs `max(n,0)+1` qword cells; the defect is assuming its callers copy only n cells, not a hidden behavior of the helper.
- `khand_bandh` and `khand_pratilip` similarly document a terminator, but in **bytes**. Case conversion, trimming, joins and reversal follow their module/function termination conventions.
- `roop_pad_vam`, `roop_pad_dakshin` and `roop_pad_madhya` need `max(sn,width)+1` **bytes** for valid nonnegative lengths. The module explicitly promises termination; no width-only allocation minimum like the faulty `pad_vam` comment was found.
- `nighantu_kunjika_ashtak` explicitly writes packed length-byte segments **without a terminator**. Its `cap*33` byte bound fits valid maps. Do not add a qword to this different API.
- `nighantu_koshtha_likh` deliberately avoids the terminating string-copy helper for a full 32-byte key. Its exact key-slot loop stays within 32 bytes; this is an existing good example of the necessary distinction.
- `brihat_gun` explicitly needs 2n cells and writes through index 2n-1. Other reviewed bigint output loops stay within their stated n-cell outputs on valid input domains.
- `meru_mala` explicitly writes **a[0..n]**, so n+1 cells are already part of its stated range. It is not a new off-by-one contradiction.
- `nighantu_mulya` and `avali_tak_mala` require cap cells and emit at most the live count, without an extra terminator. `phal` documents two-cell Results and stores only cells 0 and 1. `patra_path_sarv` reads at most cap raw bytes and does not add a NUL.
- Raw `mala_sangrah` is explicitly unchecked. Supplying an out-of-range index is not proof that it violated a promised checked bound. Likewise forged container headers and inconsistent caller-supplied capacities are not valid-constructor fixtures.

### Coverage register

All 24 files were read. The focused conclusions are:

| Modules | Capacity screen result |
|---|---|
| `vakyank` | Explicit padding minimum mismatch; renderer/terminator obligations distinguished. |
| `khand`, `varna` | Zero-limit splitter inconsistency; `khand_bhed` extra-cell footprint; ordinary terminated string writers distinguished. |
| `nighantu`, `sangrah` | Qword segment-export trailing-cell requirements; packed-byte slot/export bounds separately checked. |
| `roop`, `aadhar`, `brihat` | Output units, expansion/terminators and n versus 2n bounds reviewed; no further explicit numeric-minimum contradiction established in the normal domains inspected. |
| `suchi`, `mala`, `shreni`, `patra`, `phal` | Count/capacity/header/output-cell loops screened with valid object and caller preconditions. No further finding of this exact class established. |
| `ganita`, `ganit`, `chandas`, `kalana`, `samanvaya` | Small output/status cells, explicit inclusive range or typed output lengths screened; no additional finding of this exact class established. |
| `ank`, `gudh`, `madhava`, `sadhan`, `sankhyiki` | Scalar computation or read-only memory in this screen; no caller-output capacity overrun identified. |

This is **not a blanket PASS for 305 routines**, all source inputs, all caller sites or native code generation. A complete machine-readable per-write contract ledger and executable boundary suite are still release work. No claim that every caller of the three exporters is currently underallocated is made.

## WS2 — a numerical, reproducible assurance bar

### What can honestly be called safe?

No test count licenses **“all Sutram programs are memory-safe”** while raw pointers, unchecked stores and unverified legacy calls exist. I would approve the narrower statement **“this pinned v263-derived release passed the documented allocator/library contract qualification on the named targets and workloads”** after the following gates. That is a concrete release bar, not a refusal to provide one.

1. **Zero open confirmed capacity-contract mismatches in the qualified surface.** Every destination write and delegated writer needs an explicit extent/unit/precondition entry. Every writer needs an exact-bound and empty/boundary test; failure exits must have stated writes. If 48 fixtures do not cover that complete ledger, add fixtures rather than marking missing coverage green.
2. **Rerun the existing 577-input stage-separated guard**, plus the existing suite/library/property/crash gates at the actual candidate commit. The previously reported 225/226/86/227 counts overlap different harnesses and are not summed into an invented total. Record intentional diagnostic/allocator changes separately. Zero unexplained output/exit differences; alias changes need an explicit approved contract, not a passing majority.
3. **Add 48 named deterministic source fixtures below.** Parameter sweeps, fault schedules and target/build modes are executions of those fixtures, not extra independent programs. Run positive and invalid-input cases against their predeclared expectations.
4. **Add 1,000,000 reproducible valid-domain operations:** ten published seeds, 100,000 operations each, with boundary-biased lengths, empty/full cases, alternating allocation patterns and a reference result/footprint oracle. Record seeds, binary hashes and exact failures. This is a stress campaign, not one million proofs or a probabilistic safety certificate.
5. **Zero unexpected red-zone changes, unexplained crashes, timeouts, missing checks or unapproved semantic deltas.** Negative calibration cases must demonstrate that the harness detects the known bad footprint. A clean final printed result is not enough.

Linux direct and object/separate output paths must be tested because both use the arena. PE retaining its old allocator is a compatibility control, not a test of Linux's new arena. Make any real-Windows execution claim only from real-Windows evidence. Allocation failure, logical growth failure and later memory access failure must not be conflated. No target or mode is credited from an unrun gate.

### The test that would have caught `pad_vam`

Place nonzero red-zone cells immediately after the **logical** destination, inside a larger harness-owned allocation. Inspect them immediately after the function call, before repacking or printing the destination. This avoids relying on page slack or on the next `nirmmita` landing at an exact address.

```sutram
# PROPOSED footprint probe for the pinned body; NOT RUN.
yoj vakyank
mukhya() {
    vitti slab = nirmmita(72)
    yadi (slab == 0) { nivartanam 1 }
    slab[0] = 123456789
    vitti p = slab + 8
    p[0] = 56
    p[1] = 53
    p[6] = 123456789
    p[7] = 123456789
    pad_vam(p, 2, 6, 32)
    likha(slab[0])
    likha(p[6])
    likha(p[7])
}
```

**Predicted from the current body, not executed:** `123456789`, `0`, `123456789` on separate lines. `p[6]` is the first cell outside a six-cell logical output; the function changes it. For the corrected seven-cell terminated-output contract, cell 6 is legitimate and `p[7]` is the first post-buffer canary. The 72-byte backing allocation owns the prefix, output and both probe positions: the harness is detecting a **logical API footprint**, not claiming the probe itself performs a native allocation-boundary fault.

Use a nonzero canary: an all-zero guard would miss a terminator store. Check a sufficiently wide surrounding red zone and, where available in the test harness, record write addresses/guard pages to catch skipped or transient stores. Canary equality alone cannot prove no read-overrun or write-then-restore occurred. For the byte-packed functions use byte guards, not cell counts. For exact-capacity APIs preserve expected terminators inside the buffer; do not classify every NUL as damage.

**Negative-case rule:** a raw API without a destination-capacity parameter cannot generally detect an undersized caller buffer. Such probes calibrate the harness or expose a false documented minimum; they do not establish a new promise that the raw API rejects every malformed pointer. Positive release cases must use the corrected, explicit contract.

### The 48 additional deterministic fixtures

Each ID below denotes a named source fixture, with all parameter values and expected outcomes frozen in its manifest. All are **PROPOSED / NOT RUN here**.

| ID | Fixture / parameters | Required observation |
|---|---|---|
| C01 | `pad_vam`, count 2, width 6, logical 32-byte destination | Negative calibration detects content/terminator beyond four cells. |
| C02 | Same, logical 48-byte destination | Detect the cell-6 terminator beyond six cells. |
| C03 | Same, logical 56-byte destination | Correct content/terminator; prefix and cell-7 canaries intact. |
| C04 | `pad_vam`, count equals width | No-padding branch has no unexpected stores; preserve declared input state. |
| C05 | `khand_mukt`, two bytes -> three qword cells | Exactly two data cells plus documented zero; next canary intact. |
| C06 | `khand_bhed`, `ab`, absent comma, maxparts 1, L=3 logical cells | Calibrate the current extra-cell footprint; do not mistake representation size for full capacity. |
| C07 | Same split with four cells | Correct segment and allowed trailing cell; next canary intact under a frozen terminated-parts contract. |
| C08 | `nighantu_kunjika`, one full 32-byte key, 33 logical cells | Calibrate write to cell 33; valid map constructed normally. |
| C09 | Same with 34 cells | Encoded key plus trailing zero fits; next guard intact. |
| C10 | `rakh_tak_mala`, one full 32-byte key, 33 logical cells | Calibrate same extra-cell write. |
| C11 | Same with 34 cells | Correct sorted representation; next guard intact. |
| C12 | `varna_bhed`, empty input, maxparts 0 | Resolve and freeze zero-limit policy: preferably return 0/no writes; never silently claim cap 0 while returning 1. |
| C13 | `varna_bhed`, nonempty input, empty separator, maxparts 0 | Same zero-limit gate on the other special path. |
| C14 | `khand_bhed`, empty input, maxparts 0 | Same zero-limit gate. |
| C15 | `khand_bhed`, nonempty input, empty separator, maxparts 0 | Same gate, including delegated unpack writes. |
| C16 | `nighantu_kunjika_ashtak`, one 32-byte key, 33 BYTES | Packed length plus key fits exactly; no invented terminator write. |
| C17 | `anukram_khip_i64`, pos 0, cap 8 | Exactly eight bytes, correct encoding, guards intact. |
| C18 | Same, cap 7 | Return -1 with destination untouched. |
| C19 | `ank_tak_varna`, INT64_MIN, 22 cells | Correct 20-character result/NUL within declared capacity. |
| C20 | `roop_dwi`, INT64_MIN, 66 bytes | Sign + 64 binary digits + NUL fit; byte guards intact. |
| A21 | `nirmmita(0)` before/after arena initialization | Specified zero result and consistent allocator state. |
| A22 | Adjacent one-byte allocations | Distinct nonoverlapping spans, alignment and zeroing as specified. |
| A23 | Adjacent 15-byte allocations | Rounding gap does not become caller capacity. |
| A24 | Adjacent 16-byte allocations | Exact aligned endpoints. |
| A25 | Adjacent 17-byte allocations | Rounded spans nonoverlapping; required bytes writable. |
| A26 | Request exactly remaining arena room | Correct last allocation and frontier. Use a separately identified test-size build if necessary. |
| A27 | Request remaining room plus one | Specified fallback, no corruption of old arena state. |
| A28 | Arena exhausted, subsequent allocations | Fallback accounting and old allocation contents preserved. |
| A29 | Initial reservation forced to fail | Correct fallback and failure-sentinel handling. |
| A30 | Reservation and fallback allocation both fail | Return/failure contract, no successful-object publication. |
| A31 | Zero/negative/huge arithmetic-boundary requests, classified by API domain | No accepted wrapped-small allocation masquerading as a valid huge object; explicit outcomes. |
| A32 | Mixed aligned/unaligned allocation sizes, writes and rereads | Nonoverlap, fresh-memory contract and retained contents. |
| S33 | Unaliased single-tail collection crosses several capacities | Correct length/capacity/data and actual in-place extension. |
| S34 | Copied alias; grow original at arena tail | Record approved sharing semantics and compare legacy baseline. |
| S35 | Same alias with an intervening allocation | Exercise copy/split branch; guard the intervening allocation. |
| S36 | Grow through the copied handle | Check both handles, not only the one being appended. |
| S37 | Alias carried via raw cell/global | Test documented legacy escape paths, not only adjacent local names. |
| S38 | Growth attempted on a by-value `kosh` parameter | Preserve intended compiler rejection; distinguish parameter mutation from local growth. |
| S39 | Appended-value helper allocates before growth | Tail decision follows value evaluation; helper allocation intact. |
| S40 | Initial capacities 3 and 5 across growth boundaries | Preserve arbitrary capacities, alignment and alias outcomes. |
| F41 | Failed backing allocation for `kosh` declaration | Explicit expected failure; no unchecked zero-pointer header store accepted as clean handling. |
| F42 | Failed backing allocation for fixed `mala` declaration | Same distinction. |
| F43 | Failed copy-growth allocation | Old object intact; no partial header/cursor/length publication. |
| F44 | Collection capacity/byte-size overflow boundaries | Reject invalid size before wrapped allocation/header write. |
| R45 | One unaliased kosh[1], 1,000,000 uninterrupted appends | Retired payload and retired reserved bytes both zero. |
| R46 | Two kosh[1], A then B alternately, 1,000,000 appends each | Instrument exact retired spans and check the bounds below. |
| R47 | Same two vectors, 524,289 appends each | Just-after-doubling boundary distinguishes payload from header/padding overhead. |
| R48 | Repeated bounded-size construction/discard | Report bytes retained per iteration and high-water; no false constant-memory service claim. |

**48 = 20 capacity + 12 allocator + 8 alias + 4 failure + 4 retention fixtures.** The first 20 do not cover every writer in the 24-module ledger; extend the boundary suite to cover the remainder before a whole-library qualification claim. A source fixture can have multiple executions/inputs; do not count duplicated modes as unrelated evidence.

If an authorized repair removes an extra terminator instead of documenting it, freeze the changed footprint first and adjust the corresponding positive fixture deliberately. Retain old-source negative calibration as history. Likewise decide zero-limit semantics before recording expectations, not after observing a failing test. Failure-injection numbering must specify whether it counts allocator calls or logical growth attempts.

### Numerical retention gates — exact pass/fail

Define `N` as aggregate successful appends in the named **unaliased, append-only** fixture; `G` as copy-growth events retiring a prior backing block; `R_payload` as retired old capacities times eight; `R_reserved` as those blocks' actual allocator spans. Exclude current live buffers, but report them separately. A live alias can make an old generation live data rather than reclaimable garbage.

For the arena layout in scope:

```text
span(C) = align16(16 + 8*C)
R_payload = sum(8*C_old) for copied-away generations
R_reserved = sum(span(C_old)) for those generations
```

| Qualified workload | PASS | FAIL |
|---|---|---|
| R45 single uninterrupted tail, sufficient arena space | `R_payload == 0` AND `R_reserved == 0` | **Any positive retired count or byte total.** Current capacity/slack does not count as retirement. |
| R46/R47 two monotone alternating vectors, arena-only storage | `R_payload <= 16*N` AND `R_reserved <= 16*N + 32*G` | Exceed either inequality. Count headers and alignment, not just payload. |
| Declared finite v1 workload using retention | Additionally `R_reserved <= 67,108,864` bytes (**64 MiB**) | Any measured point over that proposed workload cap. Owner approval required; not enforced by v263. |
| Indefinite fixed-working-set bounded-memory claim | Zero net persistent retention per completed iteration after warm-up, plus a fixed total bound | Sustained positive retention slope fails that claim, even below 64 MiB during a short run. |
| Correctness | Zero unauthorized writes or unapproved semantic changes | **One confirmed case fails.** Low memory use does not compensate. |

For one doubling chain from positive initial capacity c to final C, old payload sum is `8*(C-c)` in the all-copy case. For monotone appends to a chain that grew, `C < 2*n`; summing gives the 16-byte payload-per-append bound. Headers add 16 per retired block; qword capacities and 16-byte alignment add 0 or 8 bytes here. `32*G` is a deliberately conservative overhead allowance. These are cumulative bounds, not a per-individual-append allocation limit or a bound after arbitrary clear/pop/reconstruction.

**Calculated fixtures — arithmetic, not native measurements:** for two vectors initialized A then B at capacity 1, each shared capacity boundary makes A copy after B and then B copy after A. Assuming no unrelated allocation and sufficient arena space:

| Appends each | Aggregate N | Total G | Exact predicted retired reserved bytes | Coarse gate `16*N+32*G` |
|---:|---:|---:|---:|---:|
| 3 | 6 | 4 | 128 | 224 |
| 524,289 | 1,048,578 | 40 | 16,777,856 | 16,778,528 |
| 1,000,000 | 2,000,000 | 40 | 16,777,856 | 32,001,280 |

At one million each, retired payload is **16,777,200**, headers **640**, padding **16**; total **16,777,856**, or **8.388928 bytes per aggregate append**. Require measured accounting to agree with the actual copy/extension event trace; the coarse upper bound is not permission to conceal an unexplained discrepancy. Instrumentation must not itself allocate between the vectors and perturb the schedule.

**Correction to the broad v418 wording:** abandoned storage does not always stay below current storage when all overhead is counted. In the small three-append-each all-copy fixture, retired spans total **128 bytes**, while the two current capacity-4 spans total **96 bytes**. Payload-only geometric comparisons, total reserved spans, current logical length and RSS are different quantities. Clearing a collection or repeating its lifetime further invalidates a blanket “never exceeds memory in use” claim. The 64 MiB proposal is an operational budget, not an industry standard or a theorem of safety. Mapping fallback must be charged separately rather than hidden behind the finite arena size. [R10]

## WS3 — what `mandapa` can honestly hold in the initial K0 profile

**Plain answer: scalar scratch only, including fixed-size arrays of scalar cells with statically proved accesses. It is a small feature, not Sutram's complete memory model.** A buffer can hold several numeric values; “scalar-only” does not mean exactly one scalar. It means no retained pointer graph, growable collection or opaque carrier.

| Construct within a K0-checked function | Initial status |
|---|---|
| Scalar locals, scalar arithmetic, scalar results | Allowed under the existing value-kind rules. Ordinary lexical scalar scope does not taint numeric values. |
| Direct `nirmmita(C)` with known positive constant extent | Admitted fixed-size scratch inside the block, with the required allocation-failure/null proof. No dynamic-size exemption. |
| Constant-bounded numeric reads/writes to that buffer | Allowed after owner/liveness/null/extent proof. An array of numbers is possible; arbitrary dynamic indexing is not silently accepted. |
| Fresh immutable aliases or permitted constant offsets of an admitted reference | Allowed only with preserved owner/object/extent metadata and no outward escape. |
| Scalar result loaded from scratch and returned | Evaluate the complete expression while live, preserve result/status, then clean up exited regions. Do not return the pointer. |
| Verified scalar-only direct helper | Allowed only with exact-body/transitive effect approval. A scalar return type alone is not proof. |
| `kosh` / `kosh dasham` declaration anywhere in the containing checked function | **Rejected**, even outside the textual `mandapa` braces. |
| Collection alias, index/read/write, len/cap/empty, push/pop/peek/clear/enqueue/dequeue | **Rejected initially.** A harmless-looking scalar result does not establish a collection-aware proof. |
| Collection parameter/result; pointer-bearing struct, wrapper, slice or stored reference | **Rejected** by the initial unsupported-representation/carrier rules. |
| Unverified calls, indirect/FFI calls, unchecked raw-memory manipulation | **Rejected** inside the checked boundary; a familiar function name is not an intrinsic safety contract. |
| Legacy caller uses vectors and passes a numeric value into a checked helper | Possible separation: the helper is checked; the legacy caller and vector operations are not thereby certified. |

Consequently, **do not advertise wrapping an existing vector-processing function in `mandapa` as the v1 solution**. Initial uses are small fixed-layout numerical scratch calculations, predictable temporary cells and verified scalar helpers. A loop can repeat an allocation/block lifetime while each admitted access remains statically proved; this does not add dynamic indexing or arbitrary recursion/call effects by implication.

The proposed implementation must still cover normal exit, early `nivartanam`, relevant break/continue edges and failure propagation, and must preserve the frozen zero-cost/no-block comparison against the same allocator baseline. Those are future checker/cleanup gates, not properties established by v263's bump allocator. An old compiler rejecting the word `mandapa` does not count as a successful K0 escape test.

To support real vector-heavy applications later requires a separately specified checked collection/borrow interface: length/extent tracking, alias and growth effects, owner lifetime, mutation permissions, error paths and target semantics. That is meaningful future work, **not an implicit exception to the frozen K0 restrictions**. No new word, API implementation or compiler behavior is introduced by this review.

## Evidence ledger and status

All file reads are pinned to the main SHA above. The complete 24-entry library tree was retrieved without truncation at the Git API level; larger individual files were read in ranges, including their relevant tails.

- **R1:** `Sarvam-to-ChatGPT/ROUND-140.md`, `0ee57d15de34d175c0269cfc333a9cca5742ba17`.
- **R2:** `lib/vakyank.smlib`, `a95f01ae2b22c04e409d25cad17f95c7ad3280f9`: renderer contract, pad_vam padded path and parser status writes.
- **R3:** `lib/khand.smlib`, `972de102f2bb32c896ddd799fbc41cd4a56958e7`: terminating pack/unpack helpers, splitter special cases, segment export and byte-string writers.
- **R4:** `lib/varna.smlib`, `4bf3ead14fb55239a583da7d840665f52f9ed6aa`: cell representation, splitter limit handling and direct segment copying.
- **R5:** `lib/nighantu.smlib`, `53b584607efe8065bea4e7f59d18e782607905c0`: exact key-slot copies, qword/packed export distinction, value output bound.
- **R6:** `lib/sangrah.smlib`, `539bc6e4b45efcb70096eae97339c35941649c07`: sorted export through terminating unpack helper.
- **R7:** `lib/anukram.smlib`, `39b053569dd509b58f4611030c1361fb94ac578b`: explicit encoded capacity and independent destination obligations.
- **R8:** `lib/roop.smlib`, `0a883bc71498f5ac83195e14270bb8ea12debb38`: packed-byte/NUL convention and formatter bounds.
- **R9:** other read library blobs: `aadhar` 03a29301d6b5528c0d981ad190c0bf880d9b2d7c; `ank` 047657465bdd5e92a5a6b8b72e7d6abb8db4c3cd; `brihat` 46a918138c96153781d63ab0c43ea7660afa0bbb; `chandas` ae80d6d7028fbc9e591c4a83db3ac2da689bbc21; `ganit` 57e9c41fc6fd9906208b7c7494862e51559dcb0e; `ganita` 25cc88a0374f268e8f881f8f3eb32efb0a902189; `gudh` c3c444bd27311247d484d1fa7e9617464cdd91b2; `kalana` b5155a3323042ecf46ad25fba4f7999207701247; `madhava` 28a13649c9b8442c93209ee0c2db130a78bb05f0; `mala` de4e247aeb862e0f8986ce04de47b08aac417fe4; `patra` 84a164e5e809fb73cc546cce6333abf08195385e; `phal` 9fd9dacffb9129f380ae97bd35a443be97fb5127; `sadhan` 29fd39105299302ab4521cdf900972ebedc485ac; `samanvaya` 4b56c998bbd06ee3dd2efcea75592ab687d826a9; `sankhyiki` 630965e1ca8042db924ef2a75d182b8ce06cb905; `shreni` b356405884c5f09cf1de8c806c22ce0bcc502b7d; `suchi` a6834561bf086f163c933bf18afe9e7d310eaec3.
- **R10:** `docs/CHANGELOG.md:1-65`, `e8cb7f0be099afda9212af86d263fe2686e03740`: v418 partner measurements and broad retention/caller claims; not executions by this review.
- **R11:** `examples/217_r12_report.sm:35-65`, `0de23d6058a562b0eaf342113be7f5d8cc866cf7`: shared buffer passed to renderer and padding routine.
- R137-R139 returned checker and allocator audits are the continuity basis for the unchanged K0 boundary and previous retention definitions. This round does not independently close R137's separate vocabulary-census gap.

**Executed here:** read-only source/contract comparison and small Python integer-arithmetic calculations for aligned spans, growth sums, fixture thresholds and byte/cell conversion. These are not native measurements or tests of Sutram emission.

**NOT RUN — no native toolchain invoked:** all 48 fixtures, stress campaign, canary programs, compiler/builds, Linux/Windows/Wine executions, allocator fault probes, suites/proofs, guard and release qualification. No benchmark, complete memory-safety proof or shipped K0 implementation is claimed.

**NOT APPLIED:** compiler, library, example, test, tool, canonical documentation, pack, workflow, Windows or backup changes. The 176-byte caller recommendation and all contract changes are handed to the authorized implementers, not silently installed. Only this Markdown return is to be added under `ChatGPT-to-Sarvam/`; verify readback and commit scope, then stop after Round 140.
