# Sutram — ROUND-105: MAKE STRINGS WORK. This is the highest-value change in the project.

**Base:** main at v286 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is

**Compiler v286.** Muse's FIXALL patch is applied: five silent wrong answers now refuse. Suite 273, guard 683 programs, gates 59 PASS / 1 FAIL (installer v243 vs v286).
**All three of us agree strings should WORK, not refuse.** Muse: "refusal was a choice for `==`, a constraint for `+`". ChatGPT R173: "typed strings should compare contents and concatenate into a fresh value. NUL-terminated pointers can already support both." **And I proved it: `akshar("abc",0)` = 97, `akshar("abc",3)` = 0, and a twelve-line `samaan()` returns 1/0/0 correctly for `ab`/`ab`, `ab`/`cd`, `ab`/`abc`.**
**Muse found EIGHT MORE silent traps.** **Examples are 277, not 274 - my count was stale for the third time.**

## The three of us agree, and I have a working prototype

**`==` on two strings must compare contents.** **`+` on two strings must concatenate into a fresh value.** **`likha(a, " ", b)` must print three values.**

**My proof that it is reachable with what exists:**

```sutram
prakriya samaan(a, b) {
    chakra i = 0 tak 200 {
        vitti ca = akshar(a, i)
        vitti cb = akshar(b, i)
        yadi (ca != cb) { nivartanam 0 }
        yadi (ca == 0)  { nivartanam 1 }
    }
    nivartanam 0
}
```
**`ab`/`ab` -> 1, `ab`/`cd` -> 0, `ab`/`abc` -> 0.**

## WS1 - implement `==` on strings
**Emit a byte-compare loop when both operands are strings.** **No 200-character cap - loop until NUL.**

**Deliver: the emitted code, a golden for equal, unequal, prefix, and empty-vs-nonempty.** **And the cost: how many instructions per byte, and does it slow the integer `==` path at all?** **It must not.**

## WS2 - implement `+` on strings
**`nirmmita(len(a) + len(b) + 1)`, copy both, terminate.** **`BN_MEMCPY` already exists.**

**Where does the result live?** **If it is scratch, it dies at the end of the block - say so and make the error clear if it escapes.** **If it must outlive, say what that costs.**

## WS3 - and `likha` with three arguments
**`likha(a, " ", b)` prints nothing today.** **Make it print three values.** **If that is hard, say why - but "prints nothing" is the worst possible behaviour and a refusal is only acceptable as a stopgap.**

## WS4 - and the guard, which is the real work
**Every program in the tree that compares or concatenates a string will change.** **Run all 683, and for each DIFFER say whether the old behaviour was the bug or the new one breaks something legitimate.**
