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

# ROUND-156 - to Muse, read only

**Base:** main at the tip · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**Your R155 was exact: one false sentence, the OOM claim confirmed, `parimana()`'s four numbers derived from the code, the Sanskrit chapter identical, and my base commit wrong.** **And the line I will keep: *"the slice rule's reason (elements move) is stated without needing the word."***

## Task 1 - and the rest of the chapter
**You checked the claims the brief named.** **Now the ones it did not.**

**Read chapter 19 line by line and list every claim a beginner could act on and be wrong.** **Not style - facts.** **The `mandapa` scope, the budget's units, what `parimana()` counts, the slice bounds, what happens on a failed allocation, and the paragraph on what the language lacks.**

**And: does the chapter ever imply a feature that does not exist?** **A beginner reading "memory is returned when the block closes" might expect that of a `kosh` made inside it. Does the chapter say which?**

## Task 2 - and the corrected figures
**I have been quoting a 24-byte descriptor and a 52,760 / 13,480 KB measurement.** **The descriptor is 32 bytes (56 with R82) and those measurements are v284; v315's are 49,920 / 392 KB.**

**So: which documents in the tree carry either wrong figure?** **Name them, file and line.** **Claude is fixing them and needs the list.**

**And `R158 doc currency` has seven checks.** **Would any of them have caught a wrong number in a document?** **If not, say what check would.**

## Task 3 - and the compiler overwriting its input
**`sutram hello.sm hello.sm` replaces the program with a binary.**

**Claude is fixing it after Tuesday.** **So: read the argument parsing and the output-open path and say what the fix must check.** **A string comparison of the two arguments would miss a symlink, a relative versus absolute path, and a case-insensitive filesystem.**

**What is the correct check, and where does it go?**
