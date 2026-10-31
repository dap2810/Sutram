# Aliases: five options, and the one I would actually build

**The question: `ganita` is 6 letters and a learner types it constantly.** **Can there be a short alias, the way Python
has `import numpy as np`?**

**Short answer: yes, and the good version is not the Python version.** **Below are five options, what each costs, and the
one I recommend.**

---

## Option 1 — the Python way: one alias per module, chosen by hand

```sutram
yoj ganita as gan
```

**What Python does.** **What it costs:** the alias is the user's choice, so two files can use `gan` for different things,
and no tool can know what `gan` means without reading the file.

**And there is a collision nobody has noticed:** **`gan` is already the first three letters of BOTH `ganita` and
`ganit`.** **So `yoj ganita as gan` and `yoj ganit as gan` both work today, and mean different things.**

**Verdict: usable, and it does not solve the problem it looks like it solves.**

---

## Option 2 — the sutra index: a short code the language itself provides

**Every module gets a code, computed by one rule, and the compiler accepts both.**

**The rule: the shortest module name in a collision group keeps the shortest code.**

| Code | Module | Letters saved | Functions |
|---|---|---|---|
| `aa` | aadhar | 4 | 2 |
| `an` | ank | 1 | 10 |
| `br` | brihat | 4 | 13 |
| `ch` | chandas | 5 | 6 |
| `ga` | **ganit** | 3 | 18 |
| `gu` | gudh | 2 | 2 |
| `ka` | kalana | 4 | 6 |
| `kh` | khand | 3 | 22 |
| `ma` | mala | 2 | 8 |
| `ni` | nighantu | 6 | 17 |
| `pa` | patra | 3 | 3 |
| `ph` | phal | 2 | 14 |
| `ro` | roop | 2 | 23 |
| `sa` | sadhan | 4 | 7 |
| `sh` | shreni | 4 | 14 |
| `su` | suchi | 3 | 34 |
| `va` | varna | 3 | 27 |
| `anu` | anukram | 4 | 5 |
| `gan` | **ganita** | 3 | 22 |
| `mad` | madhava | 4 | 5 |
| `sam` | samanvaya | 6 | 11 |
| `san` | sangrah | 4 | 14 |
| `vak` | vakyank | 4 | 6 |
| `sank` | sankhyiki | 5 | 16 |

**Average saving: 3.5 characters per module reference.** **`ni` for `nighantu` saves 6.**

**And it is ONE rule, not 24 decisions.** **Add a module tomorrow and the code follows from the rule.**

**What no other language does:** **Python's `np` is a convention the user writes. C's aliases are `#define`s. Rust's
`use ... as` is per-file.** **None of them SHIPS a short name.** **Sutram would: `ganita_yog` and `gan_yog` are the same
call, always, in every file, with no import line.**

**What it costs:** **`ga` (ganit) and `gan` (ganita) are still one letter apart.** **The alias inherits the ambiguity
instead of fixing it.** **So this option only works after `ganita`/`ganit` is resolved.**

---

## Option 3 — the sandhi call: drop the underscore, join the sounds

**Sanskrit compounds do not use a separator.** **`rāja` + `putra` is `rājaputra`, one word.** **And the join follows
sandhi: `suchi` + `apanay` is `sucyapanay`, because `i` before a vowel becomes `y`.**

**So the language could accept `ganitayog` for `ganita_yog`, and `sucyapanay` for `suchi_apanay`.**

| Full | Sandhi form | Letters |
|---|---|---|
| `ganita_yog` | **`ganitayog`** | 11 -> 10 |
| `suchi_apanay` | **`sucyapanay`** | 13 -> 11 |
| `brihat_ank` | **`brihadank`** | 11 -> 10 |
| `varna_yuj` | **`varnayuj`** | 10 -> 9 |
| `kosh_khip` | `koshkhip` | 10 -> 9 |

**What no other language does:** **every language treats an identifier as an opaque token; sandhi would make the JOIN
meaningful.** **`brihadank` is not a misspelling of `brihat_ank` - it is the correct Sanskrit form, and the compiler
would know that.**

