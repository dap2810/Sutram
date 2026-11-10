# Sutram — ROUND-172: the design is ready. Build the smallest piece, and answer one risk first.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**A fourth design has arrived and it is the first one that keeps the descriptor unchanged.** **ROUND-171 is superseded by it — it is narrower than necessary.** **Do not build 171's version; read this first.**

---

## 1. What the design says, and why it is better than what you were given

**Three facts that change the plan:**

1. **The `kosh` descriptor stays exactly 32 bytes (56 with R82).** **No layout change. The guard survives for every program without a `chakra` loop.**
2. **The runtime `FLAG_SLICED` pin is removed entirely.** **The compile-time check is sufficient. That eliminates the loop that would have pinned a descriptor every pass.**
3. **Slices carry their origin.** **Every symbol records `origin_scope_depth` and `origin_sym_id`, so `s2 = s1` copies them and a transitive slice escape is caught.** **That closes the case your four conditions in R171 would have missed — a slice is not a `kosh`.**

**And the reclamation covers `kosh` and `mala`, not just a big buffer:**

> *"`scratch_cur` is used for `nirmmita`, local `mala`, and `chakra`-local `kosh` descriptors and buffers. Rewound at `mandapa` exit and at the end of every `chakra` iteration."*

**So a `kosh` made every pass, and a `mala` made every pass, are both reclaimed — which is the 48 and 80 bytes a pass.**

---

## 2. WS1 — and the one risk to answer before any code

**The design tracks `scratch_high_water` — the highest the cursor ever reached before a rewind — so that an allocation above it knows it is touching virgin, kernel-zeroed pages and can skip zeroing entirely.**

> *"Both Linux `mmap(MAP_ANONYMOUS)` and Windows `VirtualAlloc(MEM_COMMIT)` hand out kernel-zeroed physical pages on first fault. By tracking `scratch_high_water`, any bump allocation where `new_cur > scratch_high_water` touches virgin OS zero pages and needs zero instructions."*

**That is where the design saves 3.4 ns an allocation.** **And it is the one place it could leak data instead of memory.**

**If `scratch_high_water` says "virgin" when the page was used, a student reads the previous iteration's values.**

**So answer, before building:**

1. **Where does `scratch_high_water` live, and what updates it?**
2. **What happens on the first allocation after a rewind — is the comparison `new_cur > high_water` done before or after the cursor moves?**
3. **Can `high_water` ever be *higher* than the memory actually written?** **A `nirmmita` that allocates without writing would raise the cursor but leave the pages untouched.** **Then a later allocation below `high_water` would be zeroed unnecessarily — safe — but a later allocation *above* a written-then-rewound region would be wrong.**
4. **And the honest question: is skipping the zeroing worth this risk at all?** **The alternative is eight unrolled `mov` stores at 0.9 ns — a third of the saving and none of the risk.**

**If the answer to 4 is "not worth it", say so and zero unconditionally with unrolled stores.**

## WS2 - and build the smallest piece that proves the approach
**Not the whole design. One thing:**

**A `kosh` declared inside a `chakra` iteration, never escaping, has its descriptor and buffer reclaimed at the end of that iteration.**

**That is the 48-bytes-a-pass case, and it is the one a student hits first.**

**Everything else — `mala`, transitive slice origins, the recycler's three tiers — comes after this works and the guard holds.**

## WS3 - and the guard, which outranks the measurement
**783 programs, ELF and PE.** **The design says programs with no `chakra` loop and no `mala` in a `mandapa` must stay byte-identical.**

**So: measure how many of the 783 contain a `chakra` loop.** **That number is how much of the guard is untouched, and it is the first thing to report.**

**If the guard DIFFERs on a program the design says should not change, the change is wrong regardless of what the measurement shows.**

## WS4 - and the proof
**The design's own test:**

> *"Places 64-byte poison redzones (`0xDEADBEEFCAFEBABE`) immediately before `d-16` and immediately after `d+16`, exercises 1,000,000 loop allocations, nested `chakra` loops, `mandapa` blocks, `kosh` growths to 20,000,000 elements and OOM refusals, asserting after each phase that every redzone qword is intact and that `d-16`, `d-8`, `d`, `d+8` contain exact expected values."*

**That is a test that does not depend on a re-baselined diff, which is exactly what I asked for.** **Build it.**

**And measure the leak the same way R169 established: current `VmRSS`, pages touched, baseline stated.** **A `kosh` made every pass, 800,000 passes, before and after.** **Before: 37,504 KB. After: it should be near the baseline.**

## WS5 - and the honest scope
**State in the report:**

- **this reclaims a `chakra`-local `kosh` — the 48 bytes a pass**
- **`mala` is next, and is not in this round**
- **a block still never returns memory to the OS**
- **reference §19 needs a sentence, and Muse has been asked to write it**
- **and the zeroing decision: which way you went and what it costs**

**Do not describe this as "the memory problem solved".**
