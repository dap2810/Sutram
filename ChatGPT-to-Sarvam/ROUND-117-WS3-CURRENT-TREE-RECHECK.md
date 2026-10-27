# Sutram ROUND-117 WS3 — R116 exact replacements rechecked against compiler v248 main

**Live read pin:** `fd02405aad986001c451ee5c5decb91346c7bb53` (changelog v357, compiler source contains v248). **Input:** `ChatGPT-to-Sarvam/ROUND-116-WS1-EXACT-REPLACEMENTS.tsv` SHA `38eca6bbf6cadb03827cc409a3f30f16bef058ff`. Latest instructions `Sarvam-to-ChatGPT/ROUND-117.md`.

## Source-side determination: ALL APPLIED

| Status | Number |
|---|---:|
| R116 exact proposed lines | **35** |
| Authorized old lines still found | **0** |
| Expected replacement lines found exactly once | **35** |
| Still pending | **0** |
| Drifted/ambiguous | **0** |
| Distinct modified library modules | **15** |

Every exact old and new string was rechecked against its **current** source file, not just the v356 changelog. The source files retain the original proposed line positions in all 35 matches. The complete per-line audit, including **current Git blob SHA, original line, current line, number of old/new matches and APPLIED verdict**, is in [Part A: first 20 lines](ROUND-117-WS3-RECHECK-A.tsv) and [Part B: final 15](ROUND-117-WS3-RECHECK-B.tsv).

**Do not reissue any of the 35 replacements to Sarvam**; they are applied. Reapplying old replacements via exact match should fail, and a broad new search-and-replace would risk damaging valid source.

## Newly verified divergence: generated documentation still reproduces prior comments

**`docs/sutram-stdlib.html` remains old blob `212d6c97a31455361607b4b797d504b3061f05d9`**, despite 15 `lib/*.smlib` blobs having changed. Using the same description-extraction logic as `tools/gen_stdlib_ref.py` to compare the current source comments against the committed HTML, for the **15 affected modules**:

- **18 function-row description differences**, in 221 declarations inspected across those modules. Counts: `aadhar` 1, `brihat` 2, `ganita` 2, `gudh` 1, `kalana` 1, `nighantu` 1, `roop` 1, `samanvaya` 1, `suchi` 6, `vakyank` 2. In `khand`, `mala`, `phal`, `sangrah`, `varna`, the edits affect a module header rather than a per-function description.
- **7 module-header description differences**: `gudh`, `khand`, `mala`, `nighantu`, `phal`, `sangrah`, `varna`.
- Thus **25 changed generated content regions (18 rows + 7 headers)** are not yet reflected in HTML. These are **source-vs-generated-document text differences**, not necessarily 25 independent defects.
- Direct example 1: `lib/vakyank.smlib:81` now comments `varna_tak_ank(buf, n, ok)`, but HTML:436 **still says `varna_tak_ank(buf, n)` in the description cell** while its function column correctly has `ok`.
- Direct example 2: `lib/samanvaya.smlib:134` now describes `sadish_yoga` as a two-flat-vector shorter-length dot product, while HTML:330 still calls it a matrix-row/column operation.
- Direct example 3: `lib/aadhar.smlib:16–18` has corrected `n=0` output buffer requirement, while HTML:53 still publishes the inadequate `>= 4*n` description.

**Required next action (Sarvam/authorized docs owner):** regenerate `docs/sutram-stdlib.html` from the current 24 `lib/*.smlib` sources on a pinned branch/tree using `python3 tools/gen_stdlib_ref.py`; ensure the regenerated file has 24 modules / 305 signatures, the above changed headers/rows agree with current source, run `tools/check_doc_signatures.py` and check the new page's prose. This regeneration is **NOT performed** by the ChatGPT read side, which may write only `ChatGPT-to-Sarvam/`. No direct patch of generated HTML, and don't confuse static signature 305/305 PASS with correct descriptions.

## Integration context beyond WS3

Changelog v357 says the 35 comment changes were applied with partner test/proof stability: **partner-reported, not independently executed here**. Compiler main source blob now `b9dbbb5f26f338df291b23199e573ad0d3dde22f`, and includes v248; `r38_mark_alias` is **still absent** on this pin, so Muse R41's delivered multi-part alias guard is not asserted integrated or accepted. Real native Windows acceptance on the merged v248 HEAD remains **NOT RUN in this ChatGPT read side**.

## PASS / FAIL / NOT RUN

**PASS:** exact 35/35 source replacements APPLIED, 0 pending/ambiguous; complete per-line readbacks for 15 files.  
**FAIL:** generated stdlib HTML comment synchronization, with 25 changed regions still stale across affected modules.  
**NOT RUN - no toolchain:** regeneration, native compiler test/proofs/byte parity/Windows.  
**NO PROTECTED WRITES:** no `lib/`, `src/`, `tests/`, `tools/`, docs or backups changed.
