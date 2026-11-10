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

# ROUND-174 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Three tests decide whether v318 can merge, and a fourth decides whether the hoist is safe at all.** **Do the tests before anything else.**

## WS1 - and this one decides the merge: test A
```
chakra i = 1 tak 2 {
    mala row[2]
    yadi i == 1 { row[1] = 99 }
    likha(row[1])
}
```

**Before the hoist this prints `99` then `0`.** **With a hoist that does not clear the `mala` on reuse it prints `99` then `99`.**

**A `mala` has no length field — all N slots are readable immediately.** **A `kosh` is safe with `length = 0`; a `mala` is not.**

**Run it on v318.** **If it prints `99` then `99`, v318 introduces the stale-data bug it was meant to avoid, and must not merge.**

## WS2 - and this one decides whether the refusal is needed: test B
```
mala row[2]
kosh table[10]
chakra i = 1 tak 5 {
    mala row[2]
    row[0] = i
    kosh_kship(table, row)
}
likha(table[0][0])
```

**Must print `1`.** **If it prints `5`, all five rows alias one buffer.**

**And the same with three other escape paths:**

- **`vitti out = 0` declared outside; inside the loop `out = row`**
- **`table[i] = row`** — indexed assignment rather than `kosh_kship`
- **`row` passed to a `prakriya` that stores it in a module-level variable**

**You said the refusal is not needed because the compiler already refuses these.** **So: run all four.** **If any of them compiles and aliases, the refusal IS needed and you were wrong.** **If all four refuse, you were right and the reason belongs in the report.**

## WS3 - and this one decides the hoist's safety: test C
**A `kosh` declared inside a `mandapa` inside a `chakra`.**

**Question: is the `kosh`'s descriptor allocated on the same arena cursor that the `mandapa` saves and restores?** **If yes, the `mandapa` exit rewinds over the hoisted descriptor and a later `nirmmita` overwrites it.**

**Evidence it may be true: a `kosh` in a `mandapa` leaks 64 bytes a pass against 48 outside — the block is touching it.**

**Answer by reading the allocation path, and test it: a `kosh` in a `mandapa` in a loop, grown, then read after the loop.**

## WS4 - and the hole two reviewers found: calls are not checked
**Muse: *"The flag rules cover assignments, returns, and stores — and never mention calls at all — and the one check that covers calls, `r108_check_call`, never runs on the statement path."***

**The program: a block `kosh` grown past 4,097 elements, passed by its own name to a foreign function taking a `ptr`, as a bare statement.** **It satisfies every escape condition, sets no flag, and hands C the address of a region the block releases.**

**Does the hoist's escape check have the same gap?** **A `kosh` passed to a `prakriya` that stores its parameter — is it flagged?**

**Test it. If it is not flagged, the hoist reuses a descriptor a function is still holding.**

## WS5 - and the stale-data bug, which is smaller than I thought
**Zero `[saved_cursor, current_cursor)` at `mandapa` exit — six instructions, no globals, no change to `nirmmita`.**

**The only cost: a block that allocated 200 MB and wrote 100 bytes zeroes all 200 MB.** **That is a case nobody has measured.**

**Is it worth taking the simple fix, or is the 200 MB case real enough to want the dirty high-water mark?**

**Answer, and say what a student would have to write to hit it.**
