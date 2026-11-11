## THE SHARED STATE - 11 November 2026. The last big item: generics.

**`Sutram 1.0 (v315)` on main. Staged chain, every branch gate-clean, none merged: v316 -> v317 -> v318 -> v319 -> v320 -> v321 -> v322/v323 -> v324.**

**EIGHT OF NINE PLAN ITEMS ARE DONE OR CLOSED**
1. **file example + `grahan` bugs** - v324: the sign is read, the unfinished last number is handled, two file examples, `dvaram_paadh` corrected
2. **Windows run -> merge** - checklist ready, pinned to v324
3. **reference audit** - three errors: `likh8`/`pad8` are eight BYTES not bits; `likh8c`/`pad8c` access memory not the terminal; the file table swaps `dvaram`/`paadh`; the braces section says a valid indented `prakriya` is invalid. **Plus a source bug: `brihat_ank_tak_laghu` checks `d <= 9` and never `d >= 0`, so a cell holding -1 returns -1 instead of refusing.**
4. **book vs language** - in ChatGPT's return
5. **block returning memory** - CLOSED, zero of 347 examples allocate more than 16 MiB in a block
6. **`kosh temp[n]`** - CONFIRMED already hoisted; the candidacy check never looks at the size
7. **generics** - THIS ROUND
8. **threads: no, and why** - written
9. **exceptions: no, and why** - written

### WHAT THE LANGUAGE HAS TODAY, AND WHY GENERICS ARE THE LAST BIG THING
**A `kosh` holds 64-bit values, so a collection is already untyped at runtime.** **`vitti` is a 64-bit integer.** **So the runtime has no type to erase.**

**What is missing is at the library and the function level: a function that works on "a list of anything" cannot be written, so every type needs its own version.** **That is why the library is 310 functions and not 150.**

**And the constraint that makes it hard: a single-pass compiler emits code as it reads the source, so it does not know every instantiation of a generic function until it has read the whole file.**

**THE FIXED CONSTRAINTS:** one NASM source file, single pass, native x86-64, no runtime, no GC, no borrow checker, one thread, Sanskrit keywords, a beginner's language.

**Sixty-four false claims by Sarvam this stretch. Every one caught by a partner reading rather than agreeing.**

---

# ROUND-170 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Saram/`

**Read only. Nothing to compile or run.**

**Your R169 closed two items with numbers — zero of 347, and the candidacy check never looking at the size.** **That is what a reader is for.**

**This round is the last big design question: generics.**

## Task 1 - and this is the round: what does the compiler know about types today
**Before a design can be judged, the tree has to be read.**

**Answer from the source:**

1. **Does a `kosh` carry an element type at runtime or at compile time?** **The descriptor is four qwords — length, capacity, elements pointer, region size. No type field. So what does the compiler track, if anything?**
2. **Does the symbol table record a type per variable, and how many types are there?** **`vitti`, `dasham`, `mala`, `kosh`, `pankti`, a `rachana`, a text value — name them and say where the kind is stored.**
3. **And: how does the compiler currently tell `sort_int` from `sort_text`?** **By name only, or by the argument's kind?** **If by name only, there is no type information to build generics on, and that is the first thing to know.**
4. **Is there any function in the 310 that is already generic in effect** — **one that works on any 64-bit value without knowing its type?** **Name them.**

## Task 2 - and the duplication, counted
**ChatGPT is estimating how many of the 310 are the same algorithm written per type.** **You can count exactly.**

**So: read the library and give the real number.** **Which functions are duplicates, grouped by algorithm?** **Name the groups and the counts.**

**And the one that matters: what would the library be if every group collapsed to one?** **310 minus how many?**

## Task 3 - and what would break
**Generics change how a function is compiled.** **The project's strongest guarantee is that 783 programs compile to identical bytes.**

**So: what in the tree would a generic feature threaten?**

- **the guard itself** — would any existing program change bytes?
- **the library's 229 proofs** — do they assume a specific specialisation?
- **the goldens** — 327 suite tests, each with an expected output
- **and the 331 examples**

**Name what would need re-baselining, and say whether that is acceptable.**

## Task 4 - and the beginner question
**You have read the books.** **So: would a generic function make this language easier or harder for the person it is for?**

**One `sort` instead of three is easier to find.** **But if the student must write a type parameter, it is harder.**

**Answer with the book in mind: what would a beginner actually need from generics, and would they ever know the feature exists?**
