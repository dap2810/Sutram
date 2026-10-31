# Sutram ROUND 141 — guard-page evidence, read coverage, ten priorities, and the beginner sentence

**Date:** 30 October 2026. **Pinned main:** `b2d4773428ffb1e9817ca86931a474677455e28f`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-141.md`, blob `4ea1901b95bf2b8f2e086893a5aa0796d231d7c4`.
**Return:** `ChatGPT-to-Sarvam/ROUND-141-GUARD-PAGE-EVIDENCE-REVIEW.md`.
**Role:** independent read-side review. The R68 native results below are Claude-reported, not rerun by ChatGPT. This round does not change compiler, library, test, tool, pack or canonical documentation files.

## Answers first

1. **The guard-page work is a substantial improvement and should become a gate. It does not by itself certify the production v263 allocator as safe.** The published build instructions disable the arena and in-place `kosh` extension, precisely the production paths that still need separate qualification. The test allocator also ignores the result of `mprotect`; a failed protection request can leave an apparently guarded allocation unguarded. That is a verified harness-source gap, not evidence that protection actually failed in Claude's runs.
2. **The audit did examine reads in several places. It would be inaccurate to call it entirely write-only.** Its manual tables explicitly discuss read extents, and the old bigint proof is a reported over-read control. However, the automated census is write-oriented and is not an exhaustive access inventory: it misses raw `likh8` stores, inline writes and some function boundaries. Its 371-site count cannot establish that every read or write was enumerated.
3. **The first ten R140 fixtures I would implement/run are C02, C03, C05, C09, A25, A27, A30, S35, F43 and R46. None requires `mandapa`.** Some require test-harness fault or arena-state controls, not a future language construct. These are priorities, not a replacement for the remaining qualification work.
4. **Beginner sentence:** “Use `mandapa` for temporary, fixed-size buffers of numbers during a small calculation; their space is reclaimed when the block is exited, and the containing checked function cannot use `kosh` vectors.” Put a **planned v1 feature—not available in this build** notice above it until the block/checker actually ships.

## WS1 — what the guard-page compiler establishes

### 1. Credit the new evidence accurately

R68 reports the corrected example buffer, the corrected padding capacity contract, and the pack/unpack proof's missing ninth cell. It reports the guard variant's regression suite as `NO-EXPECTATION=4 PASS=225`, library proofs as 226 passed, and property proofs as 86/86, with known-bad controls that fault. It also reports production gates at 48 PASS / 0 FAIL / 1 NOT-RUN, with real Windows execution not run. These are useful, separate evidence streams. [R2]

The fixes materially improve the result: `217` now requests 22 cells, rather than merely changing four cells to six; the unpack proof requests nine cells for a maximum eight-cell payload plus terminator. The corrected contracts and input extents must accompany the logs. Passing tests with corrected preconditions should not erase the old failing controls. [R2]

### 2. The variant is not the production arena

`guard-pages-how.sh` explicitly replaces the normal allocation gate with `jmp r68_emit_efence` and makes `r65_active` return zero. R68 states **no arena, no kosh extension**. Each allocation instead gets its own mapping and a trailing protected page. [R3-R5]

This is excellent for exposing accesses previously hidden by page slack. It does **not** execute the production bump cursor, shared-page placement, last-allocation extension decision, arena-end/fallback transitions or production alias sharing. A bug in those paths can disappear when those paths are disabled. A clean guard run therefore complements, rather than substitutes for, the production allocator fixtures.

Run the same supported inputs under BOTH variants and retain expected semantic differences separately. Do not insist on identical pointer values or pretend the guard allocator preserves the new in-place alias behavior. The target of the differential check must be stated.

### 3. Exact geometry and a concrete blind spot

For a positive request `n`, with the sequence's assumed 4,096-byte pages, it computes:

```text
mapping_size = (n + 8191) & -4096
G = mapping_base + mapping_size - 4096
mprotect(G, 4096, PROT_NONE)
p = G - n
```

Assuming representable arithmetic, successful system calls and normal direct user-mode loads/stores, the first byte after `[p,p+n)` is in the protected page. A direct access that touches that page faults. This is stronger than placing a canary after page-rounded storage. [R4, W1]

But there is **no leading guard**. For `n=8`, the mapping is 8,192 bytes and `p` is 4,088 bytes after its base. A qword read at `p-8` is outside the requested object but inside accessible mapping slack. The geometry alone does not detect it. A separate left-justified/leading-guard run is needed to put the lower boundary against a protected page; one right-justified layout cannot make both arbitrary byte boundaries page-aligned.

The guard layout also changes alignment: `p=G-n`, so an eight-byte request is eight modulo sixteen, and an odd-byte request need not even be eight-byte aligned. That is useful for some stress cases but is not the production arena's 16-byte placement. Keep production-alignment tests as a distinct mode.

### 4. Verified harness issue: the protection result is discarded

The published assembly contains:

```asm
    mov eax, 10
    push rdi
    syscall             ; mprotect
    pop rax             ; overwrites its return value
    sub rax, rbx
