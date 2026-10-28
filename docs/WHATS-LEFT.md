# Where Sutram stands, and everything left to do

**Compiler v255 · changelog v394 · 245 examples · 305 library functions · suite 225 · corpus 227/0 · proofs 226/226 ·
gates 44 PASS / 0 FAIL / 1 NOT-RUN.**

**The one NOT-RUN is Windows execution, and that is the owner's own test.**

---

## A. Ready to implement — small, agreed, and none of it breaks a program

| # | What | Why | Size | Who |
|---|---|---|---|---|
| **A1** | **`likha` with up to six values** | **one value is one statement; two values cost FIVE.** Claude's fix: arity `db 1,3` → `db 1,6` (line 264) + ~40 lines beside `.ge_lk_two` (16142). **Argument count known at compile time, so zero runtime cost. All 55 existing 3-arg calls pass `1` or an fd first, so no call changes.** | **small** | **Claude** |
| **A2** | **Fix the 135 three-statement print triples in `examples/`** | **405 lines that could be 135.** The language already supports the short form; the examples do not use it. **No compiler change.** | **small** | **Muse** |
| **A3** | **Document that `likha("x = ", x)` works** | **Nobody knows it.** This alone is worth more than A1, because it is the form every example should use. | **tiny** | **ChatGPT** |
| **A4** | **`lkhb(2.5)` prints `4612811918334230528`** | **The raw IEEE-754 bit pattern, not the number.** There is no float printer without a newline. **A real bug.** | **small** | **Claude** |
| **A5** | **The `yoj` error message** | `agyat prakriya: brihat_yuj` when the real answer is `yoj brihat`. **The compiler knows the function exists in the library, so it can say which module to include.** | **small** | **Claude** |
| **A6** | **`arabhya ... paryantam` as an alternative loop spelling** | **`tak` is Hindi.** `chakra i = 0 arabhya 10 paryantam` is the genuine Sanskrit range. **Alternative only, parsed contextually after `chakra`, so `tak` keeps working.** | **medium** | **Claude** |

---

## B. Vocabulary — waiting on the owner's review of `sutram-vocabulary-review.html`

| # | What | State |
|---|---|---|
| **B1** | **The 14 names both parties agree on** | **ready to accept** |
| **B2** | **The 34 names where ChatGPT and Muse disagree** | **the owner reads these** |
| **B3** | **The 3 both reject** | **drop** |
| **B4** | **The 10 Devanagari rows where the pack says a different word from the Latin** | **a defect, not a preference** - `chakra` vs पुनरावर्तन, `satya` vs परिग्रह, and eight more |
| **B5** | **`ganit` → `ganan`** | **41 sites.** ChatGPT wants a separate review; Muse says safe. **The owner decides.** |
| **B6** | **The ~140 English variables in `examples/`** | **not started.** Each needs rename-run-verify. |
| **B7** | **`janchit` → `parikshita` and `rakh` → `sthap`** | **both Hindi-derived, both used all over the library.** ChatGPT's finding. |

---

## C. Defects from the audit

| # | What | Blocked on |
|---|---|---|
| **C1** | **`Sutram Error` → `Sutram dosh`, 74 places** | **Claude STOPPED correctly: something in the Linux IDE matches the literal string.** **Needs a decision: change the IDE too, or keep English.** |
| **C2** | **The 15 mutants that survived every proof** | **including a sign error in `madhava_sin`/`cos`/`atan`.** **A maths function returning a wrong-signed answer passed 224 proofs.** |
| **C3** | **818 undecided mutants** | **the library is proven against known bugs, not proven correct.** |
| **C4** | **88 of 305 functions have no usage comment** | **29%.** **It is why I named three functions wrong: I suggested from the name because the source did not say.** |
| **C5** | **`sat_div` in a comment names a function that does not exist** | **one line** |

---

## D. Memory — parked by the owner, but real

| # | What |
|---|---|
| **D1** | **`kosh` leaks ~15.3 bytes per item.** A million appends leaks ~15 MB with no way to recover it. |
| **D2** | **There is no `free` at all** - the only memory keyword is `nirmmita`. |
| **D3** | **The design I would build: `kośa` regions as the default** (allocate = bump a pointer, free = reset it - **faster than malloc**), `nyāsa`/`pratyarpana` for manual control, **and no garbage collector.** Region inference is Tofte-Talpın 1997; nobody ships it as the default. |

---

## E. Platform

| # | What |
|---|---|
| **E1** | **The Windows manual half** - installer, UAC, IDE colours, fonts, uninstall. **The owner's test.** |
| **E2** | **The installer needs rebuilding** after the next compiler change. |
| **E3** | **The X11 IDE cannot draw Indic script** - the core font is 8-bit. |

---

## F. The decisions only the owner can make

| # | Decision | Open since |
|---|---|---|
| **F1** | **The type on variables** | **the longest.** It unblocks indexing, checked calls through function values, method dispatch and traits. |
| **F2** | **The keyword count** - 31 or 32 | ChatGPT and I both recommend 31 |
| **F3** | **`util_chinha`** | |
| **F4** | **`prati` stays** - decided | **and `nivartan` was considered and set aside** |
| **F5** | **The 34 vocabulary disagreements** | |

---

## G. Beyond v1.0

**Package manager · profiler · LSP · concurrency · generics, closures, traits, iterators · memory safety beyond bounds
guards · performance work (deferred by the owner: *"first focus on development"*) · the other ten language packs ·
the custom console window (parked as a v1.1 note).**

---

## The honest state

**The language works and is unusually well verified.** **225 tests, 227 crash cases, 226 library proofs, a 577-program
guard, 44 gates.** **Most hobby languages have none of that.**

**What is missing is not features. It is three things:**
1. **The documentation does not say what the language already does** - **`likha("x = ", x)` has worked all along and no
   example uses it.**
2. **The examples teach the opposite of the language** - **48 English function names, 135 three-statement prints.**
3. **The vocabulary is 90% Sanskrit in the library and 44% in the examples.**

**All three are fixable without touching the compiler.**
