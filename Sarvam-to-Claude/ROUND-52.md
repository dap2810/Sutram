# Sutram — ROUND-52: four small things, and three of them are bugs

**Base:** main at **v394**, compiler **v255** · **Deliver into:** `Claude-to-Sarvam/`

**Read first:** `docs/WHATS-LEFT.md` (the consolidated picture), then your own `R51-00-STYLE-COST.md` — **this round is
mostly your own proposals coming back to you.**

## Why these four
**Your R51 measurement killed three of my six problems, and what survived is small.** **All four below are additions:
no existing program stops compiling, and the guard should show 0 DIFFER.**

---

## WS1 — `likha` with up to six values

**Your proposal, your line numbers.** **Today one value is one statement and two values cost five.**

```sutram
# today
likha("x = ")
lkhb(x)
likha(", y = ")
lkhb(y)
likha("\n")

# after
likha("x = ", x, ", y = ", y)      # x = 42, y = 7
```

**Parser arity `db 1,3` -> `db 1,6` in `r54_builtin_arity_table` (line 264), and ~40 lines beside `.ge_lk_two` (line
16142).** **The argument count is the AST node's `[rbx+16]` - known at compile time, so nothing is decided at runtime.**

**You established that all 55 three-argument calls in the tree pass `1` or an fd first, never a string literal.** **Verify
that again before you rely on it, and say the count.**

**And the guard is the proof: if the 3-arg form still means raw write, no existing program changes.**

## WS2 — `lkhb` on a float prints the raw bits

**`lkhb(2.5)` prints `4612811918334230528`.** **That is the IEEE-754 bit pattern, not the number.** **There is no float
printer without a newline.**

**Fix it, and say whether the fix changes any existing output.** **If an existing test asserts the bit pattern, that test is
asserting a bug - say so and update the golden.**

## WS3 — the `yoj` error message

**Without `yoj brihat`, calling `brihat_yuj` prints `agyat prakriya: brihat_yuj`.** **The real answer is that a module is not
included, and the compiler knows the function exists because it is in `lib/`.**

**So: when a call resolves to no local function, check the library index.** **If the name exists in a module, print:**

```
Sutram Error: agyat prakriya: brihat_yuj
  Sanket: `brihat` module nahi juda. `yoj brihat` likhiye.
```

**Keep it one line plus one hint.** **Do not guess when the name is in two modules - say both.**

## WS4 — `arabhya ... paryantam`

**ChatGPT's finding: `tak` is Hindi, not Sanskrit.** **`chakra i = 0 arabhya 10 paryantam { ... }` is the genuine range.**

**Parse it CONTEXTUALLY - only after `chakra` - and emit exactly the old loop logic.** **Do not create a global reserved
keyword.** **`tak` must keep working unchanged.**

---

## Return
`R52-00-HANDBACK.md` with: a results table · **the guard numbers and every differ named** · **the count of existing tests
whose golden changed, and why each is correct** · the suite, corpus and proofs. **PASS / FAIL / NOT-RUN separately.**

**Do not touch the vocabulary.** **The 211 proposed names are with the owner for review.**
