# The indentation-parser class, tested independently on v265

**Run by me, 30 October 2026, on the built v265.** **Seven constructs, and one expectation of mine that was wrong.**

---

## The tests and the results

| # | Construct | Body | Expected | Got | |
|---|---|---|---|---|---|
| **A** | `yavat` | **2 statements** | `s=30` | **`s=30`** | **pass** |
| **B** | `yadi` | **2 statements** | `y=5 x=9` | **`y=5 x=9`** | **pass** |
| **C** | `chakra i = 0 tak 3` | **2 statements** | `s=9` | **`s=12`** | **my expectation was wrong** |
| **D** | `prakriya` | **2 statements + `nivartanam`** | `f(5)=11` | **`f(5)=11`** | **pass** |
| **E** | `yavat` | **4 statements** | `3 6 9` | **`3 6 9`** | **pass** |
| **F** | `yavat` nested inside `yadi` | **2 + 2** | `t=15` | **`t=15`** | **pass** |
| **G** | `anya` | **2 statements** | `a b` | **`a b`** | **pass** |
| **H** | `mukhya` | **4 statements** | `c=3` | **`c=3`** | **pass** |

**So the fix at v265 is complete for every indented body I could construct** — including four statements, and nesting one indented body inside another.

---

## Test C, and why it was mine that was wrong

**`chakra i = 0 tak 3` with a body of `s = s + 2` and `s = s + 1` gave `s=12`, and I expected `s=9`.**

**12 = 4 iterations x 3.** **So `tak 3` runs 0, 1, 2, 3 — four iterations, INCLUSIVE.**

**That is the documented and tested behaviour, not a bug:**
- **`examples/11_forloop.sm` writes `chakra i = 0 tak 5`, and `tests/expect/11_forloop.out` expects `0 1 2 3 4 5` — six iterations.**
- **`docs/LANGUAGE-REFERENCE.md:285` shows `chakra i = 1 tak 5` for "for (ascending)".**

**So `tak` means "up to and including", consistently, with a golden that pins it.** **My expectation came from C habits, not from this language's spec — which is exactly the kind of assumption that produced my wrong diagnosis of the loop bug an hour earlier.**

---

## What this does and does not establish

**Establishes:** **the parser fix handles multi-statement indented bodies in `yavat`, `yadi`, `anya`, `prakriya`, `mukhya`, and nesting.** **Eight cases, all correct.**

**Does not establish:** **that no other construct has a similar defect.** **I tested the seven I could think of.** **A construct I did not think of is exactly the shape of the bug that shipped — nobody thought of allocating in a loop.**

**So the durable answer is not my eight tests; it is a test that counts statements per body against the source, which is what I have asked ChatGPT to price.**

---

## The pattern, three times in one session

1. **I assumed the allocator caused the loop hang.** **It was a parser bug from 264 versions earlier — found only by testing the baseline.**
2. **I assumed `tak 3` meant three iterations.** **It means four, and a golden says so.**
3. **Earlier I assumed a one-sentence scope rule was sufficient.** **Three parties disproved it in a day.**

**All three are the same error: trusting an expectation instead of checking the artefact.** **The fix in each case was the same too — run it, or read it, rather than reason about it.**
