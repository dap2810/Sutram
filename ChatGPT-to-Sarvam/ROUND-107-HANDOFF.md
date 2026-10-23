# Sutram ROUND-107 — ChatGPT → Sarvam (23 October 2026)

**Assignment:** `Sarvam-to-ChatGPT/ROUND-107.md`. **Initial pinned live main:** `fd48619526f6dde6c2b21c7b37ee1bf56f2c505f`, changelog v322, native main compiler v246 in canonical dated status. **Read side ONLY.** The governing `LANGUAGE-PRIORITY.md` says Sanskrit-only development until v1.0; all ten other language packs are frozen. `docs/PATH-TO-COMPLETION.md` is the owner's canonical release order, even when its as-of counts are older than main. **No code, tool, test, goldens, Windows-channel, backup or pack edits.**

## WS1 — What 32, 28 and 52 *actually* count

[**Exact source-derived keyword analysis**](ROUND-107-WS1-KEYWORD-DEFINITION.md) and [**raw read-side counts**](ROUND-107-RAW-SOURCE-COUNTS.txt).

The native source `src/sutram_compiler.asm:145–176` declares **32 `KW_*` IDs**, while `kw_table` contains **31 unique direct `TOK_KEYWORD` IDs** (47 table rows including 16 Devanagari spelling duplicates). The extra ID is `KW_ATHA`, a **contextual loop-range word `tak`** recognized by its own language-pack loader path rather than the direct table. This makes “**32 core keyword IDs, including contextual tak**” a defensible public convention, or “31 ordinary lexer keywords plus contextual tak” for extra clarity.

The Sanskrit language pack actually has **58 distinct Devanagari left-hand spellings**: **35 primary rows + 18 R65 builtin aliases + 5 R66 abbreviations/extra alias**. Because `vitti/prati/prakriya` map twice, `likha` three times and `shabda` twice, those **58 spellings map to 52 distinct Latin targets**. The 52 include **callable builtins** such as `likha`, `grahan` and `shabda`, *not* 52 reserved keyword IDs. Compiler `bn_table` and the loader's `lookup_builtin` fallback prove the vocabulary categories differ.

The scorecard's **28** is **plausibly a historical keyword count before R23 `vibhag` and R25 `siddhi/dosh/prasar` added four IDs** (28+4=32). **This explanation has NOT been proven against the historical scorecard source commit**; label it plausible until Muse R32 confirms the old snapshot. The scorecard line 48 now says 32; line 237 still says 28. **Owner's decision required:** prefer **32 keyword IDs (31 ordinary+1 contextual)** for the public line; publish **52 unique pack target names** and **58 Sanskrit script spellings** separately, with those definitions. Do not treat Sanskrit counts as permission to develop frozen non-Sanskrit packs.

**Source-read verification:** 19/19 read/presence/count predicates PASS, 0 FAIL. **NOT RUN - no toolchain:** actual lexer/compiler/native pack tests. Muse Round 32 separately owns the executed/stale-claim tool and keyword measurement.

## WS2 — Which R106 prose claims have actually been fixed?

[**Current-tree status list: APPLIED / PARTIAL / STILL OPEN**](ROUND-107-WS2-P0-RECONCILIATION.md). Round 106 was based on v318; Sarvam now applied more fixes through v322. I re-read the current files rather than reissuing the full old table.

**APPLIED — do not repeat:** README's obsolete no-object/no-function-values/Windows never status; roadmap's Windows/objects gap; scorecard's **line 206** functional/methods/slices gap; Master's **performance verdict** at v321 now correctly says **two wins, two losses and one tie**, including Zig's 120 KB RSS advantage and shared no-runtime status.

**PARTIAL — finish the same paragraph/file:** `PROJECT-OVERVIEW.md:159–160` now begins with the truth that separate compilation, first-class functions and methods exist but still ends with the opposite **“No first-class functions. No collections beyond kosh and mala.”** The scorecard line 206 acknowledges function values but line 150 still says **“no C FFI.”** Apply a complete edit, not another prefixed sentence.

**STILL OPEN — priority current claims:** `PROJECT-OVERVIEW.md:153–155` denies real Windows GUI/installer execution; `PROJECT-MASTER.md` still has old functional/method/slice/Windows/FFI/fuzz statuses, old parallel Gujarati/Hindi/Sanskrit plan and old authoritative roadmap pointer; `docs/sutram-design-parameters.html` “Today” rows deny functions, methods, slices, layers, separate compile, Windows run and FFI; `docs/sutram-project-status.html` calls Windows unverified, installer untested, no FFI and stale waiting tasks; `docs/sutram-scorecard.html` still denies FFI and has stale module/test counts. [WS2](ROUND-107-WS2-P0-RECONCILIATION.md) gives exact line refs and the shortest corrections. **Master's performance is CLOSED**; its other prose remains. Preserve clear differences between **Linux-main** and **Windows v245 review-branch** status, tested Windows snapshots and current release acceptance.

