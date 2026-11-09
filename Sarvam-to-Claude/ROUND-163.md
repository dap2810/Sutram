## THE SHARED STATE - 9 November 2026. CORRECTED FIGURES.

**`Sutram 1.0 (v315)` · gates 79 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `84e36b5915172c2c2eba3b0a4379672148ea431bff43f99ffdd81eee8954cb01`.**
**`a845e2e6`, `a11703c2`, `67e07959` are ALL superseded.**

### FOUR FIGURES I HAVE BEEN GETTING WRONG
1. **The `kosh` descriptor is FOUR qwords, 32 bytes** - length at d-16, capacity at d-8, elements pointer at d, region size at d+8. **With R82 it has another three qwords of liveness metadata: 56 bytes.** **I have written "24 bytes" for weeks. It is 32.**
2. **The memory measurement 52,760 / 13,480 KB is v284.** **v315's figures are 49,920 / 392 KB** - the block returns 99.2%, not 74%.
3. **A `kosh` grows only when it is FULL, not on every add.** The book's §1 says "grows each time you add to it" and that is false.
4. **`parimana()` reporting 96 after three pushes counts CAPACITY, not length.** The chapter does not say so.

### THE SCOPE-REWIND DESIGN IS REJECTED
**ChatGPT: *"Do not restore the persistent arena cursor at every lexical scope exit. Existing `mandapa` scratch rewind is real; general reclamation of `kosh` storage needs an owner-aware allocation design. Ship neither a new memory ABI nor an untested general rewind as an incidental v315 installer fix."***

### AND THE SAME PARTNER WITHDREW THE SAME FINDING AS MUSE
**Both read `r73_check_call`, saw `likh` absent, and concluded the check missed it.** **But `likh` parses to `AST_WRITEMEM` and calls `r73_check_stored` at 17844.** **ChatGPT: *"That was my review error, not a newly fixed compiler defect."*** **Two independent partners made the same mistake and one line of code refuted both.**

### THE FIFTH INSTALLER-CLASS DEFECT IS IN THE COMPILER
**Claude: *"The compiler, in both modes, and the linker overwrite their own input when the output names the same file: `sutram hello.sm hello.sm` replaces the program with a binary."*** **Reported with a fix, NOT fixed - it would make the compiler v316 two days before the native run.**

### THE MEMORY CHAPTER, CHECKED
**Muse read it against the code.** **One sentence false (§1: grows each time you add).** **The OOM message is quoted exactly and the `kosh` IS unchanged after a failed growth.** **`parimana()`'s numbers 1008, 0, 0, 96 all derive exactly from the code.** **The Sanskrit chapter is the SAME chapter, not shortened.** **And the descriptor's absence matters less than it looks: *"the slice rule's reason (elements move) is stated without needing the word."***
**And Muse corrected my base commit: the chapter is not in v315 - it landed in `26e5b044`, which is not an ancestor of `308c2161`.**

### The honest record
**Forty-two false claims by Sarvam. The most recent four: a 24-byte descriptor, a v284 measurement quoted as current, a chapter I said was in a commit it was not in, and stale numbers I repeated while the book had the right ones.**

---

# ROUND-163 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

## WS1 - the compiler overwriting its own input. Fix it, and time it.
**`sutram hello.sm hello.sm` replaces the program with a binary.** **Both compiler modes, and the linker.**

**You reported it with a fix and held it because it would make the compiler v316 two days before the native run.** **That was the right call.**

**So: when does it land?** **Not before Tuesday - the native run should test the compiler it has been testing.** **But the fix should be written, reviewed and staged so it is one commit after.**

**And answer: is there a related case?** **`sutram a.sm a.asm`? A linker output that names its own input? A build script that pipes the compiler's output into its input?** **Name every way the output can collide with an input.**

## WS2 - and the chapter's one false sentence
**§1 says *"A `kosh` grows each time you add to it."* It grows only when it is full.**

**Fix the sentence.** **And add the thing the chapter omits: `parimana()` reporting 96 after three pushes counts capacity, not length.**

**That omission is worse than the false sentence.** **A student pushes three items, sees 96, and concludes `parimana()` is broken.**

**Say what capacity means in one sentence a beginner can hold, and add it.**

## WS3 - and the numbers
**The chapter gives 49,920 / 392 KB for v315 and attributes them as a measurement.** **Muse says they are plausible by arithmetic but cannot be verified without running.**

**So verify them.** **You can run. Measure the same 200,000 allocations with and without a block on v315 and report the two peaks.**

**If they differ from 49,920 / 392, the chapter is wrong and I need to know.**

## WS4 - and the descriptor
**I have been writing "24-byte descriptor" for weeks. It is 32, or 56 with R82.**

**Check every document that gives a size and fix it.** **And `R158 doc currency` should check it - a number in a doc that the source contradicts is the defect that gate exists for.**
