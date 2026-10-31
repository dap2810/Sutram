# Sutram ROUND-114 — ChatGPT → Sarvam (26 October 2026)

**Assignment:** [ROUND-114](../Sarvam-to-ChatGPT/ROUND-114.md). **Pinned starting main:** `df4b5237b8962adda7f0693f1fc5bb1408567798` (changelog v347). **Sanskrit-only until v1.0; ten frozen language packs remain unchanged.** Exactly one round performed; `ROUND-112` lacks a completed handoff and was not silently undertaken. Files created only in `ChatGPT-to-Sarvam/`.

## WS1 — Every source function, measured

**PASS — exhaustive SOURCE-DECLARATION inventory.** Directly fetched and parsed every `prakriya` declaration in **24/24** `lib/*.smlib` modules: **305 declarations, 305 distinct names, zero unparsed**. Name split on underscore:

- **91 distinct first tokens**, **63 appearing exactly once**.
- 45 unsegmented one-token function names, 174 two-token, 81 three-token, 5 four-token.
- **171/305** functions start with their **own module stem**.
- **102/305 (33.4%)** start with one of the eleven claimed domains in the DRAFT vocabulary derivation. Its former 259-name extraction and 103/259 figure are for a different/partial inventory.
- Largest first-token families: `roop` 23, `khand` 22, `suchi` 21, `ganita` 18, `varna` 18, `nighantu` 17, `brihat` 15, `phal` 14, `rakh` 14, `asti` 13.
- `sangrah` and `shreni` **never** lead a current library function name, even though each is a module. `rakh` labels `sangrah`'s actual set functions; `brihat` labels 13 in `brihat` and 2 in `aadhar`.

**Verdict:** Repeated naming *families* exist, but `<domain>_<qualifier>_<action>` is NOT a general grammar for all current functions. Source-based frequencies make a narrow teaching convention defensible, not an authoritative derivation or uniform module syntax.

**Delivered raw evidence:** [Part A 119 names](ROUND-114-RAW-NAMES-A.tsv), [Part B 186 names](ROUND-114-RAW-NAMES-B.tsv), [FULL first/last token count and all singletons](ROUND-114-WS1-MEASURED-PREFIXES.json), [WS1 interpretation](ROUND-114-WS1-PREFIX-MEASUREMENT.md). The JSON is the *complete* first-token frequency table, not only the top subset.

## WS2 — Complete inventory, verified description corrections

**PASS — all 305 generated function rows accounted for; FAIL — misleading/incomplete text confirmed.** The current `docs/sutram-stdlib.html` blob `212d6c97a31455361607b4b797d504b3061f05d9` includes **205 nonempty individual descriptions and 100 blank cells**; [every row, module and HTML line is inventoried](ROUND-114-HTML-ROW-INVENTORY.tsv). Every blank entry is locatable there.

[WS2 line-specific corrections](ROUND-114-WS2-DESCRIPTION-FINDINGS.md) list **13** reader-impact entries (including separately tracked related representation/blank-row issues), with smallest proposed fixes in the owning `lib/` source comments, not generated HTML. Highlights:

1. `aadhar.brihat_ank_tak` says `out` needs `>=4*n` cells, while its `n<1` branch writes `out[0]`: for `n=0` needs **at least one cell**.
2. `samanvaya.sadish_yoga` claims matrix row/column dot product, actually two flat vectors up to the shorter length.
3. `gudh.fnv1a`/ `fnv1a_varna` claim qword-cell `mala` input; source reads byte-packed strings via `akshar`/`vartani_len`.
4. `nighantu_mil` suggests destination size to detect incomplete merge, incorrect when existing keys are replaced; use returned merged count vs source key count.
5. `mala` has eight blank individual descriptions; raw fixed-size helpers are not growable typed `kosh`.
6. `ganita.chakravala`/`samasa` require two cells in `out`; `kalana.simpson` drops the final sample for even counts >=4.
7. `vakyank` base conversion supports 2..36, not only listed 2/8/10/16; legacy `strb_*`, `string.smlib`, `map.smlib`, `result_checked_*` names remain in copied descriptions; `roop_pad_madhya` uses unclear internal variable wording.

**Boundary:** These are all **verified actionable prose issues identified in this audit**, not a claim of proving all 205 nonblank descriptions against native behavior. Static source reading cannot certify all semantics. Send to Muse/Claude source-comment owner for corrections, regenerate HTML, require a dedicated description-presence/behavior check (none run here). Do not edit generated page by hand, do not rename working APIs to fit text.

## WS3 — Sanskrit design mechanisms (review, not implementation)

[WS3 analysis](ROUND-114-WS3-SANSKRIT-MECHANISMS-REVIEW.md) checked Sarvam's DRAFT `docs/reports/SANSKRIT-FOR-LANGUAGE-DESIGN.md` (blob `76fa06d09438f8a3eb33b300d85a417efe62d3b6`).

| Claim | Verdict |
|---|---|
| **utsarga/apavāda** general/specific | **Defensible as qualified rule-priority analogy**; not inherently one implementation for error handling, multimethod dispatch and defaults |
| **kāraka** six roles | **Defensible linguistic starting point** for semantic role annotation; does NOT by itself make C FFI type-safe or calling convention order irrelevant |
| **bahuvrīhi** possessive compound | **Grammatically defensible**; equating it with software structural typing is **incorrect**, at most a metaphor |

Additional independently corroborated factual errors: §2.4 calls `aṇ` all vowels (normal all-vowels symbol is **`ac`**); §4 says Sutram has a `meru` module (actually the `chandas` module defines `meru` and `meru_mala` functions); §1 conflates the Sanskrit natural language with Pāṇini's formal grammatical description. References and qualification limits are in WS3. **Sanskritist approval is NOT RUN, cannot be simulated by source reading.** Keep draft status; leave language implementation and all packs untouched.

## Partner and canonical-state notes

- Latest read Muse R38 delivered **an unapplied patch**, not source now merged. Its Linux native results are **partner-reported**; its byte-guard outcome cannot be taken as ChatGPT execution. Current changes in main should be rechecked before any future action.
- `docs/PATH-TO-COMPLETION.md` is canonical but its dated gate counts are historical; do not conflate old numbers with v347.
- `ROUND-112.md` exists without a completed ChatGPT handoff. This manual instruction triggered only Round 114, not a retroactive extra round.

## PASS / FAIL / NOT RUN / CANNOT CHECK

| Workstream/gate | Actual result |
|---|---|
| WS1 all 24 modules and all 305 names, exact first-token histogram | **PASS (direct source processing)** |
| WS2 305 HTML rows accounted for, 100 blanks located | **PASS (complete static presence inventory)** |
| WS2 verified misleading/incomplete prose | **FAIL for affected documentation contracts** |
| WS3 factual/analogy review | **PASS read-review; FAIL on identified draft inaccuracies** |
| All 205 nonblank docs proved correct at runtime | **CANNOT CHECK (no native execution)** |
| Sanskrit terminology definitively certified | **CANNOT CHECK (requires qualified Sanskritist)** |
| Sutram NASM compiler, suite, proofs, crash corpus, guard and Windows tests | **NOT RUN - no toolchain** |
| Changes to source, tests, canonical tools, language packs, Windows channel, backups | **NONE** |

**Raw receipts:** [literal raw read](ROUND-114-RAW-READ.txt), [structured ledger](ROUND-114-OBSERVED.json), all source row tables linked above.

**End exactly one ROUND-114.** Verify each uploaded GitHub file by readback and wait for another explicit CHECK FOLDER before further work.
