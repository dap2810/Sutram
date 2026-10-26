# Sutram Round 110 WS3 — Independent pre-rename vocabulary sweep (READ ONLY)

**Pinned main:** `cc69322c22b354296a3448aa3d1edf254ef319b5`, changelog v332, 26 October 2026 review. **Independent of Muse's upcoming R35 response:** no `Muse-to-Sarvam/round35` delivery was present at the latest check. The owner's `LANGUAGE-PRIORITY.md` requires Sanskrit-only development and frozen other language packs. No source, examples, docs outside this handoff, tests or tools changed.

**Scope actually read through the GitHub connector:** all **24** current `lib/*.smlib` files, all **238** `examples/**/*.sm` program files, the **13** `examples/lib/*.smlib` companion modules, and all **83** current `docs/` Markdown/HTML files (82 individually plus the versioned `docs/CHANGELOG.md`). Tree enumerated with GitHub recursive tree at the pinned SHA (non-truncated). Every read succeeded. Searched explicit **whole-token** old words in each line: `punaravartana`, `pratiyati`, `uddeshya`, `anytra`, `nishedha`, `parigrah`, `nishkriya`, `ayojan`, `srijana` and `pankti`, plus `meru_pankti` function identifier and code-quoted `to`. **Caveat:** bare English `to` is a common prose word, so it was deliberately not counted as a keyword defect without a lexer/code context; a future token-aware checker should handle it. This is a source-reading inventory, **NOT RUN - no toolchain** for any compiler/test execution.

## A. ALL CURRENT `lib/` hits — by actual source file/line

**Executable identifier — HIGH risk, owner assigned rename:**

| Source | Exact code | Classification |
|---|---|---|
| `lib/chandas.smlib:82` | `prakriya meru_pankti(a, n) {` | **Callable current API**, but the documented intended post-v166 name is `meru_mala`. Changing the declaration alone is a breaking API change for existing callers (e.g. `tests/stdlib/chandas_meru_pankti.sm`); requires approved migration and exact program/guard tests. **Muse R35 owns the code; ChatGPT does not edit it.** |

**Current `pankti` whole-word comments referring to array cells — 19 source lines in 11 modules:**

| Source module | Exact line(s) | Nature |
|---|---|---|
| `lib/aadhar.smlib` | **5, 15, 74** | Intermediate and input/output digit arrays |
| `lib/ganita.smlib` | **188** | One-cell status buffer |
| `lib/gudh.smlib` | **12, 28** | Character-code buffers in hash routines |
| `lib/nighantu.smlib` | **4** | Parallel arrays in map layout |
| `lib/phal.smlib` | **4** | Two-cell Result representation |
| `lib/roop.smlib` | **8** | Older string-to-cells comparison |
| `lib/sankhyiki.smlib` | **120** | Integer array used by a statistic |
| `lib/shreni.smlib` | **4** | In-place integer array |
| `lib/suchi.smlib` | **4, 33** | Qword elements and `ok` buffer |
| `lib/vakyank.smlib` | **6, 12, 81, 83, 235** | Numeric-character buffers and results |
| `lib/varna.smlib` | **127** | Integer character-code representation |
| **Total** | **19 comment lines / 11 modules** | `pankti` is old array spelling; `mala` is canonical current array keyword. These are documentation comments, not code-token syntax. |

**Other old keyword comments:**

| Source | Text | Classification |
|---|---|---|
| `lib/sadhan.smlib:4` | `# Usage: ayojan util` | **P0 copyable instruction:** old import keyword and obsolete module name. Current usage `yoj sadhan`. `lib/sadhan.smlib:1` also names former `util.smlib` (old module reference). |
| `lib/suchi.smlib:211` | `sorting a list meant \`ayojan sort\` plus a hand-written ...` | Historical wording inside a function comment. Not a current import instruction; label historical when generated. |

**Other requested pre-rename words:** no whole-word matches in the current 24 library sources for `punaravartana`, `pratiyati`, `uddeshya`, `anytra`, `nishedha`, `parigrah`, `nishkriya` or `srijana`. Do **not** mistake legitimate `meru_pankti` (a whole function identifier) for a stand-alone source-language keyword in other files. **`to` is not asserted absent** because ordinary English prose makes a naive whole-word count meaningless.

**Important correction to R109 source inventory:** the earlier list said 16 emitted comments. This new **independent whole-source lexical sweep** finds **19** (adds `ganita:188`, `sankhyiki:120` and `varna:127`). The older 16 covered only comments consumed by the existing generator; the larger 19 is the requested **entire lib source**, including comments not necessarily adjacent to function declarations. A raw scanner must distinguish these two scopes rather than treating the counts as contradictory.

## B. `examples/` — complete 238-program and 13 module sweep

The scan found **two `.sm` files with matching old words** (and **zero** hits among 13 companion `.smlib` files):

| File and line | Verbatim hit | Verdict |
|---|---|---|
| `examples/19_srijana_enum.sm:1` | `# Srijana (enum/constants) — Sanskrit for 'creation'` | **Comment/file title**, not active enum syntax. Actual source declares enums with current `ganana`, not `srijana`. Old term in filename is historical naming; do not rename goldens/paths gratuitously. |
| `examples/222_old_keyword_name.sm:1` | `# R4 golden: \`uddeshya\` was the keyword for \`continue\` before v157 ...` | Explicit **old-keyword negative test explanation**; retain. |
| `examples/222_old_keyword_name.sm:8` | `yadi (i == 2) { uddeshya }` | Intentional **compiler-rejection fixture**, not accidental usage. The comment says expected to FAIL to compile with undefined name/hint; never auto-rewrite to `agrim`, since that would destroy the negative test. |

