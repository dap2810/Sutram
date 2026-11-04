# Muse Round 125 — Test the reviewer's claims. Do not trust them.

- **Base:** main at v299 (`a4cc6540`, compiler `Sutram 1.0 (v299)`).
- **Deliverables:** this report, `r125.json`, WS3 probes (`r125_ws3_16.sm`,
  `r125_ws3_15.sm`), WS2 probes (`r125_ws2_nirmmita_alias.sm`,
  `r125_ws2_mala_alias.sm`), WS1 probes (`r125_ws1_vitti_kosh_alias.sm`,
  `r125_ws1_mala_holds_kosh.sm`, `r125_ws1_copy_1m.sm`), C benchmarks
  (`r125_bench.c`, `r125_bench2.c`, `r125_bench3.c` — C, not Sutram, because
  Sutram has no descriptors or value semantics yet to benchmark; stated as
  proxies, not as Sutram measurements).
- **Test and analysis only.** No descriptor, value-semantics, or lazy-commit
  design was built, no code was changed, nothing was pushed or merged by this
  round.

## Correction to the brief, stated first

The brief says of the 16-kosh number: "That number has been quoted twice now
and verified zero times." **That is stale.** Round 124 verified it on v298
(15 succeed, 16th segfaults, exit 139, commit `69a03fc7`). This round
re-verifies it on v299 (same numbers, see WS3). It has now been verified
**twice, on two versions**, with the same threshold.

## WS1 — Test the four claims

### Claim 1: The descriptor eliminates the 64 MiB reservation. PARTLY TRUE for kosh-typed accesses; FALSE as a whole-language claim.

The descriptor idea is sound for one access path: a `kosh` variable points at a
24-byte descriptor (buffer pointer, length, capacity); aliases point at the
descriptor, so growth updates the pointer inside it and every alias sees the
new buffer. For `k[i]` where `k` is a kosh variable, the buffer can then move
freely and the 64 MiB reservation is indeed unnecessary.

It does not survive for the language as a whole, because Sutram has raw-pointer
doors that bypass the descriptor — and I proved all three exist on v299 today:

