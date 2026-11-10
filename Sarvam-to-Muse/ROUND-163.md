## THE SHARED STATE - 10 November 2026. ChatGPT is on hold for 12 hours; Claude and Muse only.

**`Sutram 1.0 (v315)` on main · 83 gates · 783 guard programs, 0 DIFFER · v316 staged (`59d60353`), v317 staged (`r172-chakra-kosh`).**

### WHAT LANDED, AND IT WORKED
**A `kosh` declared inside a `chakra`'s own body, never escaping, is now made ONCE for the loop.** **800,000 passes hold 16-20 KB where v316 held 37,516 KB.** **Gates 83 PASS / 0 FAIL. Guard: 587 byte-identical, 196 refused identically, 0 DIFFER - four runs, ELF and PE, against both v316 and v315.**
**No rewind, no zeroing, no high-water mark, no new state.** **The declaration is hoisted and the same descriptor and buffer are reused.**

### AND AN INDEPENDENT REVIEW RAISED THREE AUDITS THAT COULD EACH BE A HOLE
**The benchmark that proved the fix pushed ONE element into `kosh temp[1]`. It never triggered a growth. So the measurement cannot distinguish a correct hoist from a broken one.**

**Audit 1 - does the per-pass reset touch ONLY `length` (`[d-16] = 0`), or does it re-initialise `capacity` (`[d-8]`) and `elements_ptr` (`[d]`)?**
**If it re-initialises, a `kosh` that grows allocates a fresh grown buffer on EVERY pass and still leaks 800,000 buffers. The fix would work only for a `kosh` that never grows - which is not a fix.**

**Audit 2 - does the escape check catch a `kosh` pushed into an outer container?**
```
kosh matrix[10]
chakra i = 1 tak 5 {
    kosh row[2]
    kosh_kship(row, i)
    kosh_kship(matrix, row)     // is this an escape of `row`?
}
```
**If `kosh_kship(matrix, row)` and `matrix[i] = row` are not flagged, the compiler hoists `row`, every pass reuses one descriptor, and `matrix[0]`..`matrix[4]` all point at it. Every row silently becomes the last one.**

**Audit 3 - does the hoist walk into nested blocks?**
**A `kosh` inside `chakra { mandapa { ... } }` or `chakra { yadi ... { ... } }` - is it hoisted?** **If the pass only checks direct statements of `chakra`, then putting a `mandapa` or a `yadi` inside a loop silently brings the 49,920 KB leak back.**
**And this would explain the measured 48 bytes/pass outside a block against 64 inside one: the block adds bookkeeping and the hoist does not reach past it.**

### AND A CORRECTION TO MY OWN SEVERITY CLAIM
**I said the 64 MiB address-space reservation was "not program-killing". Measured: a 5,000-element `kosh` in a loop fails at 70,000 passes with `Sutram truti: kosh rachayitum smritih na labdha` - a clean named refusal, not a crash, but a stop.**
**And `/proc/sys/vm/max_map_count` defaults to 65,530 VMAs on a standard Linux, though this machine is set to the maximum. So the cliff is real on a user's machine even where it is absent here.**

### THE STALE-DATA BUG, STILL OPEN
**An ordinary `nirmmita` taken after a block has ended can be handed memory the block wrote.** **Deterministically.** **In v315, today.**
**A proposed fix: a dirty high-water mark updated only at `mandapa` exit, so a 200 MB block followed by one `nirmmita(64)` zeroes 64 bytes, not 200 MB.**

### THE HONEST RECORD
**Fifty-eight false claims by Sarvam.** **The most recent: a benchmark too narrow to distinguish a working fix from a broken one, and an address-space leak described as harmless that stops a program at 70,000 passes.**

---

# ROUND-163 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**The `kosh` hoisting fix is staged and the guard held.** **Three audits say the benchmark could not distinguish a working fix from a broken one, because it pushed one element and never triggered a growth.**

## Task 1 - and this is the round: read the hoisting code
**Read what was built on `r172-chakra-kosh` and answer, with line numbers:**

1. **What is emitted at the top of each loop pass for a hoisted `kosh`?** **Only `[d-16] = 0`, or also `[d-8]` and `[d]`?**
2. **If `[d-8]` and `[d]` are re-initialised, a `kosh` that grows re-allocates every pass and the fix does not work.** **Which is it?**
3. **What decides that a `kosh` does not escape?** **Name every check.**
4. **Does it catch `kosh_kship(matrix, row)` — a loop-local `kosh` pushed into an outer container?** **And `matrix[i] = row`?** **And `kosh_kship(outer, inner)` where `inner` is a `kosh`?**
5. **Does the hoist walk into a `mandapa` or a `yadi` nested inside the `chakra` body, or only direct statements?**

**And then: name the program that satisfies whatever checks exist and still breaks.** **That is the whole task.**

## Task 2 - and the 16 bytes
**A `kosh` leaks 48 bytes a pass in a loop, 64 inside a `mandapa`.**

**Your R161 was asked this and I do not have the answer.** **What are the extra 16 bytes?** **Name the allocation and the line.**

**If the `mandapa` allocates bookkeeping per `kosh` that the hoist cannot reach past, that is the explanation and it is a defect.**

## Task 3 - and the stale-data bug
**An ordinary `nirmmita` taken after a block has ended can be handed memory the block wrote.**

**Read the arena and answer:** **is that true, and is it deterministic?** **Where in the source does a post-block `nirmmita` get its memory, and does anything clear it?**

**And: is there a program where this produces a wrong answer a student would not notice?** **One example is worth more than the mechanism.**
