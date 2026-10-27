# Sutram ROUND-115 WS2 — teach a SMALL PRODUCTIVE CORE + an audited lookup list, not a universal derivation rule

**Source evidence:** complete 305-name inventory [ROUND-114-WS1-MEASURED-PREFIXES.json](ROUND-114-WS1-MEASURED-PREFIXES.json) and raw source-name TSVs `ROUND-114-RAW-NAMES-A.tsv` (119) and `...B.tsv` (186), checked against main at `e2ddf0922caccb4e60c29f2c3012929125a4f67c`. All 24 library modules were read and no new public callable names were observed.

## Verdict

**Use small core of recurring conventions + explicit searchable list of all 305 current callables.** Not a strict `domain_qualifier_action` rule, and not 305 names to memorize unstructured. An ordered beginner curriculum is preferable: current Sanskrit core grammar; what modules and builtins are; a limited list of reliable word families; examples with real verified names and parameter/return expectations; complete generated reference as lookup. **No claim that Latin underscores are formal Pāṇinian samāsa grammar** until Sanskritist approval.

## Why a universal rule is mathematically false

- **305** unique function names across **24** `lib/*.smlib` modules.
- **91** distinct first underscore-delimited tokens, **63** of them present once.
- **45** names have no underscore at all; 174 have two segments, 81 three, 5 four. A universal 3-part template cannot describe 219 of the 305 without exceptions even before semantic checks.
- **171/305** begin with the name of their *own* defining module; **134 do not**.
- Draft's original **11 domain prefixes account for only 102/305** names. Three proposed prefixes (`vartani`, `kosh`, `sangrah`, plus `shreni` — actually FOUR) have **zero** source first-token occurrence. `vartani` and `kosh` also belong to builtin/type surfaces rather than 24 library module names.
- `ganita` defines `chakravala`, `samasa`, `kuttaka` and `brahmagupta_kshetr` without `ganita_`; `sangrah` exports `rakh_*`, `shreni` exports operation names; two `brihat_*` names are defined in `aadhar` rather than `brihat`. Function names are NOT guaranteed to equal or begin with module names.

## What is worth teaching explicitly

**Eight useful first-token families (141 distinct names = 46.2% of 305, counted once):**

| Family | Count | How to teach without false promises |
|---|---:|---|
| `roop_*` | 23 | Byte-oriented number/string formatting; explain output buffer convention |
| `khand_*` | 22 | Explicit-length byte-string helpers; distinguish qword cells |
| `suchi_*` | 21 | Dynamic list operations, with stack `chay_*` and queue `avali_*` as *additional* families |
| `ganita_*` | 18 | Checked/saturating arithmetic forms, but several `ganita` functions have other names |
| `varna_*` | 18 | Cell/string conversion helpers; do not assume same byte representation as `khand` |
| `nighantu_*` | 17 | Map operations, with explicit capacity and key length |
| `phal_*` | 14 | Result value conventions; checked failure carries an explicit `ok` |
| `mala_*` | 8 | Raw fixed-allocation qword helper APIs, not inherently dynamically growing `kosh` |

**Cross-module/nondomain families to teach second:** `brihat_*` (15: 13 inside `brihat`, 2 inside `aadhar`), `rakh_*` (14 set operations implemented in `sangrah`), `asti_*` (13 predicate-shaped names, not a module), `avali_*` (9 queue operations), `chay_*` (4 stack operations). These should be displayed alongside the real `yoj` module of origin so learners don't invent imports.

**Action tokens (not universal):** measured last-token frequencies include `yuj` 7, `maap` 6, `antah` 6, `anwesh` 6, `rikta` 5, `apanay` 4, `gun` 4, `nyun` 4, `srij` 4, `grah` 3, `khip` 3. Examples must be copied from real source and verified before publishing; do not manufacture a function by combining tokens and call it implemented.

## Learner-facing product format

1. **Vocabulary basics**: source keywords versus functions versus builtin operations versus user library modules. `kosh` is a type; `ganita`, `khand`, `suchi` are module names; `yoj` is an import.
2. **Cheat sheet of 8 high-value families** with one source-supported example each, expected arity, units, buffer layout and failure mode.
3. **A small set of action tokens** where documented as tendencies, not binding grammar; each pairing includes counterexample/exception.
4. **Searchable complete index of 305 real identifiers** grouped by defining module, not an inferred prefix. Each entry links its current `prakriya` line, source module, parameters, output contract and positive executable example once native-tested.
5. **Gentle failure feedback**: teach how to read "unknown function" and locate actual names, not silently add aliases or rename code to match guesses.
6. **Sanskritist-reviewed labels** only when certified; a developer naming mnemonic does not prove the word's grammatical correctness.

**Explicit nonclaims:** naming convention does not certify unique semantics, parameter kinds, ABI, memory extent, or Sanskrit morphology. Teach `ganita_paripurna_yuj`, not imaginary `ganita_sat_yuj`; `ganita_janchit_gun` is a real callable, not merely a guessed example.

**PASS — complete source counts support a restricted convention + lookup strategy. NOT RUN - no toolchain** native example acceptance. **NOT CERTIFIED — Sanskrit linguistic derivation** (qualified expert required).
