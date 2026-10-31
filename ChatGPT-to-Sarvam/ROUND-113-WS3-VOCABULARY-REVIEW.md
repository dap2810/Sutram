# Sutram ROUND-113 WS3 — DRAFT vocabulary derivation, second review

**Input:** `docs/vocabulary/VOCABULARY-DERIVATION.md` blob `9d21095a23b28687ff2278dc8f0ae1c54dfc774e`; pinned main `1ccec720dccc53ae8ed344e4f58f87fba727682a`. This is a *review of source consistency*, **not a Sanskrit grammatical certification**.

## Source-checkable defects before any linguistic judgment

1. **Count drift** `docs/vocabulary/VOCABULARY-DERIVATION.md:5,10,33,110`: says "303" function names, whereas current `docs/sutram-stdlib.html` generated footer has **24 modules / 305 functions**, matching `lib/*.smlib`. If 303 is a separate selected-vocabulary count, define exact scope and inventory rather than conflating it with all callable functions.
2. **Invented example callable** `:23` claims `ganita_sat_yuj` implements saturating addition. Current `lib/ganita.smlib:348` and HTML row name the real function `ganita_paripurna_yuj`. Treat as **wrong copyable function name**; do not rename the library to fit the draft.
3. **Inverted reference fact** `:88`: claims `ganita_janchit_gun` is NOT in reference. It **IS** in `lib/ganita.smlib:269` and `docs/sutram-stdlib.html:145`. Rewrite the demonstration using a truly absent but clearly hypothetical expression, not a current valid call.
4. **Module taxonomy false** `:38-49`: states all eleven prefixes are "already the module names" and every function in `ganita` starts with `ganita`. Current `lib/` has 24 modules; no `lib/vartani.smlib`, `lib/akshar.smlib`, or `lib/kosh.smlib`. `ganita` includes `kuttaka`, `chakravala`, `samasa` and `brahmagupta_kshetr` without that prefix. `lib/sangrah.smlib` has `rakh_*` callable functions. Fix by labeling these as **observed naming families and builtins**, not a complete module namespace grammar.
5. **Mixed API layers** `:24-25,76-79`: `akshar_rakh` is in `docs/sutram-vocabulary.html`, but not a function defined by any of the 24 `lib/*.smlib` files. `vartani_len` is in earlier builtin material, not a stdlib module declaration. A beginner needs a separate **compiler builtin vs standard library function** explanation. This audit does not claim such builtins fail to compile; no compiler executed.
6. **Qualifiers not a universal rule** `:23,56-67`: `sat` in `ganita_sat_yuj` is not the current saturating function-family spelling, which is `ganita_paripurna_*`. `vargmool` can itself be the main action rather than a qualifier plus further action. Identify productive patterns and documented exceptions rather than asserting "last word always the action".

## Sanskrit/linguistic question: qualified, not authoritative

- An underscore-delimited programming identifier built from Latin transliterations is not automatically evidence of a formally correct Sanskrit **samāsa**. The draft's "left to right, most general first" is a useful *software naming heuristic*, but its morphological derivation has **not** been validated from Sanskrit grammar.
- `rakh` resembles an everyday Hindustani/Hindi verb form rather than an unambiguous Sanskrit stem. `raksh` evokes a different Sanskrit root sense (protect/preserve); treating them as interchangeable "keep/place" in `:76` is **linguistically risky**. I cannot certify the correct Sanskrit lexical form or inflection; **Sanskritist review required**.
- `likh` is plausibly related to the Sanskrit writing root, but whether `likh`/`lekh` are acceptable canonical transliteration, stem/command pairs requires expert orthographic and grammatical checking. Don't rewrite working compiler builtin names on a guess.
- `ganita` and the qualifier order should also be validated by a qualified Sanskritist; implementation code establishes usage, not linguistic correctness.

## Suggested revision gate

Separate three layers: (1) **implemented canonical names** with automated source/HTML witness and current 305 count; (2) **learner-friendly naming families** expressed as tendencies with named exceptions and a builtin-vs-module distinction; (3) **linguistic etymology or samāsa analysis**, explicitly DRAFT pending specialist approval. Use real functions `ganita_janchit_gun`, `ganita_paripurna_yuj`, `mala_grah_surakshit`; do not claim all 24 modules follow a strict prefix grammar. Preserve project goal Sanskrit-first.

**Verdict: FAIL source consistency; Sanskrit compound/stem correctness CANNOT CHECK as qualified reviewer; request Sanskritist.** No source, language packs or vocabulary document were modified.