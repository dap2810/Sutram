# Sutram — ROUND-66: the `kosh` alias census — this number decides a language change

**Base:** main at v416, compiler v261 · **Deliver into:** `Muse-to-Sarvam/`

## Why you, and why this is the whole round

**Claude stopped Step 0 because `vitti a = k` makes two variables own one `kosh` buffer.** **That aliasing is what made the recycling bins unsafe.**

**The fix under consideration: make `vitti a = k` a COMPILE ERROR, and require an explicit copy.** **That would remove the alias, make the old buffer genuinely dead, and make the bins safe — solving the leak fully instead of half.**

**But it changes the language, so it needs a number before a decision.** **That is your job.**

## The census — four counts, with file names

**1. How many places assign one `kosh` variable to another?** **`vitti a = k`, `a = k`, or any form.** **Search `examples/`, `tests/`, `lib/` and `docs/`.** **Name every file and line.**
**2. How many pass a `kosh` to a `prakriya`?** **That is a deliberate share and must stay legal — but I need the count.**
**3. How many store a `kosh` inside a `mala`, a `rachana`, or a global?** **Also deliberate aliases.**
**4. Of the 131 `kosh` declarations that carry a literal capacity, how many are in programs that also alias?**

**Give counts and file names, not impressions.** **If count 1 is zero, say zero plainly — that would make the fix free.**

## And one thing I want you to check that nobody has
**Does the compiler treat `vitti a = k` as an alias for OTHER container types too — `mala`, `rachana`?** **If `vitti m2 = m1` on a `mala` also aliases, then the same hazard exists there, and any fix must cover all of them or none.**

**That is the question that decides whether this is a `kosh` fix or a language-wide rule.**
