# Sutram — ROUND-169: does memory ever come back? Measure it.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Your R168 corrected my measurement and it was the most useful correction of the stretch: the 14,948 KB "baseline" was Python's interpreter, not the program.** **The `env -i /usr/bin/time` numbers are the real ones, and I am using them.**

**This round is a different question, and it needs a different method.**

---

## 1. The question

**The owner wants a block whose memory is given back to the operating system when the block ends — instead of kept for reuse.**

**Today `r73_gen_rewind` resets the cursor and keeps the memory.** **Measured: `nirmmita` inside a block is flat at 312 KB over 800,000 passes.** **That is reuse working.**

**But a program that allocates 200 MB once, uses it, and never needs it again keeps 200 MB for the rest of its life.** **Is that true?** **Measure it.**

---

## 2. The method — and peak RSS cannot answer this

**`ru_maxrss` is a high-water mark. It only goes up.** **A program that allocates 200 MB and returns all of it reads the same peak as one that keeps it.**

**So peak is the right tool for a leak and the wrong tool for a return.**

**Sample *current* RSS instead:** `/proc/self/status` → `VmRSS`, at named points during the run.

**And there is a trap that would make the whole measurement meaningless: `nirmmita` may not commit pages until they are touched.** **A 200 MB allocation that is never written reads as 200 MB reserved and near-zero resident.** **So every test program must write one byte per 4 KB page before the sample is taken.**

**State in the report how you touched the pages.**

---

## 3. WS1 — a big block, run once

**Sample `VmRSS` at four points: before the block, inside after allocating and touching, just after the block closes, and at the end.**

```
mukhya() {
    # sample 1
    mandapa {
        vitti p = nirmmita(200000000)     # 200 MB
        # touch one byte per 4 KB page
        # sample 2
    }
    # sample 3
    # sample 4
}
```

**The question: does sample 3 equal sample 1, or sample 2?**

**Expected: sample 3 equals sample 2 — the memory is kept.** **That is the baseline, and it must be measured rather than assumed.**

## WS2 — and a big block, run twice

**The same block twice in sequence.** **Is the second pass faster than the first?**

**If yes, the memory is being reused and returning it would cost that speed.** **That number is the price of the feature.**

## WS3 — and this is the real question: a big `kosh` that dies

**The compiler already distinguishes big from small: `R127_BIG equ 65536` in `src/r65_arena.inc`, and `win/winrt_blob.asm:184` calls `munmap` for a `kosh`'s old region and `VirtualFree` with `MEM_RELEASE` for the whole reservation.**

**So: when a `kosh` whose buffer is above 64 KB is discarded, does its memory come back to the OS?**

```
mukhya() {
    # sample 1
    mandapa {
        kosh k[1]
        # grow it past 64 KB and touch every page
        # sample 2
    }
    # sample 3
}
```

**Two readings, and they are very different:**

**If sample 3 drops toward sample 1, the release path works and the feature is small: apply an existing mechanism to a block.**

**If sample 3 stays at sample 2, the release path is narrower than `R127_BIG` suggests — it releases an old buffer on *growth*, not on *death* — and that is a finding in itself.**

**Answer which it is.**

## WS4 — and the threshold, tested

**`R127_BIG` is 65,536.** **Measure a `kosh` grown just below it and just above it, and say whether the behaviour differs.**

**If 64 KB is the boundary, a buffer of 60 KB is kept and one of 70 KB is returned.** **That is a real behaviour a student can hit and nothing documents.**

## WS5 — and what the OS actually does

**`munmap` unmaps. But on Linux, `MADV_DONTNEED` would keep the mapping and drop the pages, which is cheaper to re-acquire.**

**Does the compiler use either?** **Read `src/r65_arena.inc` and `win/winrt_blob.asm` and say which call is made where, and what it costs to re-acquire afterwards.**

**That decides whether "return memory" is a syscall per block or a page-fault per page on the next use.**

---

## 4. What to return

1. **WS1's four samples** — does a big block return its memory? **With the page-touch method stated.**
2. **WS2** — the cost of a second pass.
3. **WS3** — does a big `kosh` return its memory when it dies? **This is the one that decides the feature.**
4. **WS4** — the 64 KB boundary, tested.
5. **WS5** — which call is made, and what re-acquisition costs.
6. **And a one-line verdict: is "give the memory back" worth a marker, on these numbers?**

**No code changes. Measurement only. No Windows machine needed.**

---

## 5. And the discipline note

**Two measurement errors have been made in this project in two days, both mine:**

**1. A "baseline" that was the measuring process, not the program.** **You caught it.**
**2. Peak RSS used to answer a question peak cannot answer.** **Peak only rises; a return is invisible to it.**

**So: state the method, state what the number includes, and state what it cannot show.** **A number without its method is a claim.**
