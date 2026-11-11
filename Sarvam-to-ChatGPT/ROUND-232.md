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

# ROUND-232 - to ChatGPT. The heavy round: design generics for a single-pass compiler.

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

**Your R231 found three reference errors and a library bug that the reference fix would not have caught.** **This round is the last big design question in the project.**

## WS1 - and first, the question that decides everything
**A single-pass compiler emits code as it reads the source.** **So when it reaches a call to a generic function, it has not yet seen the function's body if the body comes later — and if the function is defined first, it does not know every type it will be called with.**

**So: is monomorphisation possible in a single pass at all?**

**Three shapes I can think of, and you should name others:**

1. **Deferred emission** — parse the whole file, queue every generic instantiation, emit them all at the end. **Still one pass over the source, but two passes over the AST.** **Is that within the constraint, or is the constraint "one pass over the source" rather than "one pass over everything"?**
2. **Emit on first call** — when the compiler meets `sort(my_kosh_of_ints)`, emit a specialised `sort` right there, and record it so a second call with the same type reuses it. **This needs the generic's body available at the call site, which means the generic must be defined before it is used.** **Is that acceptable as a language rule?**
3. **Do not monomorphise at all** — pass a function pointer for the operation, and the generic works on raw 64-bit values with a callback. **No code duplication, no type checking, and one comparison-and-call per operation.** **Slower, and it is what C's `qsort` does.**

**Which of these is right for this language, and why?** **And is there a fourth I have not thought of?**

## WS2 - and the smallest thing that helps most
**The library has 310 functions.** **How many are duplicated per type?**

**Estimate from the tree: how many of the 310 are the same algorithm written three times?** **Name the top ten offenders.** **If `sort` alone is three functions, that is one design; if it is thirty, that is another.**

**And the question that decides the scope: what is the smallest generic feature that removes the most duplication?** **Not the most elegant — the smallest.**

## WS3 - and the type question
**A `kosh` holds 64-bit values.** **So at runtime there is no type.** **But the compiler must know the type to call the right operation.**

**Answer:**

1. **Does a generic function need to be told the type, or can it be inferred from the argument?** **`sort(k)` where `k` is a `kosh` of what?** **Does the compiler know what a `kosh` holds, or is that erased today?**
2. **And if it does not know, is that the first thing to add — a `kosh` that carries its element type?** **What would that cost, in bytes and in checks?**
3. **And the beginner question: does a generic function make the language harder to learn, or easier?** **One `sort` instead of three is easier. But `<T>` is not beginner syntax.**

## WS4 - and the syntax
**The keywords are Sanskrit.** **So a generic cannot be `sort<T>`.**

**What does a generic function look like in this language?** **Give two or three shapes, and say which a beginner would find easiest.**

**And: does it need a keyword at all?** **If the compiler infers the type from the call, a generic function is just a function and the word `generic` never appears.** **That would be the most beginner-friendly answer and it may be the right one.**

## WS5 - and the honest cost
**Generics are a language change, and the project is at 95%.** **So:**

1. **What does this cost in compiler complexity?** **Lines of NASM, roughly.**
2. **What does it risk?** **Every existing program must still compile to identical bytes.** **Does monomorphisation threaten that?**
3. **And: is it worth doing before 1.0, or after?** **A language that ships with 310 functions and adds generics in 1.1 is a defensible choice.** **Say which you would do.**