No unexpected old `punaravartana/pratiyati/uddeshya/anytra/nishedha/parigrah/nishkriya/ayojan/srijana/pankti` tokens found in executable `examples/*.sm` in the pinned files apart from that **deliberate** `uddeshya` rejection case. This is a **source-text conclusion**, not native test acceptance.

## C. `docs/` — present mentions and why most are NOT migration work

All **83** `docs/` Markdown and HTML pages were inspected. The following non-CHANGELOG source locations matched the above old words; anything saying **diagnostic `pankti`** means *line number* and is NOT the array keyword.

| Document:line | Match | Context / classification |
|---|---|---|
| `docs/LANGUAGE-REFERENCE.md:242` | `pankti` | Example error message “`vyakaran dosh, pankti 3:5`”: **line number**, not an obsolete array keyword |
| `docs/NEGATIVE-CORPUS.md:24,27` | `pankti` | Error diagnostics: **line number**, preserve |
| `docs/R56-MODULE-GLOBALS.md:28` | `ayojan` | Older R56 technical snapshot: textual inclusion named by pre-rename spelling. **Historical**, not current CLI instruction |
| `docs/R65-DEVANAGARI-SURFACE.md:3` | `pankti`, `srijana`, `nishkriya`, `parigrah` | Historical R65 language-pack statement. **Do not silently rewrite dated evidence** or touch frozen pack; flag for as-of label if cited as current. |
| `docs/R67-SOURCE-REVIEW.md:109` | `nishkriya` | Historical inline-assembly wording; do not edit as current grammar |
| `docs/R71-MEMORY-BOUNDARY.md:29` | `nishkriya` | Bounded R71 experiment description; historical |
| `docs/R71-MODULES.md:9` | `ayojan` | Older R71 supplement scope, explicitly not a full module compiler. Historical |
| `docs/sutram-book-english.html:218` | `Pankti` | Etymological exposition (“a row”), juxtaposed with **current `mala` declaration**; **not an executable obsolete keyword usage** |
| `docs/sutram-book-english.html:308` | `pankti` | Diagnostic line-number example |
| `docs/sutram-book-gujarati.html:286`, `...hindi.html:316`, `...sanskrit.html:276`, `...tamil.html:292`, `...telugu.html:315` | `pankti` | Diagnostic line-number examples. Frozen non-Sanskrit books not in active development; read only. |

**`docs/CHANGELOG.md`** (Git blob `94104973ff389c1e36dcf6869c82076857762331`): **75 source lines** include at least one named old-word token. This is **versioned project history, not an active grammar source**. Do not replace old words in dated change records to make a superficial count zero.

**Contextual `to`:** bare English “to” appears throughout normal prose and is intentionally excluded from defect totals. Explicit code-fenced old-range examples need a parser-aware audit; a naive `\bto\b` match would generate hundreds of unrelated prose hits. The checked `examples/11_forloop.sm` uses canonical `tak`.

## Recommended action, with owner/migration discipline

1. **Muse R35**: decide/execute the explicitly authorized **`meru_pankti` → `meru_mala`** public symbol rename as a **breaking ABI/API change**. Record callers/negative tests/guard. An alias or migration rule must be owner-approved; simply changing docs does not make existing calls work.
2. Correct *active copyable instructions* (`sadhan` header `Usage: ayojan util` → `yoj sadhan`) before regeneration. Review old source comments for whole-word `pankti`→`mala` where they mean the **language array keyword**; do not alter diagnostic “line” usage, proper names or intentional historical narratives.
3. Preserve `examples/222_old_keyword_name.sm` as a negative regression; preserve dated R56/R65/R67/R71 and CHANGELOG history. Give current guides links to the new grammar rather than mutating snapshots.
4. Regenerate `docs/sutram-stdlib.html` only AFTER library source/comments are reviewed, then check every public callable name against current module declarations, exact source SHA, and native behavior. Do not use a broad search/replace inside function identifiers.
5. Require the actual canonical NASM compiler, test suite and real Windows acceptance to be run by a capable owner/Muse/Windows channel. **This read side did not execute any of them.**

## PASS / FAIL / NOT RUN

- **PASS — independent pinned GitHub source reads:** 24/24 `lib/*.smlib`, 238/238 example `.sm`, 13/13 example `.smlib`, 83/83 `docs/` Markdown/HTML files.
- **PASS — classify matches** as callable identifier / obsolete copyable syntax / commented terminology / intentional negative fixture / historical / diagnostic.
- **FAIL (documentation/source contract on pinned tree):** `meru_mala` is documented but `meru_pankti` is the actual callable function until Muse's authorized migration; `Usage: ayojan util` is a wrong active instruction.
- **NOT RUN - no toolchain:** native `.sm` compiler rejection or success, proposed rename regression guard, docs snippet execution, full suites, Windows and benchmark.
- **Scope limitation:** no complete lexer-aware check of unquoted English `to` and no execution. Do not claim these were proven safe or absent.
- **No files edited** in `lib/`, `examples/`, `docs/` outside this new handoff, `src/`, `tests/`, `tools/`, Windows channel, frozen pack or `backups/`.
