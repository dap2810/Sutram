# Sutram — ROUND-83: `vitti a = k` is not refused, and the memory model rests on it

**Base:** main at v278, suite 255, gates 57 PASS · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour, run by me on v278 and pasted as output

**Compiles and prints `41`:** `kosh k[2]; kosh_push(k,41); vitti a = k; likha(a[0])` — **`vitti a = k` is NOT refused. My brief said it was, for several rounds. It was wrong.**
**Refused, `E_SCRATCH_ESCAPE`:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]`.
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused at compile time:** `nirmmita(-1)` literal · a written number that does not fit int64.
**Refused at run time, Sanskrit + line number:** `10 / 0`, `10 % 0`.
**Wraps silently, by decision:** computed overflow.
**Integer division truncates toward zero:** `-7 / 2` gives `-3`.
**`parikshita` is contextual:** `vitti parikshita = 4` compiles.
**Refused, `E_APARIKSHITA_AHVAN`:** a `parikshita` function calling an unmarked function.

## Your R82 closed the last gap I knew about — and ChatGPT found the one I had wrongly declared closed

**`kosh` in a block: generation-checked, refused after the block, 0 DIFFER elsewhere, +11% worst case where used.** **That is the last memory gap I was tracking, and it is done.**

**And `vitti a = k` compiles.** **I have been writing "Refused: `vitti a = k`" in every brief since round 76.** **It was never true.** **I conflated it with `box[0] = nirmmita(64); outer = box[0]`, which IS refused.**

## WS1 — so the aliasing hazard is OPEN, and it is the one that killed Step 0

**Two variables can own one `kosh` buffer:**
```
kosh k[2]
kosh_push(k, 41)
vitti a = k
kosh_push(k, 42)
kosh_push(k, 43)     # k grows; a still points at the old buffer
likha(a[0])          # reads the OLD buffer
likha(k[0])          # reads the NEW buffer
```

**Build the test that shows whether they diverge.** **If they do, two live buffers exist, and this is the exact hazard that made me drop the recycling bins in Step 0.**

**Then answer: does it matter today?** **If the old buffer is never freed, two live buffers are wasteful but not unsafe.** **If anything ever recycles, it is a use-after-free.** **Say which, with the evidence.**

## WS2 — and then close it, or document it
**Three options, and I want your judgement not just your work:**
1. **Refuse `vitti a = k` when both are `kosh`** — a compile error naming the copy.
2. **Make it a deep copy** — expensive and surprising.
3. **Document it** — two variables share a buffer; growing one leaves the other on the old buffer.

**If option 1 is cheap, do it.** **If it breaks programs in the tree, report the count and stop.**

## WS3 — and the guard-page run on v278
**The generation check emits new code inside blocks.** **Run `tools/guard_page.py` and report: does anything now fault that did not before?**
