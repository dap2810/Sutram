# The vocabulary: the rules, not just the list

**Status: DRAFT - needs a Sanskrit scholar's review before it is presented as authoritative.**

**Why this document exists.** The project has a frozen vocabulary of 303 function names, and a reference page that
lists them. **A list is a dictionary: it only helps someone who is already looking up a word they know.** **What makes
a vocabulary learnable is the RULES - so that a learner can predict a name they have never seen.**

**The owner's directive was that word choice be *easy to remember and easy to type*, and that someone who does not
read English can learn this language.** **A derivational rule serves both: you remember one rule instead of 303
words, and you can type a name you were never taught.**

---

## 1. The pattern that is already there

**Sutram's names are compounds, built left to right, most general first:**

| Name | Parts | Reads as |
|---|---|---|
| `ganita_janchit_yuj` | `ganita` + `janchit` + `yuj` | math + checked + join = **checked addition** |
| `ganita_janchit_nyun` | `ganita` + `janchit` + `nyun` | math + checked + less = **checked subtraction** |
| `ganita_sat_yuj` | `ganita` + `sat` + `yuj` | math + true/valid + join = **saturating addition** |
| `vartani_len` | `vartani` + `len` | string + length |
| `akshar_rakh` | `akshar` + `rakh` | character + place = **set character** |

**The rule a learner can extract:** **`<domain>_<qualifier>_<action>`**, and **the last word is what the function
does.**

## 2. The domains

**A domain prefix tells you which part of the library you are in.** **Learn eleven words and you can place any of the
303 names:**

| Prefix | Meaning | The module |
|---|---|---|
| `ganita` | mathematics | arithmetic, checked arithmetic |
| `vartani` | string, sequence | byte strings |
| `akshar` | character, letter | character operations |
| `mala` | row, array | fixed arrays |
| `kosh` | store, treasury | growable arrays |
| `suchi` | list, index | lists |
| `nighantu` | glossary | maps |
| `sangrah` | collection | sets |
| `shreni` | row, rank | sorting |
| `phal` | fruit, result | the result type |
| `roop` | form | formatting |

**These are already the module names.** **So `yoj ganita` puts you in the maths module, and every name inside it starts
with `ganita`.**

## 3. The qualifiers

**A qualifier narrows what the action does.** **The ones that recur:**

| Qualifier | Meaning | Where it appears |
|---|---|---|
| `janchit` | checked, examined | checked arithmetic that detects overflow |
| `sat` | true, valid | saturating arithmetic that clamps instead of wrapping |
| `nirapeksh` | independent, absolute | absolute value |
| `vargmool` | square root | root extraction |

**So the rule a learner applies:** **`ganita_<qualifier>_<action>` is a maths operation with that property.** **`sat`
clamps, `janchit` refuses, and no qualifier means the plain wrapping operation.**

## 4. The actions

**The last word says what happens.** **The recurring ones:**

| Action | Meaning | Example |
|---|---|---|
| `yuj` | join, add | `ganita_janchit_yuj` |
| `nyun` | less, subtract | `ganita_janchit_nyun` |
| `gun` | multiply | (see the module) |
| `bhaj` | divide | (see the module) |
| `raksh` / `rakh` | keep, place | `akshar_rakh` |
| `grah` | take, receive | `anukram_grah_ashtak` |
| `likh` | write | `likh` |
| `pad` | read | `pad` |
| `khol` | open | `dvaram`-adjacent |
| `band` | close | |
| `shreni` | arrange, sort | `suchi_shreni` |

## 5. What this buys a learner

**Three things, and they are the point of the whole document:**

1. **A name they have never seen is a name they can guess.** **`ganita_janchit_gun`** is not in the reference - but
   a learner who knows the rule reads it as "math, checked, multiply" and is right.
2. **A wrong guess is visibly wrong.** **`vartani_janchit_yuj`** does not exist, and a learner can tell *why* - the
   `janchit` qualifier belongs to `ganita`.
3. **The vocabulary can grow without a new list.** **A function added tomorrow follows the same rule**, so the
   reference page is a lookup rather than the only source of truth.

## 6. The honest limits of this draft

**Three things need checking, and I am not the person to check them:**

1. **Is `ganita` the right word for "mathematics" here, or does it carry a narrower sense?**
2. **Do the qualifiers compose the way I have described, or does Sanskrit compounding impose an order I have
   simplified?**
3. **Are `rakh`/`raksh` and `likh`/`lekh` the right stems, or have the shorter forms drifted from the roots?**

**A Sanskritist should review sections 2 to 4 before this is presented as a rule.** **Sections 1 and 5 are
observations about the code and stand on their own.**

## 7. Why this is worth doing at all

**The project's aim is that someone in India who does not read English can learn to program.** **The keywords are
already Sanskrit.** **But a vocabulary of 303 words is 303 things to memorise unless it has rules.**

**The rules are what make it a language rather than a glossary.**

---

*Draft by Sarvam, 26 October 2026. Derived from the frozen vocabulary in `docs/sutram-vocabulary.html` and the
module names in `lib/`. Needs a Sanskrit scholar's review of the compounding before it is authoritative.*
