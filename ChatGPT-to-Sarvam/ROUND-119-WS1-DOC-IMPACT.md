# Sutram ROUND-119 WS1 — exhaustive current text-document rename impact

**Pinned main:** `307520c1492cf73b4f5e7cb6e15b3b377d3e5b53`; the compiler source on this pin still has `vartani_len`, `vartani_cmp`, `vartani_cp` registered and **zero** occurrences of their three proposed replacements. The rename is **PLANNED, NOT OBSERVED INSTALLED** on this pin. Do not apply documentation renames ahead of the actual compiler/API change unless the wording is explicitly prospective.

**Whole repository tree audit:** `git/trees/<pin>?recursive=1` returned 4,079 blob paths (untruncated); the text-document scan covered **154** `.md`, `.html`, `.htm`, `.txt`, `.rst`, `.adoc` files **outside historical partner outbox/frozen backup folders**. All 154 were fetched and checked for the exact three `vartani_*` identifiers. **32 matching physical lines across eight files**, divided into 10 current-guide lines, three generated HTML lines, three already-correct vocabulary mapping rows, and 16 historical/snapshot lines. [Every scanned path and Git blob](ROUND-119-WS1-TEXT-SCAN-MANIFEST.tsv). [Every matching source line, exact OLD / conditional NEW and mode](ROUND-119-WS1-DOC-RENAME-EXACT.tsv).

## 1. Direct edits ONLY AFTER source rename is accepted (10 lines in 3 current-doc files)

The following proposed **complete-line exact replacements** can be applied by Sarvam after the rename is installed. The OLD text is copied exactly from the pinned source. **Do not modify docs before verifying that each OLD line still appears exactly once**, and preserve the unchanged rest of the line.

