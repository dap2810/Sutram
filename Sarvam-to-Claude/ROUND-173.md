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

# ROUND-173 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Your R172 works and the guard held.** **Three audits now say the benchmark could not have told the difference between your fix and a broken one.** **This round verifies, and it is not a request to rebuild.**

## WS1 - and this is the round: the growth case
**The benchmark pushed one element into `kosh temp[1]`.** **It never grew.** **So it cannot distinguish a hoist that reuses the grown buffer from one that re-allocates every pass.**

**Answer by reading your own emitted code, then measure:**

1. **At the top of each pass, what is reset?** **Only `[d-16]` (length), or also `[d-8]` (capacity) and `[d]` (elements pointer)?**
2. **If only length is reset, a `kosh` that grew on pass 1 keeps its grown buffer on pass 2.** **Confirm that from the emitted instructions.**
3. **And measure it:** a loop of 800,000 passes where the `kosh` grows to 100 elements on the first pass and stays at 100.** **If the fix is right, peak stays flat.** **If capacity is re-initialised, it leaks 800,000 grown buffers and the number will show it.**

**Report the emitted instruction sequence for the per-pass reset, not a description of it.**

## WS2 - and the container escape
```
kosh matrix[10]
chakra i = 1 tak 5 {
    kosh row[2]
    kosh_kship(row, i)
    kosh_kship(matrix, row)
}
likha(matrix[0][0])    // must be 1, not 5
```

**Does the escape check flag `kosh_kship(matrix, row)`?** **And `matrix[i] = row`?**

**If not, that is the hole: `row` is hoisted, every pass reuses one descriptor, and all five rows point at it.**

**Test it.** **If `matrix[0][0]` prints 5 instead of 1, the fix is wrong and must be withdrawn.**

## WS3 - and the nested-block case
**A `kosh` inside `chakra { mandapa { ... } }` and inside `chakra { yadi ... { ... } }`.**

**Is it hoisted?** **Measure the same 800,000-pass test in both shapes.**

**If the leak returns when a `mandapa` or `yadi` sits between the loop and the declaration, the hoist does not walk into nested blocks - and that would explain the measured 48 bytes/pass outside a block against 64 inside one.**

## WS4 - and the `mala`, which is now the largest remaining leak
**80 bytes a pass, block or not, 62,464 KB at 800,000.**

**Two things, and they must be done together:**

1. **Refuse `mala` escape with the existing `E_SCRATCH_ESCAPE` rule.** **The declaration-depth check already exists for `nirmmita`; this is the same check applied to one more type.**
2. **Then hoist a loop-local `mala` and zero its `N` qwords at the top of each pass.**

**Why zeroing is needed for a `mala` and not for a `kosh`:** **a `kosh` has a length field, so resetting it makes old elements unreachable. A `mala` has no length — all `N` slots are readable immediately on the next pass.** **Zeroing 64 bytes is eight unrolled stores, about 0.9 ns.**

**And do not hoist a `mala` without refusing escape first.** **A `mala` escapes a block with no error today; hoisting it while it can still escape would alias every row.**

## WS5 - and the stale-data bug
**An ordinary `nirmmita` after a block can be handed memory the block wrote.**

**A proposed fix: a dirty high-water mark, updated only at `mandapa` exit, so only the overlapped dirty span is zeroed.** **A 200 MB block followed by one `nirmmita(64)` zeroes 64 bytes, not 200 MB.**

**Is that right, and is it smaller than zeroing unconditionally?**

**Measure the current behaviour first:** a block that writes a known pattern, then a `nirmmita` that reads before writing.** **Does it read the pattern?** **Report the value.**