The canonical `docs/PATH-TO-COMPLETION.md` is as-of v315 and prints 25 computed allocations/6 bounded/19 exempt; R39 later reported 26/13/13. This is a **stale snapshot**, not falsified historical data. Only replace canonical measured numbers after Sarvam's new exact fresh-clone check.

## WS3 — Implement a sequence, not one giant spec rewrite

[**The order to apply the R106 spec maintenance list**](ROUND-107-WS3-SPEC-MAINTENANCE-ORDER.md):

1. **First:** fix still-present P0 product prose under Sanskrit-only owner priority.
2. **Second:** create small `docs/SPEC-STATUS.md` as a source-pinned **current-main / unmerged tested branch / historical design / future proposal** index. Make Linux `--ffi` v1/v2 and `SUTRAMO1` clearly different from Windows branch v245 `SUTRAMO2` and future v3 `cstr_ro`.
3. **Third:** refresh the current `docs/OBJECT-FORMAT.md`/FFI link: shipped `--ffi` (R97 `--ffi-sidecar` was *proposed*), R98 zero-ELF-relocation first milestone expanded by R33 bounded internal PC32; Windows FFI only accepted on its stated branch/owner test.
4. **Fourth:** annotate R97/R98 and R100 historical specs in the **index** without altering original raw evidence; honor R101's correction that checked `cstr_ro` is a **future v3**, never silent accepted v2.
5. **Fifth:** link R104's “validity before address formation” rule into public overflow/boundary docs. R39's actual **13 exact-expression exemptions** have constructor invariants, not global pointer-safety proof.
6. **Sixth, after owner Windows merge/reacceptance:** update Windows technical status. Keep the R100 Microsoft x64 ABI rules; leave R102 literal-only `cstr_ro` **DRAFT/NOT IMPLEMENTED**, pending new native tests.
7. **Last, after Sanskrit v1.0:** only then consolidate the R97 seven-workload benchmark target with R98 Gate0 preflight, explicitly **NOT RUN**, and resume frozen language packs afterward as owner directs.

The owner, Muse and Windows channel retain their separate scopes. A new Sanskrit-only `docs/SPEC-STATUS.md` **index** is the best small consolidation; rewriting the historical R97–R104 files into one large supposedly accepted spec would erase version/target boundaries.

## Independent partner and Windows readback

Latest `Windows-to-Sarvam/WIN-FFI-2026-10-21.md` was **READ**, unchanged: reports prior owner-run **21/21 native Windows FFI** on v245 branch and explicitly notes installer not rebuilt for it. It is **not** a new R107 native test or proof of current Windows release acceptance. `Muse-to-Sarvam/` did **not** yet contain R32 when last checked; our reading predates its independent result. We did not edit the Windows channel, Muse's tool or `backups/`.

## Actual result and truth table

| Check | Outcome |
|---|---|
| Directly count compiler keyword-ID/table and Sanskrit map entries | **PASS — source reading; 32 IDs, 31 direct IDs, 52 distinct targets, 58 native spellings** |
| Explain 28 historical count | **PLAUSIBLE ONLY** pending exact old source pin |
| Recheck v322 prose claim fixes and remaining contradictions | **PASS — current source audit** |
| Order versioned specification changes by priority and owner | **PASS — read-only design** |
| Pinned-source raw checks | **19 PASS / 0 FAIL** (not executable tests) |
| Native Sutram compiler or pack lexer tests | **NOT RUN - no toolchain** |
| Regression/gates/library proofs/crash corpus/fuzz | **NOT RUN - no toolchain** |
| Windows FFI/installer/GUI/ABI acceptance | **NOT RUN - no toolchain** |
| Benchmarks, historical old-keyword-version execution | **NOT RUN - no toolchain** |
| Edited `src/`, `lib/`, `tests/`, `tools/`, language packs, `Windows-to-Sarvam/` or `backups/` | **NONE** |

Machine-readable pinned source record: [ROUND-107-OBSERVED.json](ROUND-107-OBSERVED.json). Raw source-read lines: [ROUND-107-RAW-SOURCE-COUNTS.txt](ROUND-107-RAW-SOURCE-COUNTS.txt).

**STOP after this manual round.** Await owner's next `CHECK FOLDER` before Round 108.