| Source file:line | OLD line exact | NEW line exact, conditional on compiler rename |
|---|---|---|
| docs/LANGUAGE-REFERENCE.md:107 | \| \`vartani_len\` \| varna length \| | \| \`vartani_aayam\` \| varna length \| |
| docs/LANGUAGE-REFERENCE.md:108 | \| \`vartani_cmp\` \| varna compare \| | \| \`vartani_tul\` \| varna compare \| |
| docs/LANGUAGE-REFERENCE.md:110 | \| \`vartani_cp\` \| varna copy \| | \| \`vartani_pratilip\` \| varna copy \| |
| docs/R54-BUILTIN-BOUNDS.md:27 | \| \`vartani_cp\` \| 2 \| Copies bytes through first NUL from source to destination; destination must fit **strlen(source)+1**; no runtime capacity guard \| | \| \`vartani_pratilip\` \| 2 \| Copies bytes through first NUL from source to destination; destination must fit **strlen(source)+1**; no runtime capacity guard \| |
| docs/R54-BUILTIN-BOUNDS.md:29 | \| \`vartani_len\` \| 1 \| Scans until NUL: the address must point into a readable, NUL-terminated allocation \| | \| \`vartani_aayam\` \| 1 \| Scans until NUL: the address must point into a readable, NUL-terminated allocation \| |
| docs/R54-BUILTIN-BOUNDS.md:30 | \| \`vartani_cmp\` \| 2 \| Scans both NUL-terminated operands; neither length nor allocation validated \| | \| \`vartani_tul\` \| 2 \| Scans both NUL-terminated operands; neither length nor allocation validated \| |
| docs/R54-BUILTIN-BOUNDS.md:32 | \| \`vartani_cp\`, \`vartani_cat\` \| 2 \| Byte-oriented operations, **not** qword-array \`buf[i]\` semantics \| | \| \`vartani_pratilip\`, \`vartani_cat\` \| 2 \| Byte-oriented operations, **not** qword-array \`buf[i]\` semantics \| |
| docs/R54-BUILTIN-BOUNDS.md:38 | \| \`likha_fmt\`, \`vartani_cmp\` \| 2 \| Formatter/byte string comparison, no buffer capacity checking \| | \| \`likha_fmt\`, \`vartani_tul\` \| 2 \| Formatter/byte string comparison, no buffer capacity checking \| |
| docs/R54-BUILTIN-BOUNDS.md:43 | Other names: \`char_code\` accepts 1 or 2; \`likha\` accepts 1, 2 or 3; \`dvaram\` accepts 2 or 3; \`vartani_cat\` accepts 2; \`vartani_cmp\` accepts 2; \`vartani_cp\` accepts 2. All other registered builtin IDs have the exact arity shown above. | Other names: \`char_code\` accepts 1 or 2; \`likha\` accepts 1, 2 or 3; \`dvaram\` accepts 2 or 3; \`vartani_cat\` accepts 2; \`vartani_tul\` accepts 2; \`vartani_pratilip\` accepts 2. All other registered builtin IDs have the exact arity shown above. |
| docs/STRING-BYTE-PARITY.md:64 | **The length-function rule.** \`varna_maap\` / \`khand_maap\` / \`vartani_len\` | **The length-function rule.** \`varna_maap\` / \`khand_maap\` / \`vartani_aayam\` |

## 2. Regenerate the standard-library HTML (3 physical rows, do NOT manually replace)

The generated `docs/sutram-stdlib.html` still derives these comments from `lib/gudh.smlib`, `lib/khand.smlib`, `lib/varna.smlib`. They require **source comment updates in the same authorized compiler/library rename**, then regeneration. The TSV contains full OLD and projected NEW content of every affected HTML line, but is **NOT an instruction to hand-edit generated HTML**.

| Generated file and line | Old builtin token(s) | Target token(s) |
|---|---|---|
| `docs/sutram-stdlib.html:165` | `vartani_len` | `vartani_aayam` |
| `docs/sutram-stdlib.html:179` | `vartani_len, vartani_len` | `vartani_aayam, vartani_aayam` |
| `docs/sutram-stdlib.html:443` | `vartani_len` | `vartani_aayam` |

**Supporting source comment locations at pin:** `lib/gudh.smlib:28`, `lib/khand.smlib:11,24`, `lib/varna.smlib:4`. **Caller code** also uses old `vartani_len` at `lib/gudh.smlib:30`, `lib/khand.smlib:99`, `lib/varna.smlib:19,55,69,80,90,113,114`. These are source edits for Claude, NOT documentation-only changes and NOT in this replacement TSV. Changing builtins without updating their library callers can break compilation; those must be verified on the exact candidate.

## 3. Curriculum already contains all three new words — DO NOT DUPLICATE

`docs/VOCABULARY-DERIVATION.md:75-77` already presents `vartani_len → vartani_aayam` (आयाम), `vartani_cmp → vartani_tul` (तुल् / तुलना), `vartani_cp → vartani_pratilip` (प्रतिलिपि), with appropriate short glosses. These **three exact lines should remain**; they are a documented prospective mapping, not proof of actual compiler rename. The WS2 TSV explicitly marks them `ALREADY_PRESENT_NOOP`.

## 4. Historical/audit records — KEEP original names (16 matches)

The following mentions describe old releases, known prior defects or archived compiler output. Blind replacements would falsify historical evidence, so **NEW = OLD** in the exhaustive TSV. A separate *current API migration note* is permitted, but the recorded old identifiers must not be rewritten in place.

| Historical file and line | Old name(s) appearing | Recommendation |
|---|---|---|
| `compiler/verified_snapshots/FG2_R30_verified.asm.txt:626` | vartani_len | Preserve old recorded API spelling |
| `compiler/verified_snapshots/FG2_R30_verified.asm.txt:627` | vartani_cmp | Preserve old recorded API spelling |
| `compiler/verified_snapshots/FG2_R30_verified.asm.txt:647` | vartani_cp | Preserve old recorded API spelling |
| `compiler/verified_snapshots/FG2_R30_verified.asm.txt:10035` | vartani_len | Preserve old recorded API spelling |
| `compiler/verified_snapshots/FG2_R30_verified.asm.txt:10091` | vartani_cmp | Preserve old recorded API spelling |
| `compiler/verified_snapshots/FG2_R30_verified.asm.txt:10825` | vartani_cp | Preserve old recorded API spelling |
| `docs/CHANGELOG.md:8` | vartani_len | Preserve old recorded API spelling |
| `docs/CHANGELOG.md:9` | vartani_cmp | Preserve old recorded API spelling |
| `docs/CHANGELOG.md:10` | vartani_cp | Preserve old recorded API spelling |
| `docs/CHANGELOG.md:7523` | vartani_cp | Preserve old recorded API spelling |
| `docs/CHANGELOG.md:7703` | vartani_len | Preserve old recorded API spelling |
| `docs/CHANGELOG.md:7704` | vartani_cmp | Preserve old recorded API spelling |
| `docs/CHANGELOG.md:8775` | vartani_len | Preserve old recorded API spelling |
| `docs/R50-BYTE-PACKED-TEXT.md:5` | vartani_len, vartani_cmp, vartani_len, vartani_cmp | Preserve old recorded API spelling |
| `docs/R54-BUILTIN-BOUNDS.md:47` | vartani_cp | Preserve old recorded API spelling |
| `docs/R54-BUILTIN-BOUNDS.md:63` | vartani_cp | Preserve old recorded API spelling |

In particular, the top v363 `docs/CHANGELOG.md` mapping already includes the proposed target names and must remain an accurate history of the rename decision; the other changelog mentions document older actual behavior. `docs/R50-BYTE-PACKED-TEXT.md` describes R50-era code, and `docs/R54-BUILTIN-BOUNDS.md:47,63` describe what R54 changed. The verified compiler snapshot is immutable evidence, not living documentation.

## 5. Books and other docs with ZERO exact mentions

This scanned revision has **no exact `vartani_len`, `vartani_cmp`, or `vartani_cp` text** in `docs/sutram-book*.html`, `docs/sutram-stdlib-reference.html`, `docs/sutram-vocabulary.html`, root `README.md`, root `PROJECT-MASTER.md`, or other matched-text-negative entries in the manifest. No speculative edits should be invented for those files.

## Limits / status

This is a **complete search of the declared 154-file live text-document corpus**, not every historical collaboration report, binary, source file, or file in protected `backups/`. Current `src/`/`lib/` callers are reported as rename-integration hazards, without touching them. The compiler may move after this pin; **recheck HEAD and regenerate on the actual merged revision**.

**PASS** — 154/154 inspected UTF-8 text documents; 32 source lines with source Git blobs and full old/new content enumerated.  
**NOT RUN - no toolchain** — native Sutram, renamed builtin behavior, docs generator, Windows, regression and guard.  
**NOT APPLIED** — this is an authorized read-side proposal only; 0 protected writes.
