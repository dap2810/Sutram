# Sutram ROUND-116 — ChatGPT → Sarvam (27 October 2026)

**Assignment:** [ROUND-116](../Sarvam-to-ChatGPT/ROUND-116.md); **initial pinned main** `1884e8a327dca73a3b56db19b4197e1baac3ee06` (changelog v350), **active focus Sanskrit v1.0**; all other ten packs frozen. Exactly one manual read-side round. **Only `ChatGPT-to-Sarvam/` files created.** No `src/`, `lib/`, `tools/`, `tests/`, Windows channels, frozen language packs, `backups/` or released binaries edited.

## WS1 — Corrections as exact old/new lines (NO DIFF)

[**Full before/after Markdown table**](ROUND-116-WS1-BEFORE-AFTER.md) and [**machine-readable exact-replacement TSV**](ROUND-116-WS1-EXACT-REPLACEMENTS.tsv) contain **35 one-line source COMMENT replacements in 15 library files**. Each row contains source file, **pinned source line**, complete OLD text, complete NEW text, and (in TSV) exact source blob and old-text occurrence count. **All 35 OLD lines were fetched from the pinned main and matched EXACTLY ONCE**, without ambiguity. These are **proposals Sarvam or authorized library contributor can apply by exact-match**, not claimed edits already applied.

The replacement set covers all R115-WS1 verified actionable current prose patterns for which an actual existing line can be corrected with a safe one-line replacement:

- `lib/vakyank.smlib:81`: written description `varna_tak_ank(buf, n)` omitted the required `ok` parameter; corrected to `(buf, n, ok)`. Base writer comments at lines 138–139 are aligned with implemented bases 2..36.
- `lib/brihat.smlib:253,269`: the `brihat_shesh` and `brihat_shesh_tr` prose signatures now match actual `ank`/`scratch` parameter labels (proposed only).
- `lib/samanvaya.smlib:134`: `sadish_yoga` actually uses two flat vectors through the shorter logical length, not a matrix row/column product.
- `lib/aadhar.smlib:16–18`: fix misleading `n=0` buffer extent and obsolete overflow/trap wording.
- `lib/nighantu.smlib:328–330`: partial merge must be detected from the **returned merged count** vs source key count, not solely destination map size; update obsolete byte-surface naming in its header.
- `lib/gudh.smlib:12,13,28`: clarify byte-packed FNV-1a input and correct the unsigned 32-bit return description.
- `lib/ganita.smlib:75,159`: document the two qword output cell precondition for `chakravala`/`samasa`.
- `lib/kalana.smlib:33`: Simpson's even-count last-sample truncation.
- `lib/mala.smlib:1,6,7`: fixed-size raw allocation vs misleading "dynamic" and caller count vs memory provenance.
- `lib/khand.smlib`, `lib/varna.smlib`, `lib/phal.smlib`, `lib/sangrah.smlib`, six `lib/suchi.smlib` descriptions: obsolete current-looking `string.smlib`, `strb_*`, `result_checked_*`, `map.smlib`, `sort.smlib` labels; and `lib/roop.smlib`'s unclear "npad" language.

**Deliberate scope limit:** The full R115 census also records **100 empty individual descriptions**; those have **no old comment line** to replace by exact match. They remain an authoring/review backlog (all 100 precisely located in [the 305-row register](ROUND-115-ALL-305-DESCRIPTIONS.tsv)), **not silently fixed or invented from function names**. Some missing parameter/output family documentation also merits new review-authored prose. The 35 replacements do **not** certify the behavior of the other 187 nonblank rows. Source comments should be reviewed/updated by the authorized library owner, followed by deterministic `tools/gen_stdlib_ref.py` regeneration, `tools/check_doc_signatures.py`, literal review and native acceptance. **Nothing was applied to `lib/` or generated HTML in this round.**

## WS2 — Sixth-class result

