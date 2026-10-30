# STOP — `nirmmita` in a loop clobbers a live variable, and every gate missed it

**Base:** main at v264 · **Deliver into:** `Muse-to-Sarvam/`

## The bug

```
mukhya()
    vitti i = 0
    yavat (i < 3)
        likha("i=", i)
        vitti p = nirmmita(64)
        i = i + 1
    likha("done")
```

**Prints `i=0` forever on v264.** **Expected `i=0 i=1 i=2 done`.** **`nirmmita` inside a `yadi` works; inside a `yavat` it does not.**

## Your job — the census that tells us how bad this is

**1. How many programs in `examples/`, `tests/` and `lib/` call `nirmmita` inside a loop?** **Name every one.** **If the answer is zero, say zero — that is why nothing caught it.**

**2. How many call `nirmmita` anywhere a variable is live across it — inside a loop, inside a `chakra`, between two uses of a variable?**

**3. And how many call `kosh_push` inside a loop?** **That path works, because it goes through the library — but I want to know the number, because it is the same shape and it working is the reason nobody looked at `nirmmita`.**

**4. The one I most want: does `mala` or `rachana` creation inside a loop have the same problem?** **If the whole family clobbers, the fix is one place. If only `nirmmita`, it is the arena sequence alone.**

## And the guard-page question this raises

**Your R69 asked whether the guard-page variant covers every allocation path.** **It cannot catch this — a clobbered register writes no out-of-bounds memory.** **So: what test WOULD catch a register clobber?**

**The answer is probably "a program whose output depends on a variable held across the call".** **How many such tests exist today?** **If the answer is none, that is a hole in the suite larger than this one bug.**
