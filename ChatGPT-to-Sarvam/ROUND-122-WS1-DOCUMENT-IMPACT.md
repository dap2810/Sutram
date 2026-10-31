# Sutram ROUND-122 WS1 — English-word documentation impact: source-verified, **NO blanket rename**

**Input:** `Sarvam-to-ChatGPT/ROUND-122.md`, blob `9c18a3f871c8721e7ef7511d91a314c4bfac1192`. **Pinned GitHub main** `61d5f7b70e30e6711cc2171e57744de2dede70a1` (changelog v374, compiler v253). Only Sanskrit active until v1.0; frozen language packs left unchanged. Newer `docs/CHANGELOG.md` v373/v374 and `docs/reports/LIBRARY-ENGLISH-AUDIT.md` explicitly correct the broad premise of Round 122: `sat_div` never was a current `lib/` function, and `char`, `len`, and much `int` are nonpublic implementation details or explanation.

## Direct source census: two real public candidates, not five unqualified categories

Every `prakriya` declaration in **24/24** `lib/*.smlib` was read from pinned GitHub source (305 real function declarations). Public names containing these English elements are:

| Candidate | Where it really exists | Meaning | Renaming recommendation |
|---|---|---|---|
| `brihat_ank_se_int(val, arr, n)` | `lib/brihat.smlib:28` | Converts native machine integer to fixed-size base-10 digit array | **OWNER DECISION PENDING**; provisional `brihat_ank_se_laghu`, but do not re-export before final word reviewed |
| `brihat_ank_tak_int(arr, n)` | `lib/brihat.smlib:69` | Converts digit array to native machine integer | **OWNER DECISION PENDING**; provisional `brihat_ank_tak_laghu`, same condition |
| `sat_div` | **NO declaration in all 24 library modules** | Earlier source documentation incorrectly asserted a public function | **DO NOT RENAME**; current actual saturating divide is `ganita_paripurna_bhaj(a,b)` at `lib/ganita.smlib:500` |
| `char`, `div`, `len`, `slice` | No standalone exported `prakriya` with those public names | English appears mainly in local identifiers, internal labels, historical comments, prose and mathematical concepts | **DO NOT REPLACE GLOBALLY**; `akshar`, `akshar_rakh`, `aksharank` and `vartani_aayam` already exist as public builtins. `vibhag` already names the slice parameter/type. |

**Specific ambiguity:** `brihat_ank_se_anka` uses `ank` in two senses (digit vs machine integer); `laghu` expresses small/light rather than explicitly a 64-bit integer. `laghu` is a **proposal**, not an approved semantic type label. A documented API rename must preserve call semantics, full caller list, source signature, tests, compatible spellings, and generated references. All renames remain UNAPPLIED by ChatGPT and **not authorized by this audit**.

## Comprehensive documents search, with safety modes

The **untruncated** tree on the pinned commit contained 4,373 entries. We fetched and searched **92/92 current root and docs text documents** (`.md/.html/.htm/.txt/.rst`). These include active reference, all book-language HTML copies, existing corpus/specs and historical release notes. The broad whole-word scan identified **1,122 physical lines across 37 files** mentioning any of `char`, `int`, `div`, `len`, `slice`, `sat_div`, `brihat_ank_se_int` or `brihat_ank_tak_int`. **55 documents have none.** These broad hits include **valid English**, CSS/HTML `<div>` markup and historical mentions; this is NOT 1,122 defects or proposed edits. Indeed multiple `div` tags can occur per HTML line, making even the word-frequency total a false API metric.