**What it costs:** **only 1-2 characters saved per call** - **and the sandhi form differs from the written name, which is
the same defect as the 10 Devanagari mismatches already in the project.** **A learner would have to know sandhi to spell
a function.**

**Verdict: beautiful, and it makes the language harder, not easier.**

---

## Option 4 — the vibhakti idea: grammatical case says how you use it

**Sanskrit nouns decline.** **`ganita` becomes `ganitam` (object), `ganitena` (by means of), `ganitasya` (of), `ganite`
(in).**

**A language could use the case ending as a usage marker:**

| Form | Case | Meaning |
|---|---|---|
| `ganita` | nominative | the module as a subject |
| `ganitena` | instrumental | **by means of** - a call |
| `ganitasya` | genitive | **of** - a namespace |
| `ganite` | locative | **in** - a field access |

**What no other language does: nothing.** **This is genuinely unused anywhere.**

**What it costs: everything.** **`ganitena` is 8 letters - longer than `ganita`.** **And it asks a programmer to know
Sanskrit grammar to call a function.** **It would make Sutram beautiful to a Sanskritist and unusable to a beginner, and
the whole point is that a beginner can learn it.**

**Verdict: the most original idea here, and the wrong one for this project.**

---

## Option 5 — the pratyahara: a code that names a FAMILY, not a module

**This is the idea I would actually name the feature after.**

**Panini's grammar does not abbreviate by truncation.** **It uses the pratyahara: two letters that name a whole SET.**
**`an` names every vowel; `ak` names every vowel plus every consonant; `yan` names every semivowel.** **The two letters are
not the first two letters of anything - they are a boundary pair, and everything between them in the ordered list belongs
to the set.**

**So a pratyahara is: a short code whose MEANING is a range, and the range is defined once.**

**Applied here: the alias is not "the short form of one module".** **It is "the short form of one FAMILY".**

| Family code | Members | Why they belong together |
|---|---|---|
| **`sa`** | sadhan, samanvaya, sangrah, sankhyiki | **all four are about collections and measurement** |
| **`ga`** | ganit, ganita | **both are arithmetic** |
| **`ma`** | mala, madhava | **array and the Kerala series - both numeric arrays** |
| **`va`** | varna, vakyank | **character and base conversion - both about digits** |
| **`a`** | aadhar, ank, anukram | **base, number, sequence** |

**So `sa.` would open all four modules at once.** **A learner types `sa` and gets every collection operation in one
list.** **That is not an abbreviation - it is an INDEX.**

**And it is the one thing on this list that is both authentically Paninian and genuinely useful:** **Panini's problem was
"how do I name a set without listing it"; a programmer's problem is "how do I find the right function without reading
305 names".** **Same problem, same solution.**

---

## My recommendation

**Build Option 2 with Option 5 as its organising idea, and skip 3 and 4.**

**Concretely:**
1. **Fix `ganita`/`ganit` first.** **Rename `ganit` to `ganan`.** **Then the codes are `gan` (ganita) and `gan` - no,
   `ganan` - clean.**
2. **Add a module code per module, computed by the shortest-name rule.** **Both the full name and the code work.**
3. **Add family codes as a SECOND tier**, so `sa` reaches all four collection modules.
4. **The IDE shows it:** type `ga.` and the completion list is the whole arithmetic family, with the full names shown
   beside each short one.

**Why this and not the others:**
- **It is one rule, so it does not need maintaining.**
- **It costs nothing at the call site** - the full name always works, so no existing program breaks.
- **It is the only one of the five that makes the language EASIER to learn rather than harder.**
- **And the pratyahara framing is honest:** **it is not decoration on a namespace, it is a real answer to "how do I name
  a set with two letters".**

**What I would NOT do:** **sandhi joins (Option 3) and case endings (Option 4).** **Both are more beautiful and both make
a beginner's first program harder to write.** **The project's aim is that anyone in India can learn this language; a
feature that requires Sanskrit grammar to use is a feature that shrinks the audience.**

---

*Written by Sarvam, 27 October 2026. Every code in Option 2 was computed from the 24 module names on main at compiler
v253, and the six collision groups were found by trying it, not by assuming it would work. Nothing is implemented.*