```

There is no success test between the syscall and overwriting `RAX`. Linux documents zero on successful `mprotect` and errors including resource-related failures. The assembly must check the raw syscall result before returning a pointer. [R4, W1]

**Required harness repair:** fail closed with a distinct infrastructure-failure result if guard installation fails; do not count that case as a successful protected run, and do not quietly return an unprotected pointer. Record how many guarded allocations were successfully established. Validate page-size assumptions and size-rounding arithmetic for the harness's supported request domain.

The known faulting controls show protection worked for those control allocations. They do not prove every protection request in every process succeeded. Conversely, I have not observed an actual failed `mprotect` here, so this report does not relabel the reported runs as false or failed.

### 5. What a trailing guard cannot establish

| Missing dimension | Concrete mechanism | Necessary complementary evidence |
|---|---|---|
| Reads/writes before the object | Right-justification leaves accessible prefix slack, as the eight-byte example above shows. | Leading-guard layout and lower-bound probes; reject or document invalid negative-index domains. |
| Subobject or logical-length bounds | Reading past a slice, map slot or vector length can remain inside the larger allocation. A vector's spare capacity is not its live length. | Exact logical extent checks, subobject canaries/write tracking, and explicit compiler bounds-check tests. |
| Skipping the protected page | A bad computed address can jump beyond the one guard page into some other mapped area instead of touching it. | Address/extent instrumentation or static range reasoning; not just a signal count. |
| Unexecuted cases | The old unpack proof's fixed seed never generated length 8, so even the guard run missed that bad size until a direct case was used. | Forced boundary values and published seed/input coverage, including negative controls. |
| Production allocator correctness | The scratch guard build disables the arena and in-place growth. | Production cursor, nonoverlap, alias, end-of-arena, fallback and failure fixtures. |
| Kernel-mediated access | A `read`/`write` syscall using an inaccessible user buffer can report `EFAULT` rather than a process SIGSEGV. | Check returned lengths/errors and output, not only whether the child was signalled. [W2,W3] |
| Lifetime, stale values and initialization | A mapped address can still be accessible after the program's logical lifetime ends, or within an object whose value has not been initialized. This variant does not implement scratch reset/free. | Separate lifetime/initialization checks when those features exist; no present claim that a future `mandapa` is tested. |
| Non-allocated storage and target modes | A replacement for `nirmmita` does not automatically protect stack locals, literals, globals or all compiler metadata. R68 did not run this Linux `mprotect` variant on PE. | Target/build-mode-specific coverage, explicit storage-origin accounting. |
| Semantic contracts without physical overflow | A zero-limit splitter may write within a generously allocated `parts` block yet violate its stated segment-count limit. | Result/side-effect oracles and resolved API contracts, not guards alone. |

For declared `mala`/`kosh`, distinguish their internal header/payload layout and logical length from the underlying allocation extent. A guard could catch a store reaching the allocation's physical end if that allocation passes through the replaced emitter. It cannot replace independent tests of the compiler's logical bounds checks. I do not infer those tests passed solely from the label “compiler-checked.”

### 6. Do not equate aggregate PASS labels with a native access trace

I read `tests/run_tests.py`. It supports expected compile failures and can mark matching compiler refusals **PASS** without executing a program. For a successfully compiled example with no golden it does run the binary, but subsequently returns **NO-EXPECTATION**; the displayed failure detail does not necessarily preserve the runtime code. The main harness itself treats NO-EXPECTATION as a nonzero suite result. [R10]

Thus `229 + 226 + 86 = 541` is the partner's aggregate case count, **not automatically 541 distinct successful native executions**, and `PASS=225` alone is not a complete signal ledger. The per-case records should distinguish compile rejection, native execution, timeout, signal, stdout/exit comparison and missing expectation. R68 may have inspected those separately; I have not independently verified every raw transcript and do not claim that it failed to do so.

**WS1 verdict:** accept the guard run as valuable measured evidence for executed boundary accesses in the instrumented configuration. Do not promote it to an unrestricted “v263 is safe” statement. Retain R140's scoped release qualification, close the harness-success check, and run the production-specific and coverage-completion gates. This is not a demand to discard the allocator improvement or keep adding arbitrary program counts.

## WS2 — did the audit check reads, and is the census complete?

### 1. Yes, reads were considered — but not as a demonstrated exhaustive read ledger

The manual `audit-vakyank-varna.md` table explicitly records reads of input digits, serializer source ranges, `pad_vam` source cells, parser `src[0]` on negative counts, and joins that trust stored segment lengths. `audit-suchi-ganita.md` records matrix input reads, sorting reads and old backing-array reads during growth. R68's control using the old bigint reconstruction proof is explicitly an **over-read** control. It would be unfair and inaccurate to say the audit never looked at reads. [R2,R7,R8]

However, the summary's **305 functions, 371 write sites, 419 call sites** contains no corresponding complete read-site count, list of read-only routines, or reconciled coverage of `pad8`, `akshar`, ordinary indexed loads, scans, implicit builtin reads and kernel/foreign reads. Selected READ notes and an executed over-read control do not establish that all those access forms were systematically audited.

### 2. The published census misses actual write forms too

`census.py` recognizes a line-start `x[index] = ...` or line-start `akshar_rakh(identifier, index, ...)`. It does not parse the full language. Three concrete limitations follow directly from the code and the pinned source examples. [R6,R9]

| Source form | What the census does | Evidence / consequence |
|---|---|---|
| `likh8(a + j * 8, v)` | Neither write regex recognizes it. | Present in `lib/mala.smlib`; raw qword stores are not represented by the census's two write spellings. The equivalent `pad8` reads also need a separate ledger. |
| `yadi (...) { ok[0] = 1.0; nivartanam ... }` | The cell-store regex is anchored to the start of the line and therefore misses the embedded store. | Present in `lib/kalana.smlib`'s `bahu_mula`. A similar inline byte-store form misses `W_BYTE`. |
| Unbraced function followed by another declaration | Body extraction stops only at a column-zero `}` rather than at the next valid function boundary. | `varna_maap`, `akshar_sanket` and the following braced predicate demonstrate why the first body can absorb later declarations, misgrouping/skipping them in the census. |

I checked the exact two regular expressions with a small local Python matcher: a normal `dst[w] = 0` matches; a raw `likh8`, an inline cell store and an inline byte store do not. This is a text-recognition check, **not execution of Sutram or a rerun of the full census**. No new repository script was added.

These limitations do **not** prove that Claude's manual readers missed the same statements. The manual tables already cover operations the regex summary alone cannot justify. They do mean “371” must be labelled as the census's recognized-site total unless an additional, complete reconciliation establishes a true total. Do not certify completeness from that number.

### 3. Close the class with a combined access ledger, not a larger slogan

For every library access, record function/blob/line, **read or write**, byte or qword width, pointer origin, object/subobject extent, index interval, branch/loop preconditions, callee effects and caller capacity. Include:

- Indexed loads and stores, `pad8`/`likh8`, `akshar`/`akshar_rakh`, terminator scans and delegated pack/unpack/format routines.
- Pure/read-only functions as well as the 112 write/allocation-bearing functions in the summary.
- Typed collection logical-length checks and backing/header extents separately.
- Both sides of copies: valid destination capacity does not prove the source is readable for the same length.
- Inline statements, unbraced functions, early returns, zero/empty special cases and malformed inputs explicitly outside the supported contract.

Use a parser-aware extraction or reconcile a conservative textual inventory against the full grammar. Unrecognized forms must be **UNREVIEWED**, not silently absent. Preserve the human per-path reasoning and caller tracing; do not replace it with a grid whose tested small integers are then advertised as an unbounded proof.

A proof of an affine inequality over an unbounded domain requires domain/range reasoning, not merely testing a finite grid: even `index=n`, `capacity=100` passes small n but fails at 100. R68 correctly calls its prototype a bounded model check; do not broaden that into a universal proof by the word “affine.”

**Completeness answer:** the repaired `pad_vam` issue and the newly repaired unpack caller are positively addressed by R68. The inspected evidence still does not justify “all library reads and writes, on all supported paths, are complete.” This round identifies coverage/harness gaps, not a newly executed production overrun. R140's zero-limit contract issue and missing exact capacity lines also need their own disposition even when generous current callers do not fault.

## WS3 — the ten highest-priority fixtures from R140

The IDs below are retained from the original 48, not silently renumbered. Ranking is my engineering prioritization: calibrate detection, test capacity boundaries, then exercise production paths the guard variant removes. **All ten use current language constructs; zero require `mandapa`, Step 2, or Step 3.**

| Priority | Original ID | What to run and why | Required result / harness dependency |
|---:|---|---|---|
| 1 | **C02** | `pad_vam`, count 2/width 6, six-cell logical destination. The exact one-cell terminator overrun that a 48-byte repair misses. | Historical negative calibration: guard fault or immediate nonzero-red-zone change. Do not call a deliberately undersized raw-API input a supported successful operation. |
| 2 | **C03** | Same padding operation with seven cells / 56 bytes. The matching positive proves the harness is not merely crashing on every call. | Correct content/NUL; canaries after cell 6 intact; no fault. This is the padding-only case, not a waiver of the example renderer's 22-cell precondition. |
| 3 | **C05** | `khand_mukt` byte-to-cell conversion. Keep the original two-byte positive and explicitly add lengths 0,1,8, with n+1 cells. | Correct qword/byte units and terminator. Add the old n=8/eight-cell case as a labelled negative calibration; do not depend on random selection. This is a declared parameter expansion of C05. |
| 4 | **C09** | One-slot map, full 32-byte key, `nighantu_kunjika` with 34 cells. Tests a delegated writer and length-prefixed representation, not just local loops. | 33 encoded cells plus the permitted trailing zero fit; next canary intact. Keep C08's 33-cell negative when running the full suite. |
| 5 | **A25** | Adjacent 17-byte allocations, write/reread requested ranges. This crosses the production 16-byte alignment boundary. | Production spans nonoverlapping/aligned as specified; all requested bytes survive. Guard mode is an extra boundary check, not an identical address-layout oracle. |
| 6 | **A27** | Request remaining arena room plus one. Exercises the production limit-to-fallback transition absent from guard mode. | Fallback and cursor invariants match the contract; prior objects remain intact. Requires known arena state or a separately identified reduced-size test build/instrumentation, not new syntax. |
| 7 | **A30** | Force reservation and fallback allocation failure. Ensures that successful happy-path guards are not the only evidence. | Specified failure without publishing a successful object. Requires deterministic syscall/fault controls; existing `--fail-alloc` must not be assumed to simulate both internal system-call failures. |
| 8 | **S35** | Copy an alias, insert an intervening allocation, then grow the original; inspect both handles and the intervening bytes. | Owner-approved conditional copy/share semantics and no unrelated corruption. Run on the production allocator; disabling extension cannot validate extension semantics. |
| 9 | **F43** | Force the backing allocation to fail on an actual copy-growth path. | No unchecked null-header write or partial object update accepted as clean failure. Force copy rather than tail extension, and establish exactly which allocator call the injection counts. |
| 10 | **R46** | Two unaliased kosh[1] vectors, A then B, one million appends each, with non-perturbing backing-span accounting. | Correct contents and exact event-based retention accounting within the R140 gates. No claim of a fixed process-memory bound from this finite test. |

This selection does not waive the single-tail R45 gate, the rest of the 48, complete writer/read coverage, cross-target decisions or the published-seed campaign. It is a practical first batch, not a new minimum that erases previously open requirements. Fault/state-controlled fixtures require harness work before they are executable; “no new language syntax” is not “already implemented.”

### Essential guard-harness controls, separate from the ten source fixtures

R140 did not include a standalone raw-read calibration in its 48. Add that explicitly rather than pretending a write-only canary observes reads. Each failing control runs as its own child, with its expected signal/status specified in advance. These are proposed controls, **NOT RUN**:

| Control | Operation | Expected observation |
|---|---|---|
| G1, within-bound positive | Allocate eight bytes, initialize/read `p[0]`; allocate one byte and read that byte. | Successful result; establishes a functioning baseline. |
| G2, trailing read | Allocate eight bytes, then evaluate/use `pad8(p + 8)`; also one-byte `akshar(p,1)` on a one-byte allocation. | Fault under a successfully installed trailing guard. A canary alone would not detect these reads. |
| G3, trailing write | Corresponding `likh8(p + 8, value)` and `akshar_rakh(p,1,value)`. | Fault, including an access form the census regex does not recognize. |
| G4, leading-bound calibration | Allocate eight bytes and read/write at `p-8` in a child. | Current right-guard geometry can miss it; the proposed leading-guard variant must detect it. Label the current miss honestly. |
| G5, guard-install failure | Force `mprotect` failure while mapping succeeds. | Distinct harness failure; no unprotected allocation counted as guarded. |
| G6, syscall-buffer boundary | Use a valid test descriptor with a buffer crossing a guard in a read/write request. | Assert actual syscall result/bytes/error; do not require every such violation to signal the process. |

For the corrected positive library fixtures, initialize exactly the input extent, place nonzero guards at logical output boundaries, and inspect them immediately. Record input and output boundaries separately. Guard pages catch accesses to protected pages; canaries principally catch persistent writes; neither mechanism alone is a complete access oracle.

### Unchanged numerical retention gates

For the specified unaliased, append-only arena fixtures, retain the definitions and thresholds from R140:

- Single uninterrupted tail, sufficient arena room: **R_payload = R_reserved = 0**; any positive retirement fails that fixture's claim.
- Two alternating vectors: **R_payload <= 16*N** and **R_reserved <= 16*N + 32*G**, where N is aggregate successful appends and G is copy-growth retirements.
- Proposed finite-workload budget: **R_reserved <= 67,108,864 bytes (64 MiB)**, with owner approval; v263 does not enforce this policy cap.
- One confirmed unauthorized write, unexplained fault or unapproved semantic delta fails correctness qualification regardless of a low retention figure.

For R46's two million aggregate appends, the previously derived all-copy schedule predicts **16,777,856 retired reserved bytes** (16,777,200 payload +640 headers +16 padding); the coarse gate is **32,001,280 bytes** at G=40. These remain arithmetic expectations from R139/R140, not fresh native measurements. Production event accounting must explain any difference rather than merely fit below the coarse limit.

## WS4 — exact reference-page wording and honest scope

**Status line to publish now:**

> Planned v1 feature — `mandapa` and its K0 checker are not provided by the v263 bump allocator.

**The beginner sentence:**

> Use `mandapa` for temporary, fixed-size buffers of numbers during a small calculation; their space is reclaimed when the block is exited, and the containing checked function cannot use `kosh` vectors.

**One necessary explanation below it:**

> A buffer may contain several numbers, but the initial checker needs a known allocation size and provably valid accesses. It does not yet accept growable vectors, arbitrary dynamic indexing, pointer-containing structures, or calls whose memory effects have not been verified. An ordinary vector-using function can pass a numeric value to a separate checked helper; that does not make the vector-using caller memory-safe.

This describes the accepted initial K0 feature, not a general memory model or a way to wrap an existing vector-heavy application unchanged. Retain the owner's indentation-block presentation when adding an eventual example. Do not show a working `mandapa` example under today's v263 compiler or advertise release-to-the-OS on every block exit: the planned action is scratch-space reclamation/reuse. [R1,R12]

The fetched `docs/decisions/MEMORY-DECISION.md` still contains its historical staged design and later Step-0 correction; I have not changed it or asserted that the new scope paragraph is already present. The requested sentence is returned for Sarvam to integrate, with the implementation status kept visible.

## Acceptance disposition and source ledger

**Recommended disposition:** adopt and harden the guard-page gate; credit the completed library/caller repairs; require explicit read coverage and production-allocator tests before scoped release qualification. No unrestricted memory-safety certification. No new production corruption has been executed or established by this round's harness observations.

All repository reads below used the pinned main above unless a historical commit is explicitly named.

- **R1:** `Sarvam-to-ChatGPT/ROUND-141.md`, `4ea1901b95bf2b8f2e086893a5aa0796d231d7c4` — four questions and acceptance of initial K0 scope.
- **R2:** `Claude-to-Sarvam/R68-00-PAD-VAM-AND-AUDIT.md`, `942b144008d4e03eb71aeefc847124c83f9c5fbf` — reported results, repair commits, counts, known controls, fixed-seed blind spot, audit caveats. Read the opening/main audit and full remainder from source line 150 onward; selected claims are attributed, not rerun.
- **R3:** `Claude-to-Sarvam/evidence-r68/guard-pages-how.sh`, `4ec9a92b4b3985007023a48ced493d3eec4ff6a3` — replacement build and disabled arena/extension.
- **R4:** `Claude-to-Sarvam/evidence-r68/guard-page-sequence.asm`, `86e2d3b6d91cbf09d7e2f6a3f9a6e6ead58744c2` — right-guard layout and unchecked mprotect return.
- **R5:** `Claude-to-Sarvam/evidence-r68/r68_efence.inc`, `47bf0cd81e046caf0d4396a9d715dc48a054935d` — emitted byte template and emitter. No independent native disassembly/build equivalence claim is made here.
- **R6:** `Claude-to-Sarvam/evidence-r68/census.py`, `35e91366b891f289362f2bdd1fdb4440da1621e4` — write regexes and function-body extraction.
- **R7:** `Claude-to-Sarvam/evidence-r68/audit-vakyank-varna.md:1-95`, `309c0c4881f0f76eb27540346e3d8c75dc92dc83` — explicit READ notes and capacity/domain reasoning.
- **R8:** `Claude-to-Sarvam/evidence-r68/audit-suchi-ganita.md:1-90`, `97e55a97f383e5a84ac81c0a2b2c5a3d4fe5b1a2` — additional manual read/bounds reasoning and collection invariants.
- **R9:** `lib/mala.smlib:1-75`, `de4e247aeb862e0f8986ce04de47b08aac417fe4`; `lib/kalana.smlib:120-165`, `b5155a3323042ecf46ad25fba4f7999207701247`; `lib/varna.smlib:14-40`, `4bf3ead14fb55239a583da7d840665f52f9ed6aa` — live raw-access, inline-store and unbraced-function examples.
- **R10:** `tests/run_tests.py`, `edd6d7d1fae2542343a168fd760f4aeafc0afc76` — distinction between compiler refusals, native execution and NO-EXPECTATION status.
- **R11:** returned R140 report and its 48 fixtures in this conversation — unchanged ID/threshold basis; this review prioritizes rather than redefines the suite.
- **R12:** `docs/decisions/MEMORY-DECISION.md`, `6c810dbe9ab97fb433145079b2d301ce6cdf5e98` — vocabulary, indentation convention and historical staged plan.

External API verification, checked 30 October 2026, used only for protection/error behavior:
- **W1:** Linux man-pages, mprotect(2): https://man7.org/linux/man-pages/man2/mprotect.2.html — PROT_NONE, success/error reporting and protection failures.
- **W2:** Linux man-pages, read(2): https://man7.org/linux/man-pages/man2/read.2.html — inaccessible buffer/EFAULT and returned transfer counts.
- **W3:** Linux man-pages, write(2): https://man7.org/linux/man-pages/man2/write.2.html — inaccessible buffer/EFAULT and partial transfers.

**Executed here:** small local Python checks of the published census regexes on four explicit statement strings, and integer arithmetic for the eight-byte guard layout. These are not native compiler, allocation, signal or library tests. No repository source/tool was edited or executed.

**NOT RUN — no native toolchain invoked:** guard compiler construction, native controls, all ten priority fixtures, the remaining 48-suite campaign, syscall-failure injection, Linux/PE/Windows/Wine programs, benchmarks, regression/proof suites, or release gates. Full raw-log verification and a complete new library access census were not performed. All partner run totals remain attributed.

**NOT APPLIED:** production or harness fixes, canonical reference text, library, example, test, tool, workflow, pack, Windows or backup changes. Add only this handoff in `ChatGPT-to-Sarvam/`, read it back, verify its commit scope, then stop after Round 141.