- [Full 92-file manifest including ZERO-match files](ROUND-122-WS1-CORPUS-MANIFEST.tsv).
- **All 1,122 physical lines with exact file/line/source-blob/mode/source text** were preserved in seven UTF-8 TSV parts: [1](ROUND-122-WS1-DOC-PART-1.tsv) · [2](ROUND-122-WS1-DOC-PART-2.tsv) · [3](ROUND-122-WS1-DOC-PART-3.tsv) · [4](ROUND-122-WS1-DOC-PART-4.tsv) · [5](ROUND-122-WS1-DOC-PART-5.tsv) · [6](ROUND-122-WS1-DOC-PART-6.tsv) · [7](ROUND-122-WS1-DOC-PART-7.tsv). Nonhistorical broad word hits are labelled `ALREADY_PRESENT_NOOP` by default because **English prose/HTML syntax is not an approved API rename**; the generated page is marked for owner-origin regeneration only. Do not mechanically apply these broad-line parts.
- [Curated 31-line **public-name impact** TSV with exact OLD/conditional NEW and modes](ROUND-122-WS1-API-IMPACT.tsv): `KEEP_HISTORICAL=20`, `PROPOSE_EXACT_CURRENT=8`, `REGENERATE_FROM_SOURCE=3`. The conditional NEW for the two `brihat` names is NOT approved. The source remains the authority.

## Where **actual public-callable names** would need an update IF the owner approves `laghu`

| File and line | Current role | Proper mode |
|---|---|---|
| `docs/sutram-stdlib.html:86–87` | Generated function table with the two exported names and contracts | **REGENERATE_FROM_SOURCE** after renaming source declarations/comments and updating callers; generator is `tools/gen_stdlib_ref.py`; never hand-edit |
| `docs/sutram-stdlib-reference.html:317–318,334–335` | Reader-facing static reference table plus worked example calls | **PROPOSE_EXACT_CURRENT**, pending owner approval and exact-head retest |
| `docs/sutram-vocabulary.html:139,145` | Searchable vocabulary enumeration | **PROPOSE_EXACT_CURRENT**, pending owner approval and regeneration/review of whichever tool owns that distinct page |
| `docs/reports/PROPERTY-NET.md:35` | Regression property description referencing both real names | **PROPOSE_EXACT_CURRENT**, conditional on actual property/test caller integration |
| `docs/reports/EDGE-COVERAGE-30.md:36,240` | Historical R30 tested boundary defect references | **KEEP_HISTORICAL**, do not rewrite a past test's spelling |
| `docs/CHANGELOG.md`, `docs/reports/LIBRARY-ENGLISH-AUDIT.md` | Dated before/after decisions, including the **retracted** phantom `sat_div` assertion | **KEEP_HISTORICAL**. The later corrective section must be retained, not overwritten |

Other current English occurrences such as `slice` in `docs/LANGUAGE-REFERENCE.md` are explanatory English glosses of the already-existing `vibhag` construct; **"vibhag (slice)" is helpful**, blindly removing "slice" from an English technical reference is not.

## Independent real current-doc problem: the nonexistent `sat_div` cross-reference

The *published* `docs/OVERFLOW-SAFETY.md:57` says `sat_div` is a companion sentinel; the generated `docs/sutram-stdlib.html:155` also names `sat_div` as though callable, from `lib/ganita.smlib:516`. This is **public contract/copyable-name drift**, not evidence for a rename. Suggested small fix, to review before applying:

- Current-doc OLD line `docs/OVERFLOW-SAFETY.md:57`: `\`sat_div\`. \`MIN % -1\` is guarded because the hardware operation traps`
- Current-doc NEW: `\`ganita_paripurna_bhaj\`. \`MIN % -1\` is guarded because the hardware operation traps`
- Source comment `lib/ganita.smlib:516` OLD: `# result. b == 0 returns 0 (same sentinel as sat_div). Guards before`
- Source comment NEW: `# result. b == 0 returns 0 (same sentinel as ganita_paripurna_bhaj). Guards before`
- Then **REGENERATE_FROM_SOURCE** `docs/sutram-stdlib.html` and check all public references; other `sat_*` pseudonyms in `docs/reports/PROPERTY-NET.md:100` may be names of Python property/test oracles rather than public function names, so **do not blindly replace** them.

The exact source evidence is in the [curated TSV](ROUND-122-WS1-API-IMPACT.tsv); the suggested source comment edit is **NOT APPLIED**. Additional misleading `sat_*` references in historical notes should be handled by an explicitly scoped documentation correction, not confused with today's proposed English naming sweep.

**PASS:** all 24 actual library files inspected for exported names; 92-doc tracked corpus scanned; 31 public-name/reference lines curated with safe modes. **NOT RUN - no toolchain:** renaming compiled APIs/guard/Windows; no source or docs mutation.
