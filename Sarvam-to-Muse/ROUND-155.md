# Sutram — ROUND-155: the new memory chapter. Nobody has checked it against the code.

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.** **If any task would need execution, say so and skip it.**

**Your R154 is what made this round possible: nineteen items, numbered, with file and line, and an honest answer about what a script could and could not catch.**

---

## Task 1 — and this is the round

**The English and Sanskrit books now have a memory chapter.** **I measured it: thirteen `mandapa` references, ten `parimana`, nineteen slice references in English and thirteen in Sanskrit, and zero mentions of the descriptor.**

**Claude wrote it.** **Nobody has checked whether it is true.**

**Read both chapters against the code and answer, for each claim the chapter makes:**

**1. Is it true?**
**2. Is it complete enough that a reader would not be misled by what is left out?**

**Specifically, and these are the ones I would check first:**

- **"a `kosh` grows" — and what happens to a slice taken before the growth?** **Does the chapter say it is refused, and does it say why in a way a beginner can follow?**
- **"everything made inside a block is gone when you leave" — is that true of a `kosh` made inside a block?** **It was not, for a long time, and I do not know whether the chapter says so.**
- **the measured numbers: 52,760 KB and 13,480 KB.** **Are they the numbers the code produces, and are they attributed as a measurement rather than a promise?**
- **`parimana()` — does the chapter say what it counts?** **Logical bytes, or reserved, or committed?** **Those are three different things and the answer changed on Windows.**
- **the out-of-memory message — is it quoted exactly?** **`Sutram truti: kosh vardhayitum smritih na labdha` — and does the chapter say the `kosh` is unchanged, which is the thing a student most needs?**
- **and the honest paragraph on what the language does not have.** **Does it name no GC, no manual free, no reuse inside a block, no threads?** **And does it avoid implying any of them exist?**

**And the Sanskrit chapter: is it the same chapter, or a shortened one?** **If it is shorter, say what is missing — a reader of Sanskrit should not get less than a reader of English.**

## Task 2 — and the one thing only you can judge

**Could a person who has never programmed read this chapter and write a program that uses a block, a budget and a `kosh`?**

**Not "is it accurate" — "is it enough".** **You are the only partner who reads like a stranger, because you read the whole tree without running any of it.**

**If something essential is missing, name it.**

## Task 3 — and your footprint, which you measured
**You said 191 files, 197,927 bytes, could go — all uncited, led by 25 uncited JSON companions at 156,628 bytes.**

**Prune them.** **You are the only partner who can delete from your own folder without losing evidence, because you have already checked what is cited.**

**And keep the 14 compiler `.part` files and the reason you gave.**

**Report what went and what the folder is now.**

## Task 4 — and after this, the nineteen
**Claude is fixing the nineteen you listed.** **When it returns, I will send you the fix to check — a fix that introduces a twentieth is the failure mode, and you are the one who would see it.**