- **Vitti aliases.** `vitti a = k` compiles and works (probe
  `r125_ws1_vitti_kosh_alias.sm`: `k[4]`, push 41, `a = k`, `a[0] = 99`, then
  `k[0]` and `a[0]` both print `99`, exit 0). `vitti` is untyped: at the use
  site `a[i]`, the compiler cannot know whether `a` is a descriptor pointer
  (needs a double dereference) or a raw buffer (needs a single dereference).
  `nirmmita` buffers are raw (their first 8 bytes are data, not a buffer
  pointer), so `vitti` indexing **cannot** always go through a descriptor —
  that would break every `nirmmita` buffer. So either `vitti a = k` must be
  forbidden (a breaking language change; Round 124's alias probes use it), or
  `vitti` aliases keep indexing directly (buffer address, not descriptor) and
  break on growth. Under descriptors, growth happens on **every** doubling
  (frequent), not just at MAXCAP (rare) — so `vitti` aliases would break
  **more** often than today, not less.
- **Mala cells holding kosh addresses.** Probe `r125_ws1_mala_holds_kosh.sm`
  (`yoj mala`; `k[4]`, push 41, `m = mala_nava(4)`, `m[0] = k`, `p = m[0]`,
  `p[0] = 99`, then `k[0]` prints `99`, exit 0): a kosh buffer address can be
  stored in a mala cell and used later to write through to the kosh. Under
  descriptors, that stored address dangles on the kosh's next growth, unless
  mala cells holding kosh addresses are forbidden or tracked — which is a type
  system, not a descriptor.
- **Raw pointers into a buffer via arithmetic.** `kosh + int` refuses
  (`E_KOSH_GANIT`), but `vitti + int` does not — so `vitti p = k; p + offset`
  gives a raw pointer into the buffer, which dangles on movement under
  descriptors (frequently, on every growth).

The descriptor itself also needs stable storage: one per kosh, shared by
aliases, in the arena or heap — not on the stack (a stack descriptor dies on
return) and not copied (copies point at different descriptors, breaking
aliasing). That is a design constraint the review does not state.

**Verdict: the descriptor eliminates the reservation only if the language ALSO
closes the raw-pointer doors** (forbid `vitti` aliases of koshes, forbid mala
cells holding kosh addresses, forbid pointer arithmetic into kosh buffers).
Without that, it trades a rare break (at MAXCAP) for a frequent break (on every
growth) for raw-pointer users. "Two of the three defects, one change" is
optimistic: it fixes the kosh-alias cliff and the reservation for kosh-typed
accesses (two), but not the raw-pointer aliasing (the third defect class, see
WS2).

### Claim 2: The descriptor costs 1-3 cycles per access. GUESS, not a measurement — and wrong for both throughput and latency.

No benchmark, no hardware, no methodology is cited; the review says "roughly".
My measurements (AMD EPYC 9D25, 4 vCPU, TSC 1.50 GHz, `clock_gettime`, `volatile`
to force loads so the compiler cannot eliminate them or replace them with
arithmetic; benchmarks `r125_bench*.c`):

- **Array loop (the kosh access pattern: independent iterations, pipelined):**
  direct 0.276 ns/elem (0.41 TSC cycles), descriptor with a per-access descriptor
  load 0.272 ns/elem (0.41 TSC cycles) — difference ≈ 0. For the kosh pattern,
  the extra load costs **~0 cycles** (pipelined, 2 loads/cycle, L1 hit), not
  1-3. (An earlier non-`volatile` run showed direct 0.000 because the compiler
  eliminated the loop; the `volatile` run is the valid comparison.)
- **Dependent chain (the reviewer's phrasing: a load whose address depends on
  the previous load), HOT and contiguous:** direct 3.189 ns/step (4.78 TSC
  cycles), descriptor 5.429 ns/step (8.14 TSC cycles) — difference **2.240 ns/
  step** for the extra descriptor load. At a 3 GHz core that is ~6.7 cycles; at
  the 1.50 GHz TSC it is ~3.4 cycles. Either way it is **more** than 1-3 cycles
  at any plausible core frequency above ~1.5 GHz, and the brief's alternative
  (4-5 cycles) is closer (4-5 cycles at 3 GHz = 1.33-1.67 ns; measured 2.24 ns,
  a bit higher, likely address computation plus L2 hits — the descriptors are
  24 MB, sequential and prefetchable, so L1/L2 hits, not full L3).
- **Dependent chain, COLD (descriptors scattered over 24 MB, full-period
  permutation seed so loads actually miss):** 255 ns/step. That is ~250× the
  1-3-cycle claim (0.33-1.0 ns at 3 GHz). A cold descriptor load in a dependent
  chain costs hundreds of cycles (L3/DRAM misses add), not 1-3. (A second cold
  run at 5.3 ns/step is INVALID and is not used: an even seed made its
  generator degenerate, so it did not actually scatter.)

And the brief's own dichotomy — "1-3 cycles or 4-5 when it misses L1" — is
confused: **L1 hit latency is 4-5 cycles; L1 miss latency is 14+ cycles (L2),
~40 cycles (L3), ~200+ cycles (DRAM).** Neither 1-3 nor 4-5 is the miss cost.
1-3 cycles is below even the hit latency.

**Verdict: "1-3 cycles" is a guess that is correct for neither throughput (0)
nor latency (hot dependent ~2.2 ns, cold dependent ~255 ns).** The honest
statement is: ~0 cycles throughput for array loops (pipelined, hoisted or not),
~2.2 ns extra latency for a hot dependent load, ~255 ns for a cold dependent
load. For kosh array access, the descriptor is essentially free; for
pointer-chasing, it is not 1-3 cycles.

### Claim 3: Value semantics eliminates the alias cliff. PARTLY TRUE for flat scalar koshes; NOT acceptable for large koshes, and NOT true in general.

Value semantics means `vitti a = k` is a DEEP COPY: `a` gets its own copy of
`k`'s elements. Measured cost for 1M elements (8 MB) on this hardware:

- C `memcpy` (builtin, fresh destination, page faults included): **3.659 ms**
  (2.3 GB/s on this VM — not the 20 GB/s a desktop might give; the measured
  number, not a guess, is what matters here).
- Sutram loop copy (build a 1M-element kosh + copy it element-by-element, 2M
  pushes, probe `r125_ws1_copy_1m.sm`): **0.061 s total, ~30 ms per 1M-element
  copy via loop** (and it prints the correct last element, 999999).

So a single 1M-element assignment costs 3.7 ms (builtin) to 30 ms (loop) — not
free. In a loop (1000 assignments, extrapolated linearly): 3.7 s (builtin) to
30 s (loop). Plus 1000 × 8 MB = **8 GB allocated and leaked** (there is no
free): if arena-allocated, that hits the 1 GiB arena bound (`kshetra purnam`)
long before 1000 assignments; if region-allocated (64 MB per copy), 1000 copies
= 64 GB of virtual size — **the same ceiling as today, crashing at the 16th
copy under a 1 GiB limit**. Value semantics **alone** does not fix the WS3
ceiling; it needs the descriptor design (which eliminates regions) to fix it.

And "aliasing simply does not exist" is false in general: a deep copy of
elements copies **pointers**, not pointed-to data, for koshes of strings,
nested koshes, or `nirmmita` buffers (shallow at depth 2+). `a[0]` and `k[0]`
(nested koshes) would still be the same object, so pushing to `a[0]` affects
`k[0]` — the alias cliff moved one level down, not eliminated — unless the
copy is **recursive** (O(total size), and cyclic structures — a kosh containing
itself — would loop forever or need cycle detection, which is complex, not
simple).

Is it acceptable? **No for large koshes** (1M elements: 3.7-30 ms + 8 MB leak
per assignment; in a loop, seconds + gigabytes leaked + arena exhaustion).
**Maybe for small koshes** (a few elements: dozens of bytes, negligible) — but
then the performance surprise remains: assignment **looks** cheap (O(1)) in
every language a student knows, and under value semantics it is O(n). A student
writing `a = k` in a loop over a large kosh gets quadratic behaviour without
expecting it. Value semantics replaces the alias cliff with a performance cliff
plus a leak cliff, and it violates the more basic intuition (assignment is
cheap) to fix the less basic one (aliasing).

**Verdict: does not survive as a general claim.** It survives only for flat,
small, scalar koshes, with the O(n) cost stated — and it does not fix the
1 GiB ceiling without the descriptor design as well.

### Claim 4: Windows lazy commit is 4-5 instructions. SURVIVES WITH QUALIFICATION (fast path only; slow path is a syscall, amortized).

Lazy commit = `MEM_RESERVE` at startup (free, no commit, no pages) +
`committed_cursor` (end of the committed region) + on **allocation** (bump),
check whether the new allocation exceeds `committed_cursor` (`cmp` + `jbe`, 2
instructions, plus the bump itself and the return — so the allocation fast path
is ~4-5 instructions total, plausible). **The check is ONLY on the allocation
path, not on the access path:** `a[i]` and `*p` have **zero** extra
instructions, because the allocator ensures the committed region covers all
allocated memory before returning the pointer, so accesses never fault. The
slow path (once per 1 MiB chunk) is a `VirtualAlloc` (`MEM_COMMIT`) syscall —
hundreds of cycles plus a kernel transition, **not** 4-5 instructions — but
amortized over 1 MiB of allocations (131,072 × 8-byte allocations → ~1000
cycles / 131072 ≈ 0.008 cycles per allocation, negligible). For kosh regions,
each region would need its own `committed_cursor` (or commit on growth in
chunks, not at creation: a newly created kosh of capacity 4 commits only 4 KB,
one page, not 64 MB, growing on demand — so per-kosh commit is proportional to
actual size, not 64 MB, which is the point).

"Hello World drops from 1 GB to a few kilobytes" is **true for hello** (0
allocations → commit is a few KB, binary/stack only). On Linux it is already
true without any change (Round 124 WS2: hello is 16 KB RSS / 0.2 MB VSZ,
because Linux is already lazy via `MAP_NORESERVE`) — so Windows lazy commit
brings Windows to parity with Linux's existing laziness; it does not beat
Linux.

**Verdict: survives with qualification** — fast path 4-5 instructions,
allocation path only, not access path; slow path is a syscall, amortized to
negligible per allocation.

### The reviewer's two closed answers — concurred, with one qualification each

- **Reuse inside a live block is NO: concurred as a design decision.** A bump
  allocator cannot know an object is dead (no free, no refcount, no runtime
  liveness), and naive reuse (resetting the bump pointer mid-block) would
  corrupt live aliases (any alias to a "dead" object that is actually still
  reachable reads reused memory, wrong). Reuse with compiler-proven
  dead-object analysis is possible in principle, but that is a compiler
  optimization, not a runtime bump reset — and it is not trivial. "NO" is
  correct for naive reuse; it is not a theorem that reuse is impossible.
- **Threads are NEVER: concurred for the current design.** The arena cursor is
  a single global bump pointer; two threads bumping it concurrently race
  (return the same address to two threads, or corrupt the cursor) unless
  synchronized (a lock serializes allocations; thread-local arenas are a
  redesign, not a fix). Kosh regions are per-kosh `mmap`s, but a region's header
  (length/capacity) would race if two threads push to the same kosh concurrently
  (needs locks or atomics per kosh — a redesign). Threads are not a small fix;
  they are a redesign, out of scope for v1.0 — and the reference should say so
  (Round 123 WS3 gap (v) already notes the reference omits threads; the
  reviewer's "NEVER" and that gap align).

## WS2 — "Aliasing simply does not exist" under value semantics for kosh. TRUE that it closes one door; FALSE that it closes aliasing. Two doors stay open.

Probes on v299, both exit 0, both print `99` (the written value, read through
the alias — proving the alias, not the copy):

- **Nirmmita raw pointers alias — by definition, and they must.**
  `r125_ws2_nirmmita_alias.sm`: `p = nirmmita(16)`; `q = p`; `q[0] = 99`;
  `p[0]` prints `99`. `vitti` assignment copies the **address**, not the
  buffer. `nirmmita` is explicitly a raw-pointer API (for buffers, FFI, and the
  slice idiom: `string + int` pointer arithmetic **is** aliasing by design).
  Value semantics for `kosh` does not touch `nirmmita`, so it cannot close
  this door — and it must not, because `nirmmita`'s purpose is to share a
  buffer.
- **Mala arrays alias — via the same `vitti` assignment.**
  `r125_ws2_mala_alias.sm` (`yoj mala`): `m1 = mala_nava(4)`; `m2 = m1`;
  `m2[0] = 99`; `m1[0]` prints `99`. The reviewer proposed value semantics for
  `kosh` only, not for `mala`, so `mala` still aliases. Even if `mala` were
  also made value-semantics, `nirmmita` still must alias (above), so
  "aliasing simply does not exist" is false for the language as a whole.

**Therefore escape analysis does NOT become trivial overall.** It becomes
trivial for `kosh` only; `nirmmita`/`mala` escapes still need analysis
(`E_SCRATCH_ESCAPE` for `nirmmita` buffers in blocks, and the same for `mala`
buffers that escape). Value semantics for `kosh` closes one door and leaves
two open — exactly as the brief suspected.

## WS3 — Measure what the reviewer says to measure, on v299

| Program | Limit | Result |
|---|---|---|
| 16 kosh, no limit (control) | none | `made 1` … `made 16`, `all 16 made`, exit 0 |
| 16 kosh | `ulimit -v 1048576` (1 GiB) | `made 1` … `made 15`, then **segfault, exit 139**, during the 16th creation |
| 15 kosh | `ulimit -v 1048576` (1 GiB) | `made 1` … `made 15`, `all 15 made`, exit 0 |
| 1000 kosh | `ulimit -v 1048576` (1 GiB) | **segfault, exit 139** (before printing `made 1000`, consistent with crashing at the 16th) |

**The reviewer's "current design would crash under a 1 GiB limit" for 1,000
collections is TRUE — but the threshold is 16, not 1000.** Any N ≥ 16 crashes;
1000 is just an example of "many". And "the new design will consume a few
kilobytes" for 1000 collections is **loose**: for value semantics alone it is
false (1000 copies = 1000 regions = 64 GB VSZ, same ceiling, crashes at the
16th copy); for the descriptor design with bump-allocated buffers it is
1000 × 24 bytes (descriptors) + 1000 × 8 bytes (data) = **32 KB — a few TENS of
kilobytes, not a few kilobytes**; with per-buffer `mmap` pages it is
1000 × 4 KB = **4 MB**. The spirit (orders of magnitude smaller than 64 GB) is
true; the letter (a few kilobytes) is true only for hello (0 collections), not
for 1000.

## Summary: which claims survive

| Claim | Verdict | One-line reason |
|---|---|---|
| 1. Descriptor eliminates the 64 MiB reservation | PARTLY | True for kosh-typed accesses; false for the language (vitti/mala/raw-pointer doors open, and it makes raw-pointer breaks frequent, not rare) |
| 2. Descriptor costs 1-3 cycles/access | DOES NOT SURVIVE as stated | Guess, not a measurement; throughput ~0, hot dependent latency ~2.2 ns, cold dependent ~255 ns; L1 hit = 4-5 cycles, L1 miss = 14+ cycles — neither 1-3 nor 4-5 is the miss cost |
| 3. Value semantics eliminates the alias cliff | PARTLY | True for flat scalar koshes only; not for nested/pointer koshes (shallow at depth 2+, recursive copy has cycle/cost problems); not acceptable for large koshes (1M elements: 3.7 ms builtin / 30 ms loop per assignment + 8 MB leak, + arena/VSZ exhaustion in loops) |
| 4. Windows lazy commit is 4-5 instructions | SURVIVES WITH QUALIFICATION | Fast path 4-5 instructions, allocation path only (not access path); slow path is a syscall, amortized to negligible; hello drops to a few KB (true); 1000 collections drop to 32 KB - 4 MB (not a few KB, but orders of magnitude smaller than 64 GB) |
| WS2: value semantics closes aliasing | FALSE for the language | Nirmmita (must alias, by design) and mala (via vitti) still alias; escape analysis does not become trivial overall |
| WS3: 16-kosh ceiling | VERIFIED (twice) | 15 succeed, 16th segfaults, on v299 (and v298); 1000 crashes too (at the 16th); brief's "verified zero times" is stale |

## NOT RUN

Windows execution (cannot run Windows — the Windows lazy-commit analysis is by
reasoning about the proposal and the current PE shim, not by running PE code;
the Linux measurements are on v299), browser, implementation (none authorized
— test and analysis, not building the descriptor, value-semantics, or
lazy-commit designs), native-speaker review, full suite (no tree changes; the
v299 suite numbers stand, not re-run here).
