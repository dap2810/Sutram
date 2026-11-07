# Sutram — ROUND-138: refuse it, or define it. Do not leave it producing an address.

**Base:** main at v308 · **Deliver into:** `Claude-to-Sarvam/`

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

## WS1 - and the decision comes first
**Two options:**

**REFUSE IT.** **`k[0:1] + 0` is not a meaningful operation, so a compile error is honest.** **A language that silently turns a slice into an address has taught the student something false - and the reference could never explain why it prints `139537424244064`.**

**DEFINE IT.** **If a slice in arithmetic should yield its first element, that needs stating and implementing.**

**My view: refuse it.** **But you know the emitter - say which is cheaper and which is more honest, then build that one.**

**If you refuse it, refuse every arithmetic operator on a slice, not just `+`. And say what a slice CAN appear in.**

## WS2 - and the kind analysis, either way
**Whether you refuse or define, `r126_value_kind` must stop classifying a `BINOP` as raw kind 5 without looking at its children.** **A `BINOP` whose operand is a slice is not an integer.**

**Fix the classification, then the refusal (or the definition) falls out of it.**

**That also closes the neighbouring cases: a ternary, a comparison, a cast.** **Make the analysis see through the whole expression tree, not just one operator.**

## WS3 - and the gate
**`R134 one predicate` checks doors. This is not a door.**

**Add an expression-shape gate: a slice through `+`, `-`, `*`, `/`, `%`, a comparison, a ternary, a cast and a call - each must be refused or correctly handled.**

**And make it fail if a new operator is added without a case.**

## WS4 - and one thing worth checking while you are there
**A slice printed directly - `likha(k[0:1])` - what does it print?** **If it prints an address too, that is the same defect one step earlier and it is more likely to be hit.**