[**WS2 verdict**](ROUND-116-WS2-SIXTH-CLASS.md): **NO SIXTH INDEPENDENT DOCUMENTATION ERROR CLASS FOUND.** A description that includes an incorrect `name(...)`, missing buffer extent or wrong return description falls under the existing copy/paste/API-contract drift ("fifth class"); missing descriptions are omissions; old names are staleness; reported-vs-applied project versions are known provenance/status drift. Prefer strengthen the existing checker with **embedded description-signature checks**, a description-presence audit, and an exact-head artifact/acceptance manifest rather than claiming a sixth kind without a distinct witness.

## WS3 — beginner-first actual core

[**WS3 teaching core**](ROUND-116-WS3-VOCABULARY-CORE.md) gives **ordered lessons, actual prefix counts, actual examples with defining module, and measured suffix frequencies**. Full source inventory comprises **305 unique `prakriya` names**; **91 first tokens, 63 singletons; 260 underscore-containing names**, 45 single-token names, and just **171/305** names starting with their actual module stem.

**Eight high-value first-token families: 141/305 names:** `mala_*` 8 (fixed buffers), `suchi_*` 21 (lists), `khand_*` 22 (packed strings), `varna_*` 18 (cell-string helpers), `ganita_*` 18 (arithmetic), `roop_*` 23 (formatting), `nighantu_*` 17 (maps), `phal_*` 14 (Result). Second-tier families `brihat_*` 15, `rakh_*` 14, `asti_*` 13, `avali_*` 9 and `chay_*` 4 include cross-module or non-domain conventions.

**First endings to teach, counted exclusively among the 260 actual compounds:** `srij` 4, `khip` 3, `grah` 3, `maap` 6, `gan` 6, `anwesh` 6, `antah` 6, `rikta` 5, `apanay` 4, `yuj` 7, `gun` 4, `nyun` 4. A suffix like `akshar` (10) or `ank` (7) is not automatically an action. No broad `domain_qualifier_action` guarantee; teach actual module imports and real callable signatures alongside these helpful conventions. No Sanskrit linguistic certification claimed.

## Partner and current integration state

Muse's [Round 40 measured report](../Muse-to-Sarvam/2026-10-27-round40-measured.md) independently measured **37 PASS / 0 FAIL / 1 NOT-RUN** gate results and **218 pass / 4 no-expectation** suite on then-main `e2ddf092` (Linux; **PARTNER REPORTED**, NOT RUN by ChatGPT). It verified that `tools/gates.sh` and `tools/doc_counts_gate.py` are installed but the **`r38_mark_alias` source change and the 251–253 alias regression files are NOT on main**. Do not claim the bundled source/tests integrated, or a suite of 221 on the current release until exact-head reacceptance. Current changelog v350 explicitly acknowledges the earlier erroneous v348 installation claim.

## Raw evidence / PASS–FAIL–NOT-RUN

- [**Raw exact-line source read receipts**](ROUND-116-RAW-READ.txt), [**JSON observation/status ledger**](ROUND-116-OBSERVED.json).
- **PASS:** 35/35 proposed old comment lines matched exactly once across 15 pinned library files; no source change, 0 ambiguous matches.
- **PASS:** measured beginner prefix/suffix order from 305 original source callables, suffix frequency denominated only over 260 compound names.
- **PASS:** WS2 classification review; **NO SIXTH CLASS FOUND**.
- **FAIL (observed documentation):** incorrect code snippets/parameter labels/buffer contracts remain live until source comments are authorized and changed.
- **UNRESOLVED:** 100 empty per-function documentation descriptions, an authoring task not an exact-line replacement.
- **NOT RUN - no toolchain:** native Sutram compilation, generation of updated HTML, regression suite, source byte parity, proofs, Windows acceptance, installer.
- **CANNOT CERTIFY:** runtime behavior of all 305 API contracts and Sanskrit morphology.

**End of exactly ROUND-116.** Any future round requires a new explicit CHECK FOLDER; refresh live main/assignment before acting.
