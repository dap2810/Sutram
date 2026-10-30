# Sutram ROUND 139 — audit the shipped v263, not the superseded proposal

**Date:** 30 October 2026. **Pinned main:** `ad3c05cc416f4a1934751fbbd692974731d30de4`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-139.md`, blob `f0c23a19bc3006e1fcf1e0e33f614b2cf9e89f9d`.
**Return:** `ChatGPT-to-Sarvam/ROUND-139-V263-BUILD-AUDIT.md`.
**Observed baseline:** compiler v263, changelog v417. This is an independent source/evidence review. Native executions and benchmark measurements below belong to Claude unless explicitly labelled as my arithmetic model. No compiler or protected source is changed.

## Decisions and newly found issue

1. **247/248 matching outputs are useful regression evidence, not sufficient evidence of safety or unchanged semantics.** R65 itself supplies an additional executed alias probe whose result changes. The objection is now supported by the shipped build's evidence, not only my R138 prediction.
2. **The report-example diagnosis is substantially correct, but its proposed fix is incomplete.** `pad_vam` writes `dst[w] = 0` after filling positions 0 through w-1. For width 6, the actual padded-path requirement is **7 qword cells = 56 bytes**, not the recommended 48. Its current comment also understates this requirement. This is a definite source-level contract discrepancy; a native canary reproduction remains NOT RUN here.
3. **Numerical retention gates proposed here:** zero retired backing bytes for the uninterrupted single-tail benchmark; for two append-only interleaved vectors, at most **16 payload bytes per aggregate successful append**, plus explicitly counted header/alignment overhead. Use `retired_reserved <= 16*N + 32*G` as a conservative arena-only test gate, with definitions below. Additionally, I propose **64 MiB maximum retired backing storage per declared short-lived v1 workload**. These are acceptance-policy recommendations, not measurements or already-enforced limits.
4. **K0 still excludes `kosh` from the entire checked function.** Scalar-only scratch is the initial feature, not a general vector arena. Source details and exact construct decisions appear in WS3.
5. **Release disposition:** do not mark v263 fully safe/compatibility-cleared from the aggregate score. Resolve the alias-policy decision, the 56-byte padding contract, and focused boundary/failure tests. The allocator's performance improvement is not rejected merely because those gates remain open.

## WS1 — what the build evidence proves, and what it does not

### 1. Use the actual comparison boundaries

Claude's R65 handback separates the changes correctly:

| Comparison | Reported result | What it establishes |
|---|---|---|
| v261 to v262, diagnostic reword | 486 emitted programs byte-identical, 91 refused identically, 0 DIFFER on the stated paths | Regression evidence for that terminology-only stage. |
| v262 to v263, Linux ELF allocator | 248 binaries changed; 238 emitted binaries identical; 91 refused identically | The allocator changed emitted code for the affected corpus, as expected. |
| Execution of the 248 changed ELF programs | 247 same output and exit code; report example differs | Behavior on those inputs, not a universal program-equivalence or memory-safety proof. |
| PE and compiler-under-Wine comparison | 0 DIFFER | Preservation of the old target path, not validation of the new Linux arena. |
| Suite/proofs/corpus | 225 suite passes; 226/226 library proofs; 86/86 property proofs; 227/0 crash corpus, as reported | Valuable additional regression evidence, with each harness's actual coverage. Not all possible aliases, sizes, failure schedules or allocation interleavings. |

The cases are a selected corpus, not independent random samples of all valid programs. A passing count is not a probability that unsupported paths are safe. Some inputs require corrected expectations or corrected test preconditions: R65 reports that one property proof read 16 cells from two eight-cell allocations and was repaired separately. That correction must remain visible in the evidence chain. [R2, R3]

**PE/Wine qualification:** `r65_active` returns inactive when `target_pe != 0`. The old allocation sequence is retained for PE; Linux object/separate builds use the new arena. The include's opening comment still says object mode retains the old path, but its implementation and later comment say otherwise. Follow the code, not that stale opening comment. Windows has not independently exercised this new allocator simply because its old compiler output stayed identical. [R4]

### 2. The alias objection survives — in executed partner evidence

The retained R65 measurement says:

```text
kosh k[1]; push 7; vitti a = k; push 8 and 9 through k
v261: len(a)=1, len(k)=3; a[2] causes bounds error
v263: len(a)=3, len(k)=3; a[2]=9; a == k is 1
```

Those are **Claude-reported native results**, not executions I repeated. They corroborate the precise incompatibility I identified: a handle that previously remained on an old generation now sees the grown buffer when extension succeeds. This is an ordinary length/indexing result, not merely address printing. [R5]

The 247/248 statement and this probe do not contradict each other; they describe different test sets. They do contradict an inference that *all* accepted old source retains its behavior. Mark the alias probe as an additional semantic delta outside the cited guard subset.

**The wording “an alias now follows growth” is also too broad.** `r65_emit_kosh_extend` only succeeds at the tail with room remaining. With an intervening allocation or insufficient remaining arena space, the existing allocate-copy-update-selected-handle path still runs. In that path an old alias remains on the older allocation. The alias policy is therefore conditional on allocation history unless the owner chooses a different representation/contract. [R4, R6]

This also produces a **predicted target discrepancy**: Linux may keep those aliases shared while PE still uses the old copying path. The PE code gate and the Linux alias result support that inference; I have not executed the alias probe on real Windows. Require that exact cross-target probe rather than calling separate 0-DIFFER results a cross-target semantic test.

**Required decision, not an automatic rollback demand:** either explicitly accept and document conditional sharing, or constrain in-place growth by a sound uniqueness proof / disable that optimization where equivalence is required. Merging code before a review is read does not itself settle the language contract. Zero output differences are required for cases claimed unchanged; an intentional difference needs a separately approved expected behavior. A cheap lexical scan for `a = k` is not a general uniqueness proof.

### 3. What looks correct in the actual fast path

The inspected implementation addresses several R138 concerns rather than merely asserting them:

- The appended expression is evaluated before loading the selected pointer/length/capacity and attempting extension. An allocation in that expression does not leave a tail decision cached from before evaluation. [R6]
- The extension compares `align16(user_ptr + cap*8)` with the current cursor, then compares the proposed aligned new end with the arena end before publishing cursor/capacity. It uses element-to-byte scaling and does not require power-of-two capacities. [R4]
- It neither frees nor hands an old backing block to a different collection. If extension fails, the old copy-and-retain mechanism remains. [R4, R6]
- Ordinary allocation checks nonzero size against remaining room and advances monotonically; the reserve is 1 GiB and there is a per-call mapping fallback. No scratch cursor pair or `mandapa` cleanup is implemented by this Step 1. Missing a future P/S comparison is not automatically a present Step-1 defect. [R4]

**Conditional overlap argument:** with valid headers, genuine arena-tail storage, aligned cursor/end and no interleaving between check and commit, growing into the checked suffix cannot overwrite an intervening arena allocation. If a later allocation exists, the tail equality must fail. Multiple names for one allocation do not themselves occupy another suffix.

An apparent rounding concern deserves precision: when both cur and end are 16-byte aligned and the accepted size satisfies `0 < size <= end-cur`, rounding `cur+size` upward to 16 cannot pass the already-aligned end, assuming valid mapped-address arithmetic. Thus the absence of a separate rounded-size comparison is not, by itself, a demonstrated bug in that normal case.

**This is not a full native proof.** The emitted extension uses LEA/shift/add arithmetic without separate carry diagnostics and identifies the tail numerically, without a stored arena-base/object record. Those properties need domain reasoning and adversarial tests. I have not demonstrated a new well-formed-input overlap from them and do not label them proven exploits. Prior malformed-size/header issues must be separated from new allocator regressions.

### 4. A definite fresh finding: the proposed report-example repair still leaves an overrun

At this exact head:

```sutram
# examples/217_r12_report.sm
vitti koshtha = nirmmita(32)
vitti row = nirmmita(64)
...
pad_vam(koshtha, cnt, 6, 32)
```

And the actual library body at `lib/vakyank.smlib:238-259` ends its padding path with:

```sutram
dst[w] = 0
nivartanam w
```

For the example's two-digit scores, `cnt=2` and `w=6`, so the padding path is taken. It writes the six content cells **and cell 6**, the terminator. The byte intervals are:

| Allocation | Permitted qword indices | Result on padded path |
|---|---|---|
| 32 bytes | 0..3 | Content cells 4,5 and terminator cell 6 lie outside the allocation. |
| Proposed 48 bytes | 0..5 | Content fits; **terminator cell 6 still lies outside**. |
| **56 bytes minimum** | **0..6** | Content and terminator fit. |

The terminator store starts at byte offset 48 and occupies bytes 48..55. In the v263 arena, a 48-byte request is already a multiple of 16; the next allocation can start exactly there. A patch that merely changes 32 to 48 can still overwrite the next object's first qword, even if subsequent repacking happens to hide that write in final output. [R7, R8]

**Proposed owner action:** change this caller to at least 56 requested bytes, or revise the library contract/behavior deliberately. Correct the misleading `Caller must allocate >= width cells` comment: for the branch that pads and appends a terminator, require at least `width+1` cells. Separately review the no-padding branch's existing-input contract rather than making an unconditional claim about all counts. Test width 6/count 2 with exactly seven cells and an adjacent canary; retain a six-cell negative/canary case. These are recommendations only; no source or example was edited here.

**Does reverting the allocator make the example valid? No.** It still accesses cells outside its requested four-cell object; unused zeroed page slack merely hid the error. Claude's diagnosis of a pre-existing overrun is supported, but the 48-byte repair and the library's comment are not a complete resolution. The exception cannot be closed solely by obtaining the old printed scores again. [R7-R9]

### 5. Remaining evidence gaps that matter to this build

| Gap | Exact coverage needed |
|---|---|
| Conditional sharing | Same alias probe with tail extension, an intervening allocation, and exhausted-arena copy fallback; exercise writes and growth through each handle. |
| Target difference | Run that probe on Linux and real Windows; specify allowed results, not only compiler byte parity within each target. |
| Exhaustion and fallback | Exact remaining-room allocation, odd sizes, reservation failure, >arena request, and later mapping failure; retain cursor/header canaries. |
| Header write after failed copy allocation | In the inspected growth path, allocation is followed by header stores without a visible zero test. Characterize/integrate the failure fix separately; a passing generic fail-alloc suite is not proof this site returns cleanly. |
| Alignment/size domain | Capacities 1,3,5, zero/negative and arithmetic boundaries, with explicit valid/invalid-input classification. Never infer a new bug merely from a deliberately corrupted header. |
| Packed-neighbor accesses | Audit capacity contracts and test canaries, not just output; the report example and repaired property proof show why page slack used to conceal errors. |
| Fault-injection meaning | In-place growth bypasses the allocation call. Decide whether `--fail-alloc N` counts actual allocator invocations or logical growth attempts; compare against that specified meaning. |
| Retention | Count retired blocks/payload/padding and fallback mappings, including two interleaved vectors and repeated construction; one-vector RSS is insufficient. |

The arena uses `MAP_NORESERVE`. The Linux manual explicitly permits a later write fault when physical memory is unavailable despite a successful mapping. Do not promise that every resource failure becomes a convenient `nirmmita` zero return. This is an external API fact, not an observed Sutram failure in this review. [W1]

**WS1 verdict:** the build is a substantially tested implementation with open semantic and targeted failure/contract gates. I do not certify it generally safe from the stated counts. My objection survives as a specific witnessed alias change, a cross-target coverage gap, and a newly identified incomplete overrun repair—not as a refusal to examine shipped code.

## WS2 — numerical thresholds, measurements and a reproducible model

### 1. Define the quantity before choosing a number

Use a named **unaliased benchmark** so the old generations are actually unreachable. With live copied handles, some retained generations are live data, not reclaimable garbage.

Let `N` be aggregate successful appends across the benchmark vectors, `G` the count of copy-growth events that abandon a prior allocation, `R_payload` the sum of old payload capacities in bytes, and `R_reserved` the allocator spans of those retired allocations including header/padding. Exclude current backing buffers from R, but report them separately. Also report all persistent/fallback allocations and RSS separately. A 1 GiB virtual reservation is not 1 GiB of retired vector payload.

For arena storage in this implementation:

```text
span(C) = align16(16 + 8*C)
R_payload = sum(8*C_old) over copied-away generations
R_reserved = sum(span(C_old)) over those generations
```

Do not call `RSS(growing) - RSS(presized)` an exact count of retired bytes: residency, page rounding, touching and spare capacity differ. R65's 7,808 KB single-vector result is partner-reported RSS, not an instrumented zero-retired-byte counter. [R5]

### 2. My proposed v1 acceptance thresholds

These are **my policy proposals for release qualification**, not existing project limits or a universal theorem of acceptable leakage.

| Workload / claim | Numerical gate I recommend |
|---|---|
| One unaliased `kosh[1]`, one million consecutive appends, no allocating payload expression or other intervening allocation, enough initial arena space | **R_payload = 0 and R_reserved = 0.** Current live capacity/slack is not counted as a leak. Any retired generation fails the claimed uninterrupted-tail optimization for this fixture. |
| Two unaliased `kosh[1]` vectors, alternating appends, no other allocations, monotone growth, arena-only storage | **R_payload <= 16*N bytes.** For physical arena spans, **R_reserved <= 16*N + 32*G bytes**. Header/padding is charged separately, not disguised in a payload rate. |
| Declared finite/short-lived v1 workload accepted with retention | Additionally **R_reserved <= 64 MiB at any point in that workload**. Exceeding this fails this proposed default workload budget even when the per-append rate passes. This chosen operational cap needs owner approval and measurement; v263 does not enforce it. |
| Claim of bounded memory for an indefinitely repeated fixed-working-set service | **0 net persistent bytes retained per completed iteration after warm-up**, with a fixed total high-water bound. A positive permanent slope fails that claim. Current no-release collections do not qualify merely by passing the finite benchmarks. |
| Corruption / dangling access / unapproved ordinary semantic difference | **Zero accepted cases.** No low retention number compensates for a correctness defect. |

The 64 MiB figure is a deliberately chosen v1 workload budget, not a value inferred from the owner's hardware or a hidden industry standard. It covers retired backing storage, not all application RAM; the full working set needs its own published budget. A release supporting larger workloads can explicitly choose a different profile, but cannot call 64 MiB an implementation guarantee without enforcement/accounting. An unbounded `mmap` fallback does not enforce any such cap.

### 3. Why the interleaved payload threshold is 16, not an arbitrary 15.3

For a positive initial capacity c and m doubling growths ending at C:

```text
C = c * 2^m
sum(previous capacities) = C - c
R_payload = 8*(C-c)              # all-copy upper bound for that chain
```

For a monotone append fixture that has grown, `C < 2*n`, so retired payload is less than 16 bytes per successful append. Sum across the two independent chains using aggregate N. Each retired arena block adds 16 header bytes and at most 15 alignment bytes; `32*G` is a conservative allowance. With qword capacities and aligned bases here, padding is actually 0 or 8 bytes per block, permitting tighter accounting.

This is not a bound per *individual growth call*: a single boundary append can retire a large buffer. It is cumulative amortized accounting over the specified history. It is not a bound per current length after clear/pop, or per discarded object lifetime, or for arbitrary large pre-sizing and hidden aliases. A mapped fallback needs separate page-rounded accounting rather than pretending the arena-span bound covers it.

### 4. Expected numerical fixtures — arithmetic, not native measurements

I evaluated the doubling/alignment sums with a small Python arithmetic model in this review. It did not compile or execute Sutram and did not measure RSS, cycles or real allocations.

Assume two vectors start at capacity 1; A is appended before B each iteration. At each shared doubling boundary, growing A places its new allocation after B, then growing B places its new allocation after A. Thus both copy in this specified schedule. Enough arena space and no unrelated allocations are assumed.

| Appends per vector | Aggregate N | Final capacity each | Total G | Predicted R_reserved | R_reserved / N |
|---|---:|---:|---:|---:|---:|
| 3 | 6 | 4 | 4 | 128 bytes | 21.333333 bytes |
| 524,289 | 1,048,578 | 1,048,576 | 40 | 16,777,856 bytes | 16.000580 bytes |
| **1,000,000** | **2,000,000** | **1,048,576** | **40** | **16,777,856 bytes** | **8.388928 bytes** |

The first two rows explain why a bare 16-byte **all-overhead-inclusive** threshold would falsely reject correct small/boundary fixtures. At one million appends each, retired payload is 16,777,200 bytes; headers add 640 and alignment adds 16. The explicit overhead allowance makes the proposed gate reproducible. Current backing arrays, reserved virtual space and touched/RSS pages are additional categories, not hidden in these totals.

For the uninterrupted single vector, the expected retired count is zero as long as every extension succeeds in place. It stops being that fixture once growth reaches fallback or another allocation becomes the tail. Label the regime change rather than misreporting its later retention as a failed zero-leak theorem for all workloads.

**WS2 answer:** I would accept the stated finite v1 retention tradeoff only within the zero-single-tail / 16-byte-payload-plus-overhead / 64-MiB-workload gates above, after correctness and semantics are settled. I would reject an indefinite bounded-memory claim with any sustained positive retention slope. Neither Claude's single-vector RSS nor the old ~15.3 footprint figure currently proves those complete gates.

## WS3 — exact K0 collection boundary and the block's actual use

**Yes: initial K0 cannot contain a `kosh` at all in its checked function boundary.** This includes a `kosh` declared outside the braces but inside the same function. It is not merely a restriction on `kosh_push`. This retains R135-R138's deliberately small checker rather than adding unverified exceptions now.

| Construct in the checked function | K0 result | Reason / allowed alternative |
|---|---|---|
| `kosh k[...]` or `kosh dasham k[...]`, inside or outside its `mandapa` braces | Reject | Collection layout/growth/alias effects are unsupported. Fixed-size scalar-only `nirmmita(C)` buffers can be admitted under the existing extent/null rules. |
| `vitti a = k`, assignment from a collection, passing a copied handle around | Reject | A scalar-looking variable does not erase collection/reference kind. Copying depth metadata is not an ownership proof. |
| `k[i]`, `k[i] = scalar`, `kosh_len/cap/empty`, pop/peek/dequeue/clear | Reject initially | A scalar result or scalar RHS does not validate the collection operation used to obtain/store it. Metadata/read-only support requires a separately verified contract. |
| `kosh_push(k, scalar)` or enqueue | Reject | Even scalar insertion can allocate, relocate and mutate aliased headers. A zero-taint RHS is insufficient. |
| Append/store a scratch pointer into any collection or struct member | Reject | Pointer-bearing carriers are absent from initial K0; comparing `var_depth` alone is not enough. |
| A typed collection parameter, collection result, or a raw/untyped value carrying a collection reference | Reject | The value-only call interface cannot transport this reference by renaming or casting it. |
| Direct helper call | Allow only the exact-body/transitively verified scalar-only contract | A helper that secretly uses unsupported collections or retains pointers is not approved merely because it returns a number. Indirect/opaque calls stay rejected. |
| `nivartanam k` or a reference-bearing success/failure wrapper | Reject | Only Scalar/CLEAN results are admitted. |
| `nivartanam p[0]` from an admitted fixed-size scalar-only buffer | Allow after non-null and constant-bounds proof | Evaluate before scratch cleanup, preserve the scalar, restore exited marks, then return. |
| Legacy caller uses `kosh` and supplies a scalar to a checked helper | Allow that separation of functions | The legacy caller remains outside K0; the helper receives a numeric value and cannot dereference it as a pointer. This does not certify the caller. |

**What `mandapa` is for in K0:** repeated bounded fixed-layout scalar scratch, fixed-size scalar computations and verified scalar helpers whose temporary buffers die at block exit. It can reuse scratch across a loop even when the loop counter changes, provided accesses satisfy the constant-index restrictions. It is **not yet** a general region around vector parsing, collection-heavy request handling, sorting arbitrary dynamic vectors or an entire existing server.

For example, an unchecked legacy caller may compute `kosh_len(k)` and pass that number to a helper that uses an eight-byte scratch buffer at constant index 0 and returns a scalar. It may not pass k itself to that helper under K0. The useful distinction is the interface value, not the position of one brace.

If most target applications require vectors, this restriction is a genuine usability limitation. State it before implementation/release rather than broadening the safety promise. A later checked borrowed-collection interface could admit some read-only/scalar operations with verified layout, bounds, lifetime and effects. Aliasing is not a proof that such future support is impossible; it is a reason the present three-depth-field checker cannot silently approve it.

**Implementation caution:** K0 and `mandapa` are still specifications in this audit; R65 explicitly says it implemented no Steps 2-4. The shipped Linux bump allocator is not itself a region checker, and it cannot be used as evidence that the K0 rejection rules already run. Persistent fallback must not later be silently inherited by scratch while claiming cursor rewind frees that mapping. [R2]

## Focused closure checklist — all native cases NOT RUN by ChatGPT

| ID | Required acceptance work | Pass condition |
|---|---|---|
| V139-01 | Reproduce the R65 alias probe, add the full mutation probe from R138 | Record old/new outputs and explicit owner-selected alias semantics, not an undocumented waiver. |
| V139-02 | Same probe with interleaved allocation and exhausted arena | Conditional share/copy behavior is specified and tested; canaries intact. |
| V139-03 | Run those probes on Linux and real Windows | Target semantic differences are resolved or explicitly restricted; Wine compiler parity is not substituted. |
| V139-04 | Padding caller at 32,48,56 bytes; width 6/count 2; adjacent canary | 56-byte positive fits; insufficient-capacity cases reveal the access; corrected contract includes the terminator. Do not rely only on final printed scores. |
| V139-05 | Re-run the repaired property proof on both allocator baselines | Corrected input extents and output equivalence recorded, old flawed proof retained as history. |
| V139-06 | Exact arena end, odd sizes, zero, reserve failure and fallback failure | Cursor/object state remains consistent; overflow and failure outcomes are documented. |
| V139-07 | Copy-growth allocation failure | No unexamined header write through zero; independently classify/fix the existing site. |
| V139-08 | Single uninterrupted one-million-append fixture with allocation accounting | R_payload=R_reserved=0; report current capacity and RSS separately. |
| V139-09 | Two alternating one-million-append vectors, plus just-after-doubling checkpoints | Measure payload/header/padding against the defined formulas and proposed thresholds. |
| V139-10 | Repeated fixed-working-set construction/discard | Report bytes retained per iteration and total high-water; do not label positive slope bounded service memory. |
| V139-11 | K0 collection constructs and scalar-only bridge | Intended unsupported-operation diagnostics; supported positive region program must work before counting negatives. |
| V139-12 | Stage-separated guard | v262/v263 intentional allocator deltas separate from future no-mandapa Step-3/4 identity on the same allocator baseline. |

## Source ledger and execution status

All repository reads below used pinned main `ad3c05cc416f4a1934751fbbd692974731d30de4` unless a work commit is named.

- **R1:** `Sarvam-to-ChatGPT/ROUND-139.md`, blob `f0c23a19bc3006e1fcf1e0e33f614b2cf9e89f9d` — requested build audit, numeric threshold and K0 boundary.
- **R2:** `Claude-to-Sarvam/R65-00-HANDBACK.md`, blob `0eaed6f0d277f1ff1fb870e62a4dd5c539654105` — partner execution results, target scope, intentional alias delta, proposed 48-byte repair and stage limits.
- **R3:** work commit `8e6ae3508916504adbeebc4bcac19adffdb6fe29`, fetched metadata/diff — Step 1 implementation and proof status at that stage; handback identifies later proof repair `4ca6237`. No claim that I ran either revision.
- **R4:** complete `src/r65_arena.inc`, blob `25f2661100f4401c45fc3de2bc864a6ed199a90f` — emitted byte templates, arena globals/reservation/fallback, `r65_active`, object-root setup, and tail extension.
- **R5:** `Claude-to-Sarvam/evidence-r65/kosh-measurements.txt`, blob `4949952b0de74aed0237699d8e6294d2fc482d69` — partner alias outputs and single-vector RSS.
- **R6:** `src/sutram_compiler.asm:15645-15860`, blob `2cef0233ef40d481af394b090977e557bc3a1ab9` — appended-value ordering, growth arithmetic, extension hook and allocation/header stores.
- **R7:** complete `examples/217_r12_report.sm`, blob `0de23d6058a562b0eaf342113be7f5d8cc866cf7` — four-cell caller and width-six operation.
- **R8:** `lib/vakyank.smlib:233-266`, also surrounding read 170-260, blob `a95f01ae2b22c04e409d25cad17f95c7ad3280f9` — actual padding stores and `dst[w]=0`, contradicting the short capacity comment.
- **R9:** `Claude-to-Sarvam/evidence-r65/217-report-overrun.txt`, blob `2ee5ff792059665a456cf2fcc77b3c1c78fbb79a` — partner explanation/output; the missing terminator accounting is my new finding.
- **R10:** `docs/CHANGELOG.md:1-70`, blob `9aba772df3d347025e82fdfeab0f031f0530e613` — v417 and owner's unresolved example investigation. Its reported doc-count correction is not a fresh gates run by me.
- R135-R138 returned K0/alias specifications are available in this conversation and are the continuity basis; no claim of a fresh full-codebase census or rerun of R137's open search gate.

**External reference W1:** Linux man-pages `mmap(2)`, `MAP_NORESERVE`, checked 30 October 2026: https://man7.org/linux/man-pages/man2/mmap.2.html . Used only for reservation versus guaranteed future writes; not substituted for Sutram's source or tests.

**Completed:** targeted pinned-source audit; evidence-scope reconciliation; identification of the 56-byte padded-buffer requirement; explicit retention thresholds; checked arithmetic sums; exact K0 construct table; twelve proposed native acceptance cases.

**Executed here:** a small Python integer-arithmetic calculation of doubling capacities, 16-byte rounding and retired-generation sums. This was not a Sutram interpreter, allocator simulation against native code, benchmark, memory measurement or test of the implementation.

**NOT RUN — no native toolchain invoked:** Sutram compilation, changed-output reproduction, Windows/Wine execution, padding canaries, allocator/OOM/fault-injection tests, benchmarks, regression/proof suites and byte guard. All partner test counts remain attributed. No successful new safety or release gate is claimed.

**NOT APPLIED:** compiler, library, examples, tests, tools, canonical docs, packs, workflows, Windows or backup modifications. In particular, the proposed 56-byte fix is reported, not silently applied. Only this Markdown handoff is to be added to `ChatGPT-to-Sarvam/` and read back with a commit-diff check. Stop after Round 139.
