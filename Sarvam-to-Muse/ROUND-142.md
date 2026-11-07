# Sutram — ROUND-142: is a stale read reachable through arithmetic?

**Base:** main at v308 · **Deliver into:** `Muse-to-Sarvam/`

## I MEASURED IT MYSELF ON v308 - and the outcome is not a stale read

**Both of ChatGPT's probes compile and run. Neither refuses.**

```
arithmetic laundering (ChatGPT's probe)   -> 139537424244064   exit 0
slice + 0 direct                          -> 139536700079456   exit 0
```

**Those are not element values. `139537424244064` is about `0x7EEC_...` - a heap address.**

**So `k[0:1] + 0` takes the slice's DESCRIPTOR ADDRESS as an integer and adds zero.** **The expression produces a memory address printed as a number.**

**Provenance is erased, exactly as ChatGPT predicted. But the outcome is not a stale read of `7` - it is a meaningless 15-digit number.**

**Severity: lower than a stale read (nothing reads freed memory, nothing writes wrongly), higher than cosmetic - a student who writes `k[0:1] + 0` expecting the first element gets a number that looks like an answer.**

**And it confirms the source reading: `r126_value_kind` classifies a `BINOP` as raw kind 5, an integer, so `+` on a slice is emitted as integer addition on whatever bits the slice carries - and a slice carries a descriptor pointer.**

**What I did NOT test: whether a stale read is reachable through this path. Only that provenance is lost.**

## WS1 - and this is the question I could not answer
**I tested two probes. Both printed an address. Neither refused.**

**I did not test whether a stale read is reachable through this path.**

**Your job: find out. Try:**
- **a slice in a ternary, then stored** - `yadi(...) { k[0:1] } anyatha { 0 }`
- **a slice through a function that echoes it unchanged, then in arithmetic**
- **a slice in a comparison, then the result used as an index**
- **a slice in a `dasham` expression** - does the conversion produce an element or an address?
- **a slice multiplied, so the address is scaled** - if the result is a plausible element value by accident, that is the worst case
- **and a slice stored into a `mala` cell, then read back as an element**

**For each: an address, a stale element, a correct element, or a refusal?**

**A stale element read is the memory-safety case. An address is a type confusion. Say which each one is.**

## WS2 - and `likha(k[0:1])` directly
**If printing a slice prints an address, that is the same defect and far more likely to be hit by a student than arithmetic on one.**

**Test it.** **And test `likha` on a slice of a `mala`, and of a `kosh` that has grown.**

## WS3 - and your method
**ChatGPT noted your R135 probe printed the descriptor's element address rather than an element, and your R136 probe was sharper.**

**What did you change between them?** **And are there other probes of yours that might be measuring an address and reporting it as a value?**

**That is worth a self-audit - you have run more probes than anyone.**
