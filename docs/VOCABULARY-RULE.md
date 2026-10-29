# The vocabulary rule — for every word this project adds, from now on

**Agreed by the owner, 29 October 2026.** **This page is the test every future keyword, builtin and library name must pass.**

---

## Why this page exists

**Sanskrit is vast.** **That is a real advantage and a real hazard, and the difference between them is one question.**

**A rich language lets us be PRECISE with a small set of words.** **It also lets us be GENEROUS with a large set, which makes the language harder to learn and is exactly what we are trying to escape.**

**English has `field`, `region`, `area`, `zone`, `domain`, `territory`, `scope`, `space` — eight words with overlapping meanings and no visible relationship between them.** **Nobody can guess what `scope` means from `area`.** **Sanskrit has `kshetra` and its compounds, where the relationships are on the surface.**

**So the advantage is not the count. It is that the words are READABLE.** **That is the thing worth protecting.**

---

## The three rules

### Rule 1 — a new word must remove an ambiguity, or replace an existing word

**It may not simply add to a total.**

**The test: name the confusion the word removes.** **If you cannot name one, the word is decoration.**

| Word | The confusion it removed | Verdict |
|---|---|---|
| **`nivartanam`** | **`prati` is a prefix meaning "back", not the noun for returning** | **passes** |
| **`kshetra` vs `mandapa`** | **the field and the pavilion were being called one thing** | **passes** |
| **`avayava` for a struct member** | **a member is not a region; `kshetra` said the wrong thing** | **passes** |
| **`chay`** | **none — it is real Sanskrit (चय, heap) and was already right** | **fails; leave it** |
| **a fourth word for "loop"** | **none — `chakra` works and everyone can picture a wheel** | **fails** |
| **`ardhamandapa` as a size the programmer picks** | **none — it renames a number without helping you choose one** | **fails** |

### Rule 2 — prefer a compound over a new root

**If a programmer knows `mandapa`, then `ardhamandapa` and `mahamandapa` cost them nothing.** **`ardha` is half, `maha` is great.** **They can read both without a glossary.**

**That is how a vocabulary grows without the learning curve growing with it.** **A new root is a new thing to memorise; a compound of known parts is a thing you can already read.**

**This is the single most important rule, because it is the one that makes a large vocabulary affordable.**

### Rule 3 — anything the compiler can name, the programmer should not have to

**A word the programmer must choose between is a cost.** **A word the compiler reports is a benefit — it teaches the system while being read.**

**So `ardhamandapa` and `mahamandapa` earn their place as SIZE TIERS the compiler reports in an error (`ardhamandapa purnam` tells you which tier ran out), not as boxes the programmer picks from.** **The programmer writes `mandapa` and the compiler decides the tier.**

---

## The numbers this protects

**The language has 33 keywords and about 80 builtins.** **That is roughly 113 words a beginner must know before reading someone else's program.**

**For a language aimed at a school in India, that is already a great deal.** **Every future word should be treated as expensive.**

**So the standing budget: the keyword count does not rise without a word coming out, or a named confusion going away.**

---

## What this week actually was

**Worth stating, because it shows which direction is the good one.**

**The vocabulary work removed confusion far more than it added vocabulary:**

- **20 library names that described the wrong operation** — `sadish_yoga` said vector addition and computed a dot product
- **one collision caught** — `kosa` would have collided with `kosh`, both कोश
- **a second collision caught** — `kshetra` already meant "struct field" in four diagnostics
- **one prefix replaced by a real noun** — `prati` became `nivartanam`
- **seven wrong Devanagari words in the pack**

**Almost all of it was subtraction.** **That is the direction that made the language better, and it is the direction these three rules protect.**

---

## The final vocabulary for memory

| Word | Devanagari | Level | Where it appears |
|---|---|---|---|
| **`kshetra`** | **क्षेत्र** | **the whole arena — the field** | **in error messages and documentation; not a keyword the programmer types** |
| **`mandapa`** | **मण्डप** | **the scratch block — a pavilion raised in the field and struck when done** | **the one new keyword** |
| **`avayava`** | **अवयव** | **a member of a `rachana`** | **replaces `kshetra` in the four field diagnostics** |
| **`ardhamandapa` / `mahamandapa`** | **अर्धमण्डप / महामण्डप** | **size tiers — the entrance porch, the great hall** | **the compiler reports them; the programmer never chooses them** |
| **`garbhagriha`** | **गर्भगृह** | **the innermost sanctum — what must survive** | **documentation only, naming the persistent region** |

**Five words, each at its own level, each readable from the others, and exactly one of them is a new keyword.**
