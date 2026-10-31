# Where Sutram stands, and everything left — updated after the nivartanam round

**Compiler v258 · changelog v404 · suite PASS=225 · corpus 227/0 · proofs 226/226 · gates 48 PASS / 0 FAIL / 1 NOT-RUN.**

**The one NOT-RUN is Windows execution, and that is the owner's own test.**

**This page replaced the earlier version, which had six items open that were already done.**
**The lesson is in section 0.**

---

## 0. Why the earlier version of this page was wrong

**It listed `likha` with up to six values, the `lkhb` float bug and `arabhya ... paryantam` as work to do.**
**All three landed in ROUND-52 and I did not know.** **ChatGPT found them by reading the tree; I had written the page from memory.**

**It also said `likha("x = ", x)` was unused.** **It is used, in `examples/43_nested_likha.sm`, with a golden.**
**So the page was wrong about the language, wrong about the examples, and wrong about the work remaining.**

**Rule for the next version of this page: every claim carries the command that produced it.**

---

## A. Done — verified, and removed from the open list

| Item | Where | Evidence |
|---|---|---|
| **`likha` with up to six values** | **R52, v258** | arity `db 1,3` -> `db 1,6`; suite 225 |
| **The 135 three-statement print triples** | **R52 (Muse), 48 files** | 405 lines -> 135; goldens changed only by empty-line deletion |
| **`lkhb` on a `dasham` printing raw bits** | **R52** | fixed |
| **`arabhya ... paryantam`** | **R52** | tested byte-identical to `tak` loops |
| **`nivartanam` as the keyword, `prati` as alias** | **R53/R54, 162 files** | **guard 0 DIFFER; zero goldens changed** |
| **Seven wrong Devanagari words in the pack** | **v402** | `चक्र`, `माला`, `अन्य`, `अग्रिम` tested compiling |
| **The Sanskrit pack audit** | **`docs/reports/LANG-PACK-AUDIT.md`** | 11 defects found, 7 fixed |

---

## B. In flight

| Round | Who | What |
|---|---|---|
| **R55** | **Claude** | **Apply Muse's `tests.patch` + `docs.patch`, and ChatGPT's R127/R128 reference insertions** |
| **R55** | **Muse** | **Count the English variables in `examples/` and propose Sanskrit — table only, no changes** |
| **R129** | **ChatGPT** | **Audit all 305 library names against their BODIES** — the work that found `nishan` |

---

## C. Still open, and none of it is a language feature

| # | What | Blocked on |
|---|---|---|
| **C1** | **`Sutram Error` -> `Sutram dosh`, 74 places** | **a decision: the Linux IDE matches the literal string.** **Change the IDE too, or keep English in the prefix.** |
| **C2** | **The 15 mutants that survived every proof** | **including a sign error in `madhava_sin`/`cos`/`atan`.** **A maths function returning a wrong-signed answer passed 224 proofs.** |
| **C3** | **The 818 undecided mutants** | **the library is proven against KNOWN bugs, not proven correct** |
| **C4** | **`तक्` in the loop parser** | **the loop parser holds ONE spelling per keyword and last-wins, so adding `तक्` broke `पर्यन्त`.** **A compiler change, not a data change.** |
| **C5** | **`पङ्क्ति` inside `pankti_len`** | **the retired array word is still in a Devanagari builtin name** |
| **C6** | **`कोशपोप्` for `kosh_pop`** | **looks like the English "pop" transliterated, not a Sanskrit word** |
| **C7** | **The ~140 English variables in `examples/`** | **Muse is counting them; the owner reviews the table first** |
| **C8** | **The 305-name vocabulary review** | **`sutram-vocabulary-review.html` — 14 agree, 34 disagree, 3 reject, 10 Devanagari mismatches. Waiting on the owner.** |

---

## D. The decisions only the owner can make

| # | Decision | Why it matters |
|---|---|---|
| **D1** | **The type on variables** | **open longest.** It unblocks indexing, checked calls through function values, method dispatch and traits. |
| **D2** | **`Sutram Error` — change the IDE or keep English** | **blocks 74 sites** |
| **D3** | **`ganit` -> `ganan`, 41 sites** | **Muse says safe; ChatGPT wants a separate review because `ganan` may collide with the `ganana` enum keyword** |
| **D4** | **The 34 vocabulary disagreements** | **the review page** |
| **D5** | **The keyword count, 31 or 32** | **ChatGPT and I both say 31** |
| **D6** | **Did you tell Claude to apply all four patches and raise a limit?** | **Claude's R54 attributes that decision to you and I cannot see it being made.** **Same shape as the earlier "the owner chose laghu".** |

---

## E. Next, after this vocabulary round closes

**Memory — the owner has named it as the next block of work.**

**The state: `nirmmita` allocates and there is NO `free`.** **`kosh` leaks about 15.3 bytes per item.** **A garbage collector is
refused because it needs a runtime, and the promise is a native binary with no runtime.**

**The three real options, and the design is written up:**
1. **Explicit allocate / free — the programmer pairs them, leaks are possible**
2. **Region allocation — allocate is a pointer bump, free is a pointer reset.** **Faster than malloc, and nothing can leak.**
3. **Compile-time ownership — zero runtime cost, but it constrains how you write**

**The measurement to settle it is not done yet.** **It should be: N allocations of a fixed size, malloc against an arena, same
loop, cycles counted with `rdtsc`.** **This sandbox has NASM and no C compiler, so it has to be written in assembly — which is
the right language for it anyway, since Sutram's `nirmmita` uses `mmap` directly.**

---

## F. Beyond v1.0

**Package manager · profiler · LSP · concurrency · generics, closures, traits, iterators · memory safety beyond bounds guards ·
performance work (deferred by the owner) · the other ten language packs · the custom console window (a v1.1 note).**

---

## The honest state

**The language works and is unusually well verified: 225 tests, 227 crash cases, 226 library proofs, a 577-program guard,
48 gates.**

**What was missing was never features. It was three things, and two are now fixed:**
1. ~~**The documentation did not say what the language already does**~~ — **in R55**
2. ~~**The examples taught the opposite of the language**~~ — **R52 migrated 48 files, R55 finishes the variables**
3. **The vocabulary is ~90% Sanskrit in the library and lower in the examples** — **in progress**
