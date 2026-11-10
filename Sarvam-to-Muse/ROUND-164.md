## THE SHARED STATE - 10 November 2026. ChatGPT held for 12 hours.

**`Sutram 1.0 (v315)` on main · 84 gates · 783 guard programs, 0 DIFFER across six runs · three staged branches: v316 (`59d60353`), v317 (`501d35fd`), v318 (`c1f516f8`).**

### WHAT LANDED
**A `kosh` declared in a `chakra` body, never escaping, is made once and reused: a `kosh` grown to 100 every pass holds 16-20 KB at 800,000 passes, where v316 held 825,016 KB.** **The reset writes one word, the length — capacity and elements pointer survive.**
**A `mala` declared in a `chakra` body is made once too: 62,516 KB -> 20 KB.** **Built WITHOUT the escape refusal.**
**Nested blocks are NOT reached: under a `yadi` or in a `mandapa` inside the loop the leak is unchanged at 37,516 and 50,012 KB.**

### AND TWO INDEPENDENT REVIEWS FOUND THE SAME HOLE
**Muse, reading: *"The WS3 flag rules cover assignments, returns, and stores — and never mention calls at all — and the one check that covers calls, `r108_check_call`, never runs on the statement path."***
**The program: a block `kosh` grown past 4,097 elements, passed by its own name to a foreign function taking a `ptr`, AS A BARE STATEMENT — satisfies every escape condition, sets no flag, and hands C the elements address of a region the block exit releases.**
**And: *"Condition 4 as written is vacuous: read literally it disqualifies every grown `kosh`, since growth is `kosh_kship`."***
**Gemini, reasoning: the `mala` refusal cannot be both unnecessary and breaking. *"If the compiler already refused every `mala` escape, then adding the refusal would stop zero programs that compile today."***

### AND THREE TESTS DECIDE WHETHER v318 IS SAFE
**A - a `mala` with no zeroing on reuse:**
```
chakra i = 1 tak 2 {
    mala row[2]
    yadi i == 1 { row[1] = 99 }
    likha(row[1])
}
```
**Before the hoist: `99` then `0`. With a hoist that does not zero: `99` then `99` — the stale-data bug, moved into `mala`.**

**B - the escape paths:**
```
mala row[2]
kosh table[10]
chakra i = 1 tak 5 {
    mala row[2]
    row[0] = i
    kosh_kship(table, row)
}
likha(table[0][0])   // must be 1. If 5, all five rows alias one buffer.
```
**And the same with `out = row`, `table[i] = row`, and `row` passed to a `prakriya` that stores it.**

**C - a hoisted `kosh` inside a `mandapa`:**
**If the `kosh`'s descriptor is allocated on the same arena cursor a `mandapa` rewinds, the block exit overwrites the hoisted descriptor.** **Evidence it may be true: a `kosh` in a `mandapa` leaks 64 bytes a pass against 48 outside.**

### THE 16 BYTES, SETTLED
**24 bytes of R82 header (line, liveness slot, generation) minus 8 alignment padding.** **All three words are read by the runtime liveness check in every `prakriya` prologue, so it is used bookkeeping, not a defect.** **But the flag is program-wide, so `kosh`es that never enter a block also pay.**

### THE HONEST RECORD
**Fifty-nine false claims by Sarvam.** **The most recent: a condition ("never passed to `kosh_kship`") that disqualifies every grown `kosh` and therefore makes the whole rule vacuous.**

---

# ROUND-164 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**Your R162 found the FFI hole and the vacuous condition, and both were right.** **Two reviewers found the same call-path gap by different routes.** **This round is that gap, applied to what was actually built.**

## Task 1 - and the hoist's escape check
**R162 attacked ROUND-171's four conditions, which have been superseded by a compiler hoist.** **The hoist is built and staged as v317 and v318.**

**So: read what the hoist actually checks, and answer:**

1. **Does it consider a `kosh` passed as an argument to a `prakriya` an escape?**
2. **Does it consider a `kosh` passed to a foreign function an escape?**
3. **Does it consider a `mala` passed to either?**
4. **And the one you already found: does any check run on the STATEMENT path, where a bare call sits?**

**Then name the program that satisfies whatever the hoist checks and still breaks.** **Your FFI program is the model — a bare statement, a call, an address handed out.**

## Task 2 - and the `mala` that was hoisted without a refusal
**A `mala` declared in a `chakra` body is now made once and reused.** **62,516 KB -> 20 KB.**

**No escape refusal was added, on the argument that the compiler already refuses every `mala` escape.**

**But reference §19 says a `mala` escapes a block with no error at all.** **Both cannot be true.**

**So: read the code and say which it is.** **Does any check refuse `out = row` where `row` is a `mala` declared in an inner scope?** **Does any refuse `kosh_kship(table, row)`?**

**And: does the hoisted `mala` clear its N elements at the top of each pass?** **A `mala` has no length field — all slots are readable immediately.** **If it does not clear, pass 2 reads pass 1's values.**

**Name the program that would show it.**

## Task 3 - and §19, revised
**You wrote the paragraph for R162.** **The hoist changes what it must say: a `kosh` and a `mala` declared in a loop body are now reused, while one that escapes is not.**

**Write the sentence again, for what is actually built — including what happens under a `yadi` or a `mandapa` inside the loop, where the hoist does not reach.**

**And say whether the book's existing advice — *"inside a block meant to give memory back, take it with `nirmmita`"* — is still the right advice, or whether the hoist changes it.**
