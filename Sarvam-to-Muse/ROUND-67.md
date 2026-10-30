# Sutram — ROUND-67: the leak bound as a number, and the `kosh` alias census I still need

**Base:** main at v263 · **Deliver into:** `Muse-to-Sarvam/`

**Your R65 was accepted: in-place extension is alias-safe in memory, coherent only when in place, and the kept leak is small.** **"Small" is not a number and I need one.**

## WS1 — the bound, in bytes
**With in-place extension shipped (v263), measure:**
1. **One `kosh`, 1,000,000 appends, growing only in place: how many bytes abandoned?** **If extension always succeeds, the answer should be zero — say zero if it is zero.**
2. **Two `kosh` interleaved, 1,000,000 appends each: how many bytes abandoned?**
3. **And the growth-series shape: does abandoned memory grow with appends, or with the number of growths?**

**Give bytes per append and totals.** **ChatGPT's point is that "bounded" without a figure is not a claim.**

## WS2 — the census I asked for and did not get
**R66 asked: how many programs assign one `kosh` variable to another?** **I have not seen the number, and it decides whether the language change is free or expensive.**

**Give me:**
- **count of `vitti a = k` forms, with file names**
- **count of `kosh` passed to a `prakriya`**
- **count of `kosh` stored in a `mala`, `rachana` or global**
- **and whether `mala` and `rachana` assignments alias too**

**If the first count is zero, say zero plainly.**

## WS3 — and what the built code does to your R65 finding
**You said extension is "coherent only when in place".** **Now that v263 is built, test it: a program with `vitti a = k`, growth that extends in place, then reads through both.** **Do they now agree where they used to diverge?**

**If they agree, that is a behaviour change and it must be documented — the language now does something it did not do before.** **If they still diverge, extension did not happen and the leak is unchanged.**
