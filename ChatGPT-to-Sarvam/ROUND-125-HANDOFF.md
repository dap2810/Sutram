# Sutram — ROUND 125 complete lexical read-side handoff (28 October 2026)

**Issued:** [`Sarvam-to-ChatGPT/ROUND-125.md`](../Sarvam-to-ChatGPT/ROUND-125.md), Git blob `aa4f327a192f504138bca18c34d91907e5810f21`.
**Pinned starting main:** `5059e61c6d4058727a0a8a70767b82c624f8c047`.
**Requested role:** dictionary/lexicography and source-body sense verification, **not** compiler or API implementation.
**Language scope:** Sanskrit only until v1.0; frozen translations, compiler source, `docs/`, `lib/`, `tests/`, `backups/` and `Windows-to-Sarvam/` not modified by ChatGPT.

## TOP SHORT LIST — reject, change, unsafe KEEP

Read [`ROUND-125-REJECT-CHANGE-KEEP.md`](ROUND-125-REJECT-CHANGE-KEEP.md) **first**. Especially reject **`kosh_purva_yuj`** (enqueue actually appends at rear), **`kosh_shodh`** (clear does not erase), **`samanvaya_akar`** (loses NOT-fit behavior), **`sankhya_bindu`** (a point is not the dot-product), **`abhigyan`** for an identity matrix, **`chinha`** for trace, and **`pravan_dwi`** for the second derivative. `chay` **is real Sanskrit for heap/pile**, so its existing stack prefix must not be rejected as non-Sanskrit. The project should review questionable KEEP rows, notably `janchit`, `pratilip`, `pad`, `tak`, `krama`, `guna`, `bhavana`, `dasham`, and `vitti`; these are concerns about grammatical precision or semantic metaphor, **not authorization to change settled keywords**.

## Main deliverable (required exact columns)

[`ROUND-125-VOCAB-VERDICT.tsv`](ROUND-125-VOCAB-VERDICT.tsv) contains **228 full rows, 8 tab-separated columns**:

`name | english | real_word(Y/N) | dictionary_form | meaning | sense_fits(PASS/FAIL) | better_word | reason`

**Coverage:** all **156 expanded source entries** across sections 1–6 of `docs/vocabulary/VOCABULARY-TABLE.md`, plus **72 individually reviewed alternative/focus rows**. This is **228 judgments**, not 228 independently dictionary-attested headwords: duplicate proposed/current entries intentionally retain contextual classifications. Dictionary-form fields explicitly provide noun/root/compound members. **173 Y / 55 N**, **147 PASS / 81 FAIL** after final reconciliation. These are per-row counts **including alternative names**, not counts of compiler bugs, accepted changes, or the number of Sanskrit dictionary headwords.

`docs/vocabulary/VOCABULARY-TABLE.md` has **42 rows under a heading claiming 38 keywords**, **10 rows under a heading claiming eight Devanagari mismatches**, 25 builtin rows, 24 modules, 31 stems, and 22 source rows of English leftovers (24 when two two-name rows are split). Section 7 is an aggregate scorecard and has no additional names to classify; its counts should not be repeated without reconciliation. The table mixes compiler keywords with ordinary builtins; do not equate the source heading with a parser keyword-ID count.

## Requested hard cases — definitive sense verdicts

| Proposed name | Word? | Sense vs implementation |
|---|---|---|
| `karna_yog` (matrix trace) | Y, कर्ण + योग | **PASS**: sum of mathematical diagonal, verified in `samanvaya.smlib:110-118` |
| `tadatmya` / `ekatva` (identity matrix) | Y / Y | **FAIL** as matrix labels: abstract identity/oneness; prefer `ekaka_matrika` after linguistic signoff |
| `asti_ksham` (available capacity) | Y, `asti` + √क्षम | **FAIL**: ability/tolerance not an unused-slots count; better `asti_avakash` |
| `madhava_jya`, `madhava_kotijya` | Y / Y | **PASS** genuine sine/cosine terms of Indian mathematics |
| `madhava_chapsparsh` | N as a verified name | **FAIL**: arc + touch not established for inverse tangent |
| `gun_tray` | Y components, nonidiomatic compound | **FAIL** strict sense: actual routine multiplies **three arguments**; `traya` is a noun for a triad, not the usual `tri-` compound prefix |
| `kalana_paravalay` (Simpson) | Y components | **FAIL**: parabola is too broad for Simpson's 1/3 rule, `simpson` may stay as proper method name |
| `kalana_samalamb` (trapezoid) | Y components | **PASS**: samalamba is an attested trapezoid, source sums trapezoid areas |
| `anukram_khip_asht` / `...ashtak` | Y constituents | **FAIL** name scope: encoded buffer is **8-byte length + n-byte payload**, not an eight-byte-only item |
| `chiti_khip` / `chiti_apanay` | Y; चिति heap/pile | **PASS**, but `chay` चय is already real and suitable; keep current names unless an owner-approved reason exists |
| `prati` for return | Y prefix | **PASS as owner's technical convention. Do not reopen decision** |
| `nivartan` for return | Y, निवर्तन | **PASS** noun meaning return/turning back; **r belongs** to root `ni-√vṛt` |

## Evidence and limits

1. [`ROUND-125-DICTIONARY-EVIDENCE.md`](ROUND-125-DICTIONARY-EVIDENCE.md) contains **12 explicit linked dictionary/historical references**, raw lexical senses, method and scope limits. These establish the high-risk disputes (`chay`, `chiti`, `karna`, `tadatmya`, `kshamata`, `nivartan`, `jya`, `kotijya`, `samalamb`, `ashtak`, `ganita`, `ganan`). **Do not claim all 228 rows were individually searched in a dictionary; they were not.**
2. [`ROUND-125-SOURCE-RAW-READ.md`](ROUND-125-SOURCE-RAW-READ.md) contains **12 raw source-range receipts** with pinned Git blob IDs and original line numbers; actual code body decides the named behavior.
3. [`ROUND-125-OBSERVED.json`](ROUND-125-OBSERVED.json) contains counts and explicit status separation.
4. The shorter proposal file `docs/vocabulary/VOCABULARY-SHORT.md` was read but is overridden for the submitted review by the full `docs/vocabulary/VOCABULARY-TABLE.md` and by source bodies. Bad truncation rules in the short proposal (`purn`, `vip`, `nay` etc.) are **not accepted**.

**PASS:** pinned GitHub reads, TSV structural and coverage check, dictionary spot-checks for high-risk names, source-body semantics read and identified.

**NOT RUN - no toolchain:** native Sutram compiler, library runtime, regression tests, byte guard or installer acceptance.

**NOT APPLIED:** all proposed API/keyword changes. No partner-reported testing is attributed to ChatGPT. These are documented assessments awaiting owner/Sanskritist confirmation and later implementation by designated authors.

Exactly one assignment round, R125, processed. Upload all files only to `ChatGPT-to-Sarvam/` and stop.
