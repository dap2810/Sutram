# Lexer boundary test: the answer, measured

**Question:** does a name that begins with a keyword compile? **Asked because `prati` is the `return` keyword, and a
library function `vartani_pratilip` (string-copy) needs to be legal.**

**Answer: YES, on main at compiler v249, today. Nothing needs fixing.**

## The measurement

**Four programs, compiled with the v249 compiler on a fresh clone, then run:**

| Program | What it tests | Result |
|---|---|---|
| `t1` | a `prakriya` named **`prati_test`** (keyword `prati` + `_test`) | **compiles, prints `6`** |
| `t2` | a `vitti` named **`mukhyata`** (keyword `mukhya` + `ta`) | **compiles, prints `7`** |
| `t3` | a `vitti` named **`pratiX`** (keyword `prati` + `X`) | **compiles, prints `3`** |
| `t4` | a `vitti` named **`vartani_pratilip`** (the real case) | **compiles, prints `9`** |

**All four compiled ("Siddh: N baait sankalit") and all four produced the correct output.**

**So the lexer already requires a keyword to end at a non-word character.** **`prati` does not match inside
`prati_test`, `pratiX` or `vartani_pratilip`.**

## What this means

**The project has been choosing worse words to avoid a problem it does not have.** **`anuk` instead of `pratilip`,
because of a collision that does not occur.** **`aayam` instead of a cleaner word, for the same reason.**

**So the vocabulary can use the right word. `vartani_pratilip` is available today.**

## What is still worth doing

**1. The test as a permanent test file.** **These four cases should be in `tests/`, not in my scratch directory** - so a
future lexer change cannot silently break them.

**2. The Devanagari direction.** **I tested Latin identifiers only.** **The case that still needs an answer is a
Devanagari keyword followed by a Devanagari letter** - e.g. `प्रतिलिपि` where `प्रति` is a keyword. **If the boundary
check is byte-naive rather than character-aware, that case fails while these four pass.**

**3. `tools/check_keyword_prefix.py`** - **not needed as a naming constraint, but useful as a report**: it would show
which identifiers currently begin with a keyword, so the answer stays visible rather than being re-derived.

**4. The `.lang` pack files** need the Devanagari form of any new word.

## And one incidental finding

**The compiler's own error message reads `vyakaran dosh, pankti 1:8`.** **`pankti` means "line" here, which is correct
Sanskrit** - but `pankti` was also the retired keyword for *array*, now `mala`. **There are 34 occurrences of `pankti` in
the compiler source.** **Most are this "line" sense, which is legitimate; the question is whether any is the retired
array sense.** **Worth a check, not an alarm.**

---

*Measured by Sarvam, 27 October 2026, on a fresh clone of main at compiler v249. Four programs, compiled and run.*
