# Sutram — ROUND-171: one narrow case. A proven-local `kosh` releases its big buffer.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**This round reverses nothing.** **Reference §19 documents that a block does not reclaim a `kosh` or a `mala`, and gives a measurement — 200,000 calls declaring a `mala` of 31 numbers inside a block end at `parimana()` 51,200,000.** **That decision is sound: a `kosh` and a `mala` can escape, so reclaiming them would leave a live name pointing at freed memory.**

**This round narrows the decision to one provable case.**

---

## 1. What all three partners agree on

**ChatGPT, on the design:**

> *"A `kosh` is reclaimable when no permitted future use can reach its descriptor or backing storage. Scope exit is a sufficient point only for a proven non-escaping owner. Last syntactic name is not sufficient: aliases, parameters and containers can still refer to the object."*

> *"Calling that 'no escape analysis' would be misleading; it is a small conservative escape check, not a general borrow checker."*

> *"The cheapest defensible first step is a restricted non-escaping-local cleanup path that releases only its current separately mapped buffer. Keep the descriptor and small allocations on their current path in that first experiment."*

> **The rule: *"storage belongs to the collection's owner; growth keeps that owner. Do not rewind the shared persistent arena."***

**Muse, on what is and is not missing:**

> *"The pointer to it **is** recorded: in the descriptor, as the elements pointer `[d]` (the region base, by construction) plus the size as `[d+8]`. There is no side table. Freeing at death is not blocked by missing bookkeeping — the growth path already frees the old region with exactly the two words a death-free would need. What a free-at-death does not have today is (a) a decision point — knowledge that the `kosh` is dead — and (b) the aliasing guarantee."*

> *"`munmap` / `VirtualFree` releases the whole old region, on both platforms."*

**Claude, on why there is no one-line change:**

> *"The one-line change does not exist, because no `kosh` ever dies in the generated code: no descriptor is released at any scope exit, so there is no line to put a `munmap` beside."*

**And the corrected severity:** **the 64 MiB is `MAP_NORESERVE` — mapped, never committed.** **Only written pages cost anything, about 36 KB of the 64 MiB.** **1,000 passes and 20,000 passes both finish.**

---

## 2. WS1 — and the case is narrow on purpose

**Implement exactly one thing:**

**A `kosh` that satisfies all four of these, inside a `mandapa`, has its separately mapped buffer released when the block exits:**

1. **declared inside the block** — not outside it
2. **never assigned to a variable declared outside the block**
3. **never returned by `nivartanam` from the enclosing `prakriya`**
4. **never passed to `kosh_kship` or stored in any other collection**

**If any of the four fails, the `kosh` is not reclaimed — it behaves exactly as today.**

**And what is released is only the separately mapped buffer — the region above 4,097 elements.** **The descriptor stays. Small allocations stay. Nothing about the current path changes for anything else.**

## WS2 - and why only the big buffer
**Because it is the only case where the release is already written.**

**Muse: the growth path already frees the old region with exactly the two words a death-free needs.** **So the code exists, the addresses are in the descriptor, and the only missing piece is the decision point.**

**A small `kosh`'s buffer is inside the shared arena, and releasing it would mean freeing part of a region others may be using.** **Do not touch it. That is a different problem and it is not this round.**

## WS3 - and the check
**The four conditions are all decidable in one pass with a `decl_depth` comparison plus a flag per `kosh` symbol:**

- **assigned outward** — `lhs.decl_depth < rhs.decl_depth` at any assignment
- **returned** — a `nivartanam` whose expression is the symbol
- **stored** — the symbol appearing as an argument to `kosh_kship` or as the right side of a `kosh` element write

**Set the flag when any of those is seen; at block close, release only if the flag is clear.**

**And if a `kosh` is used in a way you cannot classify, do not reclaim it.** **A missed reclaim is a leak; a wrong reclaim is a crash.** **Fail toward leaking.**

## WS4 - and the message, if a student hits the limit
**If a `kosh` is not reclaimed because it escapes, that is silent — it behaves as today.** **No new error.**

**But if a student writes a loop with a `kosh` that escapes, and memory grows, the compiler could warn.** **Is a warning right here, and what would it say?** **Answer; do not build it.**

## WS5 - and the proof
**Measure before and after, with the method R169 established:**

**A `kosh` grown past 4,097 elements inside a `mandapa` inside a loop, 1,000 passes. Sample `VmSize` and `VmRSS` at four points. Pages touched. Baseline stated.**

**Before: `VmSize` grows by about 64 MiB a pass.** **After: it should not.**

**And the guard: 783 programs, ELF and PE, byte-identical or identically refused.** **If the guard DIFFERs, the change is wrong regardless of what the measurement shows.**

## WS6 - and the honest scope
**Say in the report:**

- **this reclaims one case of three** — a big `kosh`, proven local
- **a small `kosh` still leaks 48 bytes a pass, 64 in a block**
- **a `mala` still leaks 80 bytes a pass**
- **a block still never returns memory to the OS**
- **and reference §19 needs a sentence saying which case now releases and which still does not**

**Do not describe this as "the memory problem solved".** **It is the first case, and it is the one where the code already existed.**
